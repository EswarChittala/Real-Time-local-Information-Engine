from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class LocationBase(BaseModel):
    name: str = Field(..., description="Location name, e.g. Begumpet")
    slug: str = Field(..., description="URL-friendly slug, e.g. begumpet")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: int = Field(default=1000, description="Radius in meters")
    aliases: List[str] = Field(default_factory=list, description="Common aliases/spellings")

class LocationCreate(LocationBase):
    pass

class LocationRead(LocationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
