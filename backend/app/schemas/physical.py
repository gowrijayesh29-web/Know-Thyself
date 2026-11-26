"""
Physical health schemas - Sleep, Nutrition, Physical Activity, Hydration.
"""
from pydantic import AliasChoices
from datetime import date, datetime, time
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base import IDTimestampSchema, PaginationParams
from app.models.physical import (
    SleepQuality, SleepSource, NutritionSource, MealType,
    PhysicalActivityType, PhysicalActivityIntensity, PhysicalActivitySource,
    HydrationSource
)


# Enums for API
class SleepQualityStr(str, Enum):
    VERY_POOR = "very_poor"
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class SleepSourceStr(str, Enum):
    MANUAL = "manual"
    WEARABLE = "wearable"
    PHONE_APP = "phone_app"
    SMART_MATTRESS = "smart_mattress"
    IMPORTED = "imported"
    ESTIMATED = "estimated"


class NutritionSourceStr(str, Enum):
    MANUAL = "manual"
    BARCODE_SCAN = "barcode_scan"
    RECIPE = "recipe"
    RESTAURANT = "restaurant"
    MEAL_PLAN = "meal_plan"
    IMPORTED = "imported"
    AI_ESTIMATED = "ai_estimated"


class MealTypeStr(str, Enum):
    BREAKFAST = "breakfast"
    BRUNCH = "brunch"
    LUNCH = "lunch"
    SNACK = "snack"
    DINNER = "dinner"
    LATE_NIGHT = "late_night"
    OTHER = "other"


class PhysicalActivityTypeStr(str, Enum):
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WEIGHT_TRAINING = "weight_training"
    BODYWEIGHT = "bodyweight"
    YOGA = "yoga"
    PILATES = "pilates"
    HIIT = "hiit"
    CROSSFIT = "crossfit"
    ROWING = "rowing"
    ELLIPTICAL = "elliptical"
    STAIR_CLIMBING = "stair_climbing"
    HIKING = "hiking"
    SPORTS = "sports"
    DANCE = "dance"
    MARTIAL_ARTS = "martial_arts"
    STRETCHING = "stretching"
    MOBILITY = "mobility"
    OTHER = "other"


class PhysicalActivityIntensityStr(str, Enum):
    VERY_LIGHT = "very_light"
    LIGHT = "light"
    MODERATE = "moderate"
    VIGOROUS = "vigorous"
    VERY_VIGOROUS = "very_vigorous"


class PhysicalActivitySourceStr(str, Enum):
    MANUAL = "manual"
    WEARABLE = "wearable"
    PHONE_APP = "phone_app"
    GYM_EQUIPMENT = "gym_equipment"
    IMPORTED = "imported"
    AI_ESTIMATED = "ai_estimated"


class HydrationSourceStr(str, Enum):
    MANUAL = "manual"
    SMART_BOTTLE = "smart_bottle"
    APP = "app"
    IMPORTED = "imported"
    ESTIMATED = "estimated"


# Sleep schemas
class SleepRecordBase(BaseModel):
    date: date
    source: SleepSourceStr = SleepSourceStr.MANUAL
    device_id: Optional[str] = Field(None, max_length=100)
    bedtime: datetime
    sleep_start: datetime
    sleep_end: datetime
    wake_time: datetime
    time_in_bed_minutes: int = Field(..., ge=0)
    total_sleep_minutes: int = Field(..., ge=0)
    deep_sleep_minutes: Optional[int] = Field(None, ge=0)
    light_sleep_minutes: Optional[int] = Field(None, ge=0)
    rem_sleep_minutes: Optional[int] = Field(None, ge=0)
    awake_minutes: Optional[int] = Field(None, ge=0)
    sleep_latency_minutes: Optional[int] = Field(None, ge=0)
    wake_after_sleep_onset_minutes: Optional[int] = Field(None, ge=0)
    quality_rating: Optional[SleepQualityStr] = None
    quality_score: Optional[int] = Field(None, ge=0, le=100)
    restfulness_rating: Optional[int] = Field(None, ge=1, le=10)
    wake_count: int = Field(default=0, ge=0)
    interruption_details: List[Dict[str, Any]] = Field(default_factory=list)
    room_temperature: Optional[float] = None
    noise_level: Optional[str] = Field(None, max_length=20)
    light_level: Optional[str] = Field(None, max_length=20)
    screen_time_before_bed_minutes: Optional[int] = Field(None, ge=0)
    caffeine_after_noon: bool = False
    alcohol_before_bed: bool = False
    exercise_before_bed: bool = False
    meal_before_bed_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class SleepRecordCreate(SleepRecordBase):
    pass


