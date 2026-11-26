"""
AI Intelligence models - Observations, Patterns, Recommendations, Reports.
"""
import enum
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    UniqueConstraint,
    Boolean,
    Integer,
    Float,
    JSON,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import BaseModel


class ObservationType(str, enum.Enum):
    PATTERN_DETECTED = "pattern_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    GOAL_PROGRESS = "goal_progress"
    GOAL_AT_RISK = "goal_at_risk"
    THRESHOLD_CROSSED = "threshold_crossed"
    CORRELATION_FOUND = "correlation_found"
    TREND_CHANGE = "trend_change"
    MILESTONE_REACHED = "milestone_reached"
    BEHAVIORAL_INSIGHT = "behavioral_insight"
    HEALTH_INDICATOR = "health_indicator"


class ObservationSeverity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIObservation(BaseModel):
    """AI-generated observations about user patterns."""
    __tablename__ = "ai_observations"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    observation_type: Mapped[ObservationType] = mapped_column(Enum(ObservationType), nullable=False)
    severity: Mapped[ObservationSeverity] = mapped_column(Enum(ObservationSeverity), default=ObservationSeverity.INFO, nullable=False)

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Related data
    related_domains: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # digital, sleep, nutrition, activity, etc.
    related_goal_ids: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)
    related_record_ids: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)  # [{"type": "sleep_records", "ids": [...]}]

    # Evidence
    evidence_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supporting_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0-1
    evidence_quality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # strong, moderate, weak

    # Time context
    observation_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    observation_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_actionable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_feedback: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # helpful, not_helpful, inaccurate, already_known

    # AI metadata
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    generation_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_observations")
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="observation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_ai_observations_user_id", "user_id"),
        Index("ix_ai_observations_type", "observation_type"),
        Index("ix_ai_observations_severity", "severity"),
        Index("ix_ai_observations_period", "observation_period_start", "observation_period_end"),
        Index("ix_ai_observations_detected_at", "detected_at"),
        Index("ix_ai_observations_unread", "user_id", "is_read"),
    )


class PatternCategory(str, enum.Enum):
    SLEEP_DIGITAL = "sleep_digital"
    ACTIVITY_NUTRITION = "activity_nutrition"
    STRESS_SLEEP = "stress_sleep"
    WORK_LIFE_BALANCE = "work_life_balance"
    CONSISTENCY = "consistency"
    GOAL_ADHERENCE = "goal_adherence"
    SEASONAL = "seasonal"
    WEEKLY_RHYTHM = "weekly_rhythm"
    PROGRESS_TRAJECTORY = "progress_trajectory"
    BEHAVIORAL_CLUSTER = "behavioral_cluster"


class PatternStrength(str, enum.Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class DetectedPattern(BaseModel):
    """Detected patterns across user data."""
    __tablename__ = "detected_patterns"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    pattern_category: Mapped[PatternCategory] = mapped_column(Enum(PatternCategory), nullable=False)
    pattern_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Pattern details
    variables_involved: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    correlation_coefficient: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    strength: Mapped[PatternStrength] = mapped_column(Enum(PatternStrength), nullable=False)
    direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # positive, negative, complex

    # Time context
    first_detected: Mapped[date] = mapped_column(Date, nullable=False)
    last_confirmed: Mapped[date] = mapped_column(Date, nullable=False)
    detection_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0-1

    # Supporting evidence
    supporting_observations: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    date_range_start: Mapped[date] = mapped_column(Date, nullable=False)
    date_range_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Actionability
    is_actionable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    suggested_interventions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    related_goal_ids: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_feedback: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # AI metadata
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    detection_method: Mapped[str] = mapped_column(String(100), nullable=False)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="patterns")

    __table_args__ = (
        Index("ix_detected_patterns_user_id", "user_id"),
        Index("ix_detected_patterns_category", "pattern_category"),
        Index("ix_detected_patterns_active", "is_active"),
        Index("ix_detected_patterns_strength", "strength"),
    )


class RecommendationType(str, enum.Enum):
    BEHAVIORAL_CHANGE = "behavioral_change"
    ROUTINE_ADJUSTMENT = "routine_adjustment"
    GOAL_MODIFICATION = "goal_modification"
    ENVIRONMENT_CHANGE = "environment_change"
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"
    PROFESSIONAL_REFERRAL = "professional_referral"
    HABIT_FORMATION = "habit_formation"
    RECOVERY_FOCUS = "recovery_focus"


class RecommendationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class Recommendation(BaseModel):
    """Personalized AI recommendations."""
    __tablename__ = "recommendations"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    observation_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ai_observations.id", ondelete="SET NULL"),
        nullable=True,
    )
    pattern_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("detected_patterns.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Content
    recommendation_type: Mapped[RecommendationType] = mapped_column(Enum(RecommendationType), nullable=False)
    priority: Mapped[RecommendationPriority] = mapped_column(Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM, nullable=False)
    status: Mapped[RecommendationStatus] = mapped_column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING, nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)  # Why this recommendation
    evidence_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_sources: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)  # [{"title": "...", "url": "...", "source": "..."}]

    # Action details
    specific_action: Mapped[str] = mapped_column(Text, nullable=False)  # Concrete, small next step
    action_category: Mapped[str] = mapped_column(String(50), nullable=False)  # digital, sleep, nutrition, activity, etc.
    difficulty_level: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1-10
    estimated_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # daily, 3x_week, once, etc.
    duration_weeks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Measurement
    success_criteria: Mapped[str] = mapped_column(Text, nullable=False)  # How to measure success
    measurable_target: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {"metric": "sleep_duration", "target": 480, "unit": "minutes"}
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Scheduling
    suggested_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    suggested_time_of_day: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reminder_schedule: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Context
    related_goal_ids: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)
    prerequisite_recommendations: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)
    conflicting_recommendations: Mapped[List[UUID]] = mapped_column(JSON, default=list, nullable=False)

    # User interaction
    user_response: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # accepted, declined, deferred, modified
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_modified_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # AI metadata
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    generation_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    observation: Mapped[Optional["AIObservation"]] = relationship("AIObservation", back_populates="recommendations")
    effectiveness_records: Mapped[List["RecommendationEffectiveness"]] = relationship(
        "RecommendationEffectiveness",
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_recommendations_user_id", "user_id"),
        Index("ix_recommendations_status", "status"),
        Index("ix_recommendations_priority", "priority"),
        Index("ix_recommendations_type", "recommendation_type"),
        Index("ix_recommendations_suggested_start", "suggested_start_date"),
    )


class RecommendationEffectiveness(BaseModel):
    """Tracking recommendation effectiveness over time."""
    __tablename__ = "recommendation_effectiveness"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recommendation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Evaluation period
    evaluation_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    evaluation_period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Metrics
    adherence_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-1
    completion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-1
    progress_towards_target: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-1, can be >1 if exceeded

    # Outcome
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # improved, no_change, worsened, mixed
    outcome_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    measured_improvement: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage improvement
    statistical_significance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Side effects
    unintended_consequences: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    positive_spillovers: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # User feedback
    user_satisfaction: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    user_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    would_recommend: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Next steps
    suggested_adjustments: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    continue_recommendation: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Metadata
    evaluation_method: Mapped[str] = mapped_column(String(50), default="automated", nullable=False)
    data_completeness: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recommendation_effectiveness")
    recommendation: Mapped["Recommendation"] = relationship("Recommendation", back_populates="effectiveness_records")

    __table_args__ = (
        Index("ix_recommendation_effectiveness_user_id", "user_id"),
        Index("ix_recommendation_effectiveness_recommendation_id", "recommendation_id"),
        Index("ix_recommendation_effectiveness_period", "evaluation_period_start", "evaluation_period_end"),
        UniqueConstraint("recommendation_id", "evaluation_period_start", "evaluation_period_end", name="uq_recommendation_effectiveness_period"),
    )


class WeeklyReportStatus(str, enum.Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class WeeklyReport(BaseModel):
    """Weekly intelligence reports."""
    __tablename__ = "weekly_reports"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[WeeklyReportStatus] = mapped_column(Enum(WeeklyReportStatus), default=WeeklyReportStatus.GENERATING, nullable=False)

    # Report content (structured JSON)
    report_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Key sections
    week_at_a_glance: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    digital_life: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    physical_wellbeing: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    personal_patterns: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    missed_goals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommendations: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    long_term_consequences: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    next_week_action_plan: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Metadata
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    generation_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    data_completeness: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sources_used: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # User interaction
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    user_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    user_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_weekly_reports_user_id", "user_id"),
        Index("ix_weekly_reports_week_start", "week_start"),
        Index("ix_weekly_reports_status", "status"),
        UniqueConstraint("user_id", "week_start", name="uq_weekly_report"),
    )
    user: Mapped["User"] = relationship("User", back_populates="weekly_reports")


class NotificationType(str, enum.Enum):
    NUDGE = "nudge"
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"
    WARNING = "warning"
    INSIGHT = "insight"
    WEEKLY_REPORT = "weekly_report"
    GOAL_DEADLINE = "goal_deadline"
    THRESHOLD_CROSSED = "threshold_crossed"
    PATTERN_DETECTED = "pattern_detected"
    RECOMMENDATION = "recommendation"
    SYSTEM = "system"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DISMISSED = "dismissed"
    SNOOZED = "snoozed"
    FAILED = "failed"


class Notification(BaseModel):
    """Notifications and nudges."""
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    priority: Mapped[NotificationPriority] = mapped_column(Enum(NotificationPriority), default=NotificationPriority.NORMAL, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    action_text: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Context
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # goal, recommendation, threshold, report
    related_entity_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    threshold_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    # Delivery
    channels: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # in_app, push, email
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    snoozed_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Interaction
    clicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    action_taken: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Nudge-specific
    nudge_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    nudge_effectiveness: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Tracked after delivery

    # Scheduling
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Metadata
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_status", "status"),
        Index("ix_notifications_type", "notification_type"),
        Index("ix_notifications_scheduled_for", "scheduled_for"),
        Index("ix_notifications_user_unread", "user_id", "status"),
    )


class PushSubscription(BaseModel):
    """Web Push API subscriptions."""
    __tablename__ = "push_subscriptions"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    p256dh_key: Mapped[str] = mapped_column(String(100), nullable=False)
    auth_key: Mapped[str] = mapped_column(String(100), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="push_subscriptions")

    __table_args__ = (
        Index("ix_push_subscriptions_user_id", "user_id"),
        Index("ix_push_subscriptions_endpoint", "endpoint"),
        UniqueConstraint("user_id", "endpoint", name="uq_push_subscription"),
    )

# --- added by fix script: names other files expect to import from here ---
from app.models.digital import DigitalWellbeingThreshold  # noqa: E402,F401
