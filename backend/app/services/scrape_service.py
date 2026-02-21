"""Scrape service — config management, run triggering, and status tracking."""

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.scrape import ScrapeConfig, ScrapeRun
from ..models.user import User


class ScrapeService:
    """Handles scrape configuration, triggering, and run tracking."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Scrape Configs ──────────────────────────────────────────

    async def create_config(
        self,
        user_id: UUID,
        name: str,
        keywords: str,
        companies: list[str],
        employment_areas: list[str] | None = None,
        location: str | None = None,
        is_default: bool = False,
    ) -> ScrapeConfig:
        """Create a scrape configuration for a user."""
        if is_default:
            await self._clear_default_configs(user_id)

        config = ScrapeConfig(
            user_id=user_id,
            name=name,
            keywords=keywords,
            companies=companies,
            employment_areas=employment_areas or [],
            location=location,
            is_default=is_default,
        )
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def list_configs(self, user_id: UUID) -> list[ScrapeConfig]:
        """List all scrape configs for a user."""
        result = await self.db.execute(
            select(ScrapeConfig)
            .where(ScrapeConfig.user_id == user_id)
            .order_by(ScrapeConfig.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_config(self, user_id: UUID, config_id: UUID) -> ScrapeConfig | None:
        """Get a specific scrape config."""
        result = await self.db.execute(
            select(ScrapeConfig).where(
                ScrapeConfig.id == config_id,
                ScrapeConfig.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_config(
        self,
        user_id: UUID,
        config_id: UUID,
        **updates,
    ) -> ScrapeConfig | None:
        """Update a scrape config."""
        config = await self.get_config(user_id, config_id)
        if not config:
            return None

        if updates.get("is_default"):
            await self._clear_default_configs(user_id)

        for key, value in updates.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)

        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def delete_config(self, user_id: UUID, config_id: UUID) -> bool:
        """Delete a scrape config."""
        config = await self.get_config(user_id, config_id)
        if not config:
            return False
        await self.db.delete(config)
        await self.db.commit()
        return True

    async def _clear_default_configs(self, user_id: UUID) -> None:
        """Remove default flag from all user's configs."""
        result = await self.db.execute(
            select(ScrapeConfig).where(
                ScrapeConfig.user_id == user_id,
                ScrapeConfig.is_default == True,
            )
        )
        for config in result.scalars().all():
            config.is_default = False

    # ── Scrape Runs ─────────────────────────────────────────────

    async def trigger_scrape(
        self,
        user_id: UUID,
        config_id: UUID | None = None,
        companies: list[str] | None = None,
        keywords: str | None = None,
        employment_areas: list[str] | None = None,
    ) -> ScrapeRun | None:
        """Create a pending scrape run and dispatch to Celery.

        Accepts an optional config_id to load defaults from, plus optional
        overrides (companies, keywords, employment_areas).
        Returns None if quota exhausted.
        """
        # Check user quota
        user = await self.db.get(User, user_id)
        if not user or user.scrape_quota_remaining <= 0:
            return None

        # Load config defaults if provided, allow overrides
        run_companies = companies or []
        run_keywords = keywords or ""
        if config_id:
            config = await self.get_config(user_id, config_id)
            if not config:
                return None
            run_companies = companies if companies else list(config.companies or [])
            run_keywords = keywords if keywords else (config.keywords or "")

        # Decrement quota
        user.scrape_quota_remaining -= 1

        # Create run record
        run = ScrapeRun(
            user_id=user_id,
            config_id=config_id,
            status="pending",
            scraped_date=date.today(),
            companies=run_companies,
            keywords=run_keywords,
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)

        # Dispatch Celery task
        from ..tasks.scrape_task import run_scrape

        task = run_scrape.delay(str(run.id), str(user_id), str(config_id))

        # Store Celery task ID
        run.celery_task_id = task.id
        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(run)

        return run

    async def list_runs(self, user_id: UUID, limit: int = 50) -> list[ScrapeRun]:
        """List recent scrape runs for a user."""
        result = await self.db.execute(
            select(ScrapeRun)
            .where(ScrapeRun.user_id == user_id)
            .order_by(ScrapeRun.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_run(self, user_id: UUID, run_id: UUID) -> ScrapeRun | None:
        """Get a specific scrape run."""
        result = await self.db.execute(
            select(ScrapeRun).where(
                ScrapeRun.id == run_id,
                ScrapeRun.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_run_status(self, user_id: UUID, run_id: UUID) -> dict | None:
        """Get lightweight status data for a scrape run (used by polling endpoint)."""
        run = await self.get_run(user_id, run_id)
        if not run:
            return None
        return {
            "id": run.id,
            "status": run.status,
            "progress": run.progress,
            "total_jobs": run.total_jobs,
            "new_jobs": run.new_jobs,
            "duration_seconds": run.duration_seconds,
        }

    async def update_run_status(
        self,
        run_id: UUID,
        *,
        status: str | None = None,
        total_jobs: int | None = None,
        new_jobs: int | None = None,
        updated_jobs: int | None = None,
        errors: list[dict] | None = None,
        progress: dict | None = None,
        duration_seconds: float | None = None,
    ) -> ScrapeRun | None:
        """Update run status (called by Celery worker)."""
        result = await self.db.execute(
            select(ScrapeRun).where(ScrapeRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            return None

        if status:
            run.status = status
        if total_jobs is not None:
            run.total_jobs = total_jobs
        if new_jobs is not None:
            run.new_jobs = new_jobs
        if updated_jobs is not None:
            run.updated_jobs = updated_jobs
        if errors is not None:
            run.errors = errors
        if progress is not None:
            run.progress = progress
        if duration_seconds is not None:
            run.duration_seconds = duration_seconds

        if status in ("completed", "failed"):
            run.completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(run)
        return run
