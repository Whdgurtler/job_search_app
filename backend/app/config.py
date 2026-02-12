"""Backend configuration — reads from environment variables."""
import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    database_url: str = "postgresql+asyncpg://jobsearch:localdev@localhost:5432/jobsearch"
    database_url_sync: str = "postgresql://jobsearch:localdev@localhost:5432/jobsearch"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Firebase
    firebase_credentials_path: str = ""
    firebase_project_id: str = ""

    # Google Cloud Storage
    gcs_bucket_name: str = "job-search-resumes"
    gcs_credentials_path: str = ""

    # LLM (passed through to existing llm_analyzer.py)
    llm_provider: str = "huggingface"
    llm_model: str = "Qwen/Qwen2.5-72B-Instruct"
    huggingface_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # App
    api_version: str = "1.0.0"
    debug: bool = False
    allowed_origins: list[str] = ["*"]
    max_resume_size_mb: int = 10
    free_tier_scrape_quota: int = 5

    # Project root (parent of backend/)
    project_root: str = str(Path(__file__).parent.parent.parent)

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
