"""
User endpoints - Profile, Health History, Preferences.
"""
from app.schemas.base import PaginationParams
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.dependencies import get_db_session, get_current_user, get_pagination_params
from app.models.user import User, UserProfile, HealthHistory, ConsentRecord, AuditLog
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserProfileBase,
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    HealthHistoryBase,
    HealthHistoryCreate,
    HealthHistoryUpdate,
    HealthHistoryResponse,
    HealthHistoryListParams,
    UserWithProfile,
    ConsentRecordResponse,
    AuditLogResponse,
)
from app.schemas.base import PaginatedResponse, paginate


router = APIRouter()


# User Profile
@router.get("/profile", response_model=UserProfileResponse, summary="Get user profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get current user's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        # Create empty profile if doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return profile


@router.put("/profile", response_model=UserProfileResponse, summary="Update user profile")
async def update_profile(
    request: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update current user's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    # Calculate profile completeness
    profile.profile_completeness = calculate_profile_completeness(profile)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/profile/completeness", summary="Get profile completeness score")
async def get_profile_completeness(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get profile completeness percentage."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        return {"completeness": 0.0, "missing_fields": get_required_profile_fields()}

    completeness = profile.profile_completeness
    missing = get_missing_profile_fields(profile)

    return {
        "completeness": completeness,
        "missing_fields": missing,
    }


def calculate_profile_completeness(profile: UserProfile) -> float:
    """Calculate profile completeness percentage."""
    required_fields = [
        "date_of_birth",
        "gender",
        "height_cm",
        "weight_kg",
        "activity_level",
        "dietary_preference",
        "occupation",
        "typical_wake_time",
        "typical_bed_time",
    ]
    optional_fields = [
        "dietary_restrictions",
        "allergies",
        "medical_conditions",
        "medications",
        "supplements",
        "work_schedule",
        "typical_work_hours",
        "bio",
        "emergency_contact",
    ]

    filled_required = sum(1 for f in required_fields if getattr(profile, f) is not None)
    filled_optional = sum(1 for f in optional_fields if getattr(profile, f) not in (None, [], {}))

    # Required fields weight 70%, optional 30%
    required_score = (filled_required / len(required_fields)) * 0.7
    optional_score = (filled_optional / len(optional_fields)) * 0.3

    return round((required_score + optional_score) * 100, 1)


def get_required_profile_fields() -> List[str]:
    """Get list of required profile fields."""
    return [
        "date_of_birth",
        "gender",
        "height_cm",
        "weight_kg",
        "activity_level",
        "dietary_preference",
        "occupation",
        "typical_wake_time",
        "typical_bed_time",
    ]


def get_missing_profile_fields(profile: UserProfile) -> List[str]:
    """Get list of missing profile fields."""
    required = get_required_profile_fields()
    missing = []

    for field in required:
        if getattr(profile, field) is None:
            missing.append(field)

    return missing


# Health History
@router.post("/health-history", response_model=HealthHistoryResponse, status_code=status.HTTP_201_CREATED, summary="Add health history entry")
async def add_health_history(
    request: HealthHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Add a health history entry."""
    health_history = HealthHistory(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(health_history)
    await db.commit()
    await db.refresh(health_history)
    return health_history


@router.get("/health-history", response_model=PaginatedResponse[HealthHistoryResponse], summary="List health history entries")
async def list_health_history(
    params: HealthHistoryListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List health history entries with pagination."""
    query = select(HealthHistory).where(HealthHistory.user_id == current_user.id)

    if params.condition_category:
        query = query.where(HealthHistory.condition_category == params.condition_category)
    if params.is_active is not None:
        query = query.where(HealthHistory.is_active == params.is_active)

    query = query.order_by(HealthHistory.diagnosed_date.desc().nullslast())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/health-history/{entry_id}", response_model=HealthHistoryResponse, summary="Get health history entry")
async def get_health_history(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get a specific health history entry."""
    result = await db.execute(
        select(HealthHistory).where(
            HealthHistory.id == entry_id,
            HealthHistory.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health history entry not found")

    return entry


@router.put("/health-history/{entry_id}", response_model=HealthHistoryResponse, summary="Update health history entry")
async def update_health_history(
    entry_id: UUID,
    request: HealthHistoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a health history entry."""
    result = await db.execute(
        select(HealthHistory).where(
            HealthHistory.id == entry_id,
            HealthHistory.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health history entry not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/health-history/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete health history entry")
async def delete_health_history(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a health history entry."""
    result = await db.execute(
        select(HealthHistory).where(
            HealthHistory.id == entry_id,
            HealthHistory.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health history entry not found")

    await db.delete(entry)
    await db.commit()


# Consents
@router.get("/consents", response_model=List[ConsentRecordResponse], summary="List user consents")
async def list_consents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List all consent records for current user."""
    result = await db.execute(
        select(ConsentRecord).where(ConsentRecord.user_id == current_user.id)
        .order_by(ConsentRecord.created_at.desc())
    )
    return result.scalars().all()


# Audit Logs (admin only)
@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse], summary="List audit logs (admin)")
async def list_audit_logs(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List audit logs (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, pagination)


# Account deletion
@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT, summary="Delete account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete current user's account (soft delete)."""
    current_user.status = "deleted"
    current_user.email = f"deleted_{current_user.id}@{current_user.email.split('@')[1]}"
    await db.commit()