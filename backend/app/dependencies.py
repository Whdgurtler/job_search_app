"""Shared FastAPI dependencies."""
import os
import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.firebase import get_firebase_user
from app.models.user import User
from app.config import get_settings
import logging as _logging

_logger = _logging.getLogger(__name__)
_logger.info(f"[DEPENDENCIES MODULE LOADED] environment={get_settings().environment}")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    firebase_claims: dict | None = Depends(get_firebase_user),
) -> User:
    """Get or create the current user from Firebase token claims."""
    from app.config import get_settings
    import logging
    logger = logging.getLogger(__name__)
    settings = get_settings()
    logger.info(f"get_current_user called: env={settings.environment}, firebase_claims={firebase_claims}")
    
    # TEST MODE: Bypass Firebase auth for local testing
    if settings.environment == "development" and firebase_claims is None:
        result = await db.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test user not found. Run database setup first.",
            )
        logger.info(f"Dev mode: returning test user {user.email}")
        return user
    
    if not firebase_claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    firebase_uid = firebase_claims["uid"]

    result = await db.execute(
        select(User).where(User.firebase_uid == firebase_uid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not registered. Call POST /api/v1/auth/register first.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    return user
