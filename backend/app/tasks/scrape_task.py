"""Celery task that runs the job scraper orchestrator for a user."""

import asyncio
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

from app.tasks.celery_app import celery_app

# Add project root so we can import existing agents
PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _get_async_session():
    """Create a standalone async session for use inside Celery workers."""
    from app.db.session import async_session_factory
    return async_session_factory()


async def _load_run_context(run_id: str, user_id: str, config_id: str):
    """Load scrape config + active resume from DB."""
    from sqlalchemy import select
    from app.models.scrape import ScrapeConfig
    from app.models.resume import Resume

    async with _get_async_session() as db:
        result = await db.execute(
            select(ScrapeConfig).where(ScrapeConfig.id == UUID(config_id))
        )
        config = result.scalar_one_or_none()
        if not config:
            raise ValueError(f"Scrape config {config_id} not found")

        result = await db.execute(
            select(Resume).where(
                Resume.user_id == UUID(user_id),
                Resume.is_active == True,
            )
        )
        resume = result.scalar_one_or_none()

        return {
            "keywords": config.keywords,
            "companies": list(config.companies) if config.companies else [],
            "employment_areas": list(config.employment_areas) if config.employment_areas else [],
            "location": config.location or "",
            "resume_data": resume.parsed_data if resume else None,
        }


async def _update_run(run_id: str, **kwargs):
    """Update scrape run fields in DB."""
    from sqlalchemy import select
    from app.models.scrape import ScrapeRun

    async with _get_async_session() as db:
        result = await db.execute(
            select(ScrapeRun).where(ScrapeRun.id == UUID(run_id))
        )
        run = result.scalar_one_or_none()
        if run:
            for key, value in kwargs.items():
                if hasattr(run, key):
                    setattr(run, key, value)
            await db.commit()


async def _save_jobs_for_user(user_id: str, jobs: list, scraped_date: str):
    """Save scraped jobs to PostgreSQL via the DB adapter."""
    from app.services.db_adapter import PostgresDBAdapter

    async with _get_async_session() as db:
        adapter = PostgresDBAdapter(db, UUID(user_id))
        return await adapter.save_jobs(jobs, scraped_date=scraped_date)


@celery_app.task(bind=True, name="run_scrape", max_retries=1)
def run_scrape(self, run_id: str, user_id: str, config_id: str):
    """Execute a full scrape run for a user.

    1. Load user's active resume and scrape config from PostgreSQL
    2. Create JobScraperOrchestrator
    3. Run orchestrator.search_multiple_companies()
    4. Save results to PostgreSQL jobs table
    5. Update scrape_runs status
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_time = time.time()

    try:
        # Mark as running
        loop.run_until_complete(_update_run(
            run_id,
            status="running",
            started_at=datetime.now(timezone.utc),
        ))

        # Load context
        context = loop.run_until_complete(
            _load_run_context(run_id, user_id, config_id)
        )

        # Set up LLM (reuse existing config)
        from config import PROVIDER, MODEL
        from llm_analyzer import LLMAnalyzer
        llm = LLMAnalyzer(provider=PROVIDER, model=MODEL)

        # Create orchestrator (sync — manages its own Selenium driver)
        from agents.orchestrator import JobScraperOrchestrator
        orchestrator = JobScraperOrchestrator(llm=llm, headless=True)

        # Run scrape
        companies = context["companies"]
        keywords = context["keywords"]
        employment_areas = context["employment_areas"]
        resume_data = context["resume_data"]
        today = date.today().isoformat()

        all_jobs = []
        errors = []
        completed_companies = 0

        if companies:
            results = orchestrator.search_multiple_companies(
                companies=companies,
                keywords=keywords,
                location=context["location"],
                resume_data=resume_data,
            )
        elif employment_areas:
            results = []
            for area in employment_areas:
                area_results = orchestrator.search_multiple_companies(
                    employment_area=area,
                    keywords=keywords,
                    location=context["location"],
                    resume_data=resume_data,
                )
                results.extend(area_results)
        else:
            results = []

        # Collect results
        for result in results:
            completed_companies += 1
            if result.success:
                all_jobs.extend(result.matched_jobs)
            if result.errors:
                errors.extend([
                    {"company": result.company, "error": str(e)}
                    for e in result.errors
                ])

            # Update progress
            loop.run_until_complete(_update_run(
                run_id,
                progress={
                    "completed_companies": completed_companies,
                    "total_companies": len(companies) if companies else completed_companies,
                    "current_company": result.company,
                    "jobs_so_far": len(all_jobs),
                },
            ))

        # Save all jobs to PostgreSQL
        if all_jobs:
            save_result = loop.run_until_complete(
                _save_jobs_for_user(user_id, all_jobs, today)
            )
        else:
            save_result = {"inserted": 0, "updated": 0}

        duration = time.time() - start_time

        # Mark completed
        loop.run_until_complete(_update_run(
            run_id,
            status="completed",
            total_jobs=len(all_jobs),
            new_jobs=save_result["inserted"],
            updated_jobs=save_result["updated"],
            errors=errors if errors else None,
            duration_seconds=duration,
            completed_at=datetime.now(timezone.utc),
        ))

        return {
            "run_id": run_id,
            "status": "completed",
            "total_jobs": len(all_jobs),
            "new_jobs": save_result["inserted"],
            "updated_jobs": save_result["updated"],
            "duration": duration,
        }

    except Exception as exc:
        duration = time.time() - start_time
        loop.run_until_complete(_update_run(
            run_id,
            status="failed",
            errors=[{"error": str(exc)}],
            duration_seconds=duration,
            completed_at=datetime.now(timezone.utc),
        ))
        raise
    finally:
        loop.close()
