from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.observation import ObservationRead

class QuestionCreate(BaseModel):
    user_phone: str = Field(..., description="Phone number of user asking")
    raw_query: str = Field(..., description="User query, e.g. Is there heavy traffic near Begumpet?")
    location_name: Optional[str] = None
    category: Optional[str] = None

class QuestionRead(BaseModel):
    id: int
    user_id: int
    raw_query: str
    parsed_category: Optional[str] = None
    parsed_location_id: Optional[int] = None
    status: str
    answer_text: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class QuestionAnswerResponse(BaseModel):
    question_id: int
    user_phone: str
    query: str
    category: str
    location_name: Optional[str] = None
    consensus_status: str  # CONFIRMED, REPORTED, UNKNOWN, CONFLICTING
    value_state: Optional[str] = None
    witness_count: int
    answer: str
    recent_observations: List[ObservationRead] = Field(default_factory=list)
