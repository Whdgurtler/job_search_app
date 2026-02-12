"""Scrape configuration and run models."""
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import (
    String, Boolean, Text, Float, Integer, Date, ForeignKey, DateTime, ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ScrapeConfig(Base, TimestampMixin):
    __tablename__ = "scrape_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(100), default="Default")
    keywords: Mapped[str] = mapped_column(Text, default="")
    companies: Mapped[list[str] | None] = mapped_column(ARRAY(Text), default=list)
    employment_areas: Mapped[list[str] | None] = mapped_column(ARRAY(Text), default=list)
    location: Mapped[str] = mapped_column(Text, default="")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="scrape_configs")
    runs = relationship("ScrapeRun", back_populates="config")


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    config_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scrape_configs.id"),
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255))
    scraped_date: Mapped[date] = mapped_column(Date, nullable=False)
    companies: Mapped[list | None] = mapped_column(JSONB, default=list)
    keywords: Mapped[str] = mapped_column(Text, default="")
    total_jobs: Mapped[int] = mapped_column(Integer, default=0)
    new_jobs: Mapped[int] = mapped_column(Integer, default=0)
    updated_jobs: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list | None] = mapped_column(JSONB, default=list)
    progress: Mapped[dict | None] = mapped_column(JSONB)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="scrape_runs")
    config = relationship("ScrapeConfig", back_populates="runs")