class SleepRecordUpdate(BaseModel):
    date: Optional[date] = None
    source: Optional[SleepSourceStr] = None
    device_id: Optional[str] = Field(None, max_length=100)
    bedtime: Optional[datetime] = None
    sleep_start: Optional[datetime] = None
    sleep_end: Optional[datetime] = None
    wake_time: Optional[datetime] = None
    time_in_bed_minutes: Optional[int] = Field(None, ge=0)
    total_sleep_minutes: Optional[int] = Field(None, ge=0)
    deep_sleep_minutes: Optional[int] = Field(None, ge=0)
    light_sleep_minutes: Optional[int] = Field(None, ge=0)
    rem_sleep_minutes: Optional[int] = Field(None, ge=0)
    awake_minutes: Optional[int] = Field(None, ge=0)
    sleep_latency_minutes: Optional[int] = Field(None, ge=0)
    wake_after_sleep_onset_minutes: Optional[int] = Field(None, ge=0)
    quality_rating: Optional[SleepQualityStr] = None
    quality_score: Optional[int] = Field(None, ge=0, le=100)
    restfulness_rating: Optional[int] = Field(None, ge=1, le=10)
    wake_count: Optional[int] = Field(None, ge=0)
    interruption_details: Optional[List[Dict[str, Any]]] = None
    room_temperature: Optional[float] = None
    noise_level: Optional[str] = Field(None, max_length=20)
    light_level: Optional[str] = Field(None, max_length=20)
    screen_time_before_bed_minutes: Optional[int] = Field(None, ge=0)
    caffeine_after_bed: Optional[bool] = None
    alcohol_before_bed: Optional[bool] = None
    exercise_before_bed: Optional[bool] = None
    meal_before_bed_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SleepRecordResponse(IDTimestampSchema, SleepRecordBase):
    user_id: UUID


class SleepRecordListParams(PaginationParams):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    source: Optional[SleepSourceStr] = None
    quality_rating: Optional[SleepQualityStr] = None


# Nutrition schemas
class NutritionRecordBase(BaseModel):
    date: date
    meal_type: MealTypeStr = MealTypeStr.OTHER
    source: NutritionSourceStr = NutritionSourceStr.MANUAL
    timestamp: datetime
    food_name: str = Field(..., max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    barcode: Optional[str] = Field(None, max_length=50)
    food_database_id: Optional[str] = Field(None, max_length=100)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=50)
    serving_size: Optional[float] = Field(None, gt=0)
    serving_unit: Optional[str] = Field(None, max_length=50)
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    added_sugar_g: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    potassium_mg: Optional[float] = Field(None, ge=0)
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    vitamin_d_iu: Optional[float] = Field(None, ge=0)
    vitamin_b12_mcg: Optional[float] = Field(None, ge=0)
    magnesium_mg: Optional[float] = Field(None, ge=0)
    zinc_mg: Optional[float] = Field(None, ge=0)
    omega3_g: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    saturated_fat_g: Optional[float] = Field(None, ge=0)
    trans_fat_g: Optional[float] = Field(None, ge=0)
    processing_level: Optional[str] = Field(None, max_length=50)
    nutriscore: Optional[str] = Field(None, max_length=1)
    health_stars: Optional[float] = Field(None, ge=0.5, le=5)
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    recipe_id: Optional[str] = Field(None, max_length=100)
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class NutritionRecordCreate(NutritionRecordBase):
    pass


