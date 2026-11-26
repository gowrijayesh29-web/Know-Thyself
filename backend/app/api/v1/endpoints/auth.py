"""
Authentication endpoints - Login, Register, Password Reset, Token Refresh.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.dependencies import get_db_session, get_current_user, get_optional_current_user
from app.db.session import Base
from app.models.user import User, UserStatus, ConsentRecord
from app.schemas.user import (
    LoginRequest,
    RegisterRequest,
    Token,
    TokenPayload,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    RefreshTokenRequest,
    UserResponse,
    ConsentRecordCreate,
    ConsentRecordResponse,
    MessageResponse,
)
from app.schemas.base import SuccessResponse


router = APIRouter()


@router.post("/login", response_model=Token, summary="User login")
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """Authenticate user and return access/refresh tokens."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )

    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(subject=user.id)

    # Set secure cookies (optional - for web clients)
    if request.remember_me:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=int(access_token_expires.total_seconds()),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="User registration")
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new user account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=request.email.lower(),
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        timezone=request.timezone,
        locale=request.locale,
        is_verified=False,  # Email verification would be implemented
    )
    db.add(user)
    await db.flush()

    # Record consent
    consent = ConsentRecord(
        user_id=user.id,
        consent_type="terms_of_service",
        consent_given=request.accept_terms,
        consent_version="1.0",
        consent_text="Terms of Service and Privacy Policy",
    )
    db.add(consent)

    if request.marketing_consent:
        marketing_consent = ConsentRecord(
            user_id=user.id,
            consent_type="marketing",
            consent_given=True,
            consent_version="1.0",
            consent_text="Marketing communications consent",
        )
        db.add(marketing_consent)

    await db.commit()
    await db.refresh(user)

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
    )


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Refresh access token using refresh token."""
    user_id = verify_token(request.refresh_token, "refresh")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
    )


@router.post("/logout", response_model=MessageResponse, summary="User logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """Logout user (clear cookies)."""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user's profile."""
    return current_user


@router.post("/password/reset", response_model=MessageResponse, summary="Request password reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Request password reset email (placeholder - would send email in production)."""
    result = await db.execute(select(User).where(User.email == request.email.lower()))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    return MessageResponse(message="If the email exists, a password reset link has been sent")


@router.post("/password/reset/confirm", response_model=MessageResponse, summary="Confirm password reset")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db_session),
):
    """Confirm password reset with token (placeholder)."""
    # In production, verify token and update password
    return MessageResponse(message="Password has been reset successfully")


@router.post("/password/change", response_model=MessageResponse, summary="Change password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Change password for authenticated user."""
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = get_password_hash(request.new_password)
    await db.commit()

    return MessageResponse(message="Password changed successfully")


@router.post("/consent", response_model=ConsentRecordResponse, status_code=status.HTTP_201_CREATED, summary="Record user consent")
async def record_consent(
    request: ConsentRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Record user consent for data processing."""
    consent = ConsentRecord(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    return consent


@router.get("/consent", response_model=list[ConsentRecordResponse], summary="Get user consents")
async def get_consents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all consent records for current user."""
    result = await db.execute(
        select(ConsentRecord).where(ConsentRecord.user_id == current_user.id)
    )
    return result.scalars().all()