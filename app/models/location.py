from typing import Optional, List
from sqlalchemy import String, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class Location(Base, TimestampMixin):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    radius_meters: Mapped[int] = mapped_column(Integer, default=1000)
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    # Relationships
    entities = relationship("Entity", back_populates="location", cascade="all, delete-orphan")
    observations = relationship("Observation", back_populates="location")
    questions = relationship("Question", back_populates="location")
    preferences = relationship("UserPreference", back_populates="location")