class NutritionRecordUpdate(BaseModel):
    date: Optional[date] = None
    meal_type: Optional[MealTypeStr] = None
    source: Optional[NutritionSourceStr] = None
    timestamp: Optional[datetime] = None
    food_name: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    barcode: Optional[str] = Field(None, max_length=50)
    food_database_id: Optional[str] = Field(None, max_length=100)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    serving_size: Optional[float] = Field(None, gt=0)
    serving_unit: Optional[str] = Field(None, max_length=50)
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    added_sugar_g: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    potassium_mg: Optional[float] = Field(None, ge=0)
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    vitamin_d_iu: Optional[float] = Field(None, ge=0)
    vitamin_b12_mcg: Optional[float] = Field(None, ge=0)
    magnesium_mg: Optional[float] = Field(None, ge=0)
    zinc_mg: Optional[float] = Field(None, ge=0)
    omega3_g: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    saturated_fat_g: Optional[float] = Field(None, ge=0)
    trans_fat_g: Optional[float] = Field(None, ge=0)
    processing_level: Optional[str] = Field(None, max_length=50)
    nutriscore: Optional[str] = Field(None, max_length=1)
    health_stars: Optional[float] = Field(None, ge=0.5, le=5)
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    recipe_id: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class NutritionRecordResponse(IDTimestampSchema, NutritionRecordBase):
    user_id: UUID


class NutritionRecordListParams(PaginationParams):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    meal_type: Optional[MealTypeStr] = None
    source: Optional[NutritionSourceStr] = None


# Daily Nutrition Summary
class DailyNutritionSummaryResponse(IDTimestampSchema):
    user_id: UUID
    date: date
    total_calories: Optional[float] = None
    total_protein_g: Optional[float] = None
    total_carbs_g: Optional[float] = None
    total_fat_g: Optional[float] = None
    total_fiber_g: Optional[float] = None
    total_sugar_g: Optional[float] = None
    total_added_sugar_g: Optional[float] = None
    total_sodium_mg: Optional[float] = None
    meals_count: int
    meal_breakdown: Dict[str, Any]
    food_groups: Dict[str, Any]
    avg_nutriscore: Optional[str] = None
    ultra_processed_percentage: Optional[float] = None
    dietary_variety_score: Optional[float] = None
    water_from_food_ml: Optional[float] = None
    data_completeness: float
    sources: List[str]
    estimated_values: bool


# Physical Activity schemas
class PhysicalActivityBase(BaseModel):
    date: date
    activity_type: PhysicalActivityTypeStr
    source: PhysicalActivitySourceStr = PhysicalActivitySourceStr.MANUAL
    device_id: Optional[str] = Field(None, max_length=100)
    start_time: datetime
    end_time: datetime
    duration_minutes: int = Field(..., gt=0)
    intensity: Optional[PhysicalActivityIntensityStr] = None
    avg_heart_rate: Optional[int] = Field(None, ge=30, le=220)
    max_heart_rate: Optional[int] = Field(None, ge=30, le=220)
    heart_rate_zones: Optional[Dict[str, Any]] = None
    calories_burned: Optional[float] = Field(None, ge=0)
    distance_km: Optional[float] = Field(None, ge=0)
    steps: Optional[int] = Field(None, ge=0)
    pace_min_per_km: Optional[float] = Field(None, ge=0)
    elevation_gain_m: Optional[float] = Field(None, ge=0)
    sets: Optional[int] = Field(None, ge=0)
    reps: Optional[int] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    volume_kg: Optional[float] = Field(None, ge=0)
    muscle_groups: List[str] = Field(default_factory=list)
    rpe: Optional[int] = Field(None, ge=1, le=10)
    enjoyment_rating: Optional[int] = Field(None, ge=1, le=10)
    location: Optional[str] = Field(None, max_length=100)
    weather: Optional[str] = Field(None, max_length=50)
    temperature_c: Optional[float] = None
    social: bool = False
    recovery_rating: Optional[int] = Field(None, ge=1, le=10)
    soreness_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class PhysicalActivityCreate(PhysicalActivityBase):
    pass


