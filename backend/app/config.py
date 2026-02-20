"""Backend configuration — reads from environment variables."""
import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    database_url: str = "postgresql+asyncpg://jobsearch:localdev@localhost:5432/jobsearch"
    database_url_sync: str = "postgresql://jobsearch:localdev@localhost:5432/jobsearch"

    @model_validator(mode="after")
    def fix_database_urls(self):
        """Auto-convert Railway/Render postgres:// URLs to correct drivers."""
        # Async driver
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Sync driver
        if self.database_url_sync.startswith("postgres://"):
            self.database_url_sync = self.database_url_sync.replace("postgres://", "postgresql://", 1)
        return self

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Firebase
    firebase_credentials_path: str = ""
    firebase_credentials_json: str = ""  # Service account JSON as string (for Railway/Heroku)
    firebase_project_id: str = ""

    # Google Cloud Storage
    gcs_bucket_name: str = "job-search-resumes"
    gcs_credentials_path: str = ""

    # LLM (passed through to existing llm_analyzer.py)
    llm_provider: str = "huggingface"
    llm_model: str = "moonshotai/Kimi-K2.5"
    moonshot_api_key: str = ""
    huggingface_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # App
    api_version: str = "1.0.0"
    environment: str = "production"  # development, staging, production
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
