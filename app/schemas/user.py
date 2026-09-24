from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    phone_number: str = Field(..., description="Phone number with country code")
    name: Optional[str] = None
    opted_in_notifications: bool = False

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    is_active: bool
    reputation_score: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
