from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from app.models.observation import Observation
from app.models.notification import Notification
from app.models.user import User
from app.models.user_preference import UserPreference

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.cooldown_minutes = 60

    def find_eligible_recipients(self, observation: Observation) -> List[User]:
        """Find users opted-in explicitly for this category and location."""
        stmt = (
            select(User)
            .join(UserPreference, UserPreference.user_id == User.id)
            .where(
                and_(
                    User.is_active == True,
                    User.id != observation.reporter_id,
                    UserPreference.location_id == observation.location_id,
                    UserPreference.category == observation.category,
                    UserPreference.notification_enabled == True
                )
            )
            .distinct()
        )
        return list(self.db.execute(stmt).scalars().all())

    def is_in_cooldown(self, user_id: int, observation: Observation) -> bool:
        """Check if user received an alert for this location and category within the cooldown window."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.cooldown_minutes)
        stmt = (
            select(Notification)
            .join(Observation, Observation.id == Notification.observation_id)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.status == "SENT",
                    Notification.sent_at >= cutoff,
                    Observation.location_id == observation.location_id,
                    Observation.category == observation.category
                )
            )
            .order_by(desc(Notification.sent_at))
            .limit(1)
        )
        recent_notif = self.db.execute(stmt).scalar_one_or_none()
        return recent_notif is not None

    def process_observation_notifications(self, observation: Observation) -> List[Notification]:
        recipients = self.find_eligible_recipients(observation)
        created_notifications = []

        loc_name = observation.location.name if observation.location else "your area"
        alert_msg = (
            f"🔔 Alert for {loc_name}: {observation.value_state} {observation.category.lower()} reported. "
            f"Note: '{observation.raw_message}'"
        )

        for user in recipients:
            if self.is_in_cooldown(user.id, observation):
                # Record skipped due to cooldown
                notif = Notification(
                    user_id=user.id,
                    observation_id=observation.id,
                    message=alert_msg,
                    status="SKIPPED_COOLDOWN"
                )
            else:
                notif = Notification(
                    user_id=user.id,
                    observation_id=observation.id,
                    message=alert_msg,
                    status="SENT"
                )
            self.db.add(notif)
            created_notifications.append(notif)

        self.db.commit()
        return created_notifications
