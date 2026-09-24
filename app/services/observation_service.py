from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.observation import Observation
from app.schemas.observation import ObservationCreate, ObservationRead
from app.repositories.user_repository import UserRepository
from app.repositories.observation_repository import ObservationRepository
from app.services.location_service import LocationService

class ObservationService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.obs_repo = ObservationRepository(db)
        self.location_service = LocationService(db)

    def record_observation(self, data: ObservationCreate) -> Observation:
        # 1. Resolve user
        user = self.user_repo.get_or_create(phone=data.reporter_phone)

        # 2. Resolve location
        location = self.location_service.resolve_location(
            location_id=data.location_id,
            location_name=data.location_name,
            text=data.raw_message
        )
        if not location:
            # Fallback to create location if name provided, or default
            loc_name = data.location_name or "General"
            location = self.location_service.get_or_create(loc_name)

        # 3. Create observation
        obs = Observation(
            reporter_id=user.id,
            category=data.category.upper(),
            event_type=data.event_type.upper(),
            entity_id=data.entity_id,
            location_id=location.id,
            value_state=data.value_state.upper(),
            raw_message=data.raw_message,
            source=data.source,
            confidence=data.confidence,
            observed_at=data.observed_at or datetime.now(timezone.utc),
            expires_at=data.expires_at
        )

        return self.obs_repo.create(obs)

    def search_observations(
        self,
        category: Optional[str] = None,
        location_id: Optional[int] = None,
        max_age_minutes: Optional[int] = 60,
        value_state: Optional[str] = None,
        limit: int = 50
    ) -> List[Observation]:
        return self.obs_repo.get_recent(
            category=category,
            location_id=location_id,
            max_age_minutes=max_age_minutes,
            value_state=value_state,
            limit=limit
        )
