from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class Observation(Base, TimestampMixin):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reporter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # e.g., 'TRAFFIC', 'SHOP', 'ROAD', 'WATER'
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)            # e.g., 'STATUS', 'CONDITION'
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    value_state: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., 'HEAVY', 'CLEAR', 'OPEN', 'BLOCKED'
    raw_message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="WHATSAPP")              # 'WHATSAPP', 'WEB', 'API'
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    reporter = relationship("User", back_populates="observations")
    location = relationship("Location", back_populates="observations")
    entity = relationship("Entity", back_populates="observations")
    notifications = relationship("Notification", back_populates="observation")
