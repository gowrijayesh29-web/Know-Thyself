"""
Digital activity tracking models.
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


class DigitalActivityCategory(str, enum.Enum):
    WORK = "work"
    STUDY = "study"
    LEARNING = "learning"
    COMMUNICATION = "communication"
    RESEARCH = "research"
    ENTERTAINMENT = "entertainment"
    SOCIAL_MEDIA = "social_media"
    GAMING = "gaming"
    SHOPPING = "shopping"
    NEWS = "news"
    FINANCE = "finance"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    DEVELOPMENT = "development"
    DESIGN = "design"
    WRITING = "writing"
    READING = "reading"
    VIDEO = "video"
    MUSIC = "music"
    DISTRACTION = "distraction"
    UNCLASSIFIED = "unclassified"


class DigitalActivitySource(str, enum.Enum):
    BROWSER_EXTENSION = "browser_extension"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    MANUAL = "manual"
    IMPORTED = "imported"


class DigitalActivity(BaseModel):
    """Digital activity tracking records."""
    __tablename__ = "digital_activities"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    source: Mapped[DigitalActivitySource] = mapped_column(
        Enum(DigitalActivitySource),
        default=DigitalActivitySource.BROWSER_EXTENSION,
        nullable=False,
    )

    # Website/App identification
    url: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    favicon_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Classification
    category: Mapped[DigitalActivityCategory] = mapped_column(
        Enum(DigitalActivityCategory),
        default=DigitalActivityCategory.UNCLASSIFIED,
        nullable=False,
    )
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_productive: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    user_classified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # AI classification confidence

    # Timing
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    active_seconds: Mapped[int] = mapped_column(Integer, nullable=False)  # Excluding idle time
    idle_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Activity details
    tab_switches: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scroll_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    keystroke_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_fullscreen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_incognito: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    window_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tab_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Device context
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # desktop, laptop, tablet, mobile
    os: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    screen_resolution: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Metadata
    referrer_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="digital_activities")

    __table_args__ = (
        Index("ix_digital_activities_user_id", "user_id"),
        Index("ix_digital_activities_domain", "domain"),
        Index("ix_digital_activities_category", "category"),
        Index("ix_digital_activities_start_time", "start_time"),
        Index("ix_digital_activities_user_date", "user_id", "start_time"),
        CheckConstraint("duration_seconds > 0", name="ck_digital_activities_duration_positive"),
        CheckConstraint("active_seconds >= 0", name="ck_digital_activities_active_nonnegative"),
        CheckConstraint("active_seconds <= duration_seconds", name="ck_digital_activities_active_lte_duration"),
    )


class WebsiteClassification(BaseModel):
    """User-defined website classifications."""
    __tablename__ = "website_classifications"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url_pattern: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Regex pattern for specific paths

    category: Mapped[DigitalActivityCategory] = mapped_column(
        Enum(DigitalActivityCategory),
        nullable=False,
    )
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_productive: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Priority (higher = more specific, overrides general rules)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    auto_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="website_classifications")

    __table_args__ = (
        Index("ix_website_classifications_user_id", "user_id"),
        Index("ix_website_classifications_domain", "domain"),
        UniqueConstraint("user_id", "domain", "subdomain", "url_pattern", name="uq_website_classification"),
    )


class DailyDigitalSummary(BaseModel):
    """Pre-aggregated daily digital activity summaries."""
    __tablename__ = "daily_digital_summaries"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Total time
    total_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    idle_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Category breakdown (seconds)
    category_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Domain breakdown (top domains)
    top_domains: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)

    # Productivity
    productive_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unproductive_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    neutral_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Session stats
    session_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_session_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    longest_session_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Interruptions
    total_tab_switches: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_interruptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Time distribution
    hourly_distribution: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # hour -> seconds
    day_part_distribution: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # morning, afternoon, evening, night

    # Metadata
    data_completeness: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 0-1
    sources: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    __table_args__ = (
        Index("ix_daily_digital_summaries_user_id", "user_id"),
        Index("ix_daily_digital_summaries_date", "date"),
        UniqueConstraint("user_id", "date", name="uq_daily_digital_summary"),
    )


class WeeklyDigitalSummary(BaseModel):
    """Pre-aggregated weekly digital activity summaries."""
    __tablename__ = "weekly_digital_summaries"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Total time
    total_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Trends
    daily_average_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    trend_vs_previous_week: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage change

    # Category breakdown
    category_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    category_trends: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Goals
    goals_met: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    goals_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Focus sessions
    focus_sessions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    focus_sessions_total_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_focus_quality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    data_completeness: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    __table_args__ = (
        Index("ix_weekly_digital_summaries_user_id", "user_id"),
        Index("ix_weekly_digital_summaries_week_start", "week_start"),
        UniqueConstraint("user_id", "week_start", name="uq_weekly_digital_summary"),
    )


class DigitalWellbeingThreshold(BaseModel):
    """User-defined thresholds for digital wellbeing nudges."""
    __tablename__ = "digital_wellbeing_thresholds"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Threshold definition
    metric: Mapped[str] = mapped_column(String(50), nullable=False)  # total_screen_time, social_media_time, distraction_count, etc.
    category: Mapped[Optional[DigitalActivityCategory]] = mapped_column(Enum(DigitalActivityCategory), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_unit: Mapped[str] = mapped_column(String(20), default="seconds", nullable=False)  # seconds, minutes, hours, count
    comparison: Mapped[str] = mapped_column(String(10), default="gte", nullable=False)  # gte, lte, gt, lt, eq

    # Time window
    window_type: Mapped[str] = mapped_column(String(20), default="daily", nullable=False)  # daily, weekly, session
    window_start: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    window_end: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    days_of_week: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)  # Empty = all days

    # Nudge configuration
    nudge_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    nudge_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nudge_severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)  # info, warning, critical
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    max_nudges_per_day: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trigger_count_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trigger_count_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_digital_wellbeing_thresholds_user_id", "user_id"),
        Index("ix_digital_wellbeing_thresholds_active", "is_active"),
    )


class FocusSessionDigitalData(BaseModel):
    """Digital activity during focus sessions."""
    __tablename__ = "focus_session_digital_data"

    focus_session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("focus_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Session timing
    session_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    session_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Digital activity during session
    total_websites_visited: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_domains_visited: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tab_switches: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    distraction_events: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)

    # Category breakdown
    productive_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    distracting_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    neutral_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Top distractions
    top_distracting_domains: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)

    # Focus quality indicators
    focus_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    continuity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100

    __table_args__ = (
        Index("ix_focus_session_digital_data_session_id", "focus_session_id"),
        Index("ix_focus_session_digital_data_user_id", "user_id"),
        UniqueConstraint("focus_session_id", name="uq_focus_session_digital_data"),
    )