"""Scrape config and run management router."""
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.scrape import ScrapeConfig, ScrapeRun
from app.schemas.scrape import (
    ScrapeConfigCreate, ScrapeConfigUpdate, ScrapeConfigResponse,
    ScrapeRunTrigger, ScrapeRunResponse, ScrapeRunStatusResponse,
)
from app.services.scrape_service import ScrapeService

router = APIRouter()


# --- Scrape Configs ---

@router.get("/scrape-configs", response_model=list[ScrapeConfigResponse])
async def list_configs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScrapeConfig)
        .where(ScrapeConfig.user_id == user.id)
        .order_by(ScrapeConfig.created_at.desc())
    )
    return result.scalars().all()


@router.post("/scrape-configs", response_model=ScrapeConfigResponse, status_code=201)
async def create_config(
    body: ScrapeConfigCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    config = ScrapeConfig(user_id=user.id, **body.model_dump())
    db.add(config)
    await db.flush()
    await db.refresh(config)
    return config


@router.patch("/scrape-configs/{config_id}", response_model=ScrapeConfigResponse)
async def update_config(
    config_id: UUID,
    body: ScrapeConfigUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScrapeConfig)
        .where(ScrapeConfig.id == config_id, ScrapeConfig.user_id == user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    await db.flush()
    await db.refresh(config)
    return config


@router.delete("/scrape-configs/{config_id}", status_code=204)
async def delete_config(
    config_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScrapeConfig)
        .where(ScrapeConfig.id == config_id, ScrapeConfig.user_id == user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    await db.delete(config)


# --- Scrape Runs ---

@router.post("/scrapes/trigger", response_model=ScrapeRunResponse, status_code=202)
async def trigger_scrape(
    body: ScrapeRunTrigger,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a manual scrape (async via Celery)."""
    # Check quota
    if user.scrape_quota_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly scrape quota exceeded. Upgrade to Pro for more.",
        )

    # Resolve companies and keywords from config or request body
    companies = body.companies or []
    keywords = body.keywords or ""
    employment_areas = body.employment_areas or []

    if body.config_id:
        result = await db.execute(
            select(ScrapeConfig)
            .where(ScrapeConfig.id == body.config_id, ScrapeConfig.user_id == user.id)
        )
        config = result.scalar_one_or_none()
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        companies = companies or config.companies or []
        keywords = keywords or config.keywords or ""
        employment_areas = employment_areas or config.employment_areas or []

    if not companies and not employment_areas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one company or employment area",
        )

    # Create pending run
    run = ScrapeRun(
        user_id=user.id,
        config_id=body.config_id,
        status="pending",
        scraped_date=date.today(),
        companies=companies,
        keywords=keywords,
    )
    db.add(run)
    user.scrape_quota_remaining -= 1
    await db.flush()
    await db.refresh(run)

    # TODO Phase 2: Dispatch Celery task
    # from app.tasks.scrape_task import run_scrape
    # task = run_scrape.delay(str(run.id), str(user.id), {...})
    # run.celery_task_id = task.id

    return run


@router.get("/scrapes", response_model=list[ScrapeRunResponse])
async def list_runs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScrapeRun)
        .where(ScrapeRun.user_id == user.id)
        .order_by(ScrapeRun.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()


@router.get("/scrapes/{run_id}", response_model=ScrapeRunResponse)
async def get_run(
    run_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScrapeRun)
        .where(ScrapeRun.id == run_id, ScrapeRun.user_id == user.id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Scrape run not found")
    return run


@router.get("/scrapes/{run_id}/status", response_model=ScrapeRunStatusResponse)
async def get_run_status(
    run_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lightweight polling endpoint for run status."""
    result = await db.execute(
        select(ScrapeRun)
        .where(ScrapeRun.id == run_id, ScrapeRun.user_id == user.id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Scrape run not found")
    return ScrapeRunStatusResponse(
        id=run.id, status=run.status, progress=run.progress,
        total_jobs=run.total_jobs, new_jobs=run.new_jobs,
        duration_seconds=run.duration_seconds,
    )
