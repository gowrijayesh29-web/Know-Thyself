"""
AI Intelligence schemas - Observations, Patterns, Recommendations, Reports, Notifications.
"""
from pydantic import AliasChoices
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base import IDTimestampSchema, PaginationParams
from app.models.ai import (
    ObservationType, ObservationSeverity,
    PatternCategory, PatternStrength,
    RecommendationType, RecommendationPriority, RecommendationStatus,
    WeeklyReportStatus,
    NotificationType, NotificationPriority, NotificationStatus,
)


# Enums for API
class ObservationTypeStr(str, Enum):
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


class ObservationSeverityStr(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PatternCategoryStr(str, Enum):
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


class PatternStrengthStr(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class RecommendationTypeStr(str, Enum):
    BEHAVIORAL_CHANGE = "behavioral_change"
    ROUTINE_ADJUSTMENT = "routine_adjustment"
    GOAL_MODIFICATION = "goal_modification"
    ENVIRONMENT_CHANGE = "environment_change"
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"
    PROFESSIONAL_REFERRAL = "professional_referral"
    HABIT_FORMATION = "habit_formation"
    RECOVERY_FOCUS = "recovery_focus"


class RecommendationPriorityStr(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecommendationStatusStr(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class WeeklyReportStatusStr(str, Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class NotificationTypeStr(str, Enum):
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


class NotificationPriorityStr(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatusStr(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DISMISSED = "dismissed"
    SNOOZED = "snoozed"
    FAILED = "failed"


# AI Observation schemas
class AIObservationBase(BaseModel):
    observation_type: ObservationTypeStr
    severity: ObservationSeverityStr = ObservationSeverityStr.INFO
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    detailed_analysis: Optional[str] = None
    related_domains: List[str] = Field(default_factory=list)
    related_goal_ids: List[UUID] = Field(default_factory=list)
    related_record_ids: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_summary: Optional[str] = None
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    evidence_quality: Optional[str] = Field(None, max_length=50)
    observation_period_start: date
    observation_period_end: date
    is_actionable: bool = True


class AIObservationCreate(AIObservationBase):
    pass


class AIObservationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    user_feedback: Optional[str] = Field(None, pattern="^(helpful|not_helpful|inaccurate|already_known)$")


class AIObservationResponse(IDTimestampSchema, AIObservationBase):
    user_id: UUID
    detected_at: datetime
    is_read: bool
    is_dismissed: bool
    user_feedback: Optional[str] = None
    model_version: str
    prompt_version: str
    generation_metadata: Dict[str, Any]


class AIObservationListParams(PaginationParams):
    observation_type: Optional[ObservationTypeStr] = None
    severity: Optional[ObservationSeverityStr] = None
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    period_start_from: Optional[date] = None
    period_end_to: Optional[date] = None


# Detected Pattern schemas
class DetectedPatternBase(BaseModel):
    pattern_category: PatternCategoryStr
    pattern_name: str = Field(..., min_length=1, max_length=255)
    description: str
    variables_involved: List[str] = Field(default_factory=list)
    correlation_coefficient: Optional[float] = Field(None, ge=-1, le=1)
    p_value: Optional[float] = Field(None, ge=0, le=1)
    strength: PatternStrengthStr
    direction: Optional[str] = Field(None, pattern="^(positive|negative|complex)$")
    supporting_observations: List[Dict[str, Any]] = Field(default_factory=list)
    sample_size: int = Field(default=0, ge=0)
    date_range_start: date
    date_range_end: date
    is_actionable: bool = True
    suggested_interventions: List[str] = Field(default_factory=list)
    related_goal_ids: List[UUID] = Field(default_factory=list)


class DetectedPatternCreate(DetectedPatternBase):
    pass


class DetectedPatternUpdate(BaseModel):
    is_active: Optional[bool] = None
    user_acknowledged: Optional[bool] = None
    user_feedback: Optional[str] = Field(None, pattern="^(helpful|not_helpful|inaccurate|already_known)$")


class DetectedPatternResponse(IDTimestampSchema, DetectedPatternBase):
    user_id: UUID
    first_detected: date
    last_confirmed: date
    detection_count: int
    consistency_score: float
    is_active: bool
    user_acknowledged: bool
    user_feedback: Optional[str] = None
    model_version: str
    detection_method: str
    metadata: Dict[str, Any] = Field(validation_alias=AliasChoices("meta_data", "metadata"))


class DetectedPatternListParams(PaginationParams):
    pattern_category: Optional[PatternCategoryStr] = None
    strength: Optional[PatternStrengthStr] = None
    is_active: Optional[bool] = None
    user_acknowledged: Optional[bool] = None


# Recommendation schemas
class RecommendationBase(BaseModel):
    recommendation_type: RecommendationTypeStr
    priority: RecommendationPriorityStr = RecommendationPriorityStr.MEDIUM
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    rationale: str
    evidence_summary: Optional[str] = None
    evidence_sources: List[Dict[str, Any]] = Field(default_factory=list)
    specific_action: str
    action_category: str = Field(..., max_length=50)
    difficulty_level: int = Field(default=3, ge=1, le=10)
    estimated_time_minutes: Optional[int] = Field(None, ge=1)
    frequency: Optional[str] = Field(None, max_length=50)
    duration_weeks: Optional[int] = Field(None, ge=1)
    success_criteria: str
    measurable_target: Optional[Dict[str, Any]] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    suggested_start_date: Optional[date] = None
    suggested_time_of_day: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    reminder_enabled: bool = True
    reminder_schedule: Optional[Dict[str, Any]] = None
    related_goal_ids: List[UUID] = Field(default_factory=list)
    prerequisite_recommendations: List[UUID] = Field(default_factory=list)
    conflicting_recommendations: List[UUID] = Field(default_factory=list)


class RecommendationCreate(RecommendationBase):
    observation_id: Optional[UUID] = None
    pattern_id: Optional[UUID] = None


class RecommendationUpdate(BaseModel):
    status: Optional[RecommendationStatusStr] = None
    priority: Optional[RecommendationPriorityStr] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    specific_action: Optional[str] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    estimated_time_minutes: Optional[int] = Field(None, ge=1)
    frequency: Optional[str] = Field(None, max_length=50)
    duration_weeks: Optional[int] = Field(None, ge=1)
    success_criteria: Optional[str] = None
    measurable_target: Optional[Dict[str, Any]] = None
    target_value: Optional[float] = None
    suggested_start_date: Optional[date] = None
    suggested_time_of_day: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    reminder_enabled: Optional[bool] = None
    reminder_schedule: Optional[Dict[str, Any]] = None
    user_response: Optional[str] = Field(None, pattern="^(accepted|declined|deferred|modified)$")
    user_notes: Optional[str] = None
    user_modified_action: Optional[str] = None
    related_goal_ids: Optional[List[UUID]] = None


class RecommendationResponse(IDTimestampSchema, RecommendationBase):
    user_id: UUID
    observation_id: Optional[UUID] = None
    pattern_id: Optional[UUID] = None
    status: RecommendationStatusStr
    user_response: Optional[str] = None
    user_notes: Optional[str] = None
    user_modified_action: Optional[str] = None
    responded_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_version: str
    prompt_version: str
    confidence_score: float
    generation_metadata: Dict[str, Any]


class RecommendationListParams(PaginationParams):
    status: Optional[RecommendationStatusStr] = None
    recommendation_type: Optional[RecommendationTypeStr] = None
    priority: Optional[RecommendationPriorityStr] = None
    action_category: Optional[str] = None
    suggested_start_date_from: Optional[date] = None
    suggested_start_date_to: Optional[date] = None


# Recommendation Effectiveness schemas
class RecommendationEffectivenessBase(BaseModel):
    evaluation_period_start: date
    evaluation_period_end: date
    adherence_rate: Optional[float] = Field(None, ge=0, le=1)
    completion_rate: Optional[float] = Field(None, ge=0, le=1)
    progress_towards_target: Optional[float] = Field(None, ge=0)
    outcome: Optional[str] = Field(None, pattern="^(improved|no_change|worsened|mixed)$")
    outcome_details: Optional[str] = None
    measured_improvement: Optional[float] = None
    statistical_significance: Optional[float] = Field(None, ge=0, le=1)
    unintended_consequences: List[str] = Field(default_factory=list)
    positive_spillovers: List[str] = Field(default_factory=list)
    user_satisfaction: Optional[int] = Field(None, ge=1, le=10)
    user_feedback: Optional[str] = None
    would_recommend: Optional[bool] = None
    suggested_adjustments: List[str] = Field(default_factory=list)
    continue_recommendation: Optional[bool] = None
    evaluation_method: str = "automated"
    data_completeness: float = Field(default=1.0, ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class RecommendationEffectivenessCreate(RecommendationEffectivenessBase):
    recommendation_id: UUID


class RecommendationEffectivenessUpdate(BaseModel):
    adherence_rate: Optional[float] = Field(None, ge=0, le=1)
    completion_rate: Optional[float] = Field(None, ge=0, le=1)
    progress_towards_target: Optional[float] = Field(None, ge=0)
    outcome: Optional[str] = Field(None, pattern="^(improved|no_change|worsened|mixed)$")
    outcome_details: Optional[str] = None
    measured_improvement: Optional[float] = None
    statistical_significance: Optional[float] = Field(None, ge=0, le=1)
    unintended_consequences: Optional[List[str]] = None
    positive_spillovers: Optional[List[str]] = None
    user_satisfaction: Optional[int] = Field(None, ge=1, le=10)
    user_feedback: Optional[str] = None
    would_recommend: Optional[bool] = None
    suggested_adjustments: Optional[List[str]] = None
    continue_recommendation: Optional[bool] = None
    evaluation_method: Optional[str] = None
    data_completeness: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None


class RecommendationEffectivenessResponse(IDTimestampSchema, RecommendationEffectivenessBase):
    user_id: UUID
    recommendation_id: UUID


# Weekly Report schemas
class WeeklyReportBase(BaseModel):
    week_start: date
    week_end: date
    report_data: Dict[str, Any] = Field(default_factory=dict)
    week_at_a_glance: Dict[str, Any] = Field(default_factory=dict)
    digital_life: Dict[str, Any] = Field(default_factory=dict)
    physical_wellbeing: Dict[str, Any] = Field(default_factory=dict)
    personal_patterns: Dict[str, Any] = Field(default_factory=dict)
    missed_goals: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    long_term_consequences: List[Dict[str, Any]] = Field(default_factory=list)
    next_week_action_plan: Dict[str, Any] = Field(default_factory=dict)


class WeeklyReportCreate(WeeklyReportBase):
    pass


class WeeklyReportUpdate(BaseModel):
    status: Optional[WeeklyReportStatusStr] = None
    report_data: Optional[Dict[str, Any]] = None
    week_at_a_glance: Optional[Dict[str, Any]] = None
    digital_life: Optional[Dict[str, Any]] = None
    physical_wellbeing: Optional[Dict[str, Any]] = None
    personal_patterns: Optional[Dict[str, Any]] = None
    missed_goals: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    long_term_consequences: Optional[List[Dict[str, Any]]] = None
    next_week_action_plan: Optional[Dict[str, Any]] = None
    is_read: Optional[bool] = None
    user_rating: Optional[int] = Field(None, ge=1, le=10)
    user_feedback: Optional[str] = None
    shared: Optional[bool] = None


class WeeklyReportResponse(IDTimestampSchema, WeeklyReportBase):
    user_id: UUID
    status: WeeklyReportStatusStr
    generated_at: Optional[datetime] = None
    generation_duration_seconds: Optional[float] = None
    model_version: str
    prompt_version: str
    data_completeness: float
    sources_used: List[str]
    is_read: bool
    read_at: Optional[datetime] = None
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    shared: bool


class WeeklyReportListParams(PaginationParams):
    status: Optional[WeeklyReportStatusStr] = None
    week_start_from: Optional[date] = None
    week_start_to: Optional[date] = None
    is_read: Optional[bool] = None


# Notification schemas
class NotificationBase(BaseModel):
    notification_type: NotificationTypeStr
    priority: NotificationPriorityStr = NotificationPriorityStr.NORMAL
    title: str = Field(..., min_length=1, max_length=255)
    message: str
    action_text: Optional[str] = Field(None, max_length=100)
    action_url: Optional[str] = None
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[UUID] = None
    threshold_id: Optional[UUID] = None
    channels: List[str] = Field(default_factory=list)
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    recurring: bool = False
    recurrence_rule: Optional[str] = Field(None, max_length=100)
    nudge_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatusStr] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = None
    action_text: Optional[str] = Field(None, max_length=100)
    action_url: Optional[str] = None
    channels: Optional[List[str]] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    nudge_context: Optional[Dict[str, Any]] = None
    nudge_effectiveness: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(IDTimestampSchema, NotificationBase):
    user_id: UUID
    status: NotificationStatusStr
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    snoozed_until: Optional[datetime] = None
    clicked: bool
    clicked_at: Optional[datetime] = None
    action_taken: Optional[str] = None


class NotificationListParams(PaginationParams):
    notification_type: Optional[NotificationTypeStr] = None
    status: Optional[NotificationStatusStr] = None
    priority: Optional[NotificationPriorityStr] = None
    scheduled_for_from: Optional[datetime] = None
    scheduled_for_to: Optional[datetime] = None
    is_read: Optional[bool] = None


# Push Subscription schemas
class PushSubscriptionBase(BaseModel):
    endpoint: str
    p256dh_key: str = Field(..., max_length=100)
    auth_key: str = Field(..., max_length=100)
    user_agent: Optional[str] = None


class PushSubscriptionCreate(PushSubscriptionBase):
    pass


class PushSubscriptionResponse(IDTimestampSchema, PushSubscriptionBase):
    user_id: UUID
    is_active: bool
    last_used: Optional[datetime] = None