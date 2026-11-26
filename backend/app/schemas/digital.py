"""
Digital activity tracking schemas.
"""
from pydantic import AliasChoices
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, HttpUrl

from app.schemas.base import IDTimestampSchema, PaginationParams
from app.models.digital import DigitalActivityCategory, DigitalActivitySource


# Enums for API
class DigitalActivityCategoryStr(str, Enum):
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


class DigitalActivitySourceStr(str, Enum):
    BROWSER_EXTENSION = "browser_extension"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    MANUAL = "manual"
    IMPORTED = "imported"


# Digital Activity schemas
class DigitalActivityBase(BaseModel):
    url: str
    domain: str = Field(..., max_length=255)
    subdomain: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = None
    favicon_url: Optional[HttpUrl] = None
    category: DigitalActivityCategoryStr = DigitalActivityCategoryStr.UNCLASSIFIED
    subcategory: Optional[str] = Field(None, max_length=100)
    is_productive: Optional[bool] = None
    user_classified: bool = False
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    start_time: datetime
    end_time: datetime
    duration_seconds: int = Field(..., gt=0)
    active_seconds: int = Field(..., ge=0)
    idle_seconds: int = Field(default=0, ge=0)
    tab_switches: int = Field(default=0, ge=0)
    scroll_count: int = Field(default=0, ge=0)
    click_count: int = Field(default=0, ge=0)
    keystroke_count: int = Field(default=0, ge=0)
    is_fullscreen: bool = False
    is_incognito: bool = False
    window_id: Optional[int] = None
    tab_id: Optional[int] = None
    device_type: Optional[str] = Field(None, max_length=50)
    os: Optional[str] = Field(None, max_length=50)
    browser: Optional[str] = Field(None, max_length=50)
    screen_resolution: Optional[str] = Field(None, max_length=20)
    referrer_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class DigitalActivityCreate(DigitalActivityBase):
    session_id: Optional[str] = Field(None, max_length=100)
    source: DigitalActivitySourceStr = DigitalActivitySourceStr.BROWSER_EXTENSION


class DigitalActivityBatchCreate(BaseModel):
    activities: List[DigitalActivityCreate] = Field(..., min_length=1, max_length=1000)


class DigitalActivityUpdate(BaseModel):
    category: Optional[DigitalActivityCategoryStr] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    is_productive: Optional[bool] = None
    user_classified: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class DigitalActivityResponse(IDTimestampSchema, DigitalActivityBase):
    user_id: UUID
    session_id: Optional[str] = None
    source: DigitalActivitySourceStr


class DigitalActivityListParams(PaginationParams):
    category: Optional[DigitalActivityCategoryStr] = None
    domain: Optional[str] = None
    start_time_from: Optional[datetime] = None
    start_time_to: Optional[datetime] = None
    is_productive: Optional[bool] = None
    session_id: Optional[str] = None


# Website Classification schemas
class WebsiteClassificationBase(BaseModel):
    domain: str = Field(..., max_length=255)
    subdomain: Optional[str] = Field(None, max_length=255)
    url_pattern: Optional[str] = None
    category: DigitalActivityCategoryStr
    subcategory: Optional[str] = Field(None, max_length=100)
    is_productive: Optional[bool] = None
    priority: int = Field(default=0, ge=0)
    notes: Optional[str] = None


class WebsiteClassificationCreate(WebsiteClassificationBase):
    pass


class WebsiteClassificationUpdate(BaseModel):
    category: Optional[DigitalActivityCategoryStr] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    is_productive: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class WebsiteClassificationResponse(IDTimestampSchema, WebsiteClassificationBase):
    user_id: UUID
    auto_created: bool


# Daily Digital Summary schemas
class DailyDigitalSummaryResponse(IDTimestampSchema):
    user_id: UUID
    date: date
    total_seconds: int
    active_seconds: int
    idle_seconds: int
    category_breakdown: Dict[str, int]
    top_domains: List[Dict[str, Any]]
    productive_seconds: int
    unproductive_seconds: int
    neutral_seconds: int
    session_count: int
    avg_session_seconds: float
    longest_session_seconds: int
    total_tab_switches: int
    total_interruptions: int
    hourly_distribution: Dict[str, int]
    day_part_distribution: Dict[str, int]
    data_completeness: float
    sources: List[str]


class WeeklyDigitalSummaryResponse(IDTimestampSchema):
    user_id: UUID
    week_start: date
    week_end: date
    total_seconds: int
    active_seconds: int
    daily_average_seconds: float
    trend_vs_previous_week: Optional[float] = None
    category_breakdown: Dict[str, int]
    category_trends: Dict[str, float]
    goals_met: int
    goals_total: int
    focus_sessions_count: int
    focus_sessions_total_minutes: int
    avg_focus_quality: Optional[float] = None
    data_completeness: float


# Digital Wellbeing Threshold schemas
class DigitalWellbeingThresholdBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    metric: str = Field(..., max_length=50)
    category: Optional[DigitalActivityCategoryStr] = None
    domain: Optional[str] = Field(None, max_length=255)
    threshold_value: float
    threshold_unit: str = Field(default="seconds", max_length=20)
    comparison: str = Field(default="gte", pattern="^(gte|lte|gt|lt|eq)$")
    window_type: str = Field(default="daily", pattern="^(daily|weekly|session)$")
    window_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    window_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    days_of_week: List[int] = Field(default_factory=list)
    nudge_enabled: bool = True
    nudge_message: Optional[str] = None
    nudge_severity: str = Field(default="info", pattern="^(info|warning|critical)$")
    cooldown_minutes: int = Field(default=60, ge=0)
    max_nudges_per_day: int = Field(default=3, ge=1)


class DigitalWellbeingThresholdCreate(DigitalWellbeingThresholdBase):
    pass


class DigitalWellbeingThresholdUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    metric: Optional[str] = Field(None, max_length=50)
    category: Optional[DigitalActivityCategoryStr] = None
    domain: Optional[str] = Field(None, max_length=255)
    threshold_value: Optional[float] = None
    threshold_unit: Optional[str] = Field(None, max_length=20)
    comparison: Optional[str] = Field(None, pattern="^(gte|lte|gt|lt|eq)$")
    window_type: Optional[str] = Field(None, pattern="^(daily|weekly|session)$")
    window_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    window_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    days_of_week: Optional[List[int]] = None
    nudge_enabled: Optional[bool] = None
    nudge_message: Optional[str] = None
    nudge_severity: Optional[str] = Field(None, pattern="^(info|warning|critical)$")
    cooldown_minutes: Optional[int] = Field(None, ge=0)
    max_nudges_per_day: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class DigitalWellbeingThresholdResponse(IDTimestampSchema, DigitalWellbeingThresholdBase):
    user_id: UUID
    is_active: bool
    last_triggered: Optional[datetime] = None
    trigger_count_today: int
    trigger_count_total: int


# Focus Session Digital Data
class FocusSessionDigitalDataResponse(IDTimestampSchema):
    focus_session_id: UUID
    user_id: UUID
    session_start: datetime
    session_end: Optional[datetime] = None
    total_websites_visited: int
    unique_domains_visited: int
    tab_switches: int
    distraction_events: List[Dict[str, Any]]
    productive_seconds: int
    distracting_seconds: int
    neutral_seconds: int
    top_distracting_domains: List[Dict[str, Any]]
    focus_score: Optional[float] = None
    continuity_score: Optional[float] = None