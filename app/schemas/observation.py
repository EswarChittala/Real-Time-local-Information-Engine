from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ObservationBase(BaseModel):
    category: str = Field(..., description="Category: TRAFFIC, SHOP, ROAD, WATER, POWER")
    event_type: str = Field(default="STATUS", description="Event type or attribute: CONDITION, STATUS, OUTAGE")
    value_state: str = Field(..., description="Value or state: HEAVY, CLEAR, OPEN, CLOSED, BLOCKED")
    raw_message: str = Field(..., description="Original raw report message")
    source: str = Field(default="WHATSAPP", description="Source channel: WHATSAPP, WEB, API")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    observed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class ObservationCreate(ObservationBase):
    reporter_phone: str = Field(..., description="Phone number of reporter")
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    entity_id: Optional[int] = None

class ObservationRead(ObservationBase):
    id: int
    reporter_id: int
    location_id: int
    entity_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ObservationSearchParams(BaseModel):
    category: Optional[str] = None
    location_id: Optional[int] = None
    value_state: Optional[str] = None
    max_age_minutes: Optional[int] = None
