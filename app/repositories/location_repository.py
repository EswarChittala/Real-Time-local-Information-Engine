from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.location import Location

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, location_id: int) -> Optional[Location]:
        return self.db.get(Location, location_id)

    def get_by_name(self, name: str) -> Optional[Location]:
        stmt = select(Location).where(func.lower(Location.name) == name.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_or_create(self, name: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Location:
        name_clean = name.strip()
        slug = name_clean.lower().replace(" ", "-")
        location = self.get_by_name(name_clean)
        if not location:
            location = Location(
                name=name_clean,
                slug=slug,
                latitude=latitude,
                longitude=longitude,
                aliases=[name_clean.lower(), slug]
            )
            self.db.add(location)
            self.db.commit()
            self.db.refresh(location)
        return location

    def find_in_text(self, text: str) -> Optional[Location]:
        """Find matching location mentioned inside a natural language query string."""
        text_lower = text.lower()
        locations = self.db.execute(select(Location)).scalars().all()
        for loc in locations:
            if loc.name.lower() in text_lower or loc.slug in text_lower:
                return loc
            if loc.aliases:
                for alias in loc.aliases:
                    if alias.lower() in text_lower:
                        return loc
        return None

    def list_all(self) -> List[Location]:
        return list(self.db.execute(select(Location)).scalars().all())
