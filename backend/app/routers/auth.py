"""Auth router — user registration after Firebase signup."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.firebase import get_firebase_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: UserCreate,
    firebase_claims: dict = Depends(get_firebase_user),
    db: AsyncSession = Depends(get_db),
):
    """Create the server-side user record after Firebase client-side signup."""
    firebase_uid = firebase_claims["uid"]

    # Check if already registered
    existing = await db.execute(
        select(User).where(User.firebase_uid == firebase_uid)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered",
        )

    user = User(
        firebase_uid=firebase_uid,
        email=body.email,
        display_name=body.display_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user
