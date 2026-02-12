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
from app.services.job_service import JobService

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    company: str | None = None,
    remote_only: bool = False,
    min_score: float | None = None,
    recommendation: str | None = None,
    sort_by: str = Query("date", pattern="^(date|score|company)$"),
    search: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List jobs with filters and pagination."""
    service = JobService(db)
    jobs, total = await service.list_jobs(
        user.id,
        page=page,
        per_page=per_page,
        company=company,
        remote_only=remote_only,
        min_score=min_score,
        recommendation=recommendation,
        sort_by=sort_by,
        search=search,
    )
    return JobListResponse(jobs=jobs, total=total, page=page, per_page=per_page)


@router.get("/stats", response_model=JobStatsResponse)
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get summary stats for the current user's jobs."""
    service = JobService(db)
    stats = await service.get_stats(user.id)
    return stats


@router.get("/companies", response_model=list[str])
async def get_companies(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get distinct company names."""
    service = JobService(db)
    return await service.get_companies(user.id)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single job's full details."""
    service = JobService(db)
    job = await service.get_job(user.id, job_id)
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
    service = JobService(db)
    job = await service.update_bookmark(user.id, job_id, body.is_bookmarked)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
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
