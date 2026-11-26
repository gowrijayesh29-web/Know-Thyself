"""
Notifications and Push endpoints.
"""
from fastapi import Query
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.core.dependencies import get_db_session, get_current_user, get_pagination_params
from app.core.security import get_encryption_key
from app.models.ai import Notification, PushSubscription
from app.models.user import User
from app.schemas.ai import (
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListParams,
    PushSubscriptionBase,
    PushSubscriptionCreate,
    PushSubscriptionResponse,
)
from app.schemas.base import PaginatedResponse, paginate


router = APIRouter()


# Notification preferences (user settings)
@router.get("/preferences", summary="Get notification preferences")
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get user's notification preferences."""
    prefs = current_user.preferences.get("notifications", {})
    return {
        "enabled": prefs.get("enabled", True),
        "channels": prefs.get("channels", ["in_app", "push"]),
        "quiet_hours": prefs.get("quiet_hours", {"start": "22:00", "end": "07:00"}),
        "frequency_limits": prefs.get("frequency_limits", {"max_per_hour": 3, "max_per_day": 10}),
        "categories": prefs.get("categories", {
            "nudges": True,
            "reminders": True,
            "achievements": True,
            "warnings": True,
            "insights": True,
            "weekly_reports": True,
            "goal_deadlines": True,
        }),
    }


@router.put("/preferences", summary="Update notification preferences")
async def update_notification_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update user's notification preferences."""
    current_prefs = current_user.preferences or {}
    current_prefs["notifications"] = preferences
    current_user.preferences = current_prefs
    await db.commit()
    return {"message": "Preferences updated", "preferences": preferences}


# VAPID public key for web push
@router.get("/vapid-public-key", summary="Get VAPID public key")
async def get_vapid_public_key(
    current_user: User = Depends(get_current_user),
):
    """Get VAPID public key for web push subscription."""
    from app.core.config import settings
    return {"public_key": settings.VAPID_PUBLIC_KEY}


# Send test notification
@router.post("/test", response_model=NotificationResponse, summary="Send test notification")
async def send_test_notification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Send a test notification to the user."""
    notification = Notification(
        user_id=current_user.id,
        notification_type="system",
        priority="normal",
        title="Test Notification",
        message="This is a test notification from Know Thyself.",
        channels=["in_app"],
        status="pending",
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


# Notification history with stats
@router.get("/stats", summary="Get notification statistics")
async def get_notification_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get notification statistics for the user."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total sent
    total_result = await db.execute(
        select(func.count(Notification.id))
        .where(
            Notification.user_id == current_user.id,
            Notification.created_at >= start_date,
        )
    )
    total = total_result.scalar()

    # By type
    type_result = await db.execute(
        select(Notification.notification_type, func.count(Notification.id))
        .where(
            Notification.user_id == current_user.id,
            Notification.created_at >= start_date,
        )
        .group_by(Notification.notification_type)
    )
    by_type = {row[0]: row[1] for row in type_result.all()}

    # By status
    status_result = await db.execute(
        select(Notification.status, func.count(Notification.id))
        .where(
            Notification.user_id == current_user.id,
            Notification.created_at >= start_date,
        )
        .group_by(Notification.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    # Click-through rate
    clicked_result = await db.execute(
        select(func.count(Notification.id))
        .where(
            Notification.user_id == current_user.id,
            Notification.created_at >= start_date,
            Notification.clicked == True,
        )
    )
    clicked = clicked_result.scalar()
    ctr = (clicked / total * 100) if total > 0 else 0

    return {
        "period_days": days,
        "total_notifications": total,
        "by_type": by_type,
        "by_status": by_status,
        "clicked": clicked,
        "click_through_rate": round(ctr, 2),
    }