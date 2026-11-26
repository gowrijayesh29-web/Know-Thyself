"""
AI Intelligence endpoints - Observations, Patterns, Recommendations, Reports.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.dependencies import get_db_session, get_current_user, get_pagination_params
from app.models.ai import (
    AIObservation,
    DetectedPattern,
    Recommendation,
    RecommendationEffectiveness,
    WeeklyReport,
    Notification,
    PushSubscription,
)
from app.models.user import User
from app.schemas.ai import (
    AIObservationBase,
    AIObservationCreate,
    AIObservationUpdate,
    AIObservationResponse,
    AIObservationListParams,
    DetectedPatternBase,
    DetectedPatternCreate,
    DetectedPatternUpdate,
    DetectedPatternResponse,
    DetectedPatternListParams,
    RecommendationBase,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationListParams,
    RecommendationEffectivenessBase,
    RecommendationEffectivenessCreate,
    RecommendationEffectivenessResponse,
    WeeklyReportBase,
    WeeklyReportCreate,
    WeeklyReportUpdate,
    WeeklyReportResponse,
    WeeklyReportListParams,
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


# AI Observations
@router.get("/observations", response_model=PaginatedResponse[AIObservationResponse], summary="List AI observations")
async def list_ai_observations(
    params: AIObservationListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List AI observations with pagination."""
    query = select(AIObservation).where(AIObservation.user_id == current_user.id)

    if params.observation_type:
        query = query.where(AIObservation.observation_type == params.observation_type)
    if params.severity:
        query = query.where(AIObservation.severity == params.severity)
    if params.is_read is not None:
        query = query.where(AIObservation.is_read == params.is_read)
    if params.is_dismissed is not None:
        query = query.where(AIObservation.is_dismissed == params.is_dismissed)
    if params.period_start_from:
        query = query.where(AIObservation.observation_period_start >= params.period_start_from)
    if params.period_end_to:
        query = query.where(AIObservation.observation_period_end <= params.period_end_to)

    query = query.order_by(desc(AIObservation.detected_at))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/observations/unread-count", summary="Get unread observations count")
async def get_unread_observations_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get count of unread observations."""
    result = await db.execute(
        select(func.count(AIObservation.id))
        .where(
            AIObservation.user_id == current_user.id,
            AIObservation.is_read == False,
            AIObservation.is_dismissed == False,
        )
    )
    return {"count": result.scalar()}


@router.put("/observations/{observation_id}/read", response_model=AIObservationResponse, summary="Mark observation as read")
async def mark_observation_read(
    observation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Mark an observation as read."""
    result = await db.execute(
        select(AIObservation).where(
            AIObservation.id == observation_id,
            AIObservation.user_id == current_user.id,
        )
    )
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")

    observation.is_read = True
    await db.commit()
    await db.refresh(observation)
    return observation


