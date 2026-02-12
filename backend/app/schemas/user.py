"""User request/response schemas."""
import uuid
from datetime import date, datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Sent after Firebase client-side signup."""
    email: str
    display_name: str | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None
    subscription_tier: str
    scrape_quota_remaining: int
    quota_reset_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = None
