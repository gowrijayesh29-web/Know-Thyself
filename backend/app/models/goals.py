"""
Goals, tasks, and focus session models.
"""
import enum
from datetime import date, datetime, time
from typing import Optional, List
from uuid import UUID

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    Time,
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


class GoalCategory(str, enum.Enum):
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


class GoalFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class GoalUnit(str, enum.Enum):
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


class Goal(BaseModel):
    """User goals model."""
    __tablename__ = "goals"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[GoalCategory] = mapped_column(Enum(GoalCategory), nullable=False)
    frequency: Mapped[GoalFrequency] = mapped_column(Enum(GoalFrequency), default=GoalFrequency.DAILY, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.ACTIVE, nullable=False)

    # Target configuration
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_unit: Mapped[GoalUnit] = mapped_column(Enum(GoalUnit), nullable=False)
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timeframe
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    target_days_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # For custom frequency

    # Reminders
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reminder_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    reminder_days: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)  # 0=Monday, 6=Sunday

    # Progress tracking
    current_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # AI and personalization
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1=high, 3=low

    # Metadata
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="goals")
    progress_records: Mapped[List["GoalProgress"]] = relationship(
        "GoalProgress",
        back_populates="goal",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_goals_user_id", "user_id"),
        Index("ix_goals_category", "category"),
        Index("ix_goals_status", "status"),
        Index("ix_goals_dates", "start_date", "end_date"),
        CheckConstraint("target_value >= 0", name="ck_goals_target_nonnegative"),
        CheckConstraint("current_value >= 0", name="ck_goals_current_nonnegative"),
    )


class GoalProgress(BaseModel):
    """Daily/periodic progress records for goals."""
    __tablename__ = "goal_progress"

    goal_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    achieved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)  # manual, auto, imported
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="progress_records")

    __table_args__ = (
        Index("ix_goal_progress_goal_id", "goal_id"),
        Index("ix_goal_progress_date", "date"),
        UniqueConstraint("goal_id", "date", name="uq_goal_progress_date"),
        CheckConstraint("value >= 0", name="ck_goal_progress_value_nonnegative"),
    )


class TaskCategory(str, enum.Enum):
    WORK = "work"
    STUDY = "study"
    PERSONAL = "personal"
    HEALTH = "health"
    ADMIN = "admin"
    CREATIVE = "creative"
    LEARNING = "learning"
    SOCIAL = "social"
    OTHER = "other"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class Task(BaseModel):
    """User-defined tasks."""
    __tablename__ = "tasks"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[TaskCategory] = mapped_column(Enum(TaskCategory), default=TaskCategory.PERSONAL, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)

    # Scheduling
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    scheduled_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Recurrence
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # RRULE format
    recurrence_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Completion
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    goal: Mapped[Optional["Goal"]] = relationship("Goal")
    focus_sessions: Mapped[List["FocusSession"]] = relationship(
        "FocusSession",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_tasks_user_id", "user_id"),
        Index("ix_tasks_goal_id", "goal_id"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_scheduled_date", "scheduled_date"),
        Index("ix_tasks_due_date", "due_date"),
    )


class FocusSessionStatus(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"


class FocusSession(BaseModel):
    """Focus/Pomodoro sessions."""
    __tablename__ = "focus_sessions"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    goal_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[FocusSessionStatus] = mapped_column(
        Enum(FocusSessionStatus),
        default=FocusSessionStatus.PLANNED,
        nullable=False,
    )

    # Timing
    planned_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    planned_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Interruptions
    interruption_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interruption_details: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    total_interruption_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Quality metrics
    focus_quality_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    productivity_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Environment
    environment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # home, office, library, cafe
    noise_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # quiet, moderate, noisy
    device_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="focus_sessions")
    task: Mapped[Optional["Task"]] = relationship("Task", back_populates="focus_sessions")
    goal: Mapped[Optional["Goal"]] = relationship("Goal")

    __table_args__ = (
        Index("ix_focus_sessions_user_id", "user_id"),
        Index("ix_focus_sessions_task_id", "task_id"),
        Index("ix_focus_sessions_status", "status"),
        Index("ix_focus_sessions_actual_start", "actual_start"),
    )