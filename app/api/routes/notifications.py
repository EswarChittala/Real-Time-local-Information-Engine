from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.location_repository import LocationRepository
from app.models.user_preference import UserPreference
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class PreferencePayload(BaseModel):
    user_phone: str = Field(..., description="User phone number")
    category: str = Field(..., description="Category, e.g. TRAFFIC")
    location_name: str = Field(..., description="Location name, e.g. Begumpet")
    notification_enabled: bool = True

class NotificationItem(BaseModel):
    id: int
    message: str
    channel: str
    status: str

@router.post("/preferences", status_code=status.HTTP_200_OK)
def update_preference(
    payload: PreferencePayload,
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    loc_repo = LocationRepository(db)

    user = user_repo.get_or_create(payload.user_phone)
    location = loc_repo.get_or_create(payload.location_name)

    # Check existing preference
    pref = (
        db.query(UserPreference)
        .filter_by(user_id=user.id, category=payload.category.upper(), location_id=location.id)
        .first()
    )
    if pref:
        pref.notification_enabled = payload.notification_enabled
    else:
        pref = UserPreference(
            user_id=user.id,
            category=payload.category.upper(),
            location_id=location.id,
            notification_enabled=payload.notification_enabled
        )
        db.add(pref)

    # Enable user notifications overall
    user.opted_in_notifications = True
    db.commit()

    return {
        "status": "success",
        "user_phone": user.phone_number,
        "category": payload.category.upper(),
        "location": location.name,
        "notification_enabled": payload.notification_enabled
    }

@router.get("/user/{phone}", response_model=List[NotificationItem])
def get_user_notifications(phone: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    notifs = (
        db.query(Notification)
        .filter_by(user_id=user.id)
        .order_by(Notification.sent_at.desc())
        .limit(20)
        .all()
    )
    return [
        NotificationItem(
            id=n.id,
            message=n.message,
            channel=n.channel,
            status=n.status
        )
        for n in notifs
    ]
