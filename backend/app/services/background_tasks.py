"""
Background tasks - Report generation, notifications, data aggregation.
"""
import json
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from celery import Celery

from app.core.config import settings
from app.db.session import async_session_maker
from app.models.digital import DigitalActivity, DailyDigitalSummary, WeeklyDigitalSummary
from app.models.physical import (
    SleepRecord, NutritionRecord, PhysicalActivity, HydrationRecord,
    DailyNutritionSummary, DailyPhysicalActivitySummary, DailyHydrationSummary
)
from app.models.ai import WeeklyReport, Notification, DigitalWellbeingThreshold
from app.models.goals import Goal, GoalProgress
from app.models.knowledge import WeeklySurvey
from app.services.ai_engine import ai_engine

logger = logging.getLogger(__name__)

# Celery app
celery_app = Celery(
    "knowthyself",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def generate_weekly_report_task(self, user_id: str, week_start: str):
    """Celery task to generate weekly report."""
    import asyncio
    asyncio.run(_generate_weekly_report(UUID(user_id), date.fromisoformat(week_start)))


async def _generate_weekly_report(user_id: UUID, week_start: date):
    """Generate weekly intelligence report for a user."""
    week_end = week_start + timedelta(days=6)

    async with async_session_maker() as db:
        try:
            # Check if report already exists
            from app.models.ai import WeeklyReport, WeeklyReportStatus
            existing = await db.execute(
                select(WeeklyReport).where(
                    WeeklyReport.user_id == user_id,
                    WeeklyReport.week_start == week_start,
                )
            )
            report = existing.scalar_one_or_none()

            if not report:
                report = WeeklyReport(
                    user_id=user_id,
                    week_start=week_start,
                    week_end=week_end,
                    status=WeeklyReportStatus.GENERATING,
                )
                db.add(report)
                await db.commit()
                await db.refresh(report)

            # Assemble context and generate report
            context = await ai_engine.assemble_user_context(user_id, db, days_back=30)
            report_data = await ai_engine.generate_weekly_report(context, week_start, week_end)

            # Update report
            report.status = WeeklyReportStatus.COMPLETED
            report.report_data = report_data
            report.week_at_a_glance = report_data.get("week_at_a_glance", {})
            report.digital_life = report_data.get("digital_life", {})
            report.physical_wellbeing = report_data.get("physical_wellbeing", {})
            report.personal_patterns = report_data.get("personal_patterns", {})
            report.missed_goals = report_data.get("missed_goals", {})
            report.recommendations = report_data.get("recommendations", [])
            report.long_term_consequences = report_data.get("long_term_consequences", [])
            report.next_week_action_plan = report_data.get("next_week_action_plan", {})
            report.generated_at = datetime.utcnow()
            report.model_version = settings.NVIDIA_MODEL
            report.prompt_version = "1.0"
            report.data_completeness = 1.0

            await db.commit()
            logger.info(f"Weekly report generated for user {user_id}, week {week_start}")

        except Exception as e:
            logger.error(f"Weekly report generation failed for user {user_id}: {e}")
            if 'report' in locals():
                report.status = WeeklyReportStatus.FAILED
                await db.commit()
            raise


@celery_app.task
def aggregate_daily_digital_summaries_task(target_date: str = None):
    """Aggregate daily digital activity summaries for all users."""
    import asyncio
    target = date.fromisoformat(target_date) if target_date else date.today() - timedelta(days=1)
    asyncio.run(_aggregate_daily_digital_summaries(target))


async def _aggregate_daily_digital_summaries(target_date: date):
    """Aggregate daily digital summaries for all users."""
    async with async_session_maker() as db:
        # Get all users with digital activity
        from app.models.user import User
        user_result = await db.execute(select(User.id).distinct())
        user_ids = [row[0] for row in user_result.all()]

        for user_id in user_ids:
            await _aggregate_user_daily_digital(user_id, target_date, db)

        logger.info(f"Daily digital summaries aggregated for {target_date}")


async def _aggregate_user_daily_digital(user_id: UUID, target_date: date, db: AsyncSession):
    """Aggregate digital activity for a single user for a specific date."""
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    # Get activities for the day
    result = await db.execute(
        select(DigitalActivity).where(
            DigitalActivity.user_id == user_id,
            DigitalActivity.start_time >= start_of_day,
            DigitalActivity.start_time <= end_of_day,
        )
    )
    activities = result.scalars().all()

    if not activities:
        return

    # Calculate aggregates
    total_seconds = sum(a.duration_seconds for a in activities)
    active_seconds = sum(a.active_seconds for a in activities)
    idle_seconds = sum(a.idle_seconds for a in activities)

    category_breakdown = {}
    domain_breakdown = {}
    productive_seconds = 0
    unproductive_seconds = 0
    neutral_seconds = 0

    for a in activities:
        cat = a.category.value
        category_breakdown[cat] = category_breakdown.get(cat, 0) + a.active_seconds
        domain_breakdown[a.domain] = domain_breakdown.get(a.domain, 0) + a.active_seconds

        if a.is_productive is True:
            productive_seconds += a.active_seconds
        elif a.is_productive is False:
            unproductive_seconds += a.active_seconds
        else:
            neutral_seconds += a.active_seconds

    # Top domains
    top_domains = sorted(domain_breakdown.items(), key=lambda x: x[1], reverse=True)[:10]

    # Hourly distribution
    hourly_distribution = {}
    for a in activities:
        hour = a.start_time.hour
        hourly_distribution[hour] = hourly_distribution.get(hour, 0) + a.active_seconds

    # Day part distribution
    day_parts = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
    for a in activities:
        hour = a.start_time.hour
        if 5 <= hour < 12:
            day_parts["morning"] += a.active_seconds
        elif 12 <= hour < 17:
            day_parts["afternoon"] += a.active_seconds
        elif 17 <= hour < 22:
            day_parts["evening"] += a.active_seconds
        else:
            day_parts["night"] += a.active_seconds

    session_count = len(activities)
    avg_session = total_seconds / session_count if session_count > 0 else 0
    longest_session = max((a.duration_seconds for a in activities), default=0)

    total_tab_switches = sum(a.tab_switches for a in activities)

    # Upsert summary
    from app.models.digital import DailyDigitalSummary
    existing = await db.execute(
        select(DailyDigitalSummary).where(
            DailyDigitalSummary.user_id == user_id,
            DailyDigitalSummary.date == target_date,
        )
    )
    summary = existing.scalar_one_or_none()

    if not summary:
        summary = DailyDigitalSummary(user_id=user_id, date=target_date)
        db.add(summary)

    summary.total_seconds = total_seconds
    summary.active_seconds = active_seconds
    summary.idle_seconds = idle_seconds
    summary.category_breakdown = category_breakdown
    summary.top_domains = [{"domain": d, "seconds": s} for d, s in top_domains]
    summary.productive_seconds = productive_seconds
    summary.unproductive_seconds = unproductive_seconds
    summary.neutral_seconds = neutral_seconds
    summary.session_count = session_count
    summary.avg_session_seconds = avg_session
    summary.longest_session_seconds = longest_session
    summary.total_tab_switches = total_tab_switches
    summary.hourly_distribution = hourly_distribution
    summary.day_part_distribution = day_parts
    summary.data_completeness = 1.0
    summary.sources = list(set(a.source.value for a in activities))

    await db.commit()


@celery_app.task
def aggregate_weekly_digital_summaries_task(week_start: str = None):
    """Aggregate weekly digital summaries."""
    import asyncio
    start = date.fromisoformat(week_start) if week_start else date.today() - timedelta(weeks=1)
    asyncio.run(_aggregate_weekly_digital_summaries(start))


async def _aggregate_weekly_digital_summaries(week_start: date):
    """Aggregate weekly digital summaries for all users."""
    week_end = week_start + timedelta(days=6)

    async with async_session_maker() as db:
        from app.models.user import User
        user_result = await db.execute(select(User.id).distinct())
        user_ids = [row[0] for row in user_result.all()]

        for user_id in user_ids:
            await _aggregate_user_weekly_digital(user_id, week_start, week_end, db)

        logger.info(f"Weekly digital summaries aggregated for week {week_start}")


async def _aggregate_user_weekly_digital(user_id: UUID, week_start: date, week_end: date, db: AsyncSession):
    """Aggregate weekly digital summary for a user."""
    # Get daily summaries for the week
    result = await db.execute(
        select(DailyDigitalSummary).where(
            DailyDigitalSummary.user_id == user_id,
            DailyDigitalSummary.date >= week_start,
            DailyDigitalSummary.date <= week_end,
        )
    )
    daily_summaries = result.scalars().all()

    if not daily_summaries:
        return

    total_seconds = sum(d.total_seconds for d in daily_summaries)
    active_seconds = sum(d.active_seconds for d in daily_summaries)
    daily_average = total_seconds / 7

    # Category breakdown for week
    category_breakdown = {}
    for d in daily_summaries:
        for cat, seconds in d.category_breakdown.items():
            category_breakdown[cat] = category_breakdown.get(cat, 0) + seconds

    # Get previous week for trend
    prev_week_start = week_start - timedelta(weeks=1)
    prev_week_end = week_start - timedelta(days=1)
    prev_result = await db.execute(
        select(func.sum(DailyDigitalSummary.total_seconds))
        .where(
            DailyDigitalSummary.user_id == user_id,
            DailyDigitalSummary.date >= prev_week_start,
            DailyDigitalSummary.date <= prev_week_end,
        )
    )
    prev_total = prev_result.scalar() or 0
    trend = ((total_seconds - prev_total) / prev_total * 100) if prev_total > 0 else None

    # Goals met this week
    from app.models.goals import Goal, GoalProgress
    goals_result = await db.execute(
        select(Goal).where(Goal.user_id == user_id, Goal.status == "active")
    )
    goals = goals_result.scalars().all()

    goals_met = 0
    goals_total = len(goals)
    for goal in goals:
        progress_result = await db.execute(
            select(func.count(GoalProgress.id))
            .where(
                GoalProgress.goal_id == goal.id,
                GoalProgress.date >= week_start,
                GoalProgress.date <= week_end,
                GoalProgress.achieved == True,
            )
        )
        if progress_result.scalar() > 0:
            goals_met += 1

    # Focus sessions
    from app.models.goals import FocusSession
    focus_result = await db.execute(
        select(FocusSession).where(
            FocusSession.user_id == user_id,
            FocusSession.actual_start >= week_start,
            FocusSession.actual_start <= week_end,
            FocusSession.status == "completed",
        )
    )
    focus_sessions = focus_result.scalars().all()
    focus_count = len(focus_sessions)
    focus_minutes = sum(s.actual_duration_minutes or 0 for s in focus_sessions)
    avg_focus_quality = (
        sum(s.focus_quality_rating for s in focus_sessions if s.focus_quality_rating) / focus_count
        if focus_count > 0 else None
    )

    # Upsert weekly summary
    from app.models.digital import WeeklyDigitalSummary
    existing = await db.execute(
        select(WeeklyDigitalSummary).where(
            WeeklyDigitalSummary.user_id == user_id,
            WeeklyDigitalSummary.week_start == week_start,
        )
    )
    summary = existing.scalar_one_or_none()

    if not summary:
        summary = WeeklyDigitalSummary(user_id=user_id, week_start=week_start, week_end=week_end)
        db.add(summary)

    summary.total_seconds = total_seconds
    summary.active_seconds = active_seconds
    summary.daily_average_seconds = daily_average
    summary.trend_vs_previous_week = trend
    summary.category_breakdown = category_breakdown
    summary.goals_met = goals_met
    summary.goals_total = goals_total
    summary.focus_sessions_count = focus_count
    summary.focus_sessions_total_minutes = focus_minutes
    summary.avg_focus_quality = avg_focus_quality
    summary.data_completeness = 1.0

    await db.commit()


@celery_app.task
def check_digital_thresholds_task():
    """Check digital wellbeing thresholds and send nudges."""
    import asyncio
    asyncio.run(_check_digital_thresholds())


async def _check_digital_thresholds():
    """Check all active thresholds and trigger nudges."""
    async with async_session_maker() as db:
        # Get all active thresholds
        result = await db.execute(
            select(DigitalWellbeingThreshold).where(DigitalWellbeingThreshold.is_active == True)
        )
        thresholds = result.scalars().all()

        for threshold in thresholds:
            await _check_single_threshold(threshold, db)

        logger.info(f"Checked {len(thresholds)} digital wellbeing thresholds")


async def _check_single_threshold(threshold: DigitalWellbeingThreshold, db: AsyncSession):
    """Check a single threshold and trigger nudge if needed."""
    from app.models.ai import Notification, NotificationType, NotificationPriority, NotificationStatus
    from app.models.digital import DailyDigitalSummary
    from app.models.user import User

    # Check cooldown
    if threshold.last_triggered:
        cooldown_end = threshold.last_triggered + timedelta(minutes=threshold.cooldown_minutes)
        if datetime.utcnow() < cooldown_end:
            return

    # Check daily limit
    today = date.today()
    if threshold.trigger_count_today >= threshold.max_nudges_per_day:
        # Reset daily count if it's a new day
        if threshold.last_triggered and threshold.last_triggered.date() < today:
            threshold.trigger_count_today = 0
        else:
            return

    # Check day of week
    if threshold.days_of_week and today.weekday() not in threshold.days_of_week:
        return

    # Check time window
    if threshold.window_start and threshold.window_end:
        now_time = datetime.utcnow().time()
        start = datetime.strptime(threshold.window_start, "%H:%M").time()
        end = datetime.strptime(threshold.window_end, "%H:%M").time()
        if not (start <= now_time <= end):
            return

    # Get today's digital summary
    summary_result = await db.execute(
        select(DailyDigitalSummary).where(
            DailyDigitalSummary.user_id == threshold.user_id,
            DailyDigitalSummary.date == today,
        )
    )
    summary = summary_result.scalar_one_or_none()

    if not summary:
        return

    # Evaluate threshold
    metric_value = _get_metric_value(summary, threshold)
    if metric_value is None:
        return

    triggered = _evaluate_threshold(metric_value, threshold.threshold_value, threshold.comparison)

    if triggered:
        # Create notification
        user_result = await db.execute(select(User).where(User.id == threshold.user_id))
        user = user_result.scalar_one_or_none()

        notification = Notification(
            user_id=threshold.user_id,
            notification_type=NotificationType.NUDGE,
            priority=NotificationPriority.HIGH if threshold.nudge_severity == "critical" else NotificationPriority.NORMAL,
            title=f"Digital Wellbeing: {threshold.name}",
            message=threshold.nudge_message or f"Your {threshold.metric} has exceeded the threshold.",
            action_text="View Details",
            action_url=f"/digital?threshold={threshold.id}",
            channels=["in_app", "push"] if threshold.nudge_severity != "info" else ["in_app"],
            status=NotificationStatus.PENDING,
            related_entity_type="threshold",
            related_entity_id=threshold.id,
            nudge_context={
                "threshold_id": str(threshold.id),
                "metric": threshold.metric,
                "value": metric_value,
                "threshold": threshold.threshold_value,
            },
        )
        db.add(notification)

        # Update threshold
        threshold.last_triggered = datetime.utcnow()
        threshold.trigger_count_today += 1
        threshold.trigger_count_total += 1

        await db.commit()
        logger.info(f"Threshold nudge triggered for user {threshold.user_id}: {threshold.name}")


def _get_metric_value(summary: DailyDigitalSummary, threshold: DigitalWellbeingThreshold) -> Optional[float]:
    """Extract metric value from summary based on threshold metric."""
    metric = threshold.metric

    if metric == "total_screen_time":
        return summary.total_seconds
    elif metric == "active_screen_time":
        return summary.active_seconds
    elif metric == "social_media_time":
        return summary.category_breakdown.get("social_media", 0)
    elif metric == "entertainment_time":
        return summary.category_breakdown.get("entertainment", 0)
    elif metric == "distraction_count":
        return summary.total_interruptions
    elif metric == "tab_switches":
        return summary.total_tab_switches
    elif metric == "productive_time":
        return summary.productive_seconds
    elif metric == "unproductive_time":
        return summary.unproductive_seconds
    elif metric == "session_count":
        return summary.session_count
    elif threshold.category:
        return summary.category_breakdown.get(threshold.category.value, 0)
    elif threshold.domain:
        for domain in summary.top_domains:
            if domain["domain"] == threshold.domain:
                return domain["seconds"]
        return 0

    return None


def _evaluate_threshold(value: float, threshold_value: float, comparison: str) -> bool:
    """Evaluate if threshold is triggered."""
    if comparison == "gte":
        return value >= threshold_value
    elif comparison == "lte":
        return value <= threshold_value
    elif comparison == "gt":
        return value > threshold_value
    elif comparison == "lt":
        return value < threshold_value
    elif comparison == "eq":
        return value == threshold_value
    return False


@celery_app.task
def send_pending_notifications_task():
    """Send pending notifications (push, email)."""
    import asyncio
    asyncio.run(_send_pending_notifications())


async def _send_pending_notifications():
    """Send pending notifications."""
    async with async_session_maker() as db:
        from app.models.ai import Notification, NotificationStatus

        # Get pending notifications
        result = await db.execute(
            select(Notification).where(
                Notification.status.in_(["pending", "snoozed"]),
                Notification.scheduled_for <= datetime.utcnow(),
            )
        )
        notifications = result.scalars().all()

        for notification in notifications:
            await _send_notification(notification, db)

        logger.info(f"Processed {len(notifications)} pending notifications")


async def _send_notification(notification: Notification, db: AsyncSession):
    """Send a single notification."""
    from app.models.ai import NotificationStatus

    try:
        # Send in-app (already in database)
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()

        # Send push if enabled
        if "push" in notification.channels:
            await _send_push_notification(notification, db)

        # Send email if enabled
        if "email" in notification.channels:
            await _send_email_notification(notification, db)

        notification.status = NotificationStatus.DELIVERED
        notification.delivered_at = datetime.utcnow()

    except Exception as e:
        logger.error(f"Failed to send notification {notification.id}: {e}")
        notification.status = NotificationStatus.FAILED

    await db.commit()


async def _send_push_notification(notification: Notification, db: AsyncSession):
    """Send web push notification."""
    from app.models.ai import PushSubscription
    import aiohttp

    # Get user's push subscriptions
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == notification.user_id,
            PushSubscription.is_active == True,
        )
    )
    subscriptions = result.scalars().all()

    if not subscriptions:
        return

    from app.core.config import settings
    from pywebpush import webpush

    vapid_private_key = settings.VAPID_PRIVATE_KEY
    vapid_claims = {"sub": settings.VAPID_CLAIMS_SUB}

    payload = {
        "title": notification.title,
        "body": notification.message,
        "icon": "/icon-192.png",
        "badge": "/badge-72.png",
        "data": {
            "url": notification.action_url or "/",
            "notification_id": str(notification.id),
        },
        "actions": [
            {"action": "view", "title": notification.action_text or "View"},
            {"action": "dismiss", "title": "Dismiss"},
        ],
    }

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh_key,
                        "auth": sub.auth_key,
                    },
                },
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims,
            )
            sub.last_used = datetime.utcnow()
        except Exception as e:
            logger.warning(f"Push notification failed for subscription {sub.id}: {e}")
            if "410" in str(e) or "404" in str(e):
                sub.is_active = False


async def _send_email_notification(notification: Notification, db: AsyncSession):
    """Send email notification."""
    # Placeholder - implement with your email service
    pass


# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "aggregate-daily-digital": {
        "task": "app.services.background_tasks.aggregate_daily_digital_summaries_task",
        "schedule": 3600.0,  # Every hour
    },
    "aggregate-weekly-digital": {
        "task": "app.services.background_tasks.aggregate_weekly_digital_summaries_task",
        "schedule": 86400.0,  # Daily
    },
    "check-thresholds": {
        "task": "app.services.background_tasks.check_digital_thresholds_task",
        "schedule": 300.0,  # Every 5 minutes
    },
    "send-notifications": {
        "task": "app.services.background_tasks.send_pending_notifications_task",
        "schedule": 60.0,  # Every minute
    },
}