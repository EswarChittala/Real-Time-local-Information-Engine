from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    observation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("observations.id", ondelete="SET NULL"), nullable=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="WHATSAPP")
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    status: Mapped[str] = mapped_column(String(50), default="SENT")  # 'PENDING', 'SENT', 'FAILED', 'SKIPPED_COOLDOWN'

    # Relationships
    user = relationship("User", back_populates="notifications")
    observation = relationship("Observation", back_populates="notifications")
