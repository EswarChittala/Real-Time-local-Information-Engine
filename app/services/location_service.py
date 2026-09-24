from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.location import Location
from app.repositories.location_repository import LocationRepository

class LocationService:
    def __init__(self, db: Session):
        self.repo = LocationRepository(db)

    def resolve_location(self, location_id: Optional[int] = None, location_name: Optional[str] = None, text: Optional[str] = None) -> Optional[Location]:
        if location_id:
            return self.repo.get_by_id(location_id)
        if location_name:
            loc = self.repo.get_by_name(location_name)
            if loc:
                return loc
            return self.repo.get_or_create(location_name)
        if text:
            return self.repo.find_in_text(text)
        return None

    def get_or_create(self, name: str) -> Location:
        return self.repo.get_or_create(name)

    def list_all(self) -> List[Location]:
        return self.repo.list_all()
