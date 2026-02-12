"""Job service — queries, filtering, stats, and bookmarks."""

from uuid import UUID

from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.job import Job


class JobService:
    """Handles job listing, filtering, stats, and user actions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_jobs(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        per_page: int = 20,
        company: str | None = None,
        remote_only: bool = False,
        min_score: int | None = None,
        recommendation: str | None = None,
        sort_by: str = "date",
        search: str | None = None,
    ) -> tuple[list[Job], int]:
        """Return paginated, filtered jobs with total count."""

        query = select(Job).where(Job.user_id == user_id)
        count_query = select(func.count(Job.id)).where(Job.user_id == user_id)

        # Apply filters
        if company:
            query = query.where(Job.company == company)
            count_query = count_query.where(Job.company == company)
        if remote_only:
            query = query.where(Job.is_remote == True)
            count_query = count_query.where(Job.is_remote == True)
        if min_score is not None:
            query = query.where(Job.match_score >= min_score)
            count_query = count_query.where(Job.match_score >= min_score)
        if recommendation:
            query = query.where(Job.recommendation == recommendation)
            count_query = count_query.where(Job.recommendation == recommendation)
        if search:
            pattern = f"%{search}%"
            search_filter = Job.title.ilike(pattern) | Job.company.ilike(pattern)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Sorting
        if sort_by == "score":
            query = query.order_by(Job.match_score.desc().nullslast(), Job.last_seen.desc())
        elif sort_by == "company":
            query = query.order_by(Job.company.asc(), Job.match_score.desc().nullslast())
        else:  # date
            query = query.order_by(Job.last_seen.desc(), Job.match_score.desc().nullslast())

        # Pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        jobs = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        return jobs, total

    async def get_job(self, user_id: UUID, job_id: UUID) -> Job | None:
        """Get a single job by ID."""
        result = await self.db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_stats(self, user_id: UUID) -> dict:
        """Get summary stats for user's jobs."""
        base = select(Job).where(Job.user_id == user_id)

        # Total count
        total_result = await self.db.execute(
            select(func.count(Job.id)).where(Job.user_id == user_id)
        )
        total = total_result.scalar()

        # Recommendation breakdown
        rec_result = await self.db.execute(
            select(Job.recommendation, func.count(Job.id))
            .where(Job.user_id == user_id)
            .group_by(Job.recommendation)
        )
        rec_counts = {row[0]: row[1] for row in rec_result.all()}

        # Remote count
        remote_result = await self.db.execute(
            select(func.count(Job.id)).where(Job.user_id == user_id, Job.is_remote == True)
        )
        remote_count = remote_result.scalar()

        # Company count
        company_result = await self.db.execute(
            select(func.count(distinct(Job.company))).where(Job.user_id == user_id)
        )
        company_count = company_result.scalar()

        # Latest scrape
        latest_result = await self.db.execute(
            select(func.max(Job.last_seen)).where(Job.user_id == user_id)
        )
        latest_scrape = latest_result.scalar()

        # Bookmarked count
        bookmark_result = await self.db.execute(
            select(func.count(Job.id)).where(Job.user_id == user_id, Job.is_bookmarked == True)
        )
        bookmarked = bookmark_result.scalar()

        return {
            "total_jobs": total,
            "strong_matches": rec_counts.get("Strong Match", 0),
            "moderate_matches": rec_counts.get("Moderate Match", 0),
            "weak_matches": rec_counts.get("Weak Match", 0),
            "remote_jobs": remote_count,
            "companies": company_count,
            "bookmarked": bookmarked,
            "latest_scrape": latest_scrape.isoformat() if latest_scrape else None,
        }

    async def get_companies(self, user_id: UUID) -> list[str]:
        """Get distinct company names for a user."""
        result = await self.db.execute(
            select(distinct(Job.company))
            .where(Job.user_id == user_id)
            .order_by(Job.company)
        )
        return [row[0] for row in result.all()]

    async def toggle_bookmark(self, user_id: UUID, job_id: UUID, is_bookmarked: bool) -> Job | None:
        """Set bookmark status on a job."""
        job = await self.get_job(user_id, job_id)
        if job:
            job.is_bookmarked = is_bookmarked
            await self.db.commit()
            await self.db.refresh(job)
        return job

    async def mark_applied(self, user_id: UUID, job_id: UUID, is_applied: bool) -> Job | None:
        """Set applied status on a job."""
        job = await self.get_job(user_id, job_id)
        if job:
            job.is_applied = is_applied
            await self.db.commit()
            await self.db.refresh(job)
        return job
