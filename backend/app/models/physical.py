"""
Physical health tracking models - Sleep, Nutrition, Physical Activity, Hydration.
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


class SleepQuality(str, enum.Enum):
    VERY_POOR = "very_poor"
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class SleepSource(str, enum.Enum):
    MANUAL = "manual"
    WEARABLE = "wearable"
    PHONE_APP = "phone_app"
    SMART_MATTRESS = "smart_mattress"
    IMPORTED = "imported"
    ESTIMATED = "estimated"


class SleepRecord(BaseModel):
    """Sleep tracking records."""
    __tablename__ = "sleep_records"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[SleepSource] = mapped_column(Enum(SleepSource), default=SleepSource.MANUAL, nullable=False)
    device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Sleep timing
    bedtime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sleep_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sleep_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    wake_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Duration (minutes)
    time_in_bed_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    total_sleep_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    deep_sleep_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    light_sleep_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rem_sleep_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    awake_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleep_latency_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Time to fall asleep
    wake_after_sleep_onset_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Quality
    quality_rating: Mapped[Optional[SleepQuality]] = mapped_column(Enum(SleepQuality), nullable=True)
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-100
    restfulness_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10

    # Disruptions
    wake_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interruption_details: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)

    # Environment
    room_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    noise_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    light_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Pre-sleep behavior
    screen_time_before_bed_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    caffeine_after_noon: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alcohol_before_bed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exercise_before_bed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meal_before_bed_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sleep_records")

    __table_args__ = (
        Index("ix_sleep_records_user_id", "user_id"),
        Index("ix_sleep_records_date", "date"),
        Index("ix_sleep_records_sleep_start", "sleep_start"),
        UniqueConstraint("user_id", "date", "sleep_start", name="uq_sleep_record"),
        CheckConstraint("total_sleep_minutes >= 0", name="ck_sleep_total_nonnegative"),
        CheckConstraint("time_in_bed_minutes >= total_sleep_minutes", name="ck_sleep_time_in_bed_gte_total"),
    )


class NutritionSource(str, enum.Enum):
    MANUAL = "manual"
    BARCODE_SCAN = "barcode_scan"
    RECIPE = "recipe"
    RESTAURANT = "restaurant"
    MEAL_PLAN = "meal_plan"
    IMPORTED = "imported"
    AI_ESTIMATED = "ai_estimated"


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    BRUNCH = "brunch"
    LUNCH = "lunch"
    SNACK = "snack"
    DINNER = "dinner"
    LATE_NIGHT = "late_night"
    OTHER = "other"


class NutritionRecord(BaseModel):
    """Nutrition/food tracking records."""
    __tablename__ = "nutrition_records"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType), default=MealType.OTHER, nullable=False)
    source: Mapped[NutritionSource] = mapped_column(Enum(NutritionSource), default=NutritionSource.MANUAL, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Food identification
    food_name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    food_database_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # USDA, OpenFoodFacts, etc.

    # Quantity
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # grams, ml, pieces, cups, etc.
    serving_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    serving_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Macronutrients (per record)
    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    protein_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fat_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sugar_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    added_sugar_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Micronutrients (key ones)
    sodium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    potassium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calcium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    iron_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vitamin_c_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vitamin_d_iu: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vitamin_b12_mcg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    magnesium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    zinc_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    omega3_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Additional
    cholesterol_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    saturated_fat_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trans_fat_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Quality indicators
    processing_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # unprocessed, minimally, processed, ultra_processed
    nutriscore: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # A, B, C, D, E
    health_stars: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.5-5

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recipe_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="nutrition_records")

    __table_args__ = (
        Index("ix_nutrition_records_user_id", "user_id"),
        Index("ix_nutrition_records_date", "date"),
        Index("ix_nutrition_records_timestamp", "timestamp"),
        Index("ix_nutrition_records_meal_type", "meal_type"),
        CheckConstraint("quantity > 0", name="ck_nutrition_quantity_positive"),
        CheckConstraint("calories IS NULL OR calories >= 0", name="ck_nutrition_calories_nonnegative"),
    )


class DailyNutritionSummary(BaseModel):
    """Pre-aggregated daily nutrition summaries."""
    __tablename__ = "daily_nutrition_summaries"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Totals
    total_calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_protein_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_carbs_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_fat_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_fiber_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_sugar_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_added_sugar_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_sodium_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Meal breakdown
    meals_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meal_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # meal_type -> {calories, protein, etc.}

    # Food groups
    food_groups: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # group -> servings

    # Quality
    avg_nutriscore: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    ultra_processed_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dietary_variety_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100

    # Hydration (from nutrition records)
    water_from_food_ml: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    data_completeness: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sources: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    estimated_values: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_daily_nutrition_summaries_user_id", "user_id"),
        Index("ix_daily_nutrition_summaries_date", "date"),
        UniqueConstraint("user_id", "date", name="uq_daily_nutrition_summary"),
    )


class PhysicalActivityType(str, enum.Enum):
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


class PhysicalActivityIntensity(str, enum.Enum):
    VERY_LIGHT = "very_light"
    LIGHT = "light"
    MODERATE = "moderate"
    VIGOROUS = "vigorous"
    VERY_VIGOROUS = "very_vigorous"


class PhysicalActivitySource(str, enum.Enum):
    MANUAL = "manual"
    WEARABLE = "wearable"
    PHONE_APP = "phone_app"
    GYM_EQUIPMENT = "gym_equipment"
    IMPORTED = "imported"
    AI_ESTIMATED = "ai_estimated"


class PhysicalActivity(BaseModel):
    """Physical activity/exercise records."""
    __tablename__ = "physical_activities"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    activity_type: Mapped[PhysicalActivityType] = mapped_column(Enum(PhysicalActivityType), nullable=False)
    source: Mapped[PhysicalActivitySource] = mapped_column(Enum(PhysicalActivitySource), default=PhysicalActivitySource.MANUAL, nullable=False)
    device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Duration and intensity
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    intensity: Mapped[Optional[PhysicalActivityIntensity]] = mapped_column(Enum(PhysicalActivityIntensity), nullable=True)
    avg_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    heart_rate_zones: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # zone -> minutes

    # Metrics
    calories_burned: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pace_min_per_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    elevation_gain_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Strength training specifics
    sets: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # sets * reps * weight
    muscle_groups: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Perceived exertion
    rpe: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Rate of Perceived Exertion 1-10
    enjoyment_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10

    # Context
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # gym, home, outdoors, pool
    weather: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    social: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Group activity

    # Recovery
    recovery_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10 next day
    soreness_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="physical_activities")

    __table_args__ = (
        Index("ix_physical_activities_user_id", "user_id"),
        Index("ix_physical_activities_date", "date"),
        Index("ix_physical_activities_type", "activity_type"),
        Index("ix_physical_activities_start_time", "start_time"),
        CheckConstraint("duration_minutes > 0", name="ck_physical_activity_duration_positive"),
        CheckConstraint("calories_burned IS NULL OR calories_burned >= 0", name="ck_physical_activity_calories_nonnegative"),
        CheckConstraint("rpe IS NULL OR (rpe >= 1 AND rpe <= 10)", name="ck_physical_activity_rpe_range"),
    )


class DailyPhysicalActivitySummary(BaseModel):
    """Pre-aggregated daily physical activity summaries."""
    __tablename__ = "daily_physical_activity_summaries"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Totals
    total_duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_calories_burned: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Activity breakdown
    activity_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # type -> minutes
    intensity_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # intensity -> minutes

    # Sessions
    session_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    strength_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cardio_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    flexibility_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Metrics
    avg_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    active_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Moderate+ intensity

    # Goals
    mvpa_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Moderate-to-Vigorous Physical Activity
    step_goal_met: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activity_goal_met: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Sedentary behavior
    sedentary_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prolonged_sedentary_bouts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # >60 min

    # Metadata
    data_completeness: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sources: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    __table_args__ = (
        Index("ix_daily_physical_activity_summaries_user_id", "user_id"),
        Index("ix_daily_physical_activity_summaries_date", "date"),
        UniqueConstraint("user_id", "date", name="uq_daily_physical_activity_summary"),
    )


class HydrationSource(str, enum.Enum):
    MANUAL = "manual"
    SMART_BOTTLE = "smart_bottle"
    APP = "app"
    IMPORTED = "imported"
    ESTIMATED = "estimated"


class HydrationRecord(BaseModel):
    """Hydration tracking records."""
    __tablename__ = "hydration_records"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source: Mapped[HydrationSource] = mapped_column(Enum(HydrationSource), default=HydrationSource.MANUAL, nullable=False)

    # Amount
    amount_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    beverage_type: Mapped[str] = mapped_column(String(50), default="water", nullable=False)  # water, tea, coffee, juice, soda, alcohol, sports_drink, other

    # Hydration quality
    hydration_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Net hydration effect (water=1.0, coffee=0.8, alcohol=-0.5, etc.)
    caffeine_mg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sugar_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    electrolytes_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Context
    meal_related: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exercise_related: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="hydration_records")

    __table_args__ = (
        Index("ix_hydration_records_user_id", "user_id"),
        Index("ix_hydration_records_date", "date"),
        Index("ix_hydration_records_timestamp", "timestamp"),
        CheckConstraint("amount_ml > 0", name="ck_hydration_amount_positive"),
    )


class DailyHydrationSummary(BaseModel):
    """Pre-aggregated daily hydration summaries."""
    __tablename__ = "daily_hydration_summaries"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Totals
    total_ml: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    net_hydration_ml: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Adjusted for diuretic effects
    beverage_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # type -> ml

    # Timing
    first_drink_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    last_drink_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    hourly_distribution: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # hour -> ml

    # Goals
    goal_ml: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    goal_met: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Quality
    total_caffeine_mg: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_sugar_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    water_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    data_completeness: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sources: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    __table_args__ = (
        Index("ix_daily_hydration_summaries_user_id", "user_id"),
        Index("ix_daily_hydration_summaries_date", "date"),
        UniqueConstraint("user_id", "date", name="uq_daily_hydration_summary"),
    )

class DailyStepCount(BaseModel):
    """Daily step totals imported from a phone health export."""
    __tablename__ = "daily_step_counts"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    steps: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="apple_health_export", nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_step_count"),
    )
