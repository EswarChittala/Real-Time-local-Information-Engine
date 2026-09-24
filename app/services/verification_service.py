from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.notification import Notification
from app.models.location import Location
from app.models.question import Question

class VerificationService:
    def __init__(self, db: Session):
        self.db = db

    def find_eligible_verifiers(
        self,
        category: str,
        location_id: int,
        exclude_user_id: int,
        limit: int = 5
    ) -> List[User]:
        """
        Finds users who have opted into notifications or preferences for this location/category,
        excluding the user who asked the question.
        """
        # Query users with matching preference or general opt-in
        stmt = (
            select(User)
            .join(UserPreference, UserPreference.user_id == User.id, isouter=True)
            .where(
                and_(
                    User.id != exclude_user_id,
                    User.is_active == True,
                    (User.opted_in_notifications == True) | (
                        (UserPreference.location_id == location_id) &
                        (UserPreference.notification_enabled == True)
                    )
                )
            )
            .distinct()
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def request_verification(
        self,
        question_id: int,
        category: str,
        location_id: int,
        requester_id: int
    ) -> int:
        """
        Dispatches verification requests to eligible users and updates question status.
        """
        location = self.db.get(Location, location_id)
        loc_name = location.name if location else "your area"

        verifiers = self.find_eligible_verifiers(
            category=category,
            location_id=location_id,
            exclude_user_id=requester_id
        )

        if not verifiers:
            return 0

        # Mark question as PENDING_VERIFICATION
        question = self.db.get(Question, question_id)
        if question:
            question.status = "PENDING_VERIFICATION"

        prompt_message = (
            f"📍 Quick verification needed: A community member is asking about {category.lower()} "
            f"near {loc_name}. If you are nearby, could you report current conditions?"
        )

        for verifier in verifiers:
            notif = Notification(
                user_id=verifier.id,
                message=prompt_message,
                channel="WHATSAPP",
                status="SENT"
            )
            self.db.add(notif)

        self.db.commit()
        return len(verifiers)