@router.put("/observations/{observation_id}/dismiss", response_model=AIObservationResponse, summary="Dismiss observation")
async def dismiss_observation(
    observation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Dismiss an observation."""
    result = await db.execute(
        select(AIObservation).where(
            AIObservation.id == observation_id,
            AIObservation.user_id == current_user.id,
        )
    )
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")

    observation.is_dismissed = True
    await db.commit()
    await db.refresh(observation)
    return observation


@router.put("/observations/{observation_id}/feedback", response_model=AIObservationResponse, summary="Provide observation feedback")
async def provide_observation_feedback(
    observation_id: UUID,
    feedback: str = Query(..., pattern="^(helpful|not_helpful|inaccurate|already_known)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Provide feedback on an observation."""
    result = await db.execute(
        select(AIObservation).where(
            AIObservation.id == observation_id,
            AIObservation.user_id == current_user.id,
        )
    )
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")

    observation.user_feedback = feedback
    await db.commit()
    await db.refresh(observation)
    return observation


# Detected Patterns
@router.get("/patterns", response_model=PaginatedResponse[DetectedPatternResponse], summary="List detected patterns")
async def list_detected_patterns(
    params: DetectedPatternListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List detected patterns with pagination."""
    query = select(DetectedPattern).where(DetectedPattern.user_id == current_user.id)

    if params.pattern_category:
        query = query.where(DetectedPattern.pattern_category == params.pattern_category)
    if params.strength:
        query = query.where(DetectedPattern.strength == params.strength)
    if params.is_active is not None:
        query = query.where(DetectedPattern.is_active == params.is_active)
    if params.user_acknowledged is not None:
        query = query.where(DetectedPattern.user_acknowledged == params.user_acknowledged)

    query = query.order_by(desc(DetectedPattern.consistency_score))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.put("/patterns/{pattern_id}/acknowledge", response_model=DetectedPatternResponse, summary="Acknowledge pattern")
async def acknowledge_pattern(
    pattern_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Acknowledge a detected pattern."""
    result = await db.execute(
        select(DetectedPattern).where(
            DetectedPattern.id == pattern_id,
            DetectedPattern.user_id == current_user.id,
        )
    )
    pattern = result.scalar_one_or_none()

    if not pattern:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")

    pattern.user_acknowledged = True
    await db.commit()
    await db.refresh(pattern)
    return pattern


# Recommendations
@router.get("/recommendations", response_model=PaginatedResponse[RecommendationResponse], summary="List recommendations")
async def list_recommendations(
    params: RecommendationListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List recommendations with pagination."""
    query = select(Recommendation).where(Recommendation.user_id == current_user.id)

    if params.status:
        query = query.where(Recommendation.status == params.status)
    if params.recommendation_type:
        query = query.where(Recommendation.recommendation_type == params.recommendation_type)
    if params.priority:
        query = query.where(Recommendation.priority == params.priority)
    if params.action_category:
        query = query.where(Recommendation.action_category == params.action_category)
    if params.suggested_start_date_from:
        query = query.where(Recommendation.suggested_start_date >= params.suggested_start_date_from)
    if params.suggested_start_date_to:
        query = query.where(Recommendation.suggested_start_date <= params.suggested_start_date_to)

    query = query.order_by(Recommendation.priority.desc(), desc(Recommendation.created_at))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/recommendations/pending", response_model=List[RecommendationResponse], summary="Get pending recommendations")
async def get_pending_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all pending recommendations for the user."""
    result = await db.execute(
        select(Recommendation)
        .where(
            Recommendation.user_id == current_user.id,
            Recommendation.status == "pending",
        )
        .order_by(Recommendation.priority.desc(), desc(Recommendation.created_at))
    )
    return result.scalars().all()


@router.put("/recommendations/{recommendation_id}/accept", response_model=RecommendationResponse, summary="Accept recommendation")
async def accept_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Accept a recommendation."""
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id,
        )
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    recommendation.status = "accepted"
    recommendation.user_response = "accepted"
    recommendation.responded_at = datetime.utcnow()
    recommendation.started_at = datetime.utcnow()
    await db.commit()
    await db.refresh(recommendation)
    return recommendation


@router.put("/recommendations/{recommendation_id}/decline", response_model=RecommendationResponse, summary="Decline recommendation")
async def decline_recommendation(
    recommendation_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Decline a recommendation."""
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id,
        )
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    recommendation.status = "declined"
    recommendation.user_response = "declined"
    recommendation.user_notes = reason
    recommendation.responded_at = datetime.utcnow()
    await db.commit()
    await db.refresh(recommendation)
    return recommendation


@router.put("/recommendations/{recommendation_id}/complete", response_model=RecommendationResponse, summary="Mark recommendation as complete")
async def complete_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Mark a recommendation as completed."""
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id,
        )
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    recommendation.status = "completed"
    recommendation.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(recommendation)
    return recommendation


# Recommendation Effectiveness
@router.post("/recommendations/{recommendation_id}/effectiveness", response_model=RecommendationEffectivenessResponse, status_code=status.HTTP_201_CREATED, summary="Record recommendation effectiveness")
async def record_recommendation_effectiveness(
    recommendation_id: UUID,
    request: RecommendationEffectivenessCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Record effectiveness evaluation for a recommendation."""
    # Verify recommendation ownership
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    effectiveness = RecommendationEffectiveness(
        user_id=current_user.id,
        recommendation_id=recommendation_id,
        **request.model_dump(),
    )
    db.add(effectiveness)
    await db.commit()
    await db.refresh(effectiveness)
    return effectiveness


@router.get("/recommendations/{recommendation_id}/effectiveness", response_model=List[RecommendationEffectivenessResponse], summary="Get recommendation effectiveness history")
async def get_recommendation_effectiveness(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get effectiveness history for a recommendation."""
    result = await db.execute(
        select(RecommendationEffectiveness)
        .where(
            RecommendationEffectiveness.recommendation_id == recommendation_id,
            RecommendationEffectiveness.user_id == current_user.id,
        )
        .order_by(RecommendationEffectiveness.evaluation_period_start)
    )
    return result.scalars().all()


# Weekly Reports
@router.get("/reports/weekly", response_model=PaginatedResponse[WeeklyReportResponse], summary="List weekly reports")
async def list_weekly_reports(
    params: WeeklyReportListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List weekly reports with pagination."""
    query = select(WeeklyReport).where(WeeklyReport.user_id == current_user.id)

    if params.status:
        query = query.where(WeeklyReport.status == params.status)
    if params.week_start_from:
        query = query.where(WeeklyReport.week_start >= params.week_start_from)
    if params.week_start_to:
        query = query.where(WeeklyReport.week_start <= params.week_start_to)
    if params.is_read is not None:
        query = query.where(WeeklyReport.is_read == params.is_read)

    query = query.order_by(desc(WeeklyReport.week_start))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/reports/weekly/latest", response_model=Optional[WeeklyReportResponse], summary="Get latest weekly report")
async def get_latest_weekly_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the most recent weekly report."""
    result = await db.execute(
        select(WeeklyReport)
        .where(WeeklyReport.user_id == current_user.id)
        .order_by(desc(WeeklyReport.week_start))
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/reports/weekly/{week_start}", response_model=WeeklyReportResponse, summary="Get weekly report by week")
async def get_weekly_report(
    week_start: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get weekly report for a specific week."""
    result = await db.execute(
        select(WeeklyReport).where(
            WeeklyReport.user_id == current_user.id,
            WeeklyReport.week_start == week_start,
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report not found")

    return report


@router.put("/reports/weekly/{report_id}/read", response_model=WeeklyReportResponse, summary="Mark weekly report as read")
async def mark_weekly_report_read(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Mark a weekly report as read."""
    result = await db.execute(
        select(WeeklyReport).where(
            WeeklyReport.id == report_id,
            WeeklyReport.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report not found")

    report.is_read = True
    report.read_at = datetime.utcnow()
    await db.commit()
    await db.refresh(report)
    return report


# Notifications
@router.get("/notifications", response_model=PaginatedResponse[NotificationResponse], summary="List notifications")
async def list_notifications(
    params: NotificationListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List notifications with pagination."""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if params.notification_type:
        query = query.where(Notification.notification_type == params.notification_type)
    if params.status:
        query = query.where(Notification.status == params.status)
    if params.priority:
        query = query.where(Notification.priority == params.priority)
    if params.scheduled_for_from:
        query = query.where(Notification.scheduled_for >= params.scheduled_for_from)
    if params.scheduled_for_to:
        query = query.where(Notification.scheduled_for <= params.scheduled_for_to)

    query = query.order_by(desc(Notification.created_at))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/notifications/unread-count", summary="Get unread notifications count")
async def get_unread_notifications_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get count of unread notifications."""
    result = await db.execute(
        select(func.count(Notification.id))
        .where(
            Notification.user_id == current_user.id,
            Notification.status.in_(["pending", "sent", "delivered"]),
        )
    )
    return {"count": result.scalar()}


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse, summary="Mark notification as read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.status = "read"
    notification.read_at = datetime.utcnow()
    await db.commit()
    await db.refresh(notification)
    return notification


@router.put("/notifications/{notification_id}/dismiss", response_model=NotificationResponse, summary="Dismiss notification")
async def dismiss_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Dismiss a notification."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.status = "dismissed"
    notification.dismissed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(notification)
    return notification


@router.put("/notifications/{notification_id}/snooze", response_model=NotificationResponse, summary="Snooze notification")
async def snooze_notification(
    notification_id: UUID,
    minutes: int = Query(..., ge=1, le=1440),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Snooze a notification for specified minutes."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.status = "snoozed"
    notification.snoozed_until = datetime.utcnow() + timedelta(minutes=minutes)
    await db.commit()
    await db.refresh(notification)
    return notification


# Push Subscriptions
@router.post("/push-subscriptions", response_model=PushSubscriptionResponse, status_code=status.HTTP_201_CREATED, summary="Create push subscription")
async def create_push_subscription(
    request: PushSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Register a push subscription for web push notifications."""
    # Check if already exists
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == current_user.id,
            PushSubscription.endpoint == request.endpoint,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing
        existing.p256dh_key = request.p256dh_key
        existing.auth_key = request.auth_key
        existing.user_agent = request.user_agent
        existing.is_active = True
        existing.last_used = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing

    subscription = PushSubscription(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.get("/push-subscriptions", response_model=List[PushSubscriptionResponse], summary="List push subscriptions")
async def list_push_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List user's push subscriptions."""
    result = await db.execute(
        select(PushSubscription)
        .where(PushSubscription.user_id == current_user.id)
        .order_by(desc(PushSubscription.created_at))
    )
    return result.scalars().all()


@router.delete("/push-subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete push subscription")
async def delete_push_subscription(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a push subscription."""
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.id == subscription_id,
            PushSubscription.user_id == current_user.id,
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Push subscription not found")

    await db.delete(subscription)
    await db.commit()


import httpx as _httpx
from pydantic import BaseModel as _PBM
from app.core.config import settings as _settings


class AskRequest(_PBM):
    question: str
    context: str = ""
    mode: str = "chat"


@router.post("/ask", summary="Ask the AI about your logged data")
async def ask_ai(body: AskRequest, current_user: User = Depends(get_current_user)):
    key = _settings.NVIDIA_API_KEY
    if not key:
        raise HTTPException(status_code=503, detail="NVIDIA_API_KEY is not set in backend/.env")
    system = (
        "You are the assistant inside KnowThyself, a personal wellbeing app. "
        "Answer using ONLY the user's data summary below. If the data does not cover something, say so. "
        "Be specific: cite exact numbers and dates from the data, compare days or this week against earlier days, name the likely cause when the data supports it, and end with ONE concrete action for tomorrow. Write 3 to 6 short sentences in plain text with no markdown headings. If the question needs data that is missing, say exactly what is missing. You are not a doctor; do not diagnose.\n\n"
        "USER DATA:\n" + body.context[:12000]
    )
    payload = {
        "model": _settings.NVIDIA_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": body.question[:2000]}],
        "temperature": 0.4,
        "max_tokens": 4096,
        "reasoning_effort": "none",
    }
    try:
        async with _httpx.AsyncClient(timeout=110) as c:
            r = await c.post(_settings.NVIDIA_BASE_URL.rstrip("/") + "/chat/completions", headers={"Authorization": "Bearer " + key}, json=payload)
            if r.status_code == 400 and "reasoning_effort" in payload:
                payload.pop("reasoning_effort")
                payload["max_tokens"] = 8000
                r = await c.post(_settings.NVIDIA_BASE_URL.rstrip("/") + "/chat/completions", headers={"Authorization": "Bearer " + key}, json=payload)
    except _httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail="Could not reach NVIDIA: " + str(e))
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="NVIDIA returned %s: %s" % (r.status_code, r.text[:300]))
    choice = r.json()["choices"][0]
    msg = choice["message"]
    answer = (msg.get("content") or "").strip()
    if not answer:
        raise HTTPException(status_code=502, detail="Model returned no answer text (finish_reason=%s, fields=%s)." % (choice.get("finish_reason"), ",".join(k for k, v in msg.items() if v)))
    return {"answer": answer, "model": _settings.NVIDIA_MODEL}


import re as _re
import httpx as _httpx
from pydantic import BaseModel as _BaseModel
from app.core.config import settings as _settings


class AIChatMessage(_BaseModel):
    role: str
    content: str


class AIChatRequest(_BaseModel):
    messages: List[AIChatMessage]
    context: Optional[str] = None
    mode: str = "chat"


_BASE_RULES = (
    "You are the assistant inside Know Thyself, a personal wellbeing tracker. "
    "Use ONLY the user's logged data given below. If the data does not show something, say so. "
    "Never invent numbers. You are not a doctor: do not diagnose, and suggest seeing a professional for medical concerns. "
)
_MODE_PROMPTS = {
    "chat": "Answer in under 150 words, plain text, no tables. Quote specific numbers from the data.",
    "insights": (
        "Return ONLY a JSON array (no prose, no code fences) of 3 to 5 objects. Each object has keys: "
        "\"title\" (short), \"description\" (1 to 2 sentences using real numbers from the data), "
        "\"severity\" (one of high, medium, low, positive), "
        "\"domains\" (array chosen from sleep, activity, nutrition, digital, hydration), "
        "\"action\" (one concrete suggestion)."
    ),
    "report": (
        "Write a weekly wellbeing summary in plain text with 3 short paragraphs: what went well, "
        "what needs attention, and 3 specific goals for next week. Under 220 words. Use specific numbers."
    ),
}


@router.post("/chat", summary="Ask the AI about your logged data")
async def ai_chat(request: AIChatRequest, current_user: User = Depends(get_current_user)):
    key = _settings.NVIDIA_API_KEY
    if not key:
        raise HTTPException(status_code=503, detail="AI is not configured: add NVIDIA_API_KEY to backend\\.env and restart the backend.")
    model = _settings.NVIDIA_MODEL
    system = _BASE_RULES + _MODE_PROMPTS.get(request.mode, _MODE_PROMPTS["chat"])
    if request.context:
        system += "\n\nUSER DATA:\n" + request.context[:12000]
    msgs = [{"role": "system", "content": system}] + [
        {"role": (m.role if m.role in ("user", "assistant") else "user"), "content": m.content[:2000]}
        for m in request.messages[-10:]
    ]
    body = {"model": model, "messages": msgs, "temperature": 0.4, "max_tokens": 2000}
    attempts = [dict(body, reasoning_effort="none"), body] if "ultra" in model else [body]
    url = _settings.NVIDIA_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}
    resp = None
    try:
        async with _httpx.AsyncClient(timeout=90) as client:
            for b in attempts:
                resp = await client.post(url, json=b, headers=headers)
                if resp.status_code != 400:
                    break
    except _httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail="Could not reach the AI service: " + str(e)[:200])
    if resp.status_code in (401, 403):
        raise HTTPException(status_code=502, detail="The AI service rejected the API key. Check NVIDIA_API_KEY in backend\\.env.")
    if resp.status_code == 404:
        raise HTTPException(status_code=502, detail="Model not found. Check NVIDIA_MODEL in backend\\.env (now: " + model + ").")
    if resp.status_code == 429:
        raise HTTPException(status_code=502, detail="AI rate limit reached. Wait a minute and try again.")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="AI service error %s: %s" % (resp.status_code, resp.text[:300]))
    try:
        text = resp.json()["choices"][0]["message"].get("content") or ""
    except Exception:
        text = ""
    text = _re.sub(r"<think>.*?</think>", "", text, flags=_re.S).strip()
    if not text:
        raise HTTPException(status_code=502, detail="The AI returned an empty answer. Try again.")
    return {"reply": text, "model": model}

