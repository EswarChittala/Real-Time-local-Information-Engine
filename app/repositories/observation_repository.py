from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from app.models.observation import Observation

class ObservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, observation: Observation) -> Observation:
        self.db.add(observation)
        self.db.commit()
        self.db.refresh(observation)
        return observation

    def get_by_id(self, observation_id: int) -> Optional[Observation]:
        return self.db.get(Observation, observation_id)

    def get_recent(
        self,
        category: Optional[str] = None,
        location_id: Optional[int] = None,
        max_age_minutes: Optional[int] = 60,
        value_state: Optional[str] = None,
        limit: int = 50
    ) -> List[Observation]:
        query = select(Observation)
        conditions = []

        if max_age_minutes:
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
            conditions.append(Observation.observed_at >= cutoff)

        if category:
            conditions.append(Observation.category == category.upper())

        if location_id:
            conditions.append(Observation.location_id == location_id)

        if value_state:
            conditions.append(Observation.value_state == value_state.upper())

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(Observation.observed_at)).limit(limit)
        return list(self.db.execute(query).scalars().all())
