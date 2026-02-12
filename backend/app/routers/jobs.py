"""Jobs router — list, detail, bookmark, stats."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.job import Job
from app.schemas.job import (
    JobResponse, JobListResponse, JobStatsResponse,
    BookmarkUpdate, AppliedUpdate,
)

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    company: str | None = None,
    remote_only: bool = False,
    min_score: float | None = None,
    recommendation: str | None = None,
    sort_by: str = Query("last_seen", pattern="^(last_seen|match_score|company|title)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    search: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List jobs with filters and pagination."""
    query = select(Job).where(Job.user_id == user.id)

    if company:
        query = query.where(Job.company == company)
    if remote_only:
        query = query.where(Job.is_remote == True)
    if min_score is not None:
        query = query.where(Job.match_score >= min_score)
    if recommendation:
        query = query.where(Job.recommendation == recommendation)
    if search:
        query = query.where(Job.title.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Sort
    sort_col = getattr(Job, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    # Paginate
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return JobListResponse(jobs=jobs, total=total, page=page, per_page=per_page)


@router.get("/stats", response_model=JobStatsResponse)
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get summary stats for the current user's jobs."""
    base = select(Job).where(Job.user_id == user.id)

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    strong = (await db.execute(
        select(func.count()).where(Job.user_id == user.id, Job.recommendation == "strong")
    )).scalar() or 0
    moderate = (await db.execute(
        select(func.count()).where(Job.user_id == user.id, Job.recommendation == "moderate")
    )).scalar() or 0
    weak = total - strong - moderate
    remote = (await db.execute(
        select(func.count()).where(Job.user_id == user.id, Job.is_remote == True)
    )).scalar() or 0
    companies = (await db.execute(
        select(func.count(func.distinct(Job.company))).where(Job.user_id == user.id)
    )).scalar() or 0
    latest = (await db.execute(
        select(func.max(Job.last_seen)).where(Job.user_id == user.id)
    )).scalar()

    return JobStatsResponse(
        total_jobs=total, strong_matches=strong, moderate_matches=moderate,
        weak_matches=weak, remote_jobs=remote, companies=companies,
        latest_scrape=latest,
    )


@router.get("/companies", response_model=list[str])
async def get_companies(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get distinct company names."""
    result = await db.execute(
        select(func.distinct(Job.company))
        .where(Job.user_id == user.id)
        .order_by(Job.company)
    )
    return [row[0] for row in result.all()]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single job's full details."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}/bookmark", response_model=JobResponse)
async def toggle_bookmark(
    job_id: UUID,
    body: BookmarkUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle bookmark on a job."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_bookmarked = body.is_bookmarked
    await db.flush()
    await db.refresh(job)
    return job


@router.patch("/{job_id}/applied", response_model=JobResponse)
async def mark_applied(
    job_id: UUID,
    body: AppliedUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a job as applied."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_applied = body.is_applied
    await db.flush()
    await db.refresh(job)
    return job
