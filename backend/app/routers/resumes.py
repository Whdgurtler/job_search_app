"""Resume upload and management router."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeListResponse

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload and parse a resume file."""
    # Validate file type
    allowed_types = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in ("pdf", "docx", "txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be PDF, DOCX, or TXT",
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File must be under 10 MB",
        )

    # TODO Phase 1: Upload to GCS, parse with ResumeFileParser + ResumeParser
    # For now, store a placeholder
    resume = Resume(
        user_id=user.id,
        file_url=f"pending://{file.filename}",
        file_name=file.filename or "resume",
        file_type=ext,
        file_size_bytes=len(content),
        is_active=True,
    )

    # Deactivate previous resumes
    await db.execute(
        update(Resume)
        .where(Resume.user_id == user.id, Resume.is_active == True)
        .values(is_active=False)
    )

    db.add(resume)
    await db.flush()
    await db.refresh(resume)
    return resume


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all resumes for the current user."""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == user.id)
        .order_by(Resume.uploaded_at.desc())
    )
    resumes = result.scalars().all()
    return ResumeListResponse(resumes=resumes)
