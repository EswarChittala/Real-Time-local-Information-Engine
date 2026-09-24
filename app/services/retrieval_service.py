from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.observation import Observation
from app.repositories.observation_repository import ObservationRepository
from app.core.config import settings

class RetrievalService:
    def __init__(self, db: Session):
        self.repo = ObservationRepository(db)

    def get_max_age_for_category(self, category: str) -> int:
        cat_upper = category.upper()
        if cat_upper == "TRAFFIC":
            return settings.traffic_report_max_age_minutes
        elif cat_upper == "SHOP":
            return settings.shop_report_max_age_minutes
        return settings.default_report_max_age_minutes

    def retrieve_fresh_observations(
        self,
        category: str,
        location_id: int,
        custom_max_age: Optional[int] = None
    ) -> List[Observation]:
        max_age = custom_max_age or self.get_max_age_for_category(category)
        return self.repo.get_recent(
            category=category,
            location_id=location_id,
            max_age_minutes=max_age
        )
