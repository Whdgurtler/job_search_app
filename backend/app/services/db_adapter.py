"""PostgreSQL DB adapter for the orchestrator.

Implements the same interface as the existing db.py module so the
orchestrator can be used in multi-user mode with PostgreSQL instead of SQLite.
"""

import json
from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.job import Job


class PostgresDBAdapter:
    """Drop-in replacement for db.py functions, scoped to a single user."""

    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        # Synchronous wrappers are needed because the orchestrator is sync.
        # We use a separate sync connection approach.
        self._known_urls: set | None = None
        self._known_keys: set | None = None

    def get_known_job_urls(self, company: str) -> set:
        """Return already-known job URLs for this user + company.

        NOTE: Must be called from an async context; the orchestrator
        calls this before spawning the sync scrape. Pre-loaded by
        the Celery task before running the orchestrator.
        """
        if self._known_urls is not None:
            return self._known_urls
        return set()

    def get_known_job_keys(self, company: str) -> set:
        """Return known title|||location keys for this user + company."""
        if self._known_keys is not None:
            return self._known_keys
        return set()

    async def load_known_jobs(self, company: str) -> None:
        """Pre-load known URLs and keys for a company (async, call before sync orchestrator)."""
        result = await self.db.execute(
            select(Job.url, Job.title, Job.location).where(
                Job.user_id == self.user_id,
                Job.company == company,
            )
        )
        rows = result.all()
        self._known_urls = {row[0] for row in rows if row[0]}
        self._known_keys = {
            f"{row[1]}|||{row[2]}" for row in rows if row[1]
        }

    @staticmethod
    def _parse_posting_date(raw) -> date | None:
        """Parse posting_date from scraper output into a date object."""
        if raw is None:
            return None
        if isinstance(raw, date):
            return raw
        if isinstance(raw, datetime):
            return raw.date()
        if isinstance(raw, str):
            raw = raw.strip()
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
                try:
                    return datetime.strptime(raw, fmt).date()
                except ValueError:
                    continue
        return None

    async def save_jobs(self, jobs: list[dict], scraped_date: date | None = None) -> dict:
        """Save scraped jobs to PostgreSQL with upsert logic.

        Returns {"inserted": int, "updated": int, "skipped": int}.
        """
        if not scraped_date:
            scraped_date = date.today()

        inserted = 0
        updated = 0
        skipped = 0
        today = date.today()

        for job_data in jobs:
            url = job_data.get("url", "")
            title = job_data.get("title", "")
            company = job_data.get("company", "")
            location = job_data.get("location", "")

            # Try to find existing job by URL
            existing = None
            if url:
                result = await self.db.execute(
                    select(Job).where(
                        Job.user_id == self.user_id,
                        Job.url == url,
                    )
                )
                existing = result.scalar_one_or_none()

            # Fallback: match by title + company + location
            if not existing and title and company:
                result = await self.db.execute(
                    select(Job).where(
                        Job.user_id == self.user_id,
                        Job.title == title,
                        Job.company == company,
                        Job.location == location,
                    )
                )
                existing = result.scalar_one_or_none()

            if existing:
                # Update existing job
                existing.last_seen = today
                existing.match_score = job_data.get("match_score", existing.match_score)
                existing.skill_match = job_data.get("skill_match", existing.skill_match)
                existing.level_match = job_data.get("level_match", existing.level_match)
                existing.recommendation = job_data.get("recommendation", existing.recommendation)
                existing.level_assessment = job_data.get("level_assessment", existing.level_assessment)
                existing.matched_skills = job_data.get("matched_skills", existing.matched_skills)
                existing.missing_skills = job_data.get("missing_skills", existing.missing_skills)
                existing.scraped_date = scraped_date
                # Backfill posting_date if we have it now and didn't before
                parsed_date = self._parse_posting_date(job_data.get("posting_date"))
                if parsed_date and not existing.posting_date:
                    existing.posting_date = parsed_date
                updated += 1
            else:
                # Insert new job
                try:
                    job = Job(
                        user_id=self.user_id,
                        title=title,
                        company=company,
                        location=location,
                        is_remote=job_data.get("is_remote", False),
                        url=url or None,
                        description=job_data.get("description"),
                        department=job_data.get("department"),
                        source=job_data.get("source"),
                        posting_date=self._parse_posting_date(job_data.get("posting_date")),
                        first_seen=today,
                        last_seen=today,
                        match_score=job_data.get("match_score"),
                        skill_match=job_data.get("skill_match"),
                        level_match=job_data.get("level_match"),
                        recommendation=job_data.get("recommendation"),
                        level_assessment=job_data.get("level_assessment"),
                        matched_skills=job_data.get("matched_skills", []),
                        missing_skills=job_data.get("missing_skills", []),
                        scraped_date=scraped_date,
                    )
                    self.db.add(job)
                    await self.db.flush()
                    inserted += 1
                except IntegrityError:
                    await self.db.rollback()
                    skipped += 1

        await self.db.commit()
        return {"inserted": inserted, "updated": updated, "skipped": skipped}

    def clear_cache(self) -> None:
        """Clear pre-loaded caches (call between companies)."""
        self._known_urls = None
        self._known_keys = None
