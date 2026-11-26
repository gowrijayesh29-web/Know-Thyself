"""
User and authentication schemas.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from app.schemas.base import IDTimestampSchema, PaginationParams
from app.models.user import UserRole, UserStatus, Gender, ActivityLevel, DietaryPreference


# Enums for API
class UserRoleStr(str, Enum):
    USER = "user"
    ADMIN = "admin"
    RESEARCHER = "researcher"


class UserStatusStr(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class GenderStr(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class ActivityLevelStr(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"


class DietaryPreferenceStr(str, Enum):
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


# Auth schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: UUID
    exp: int
    type: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    timezone: str = "UTC"
    locale: str = "en"
    accept_terms: bool = True
    marketing_consent: bool = False


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    timezone: str = "UTC"
    locale: str = "en"
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRoleStr = UserRoleStr.USER


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = None
    locale: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    avatar_url: Optional[str] = None


class UserResponse(IDTimestampSchema, UserBase):
    role: UserRoleStr
    status: UserStatusStr
    is_verified: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    profile_completeness: float = 0.0


class UserProfileBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[GenderStr] = None
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    weight_kg: Optional[float] = Field(None, ge=20, le=500)
    activity_level: Optional[ActivityLevelStr] = None
    dietary_preference: Optional[DietaryPreferenceStr] = None
    dietary_restrictions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    supplements: List[str] = Field(default_factory=list)
    occupation: Optional[str] = Field(None, max_length=100)
    work_schedule: Optional[str] = Field(None, max_length=50)
    typical_wake_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    typical_bed_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    typical_work_hours: Optional[Dict[str, Any]] = None
    bio: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    health_provider: Optional[str] = None
    health_insurance: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(IDTimestampSchema, UserProfileBase):
    user_id: UUID
    onboarding_completed: bool
    onboarding_step: int
    profile_completeness: float


class HealthHistoryBase(BaseModel):
    condition_name: str = Field(..., max_length=255)
    condition_category: str = Field(..., max_length=100)
    diagnosed_date: Optional[date] = None
    resolved_date: Optional[date] = None
    is_active: bool = True
    severity: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    diagnosed_by: Optional[str] = None
    icd_code: Optional[str] = Field(None, max_length=20)
    source: str = "user_reported"


class HealthHistoryCreate(HealthHistoryBase):
    pass


class HealthHistoryUpdate(BaseModel):
    condition_name: Optional[str] = Field(None, max_length=255)
    condition_category: Optional[str] = Field(None, max_length=100)
    diagnosed_date: Optional[date] = None
    resolved_date: Optional[date] = None
    is_active: Optional[bool] = None
    severity: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    diagnosed_by: Optional[str] = None
    icd_code: Optional[str] = Field(None, max_length=20)


class HealthHistoryResponse(IDTimestampSchema, HealthHistoryBase):
    user_id: UUID


class ConsentRecordBase(BaseModel):
    consent_type: str = Field(..., max_length=100)
    consent_given: bool
    consent_version: str = Field(..., max_length=20)
    consent_text: str


class ConsentRecordCreate(ConsentRecordBase):
    pass


class ConsentRecordUpdate(BaseModel):
    consent_given: Optional[bool] = None
    withdrawal_reason: Optional[str] = None


class ConsentRecordResponse(IDTimestampSchema, ConsentRecordBase):
    user_id: UUID
    withdrawn_at: Optional[datetime] = None
    withdrawal_reason: Optional[str] = None


class AuditLogResponse(IDTimestampSchema):
    user_id: Optional[UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    error_message: Optional[str] = None


# Pagination
class UserListParams(PaginationParams):
    search: Optional[str] = None
    role: Optional[UserRoleStr] = None
    status: Optional[UserStatusStr] = None
    is_verified: Optional[bool] = None


class HealthHistoryListParams(PaginationParams):
    condition_category: Optional[str] = None
    is_active: Optional[bool] = None


# Combined response
class UserWithProfile(UserResponse):
    profile: Optional[UserProfileResponse] = None
    health_history: List[HealthHistoryResponse] = Field(default_factory=list)

# --- added by fix script: names other files expect to import from here ---
from app.schemas.base import MessageResponse  # noqa: E402,F401
