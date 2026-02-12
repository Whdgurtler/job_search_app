"""Job model — mirrors existing SQLite schema with user scoping."""
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import (
    String, Boolean, Text, Float, Date, ForeignKey, Index, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    company: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, default="Not specified")
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    url: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(Text, default="")
    posting_date: Mapped[date | None] = mapped_column(Date)
    first_seen: Mapped[date] = mapped_column(Date, nullable=False)
    last_seen: Mapped[date] = mapped_column(Date, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, default=0)
    skill_match: Mapped[float] = mapped_column(Float, default=0)
    level_match: Mapped[float] = mapped_column(Float, default=0)
    recommendation: Mapped[str] = mapped_column(String(20), default="")
    level_assessment: Mapped[str] = mapped_column(String(30), default="")
    matched_skills: Mapped[list | None] = mapped_column(JSONB, default=list)
    missing_skills: Mapped[list | None] = mapped_column(JSONB, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")
    scraped_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="jobs")

    __table_args__ = (
        # Per-user URL dedup
        Index("idx_jobs_user_url", "user_id", "url", unique=True,
              postgresql_where=("url != ''")),
        # Per-user fallback dedup (no URL)
        Index("idx_jobs_user_title_co_loc", "user_id", "title", "company", "location",
              unique=True, postgresql_where=("url = ''")),
        # Query indexes
        Index("idx_jobs_user_date", "user_id", "last_seen", "match_score"),
        Index("idx_jobs_user_company", "user_id", "company"),
    )
