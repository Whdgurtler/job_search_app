"""Scrape config and run request/response schemas."""
import uuid
from datetime import date, datetime
from pydantic import BaseModel


# --- Scrape Config ---

class ScrapeConfigCreate(BaseModel):
    name: str = "Default"
    keywords: str = ""
    companies: list[str] = []
    employment_areas: list[str] = []
    location: str = ""
    is_default: bool = False


class ScrapeConfigUpdate(BaseModel):
    name: str | None = None
    keywords: str | None = None
    companies: list[str] | None = None
    employment_areas: list[str] | None = None
    location: str | None = None
    is_default: bool | None = None


class ScrapeConfigResponse(BaseModel):
    id: uuid.UUID
    name: str
    keywords: str
    companies: list[str] | None
    employment_areas: list[str] | None
    location: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Scrape Run ---

class ScrapeRunTrigger(BaseModel):
    """Trigger a manual scrape."""
    config_id: uuid.UUID | None = None
    companies: list[str] | None = None
    keywords: str | None = None
    employment_areas: list[str] | None = None


class ScrapeRunResponse(BaseModel):
    id: uuid.UUID
    status: str
    scraped_date: date
    companies: list[str] | None
    keywords: str
    total_jobs: int
    new_jobs: int
    updated_jobs: int
    errors: list[str] | None
    progress: dict | None
    duration_seconds: float
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScrapeRunStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    progress: dict | None
    total_jobs: int
    new_jobs: int
    duration_seconds: float
