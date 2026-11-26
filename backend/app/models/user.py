"""
User and Profile models.
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
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    RESEARCHER = "researcher"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class ActivityLevel(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"


class DietaryPreference(str, enum.Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    OTHER = "other"
    NO_PREFERENCE = "no_preference"


class SleepQuality(str, enum.Enum):
    VERY_POOR = "very_poor"
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class StressLevel(str, enum.Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class User(BaseModel):
    """User account model."""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    health_history: Mapped[List["HealthHistory"]] = relationship(
        "HealthHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    goals: Mapped[List["Goal"]] = relationship(
        "Goal",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    digital_activities: Mapped[List["DigitalActivity"]] = relationship(
        "DigitalActivity",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    physical_activities: Mapped[List["PhysicalActivity"]] = relationship(
        "PhysicalActivity",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sleep_records: Mapped[List["SleepRecord"]] = relationship(
        "SleepRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    nutrition_records: Mapped[List["NutritionRecord"]] = relationship(
        "NutritionRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    hydration_records: Mapped[List["HydrationRecord"]] = relationship(
        "HydrationRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    weekly_surveys: Mapped[List["WeeklySurvey"]] = relationship(
        "WeeklySurvey",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    focus_sessions: Mapped[List["FocusSession"]] = relationship(
        "FocusSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    ai_observations: Mapped[List["AIObservation"]] = relationship(
        "AIObservation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    patterns: Mapped[List["DetectedPattern"]] = relationship(
        "DetectedPattern",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    weekly_reports: Mapped[List["WeeklyReport"]] = relationship(
        "WeeklyReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recommendation_effectiveness: Mapped[List["RecommendationEffectiveness"]] = relationship(
        "RecommendationEffectiveness",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    consent_records: Mapped[List["ConsentRecord"]] = relationship(
        "ConsentRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    push_subscriptions: Mapped[List["PushSubscription"]] = relationship(
        "PushSubscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    website_classifications: Mapped[List["WebsiteClassification"]] = relationship(
        "WebsiteClassification",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(BaseModel):
    """Extended user profile with lifestyle information."""
    __tablename__ = "user_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    activity_level: Mapped[Optional[ActivityLevel]] = mapped_column(Enum(ActivityLevel), nullable=True)
    dietary_preference: Mapped[Optional[DietaryPreference]] = mapped_column(Enum(DietaryPreference), nullable=True)
    dietary_restrictions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    allergies: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    medical_conditions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    medications: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    supplements: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    work_schedule: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "9-5", "shift", "flexible"
    typical_wake_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    typical_bed_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    typical_work_hours: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {"start": "09:00", "end": "17:00", "days": [1,2,3,4,5]}
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    health_provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    health_insurance: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    profile_completeness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")

    __table_args__ = (
        Index("ix_user_profiles_user_id", "user_id"),
    )


class HealthHistory(BaseModel):
    """User-reported health history."""
    __tablename__ = "health_history"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    condition_name: Mapped[str] = mapped_column(String(255), nullable=False)
    condition_category: Mapped[str] = mapped_column(String(100), nullable=False)  # chronic, acute, mental, etc.
    diagnosed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    resolved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # mild, moderate, severe
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diagnosed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    icd_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="user_reported", nullable=False)  # user_reported, imported, verified

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="health_history")

    __table_args__ = (
        Index("ix_health_history_user_id", "user_id"),
        Index("ix_health_history_condition", "condition_name"),
        Index("ix_health_history_active", "is_active"),
    )


class ConsentRecord(BaseModel):
    """User consent and permissions tracking."""
    __tablename__ = "consent_records"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    consent_type: Mapped[str] = mapped_column(String(100), nullable=False)  # data_collection, analytics, marketing, ai_processing, third_party_sharing, push_notifications, browser_tracking
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    consent_version: Mapped[str] = mapped_column(String(20), nullable=False)
    consent_text: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawal_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="consent_records")

    __table_args__ = (
        Index("ix_consent_records_user_id", "user_id"),
        Index("ix_consent_records_type", "consent_type"),
        UniqueConstraint("user_id", "consent_type", "consent_version", name="uq_user_consent_version"),
    )


class AuditLog(BaseModel):
    """Audit trail for sensitive operations."""
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )