from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.db.session import get_db
from app.models.observation import Observation
from app.models.location import Location
from app.models.question import Question

router = APIRouter(prefix="/summary", tags=["Summary"])

@router.get("", response_model=Dict[str, Any])
def get_engine_summary(db: Session = Depends(get_db)):
    total_obs = db.query(func.count(Observation.id)).scalar() or 0
    total_locs = db.query(func.count(Location.id)).scalar() or 0
    total_questions = db.query(func.count(Question.id)).scalar() or 0

    # Count by category
    category_counts = dict(
        db.query(Observation.category, func.count(Observation.id))
        .group_by(Observation.category)
        .all()
    )

    # Latest 5 observations
    latest_obs = (
        db.query(Observation)
        .order_by(Observation.observed_at.desc())
        .limit(5)
        .all()
    )

    return {
        "status": "healthy",
        "total_observations": total_obs,
        "total_locations": total_locs,
        "total_questions_processed": total_questions,
        "observations_by_category": category_counts,
        "supported_categories": ["TRAFFIC", "SHOP", "ROAD", "WATER", "POWER", "GENERAL"],
        "recent_activity": [
            {
                "id": o.id,
                "category": o.category,
                "state": o.value_state,
                "location": o.location.name if o.location else "Unknown",
                "observed_at": o.observed_at.isoformat() if o.observed_at else None
            }
            for o in latest_obs
        ]
    }
