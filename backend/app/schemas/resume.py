"""Resume request/response schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: uuid.UUID
    file_name: str
    file_type: str
    current_title: str | None
    experience_years: float | None
    skills: list[str] | None
    parsed_data: dict | None
    is_active: bool
    uploaded_at: datetime
    parsed_at: datetime | None

    model_config = {"from_attributes": True}


class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]
