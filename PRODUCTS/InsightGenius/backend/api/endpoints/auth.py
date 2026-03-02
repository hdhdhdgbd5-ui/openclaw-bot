"""
Authentication API Endpoints
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from models.user import User
from schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    PasswordResetRequest,
    PasswordReset
)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    db_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        company=user.company,
        plan="free"
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "plan": user.plan
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return current_user

@router.post("/password-reset-request")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset (send email)"""
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # TODO: Send reset email
        pass
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/password-reset")
async def reset_password(
    reset: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token"""
    # TODO: Verify token and reset password
    return {"message": "Password reset successful"}