class PhysicalActivityUpdate(BaseModel):
    date: Optional[date] = None
    activity_type: Optional[PhysicalActivityTypeStr] = None
    source: Optional[PhysicalActivitySourceStr] = None
    device_id: Optional[str] = Field(None, max_length=100)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    intensity: Optional[PhysicalActivityIntensityStr] = None
    avg_heart_rate: Optional[int] = Field(None, ge=30, le=220)
    max_heart_rate: Optional[int] = Field(None, ge=30, le=220)
    heart_rate_zones: Optional[Dict[str, Any]] = None
    calories_burned: Optional[float] = Field(None, ge=0)
    distance_km: Optional[float] = Field(None, ge=0)
    steps: Optional[int] = Field(None, ge=0)
    pace_min_per_km: Optional[float] = Field(None, ge=0)
    elevation_gain_m: Optional[float] = Field(None, ge=0)
    sets: Optional[int] = Field(None, ge=0)
    reps: Optional[int] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    volume_kg: Optional[float] = Field(None, ge=0)
    muscle_groups: Optional[List[str]] = None
    rpe: Optional[int] = Field(None, ge=1, le=10)
    enjoyment_rating: Optional[int] = Field(None, ge=1, le=10)
    location: Optional[str] = Field(None, max_length=100)
    weather: Optional[str] = Field(None, max_length=50)
    temperature_c: Optional[float] = None
    social: Optional[bool] = None
    recovery_rating: Optional[int] = Field(None, ge=1, le=10)
    soreness_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PhysicalActivityResponse(IDTimestampSchema, PhysicalActivityBase):
    user_id: UUID


class PhysicalActivityListParams(PaginationParams):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    activity_type: Optional[PhysicalActivityTypeStr] = None
    source: Optional[PhysicalActivitySourceStr] = None
    intensity: Optional[PhysicalActivityIntensityStr] = None


# Daily Physical Activity Summary
class DailyPhysicalActivitySummaryResponse(IDTimestampSchema):
    user_id: UUID
    date: date
    total_duration_minutes: int
    total_calories_burned: Optional[float] = None
    total_steps: Optional[int] = None
    total_distance_km: Optional[float] = None
    activity_breakdown: Dict[str, int]
    intensity_breakdown: Dict[str, int]
    session_count: int
    strength_sessions: int
    cardio_sessions: int
    flexibility_sessions: int
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    active_minutes: int
    mvpa_minutes: int
    step_goal_met: bool
    activity_goal_met: bool
    sedentary_hours: Optional[float] = None
    prolonged_sedentary_bouts: int
    data_completeness: float
    sources: List[str]


# Hydration schemas
class HydrationRecordBase(BaseModel):
    date: date
    timestamp: datetime
    source: HydrationSourceStr = HydrationSourceStr.MANUAL
    amount_ml: int = Field(..., gt=0)
    beverage_type: str = Field(default="water", max_length=50)
    hydration_index: Optional[float] = None
    caffeine_mg: Optional[int] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    electrolytes_mg: Optional[float] = Field(None, ge=0)
    meal_related: bool = False
    exercise_related: bool = False
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("meta_data", "metadata"))


class HydrationRecordCreate(HydrationRecordBase):
    pass


class HydrationRecordUpdate(BaseModel):
    date: Optional[date] = None
    timestamp: Optional[datetime] = None
    source: Optional[HydrationSourceStr] = None
    amount_ml: Optional[int] = Field(None, gt=0)
    beverage_type: Optional[str] = Field(None, max_length=50)
    hydration_index: Optional[float] = None
    caffeine_mg: Optional[int] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    electrolytes_mg: Optional[float] = Field(None, ge=0)
    meal_related: Optional[bool] = None
    exercise_related: Optional[bool] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HydrationRecordResponse(IDTimestampSchema, HydrationRecordBase):
    user_id: UUID


class HydrationRecordListParams(PaginationParams):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    beverage_type: Optional[str] = None


# Daily Hydration Summary
class DailyHydrationSummaryResponse(IDTimestampSchema):
    user_id: UUID
    date: date
    total_ml: int
    net_hydration_ml: Optional[float] = None
    beverage_breakdown: Dict[str, int]
    first_drink_time: Optional[time] = None
    last_drink_time: Optional[time] = None
    hourly_distribution: Dict[str, int]
    goal_ml: Optional[int] = None
    goal_met: bool
    total_caffeine_mg: int
    total_sugar_g: Optional[float] = None
    water_percentage: Optional[float] = None
    data_completeness: float
    sources: List[str]