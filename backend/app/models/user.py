"""User model."""
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Boolean, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    firebase_uid: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subscription_tier: Mapped[str] = mapped_column(
        String(20), default="free"
    )
    scrape_quota_remaining: Mapped[int] = mapped_column(Integer, default=5)
    quota_reset_date: Mapped[date | None] = mapped_column(Date)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    scrape_configs = relationship("ScrapeConfig", back_populates="user", cascade="all, delete-orphan")
    scrape_runs = relationship("ScrapeRun", back_populates="user", cascade="all, delete-orphan")
