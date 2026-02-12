"""Job request/response schemas."""
import uuid
from datetime import date, datetime
from pydantic import BaseModel


class JobResponse(BaseModel):
    id: uuid.UUID
    title: str
    company: str
    location: str
    is_remote: bool
    url: str
    match_score: float
    skill_match: float
    level_match: float
    recommendation: str
    level_assessment: str
    matched_skills: list[str]
    missing_skills: list[str]
    notes: str
    posting_date: date | None
    first_seen: date
    last_seen: date
    is_bookmarked: bool
    is_applied: bool

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    per_page: int


class JobStatsResponse(BaseModel):
    total_jobs: int
    strong_matches: int
    moderate_matches: int
    weak_matches: int
    remote_jobs: int
    companies: int
    latest_scrape: date | None


class BookmarkUpdate(BaseModel):
    is_bookmarked: bool


class AppliedUpdate(BaseModel):
    is_applied: bool
