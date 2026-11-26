"""
Goals, tasks, and focus session schemas.
"""
from pydantic import AliasChoices
from datetime import date, datetime, time
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base import IDTimestampSchema, PaginationParams
from app.models.goals import (
    GoalCategory, GoalFrequency, GoalStatus, GoalUnit,
    TaskCategory, TaskPriority, TaskStatus,
    FocusSessionStatus
)


# Enums for API
class GoalCategoryStr(str, Enum):
    DIGITAL_WELLBEING = "digital_wellbeing"
    PHYSICAL_ACTIVITY = "physical_activity"
    NUTRITION = "nutrition"
    SLEEP = "sleep"
    STUDY = "study"
    WORK = "work"
    PERSONAL_ROUTINE = "personal_routine"
    MENTAL_WELLBEING = "mental_wellbeing"
    HYDRATION = "hydration"
    GENERAL_LIFESTYLE = "general_lifestyle"


class GoalFrequencyStr(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class GoalStatusStr(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class GoalUnitStr(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    COUNT = "count"
    STEPS = "steps"
    CALORIES = "calories"
    GRAMS = "grams"
    MILLILITERS = "milliliters"
    LITERS = "liters"
    KG = "kg"
    PERCENTAGE = "percentage"
    SCORE = "score"
    BOOLEAN = "boolean"


class TaskCategoryStr(str, Enum):
    WORK = "work"
    STUDY = "study"
    PERSONAL = "personal"
    HEALTH = "health"
    ADMIN = "admin"
    CREATIVE = "creative"
    LEARNING = "learning"
    SOCIAL = "social"
    OTHER = "other"


class TaskPriorityStr(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatusStr(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class FocusSessionStatusStr(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"


# Goal schemas
class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: GoalCategoryStr
    frequency: GoalFrequencyStr = GoalFrequencyStr.DAILY
    target_value: float = Field(..., ge=0)
    target_unit: GoalUnitStr
    baseline_value: Optional[float] = Field(None, ge=0)
    start_date: date
    end_date: Optional[date] = None
    target_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    reminder_enabled: bool = True
    reminder_time: Optional[time] = None
    reminder_days: List[int] = Field(default_factory=list)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=10)
    priority: int = Field(default=1, ge=1, le=3)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[GoalCategoryStr] = None
    frequency: Optional[GoalFrequencyStr] = None
    status: Optional[GoalStatusStr] = None
    target_value: Optional[float] = Field(None, ge=0)
    target_unit: Optional[GoalUnitStr] = None
    baseline_value: Optional[float] = Field(None, ge=0)
    end_date: Optional[date] = None
    target_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[time] = None
    reminder_days: Optional[List[int]] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=10)
    priority: Optional[int] = Field(None, ge=1, le=3)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class GoalResponse(IDTimestampSchema, GoalBase):
    user_id: UUID
    status: GoalStatusStr
    current_value: float
    progress_percentage: float
    streak_days: int
    longest_streak: int
    last_completed_date: Optional[date] = None
    ai_generated: bool
    ai_reasoning: Optional[str] = None


class GoalProgressBase(BaseModel):
    date: date
    value: float = Field(..., ge=0)
    target_value: float = Field(..., ge=0)
    achieved: bool
    notes: Optional[str] = None
    source: str = "manual"
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class GoalProgressCreate(GoalProgressBase):
    pass


class GoalProgressUpdate(BaseModel):
    value: Optional[float] = Field(None, ge=0)
    achieved: Optional[bool] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GoalProgressResponse(IDTimestampSchema, GoalProgressBase):
    goal_id: UUID


class GoalWithProgress(GoalResponse):
    progress_records: List[GoalProgressResponse] = Field(default_factory=list)


# Goal list params
class GoalListParams(PaginationParams):
    category: Optional[GoalCategoryStr] = None
    status: Optional[GoalStatusStr] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None


# Task schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: TaskCategoryStr = TaskCategoryStr.PERSONAL
    priority: TaskPriorityStr = TaskPriorityStr.MEDIUM
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    recurrence_end_date: Optional[date] = None
    goal_id: Optional[UUID] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[TaskCategoryStr] = None
    priority: Optional[TaskPriorityStr] = None
    status: Optional[TaskStatusStr] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    actual_duration_minutes: Optional[int] = Field(None, ge=0)
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    recurrence_end_date: Optional[date] = None
    goal_id: Optional[UUID] = None
    completion_notes: Optional[str] = None


class TaskResponse(IDTimestampSchema, TaskBase):
    user_id: UUID
    goal_id: Optional[UUID] = None
    status: TaskStatusStr
    actual_duration_minutes: Optional[int] = None
    completed_at: Optional[datetime] = None
    completion_notes: Optional[str] = None


class TaskListParams(PaginationParams):
    status: Optional[TaskStatusStr] = None
    category: Optional[TaskCategoryStr] = None
    priority: Optional[TaskPriorityStr] = None
    scheduled_date_from: Optional[date] = None
    scheduled_date_to: Optional[date] = None
    goal_id: Optional[UUID] = None


# Focus Session schemas
class FocusSessionBase(BaseModel):
    task_id: Optional[UUID] = None
    goal_id: Optional[UUID] = None
    planned_duration_minutes: int = Field(..., ge=1, le=480)
    planned_start: Optional[datetime] = None
    environment_type: Optional[str] = Field(None, max_length=50)
    noise_level: Optional[str] = Field(None, max_length=20)
    device_used: Optional[str] = Field(None, max_length=100)


class FocusSessionCreate(FocusSessionBase):
    pass


class FocusSessionUpdate(BaseModel):
    status: Optional[FocusSessionStatusStr] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = Field(None, ge=0)
    interruption_count: Optional[int] = Field(None, ge=0)
    interruption_details: Optional[List[Dict[str, Any]]] = None
    total_interruption_minutes: Optional[int] = Field(None, ge=0)
    focus_quality_rating: Optional[int] = Field(None, ge=1, le=10)
    productivity_rating: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    environment_type: Optional[str] = Field(None, max_length=50)
    noise_level: Optional[str] = Field(None, max_length=20)
    device_used: Optional[str] = Field(None, max_length=100)


class FocusSessionResponse(IDTimestampSchema, FocusSessionBase):
    user_id: UUID
    task_id: Optional[UUID] = None
    goal_id: Optional[UUID] = None
    status: FocusSessionStatusStr
    actual_duration_minutes: Optional[int] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    interruption_count: int
    interruption_details: List[Dict[str, Any]]
    total_interruption_minutes: int
    focus_quality_rating: Optional[int] = None
    productivity_rating: Optional[int] = None


class FocusSessionListParams(PaginationParams):
    status: Optional[FocusSessionStatusStr] = None
    task_id: Optional[UUID] = None
    goal_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None