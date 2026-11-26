"""
Services package initialization.
"""
from app.services.ai_engine import ai_engine, AIEngine, UserContext
from app.services.background_tasks import (
    celery_app,
    generate_weekly_report_task,
    aggregate_daily_digital_summaries_task,
    aggregate_weekly_digital_summaries_task,
    check_digital_thresholds_task,
    send_pending_notifications_task,
)

__all__ = [
    "ai_engine",
    "AIEngine",
    "UserContext",
    "celery_app",
    "generate_weekly_report_task",
    "aggregate_daily_digital_summaries_task",
    "aggregate_weekly_digital_summaries_task",
    "check_digital_thresholds_task",
    "send_pending_notifications_task",
]