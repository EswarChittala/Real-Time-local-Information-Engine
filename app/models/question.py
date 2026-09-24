from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_query: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    parsed_location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    parsed_entity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("entities.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # 'ANSWERED', 'PENDING_VERIFICATION', 'UNKNOWN'
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="questions")
    location = relationship("Location", back_populates="questions")
