"""Shared FastAPI dependencies."""
import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.firebase import get_firebase_user
from app.models.user import User


async def get_current_user(
    firebase_claims: dict = Depends(get_firebase_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get or create the current user from Firebase token claims."""
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
