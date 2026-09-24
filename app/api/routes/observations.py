from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.observation import ObservationCreate, ObservationRead
from app.services.observation_service import ObservationService

router = APIRouter(prefix="/observations", tags=["Observations"])

@router.post("", response_model=ObservationRead, status_code=status.HTTP_201_CREATED)
def create_observation(
    data: ObservationCreate,
    db: Session = Depends(get_db)
):
    service = ObservationService(db)
    obs = service.record_observation(data)
    return obs

@router.get("/search", response_model=List[ObservationRead])
def search_observations(
    category: Optional[str] = Query(None, description="Filter by category (e.g. TRAFFIC)"),
    location_id: Optional[int] = Query(None, description="Filter by location id"),
    value_state: Optional[str] = Query(None, description="Filter by state (e.g. HEAVY, CLEAR)"),
    max_age_minutes: Optional[int] = Query(60, description="Max age in minutes"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = ObservationService(db)
    return service.search_observations(
        category=category,
        location_id=location_id,
        value_state=value_state,
        max_age_minutes=max_age_minutes,
        limit=limit
    )
