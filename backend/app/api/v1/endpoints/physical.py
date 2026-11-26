"""
Physical Health endpoints - Sleep, Nutrition, Physical Activity, Hydration.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.dependencies import get_db_session, get_current_user, get_pagination_params
from app.models.physical import (
    SleepRecord,
    NutritionRecord,
    DailyNutritionSummary,
    PhysicalActivity,
    DailyPhysicalActivitySummary,
    HydrationRecord,
    DailyHydrationSummary,
)
from app.models.user import User
from app.schemas.physical import (
    SleepRecordBase,
    SleepRecordCreate,
    SleepRecordUpdate,
    SleepRecordResponse,
    SleepRecordListParams,
    NutritionRecordBase,
    NutritionRecordCreate,
    NutritionRecordUpdate,
    NutritionRecordResponse,
    NutritionRecordListParams,
    DailyNutritionSummaryResponse,
    PhysicalActivityBase,
    PhysicalActivityCreate,
    PhysicalActivityUpdate,
    PhysicalActivityResponse,
    PhysicalActivityListParams,
    DailyPhysicalActivitySummaryResponse,
    HydrationRecordBase,
    HydrationRecordCreate,
    HydrationRecordUpdate,
    HydrationRecordResponse,
    HydrationRecordListParams,
    DailyHydrationSummaryResponse,
)
from app.schemas.base import PaginatedResponse, paginate


router = APIRouter()


# Sleep Records
@router.post("/sleep", response_model=SleepRecordResponse, status_code=status.HTTP_201_CREATED, summary="Create sleep record")
async def create_sleep_record(
    request: SleepRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a sleep record."""
    sleep_record = SleepRecord(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(sleep_record)
    await db.commit()
    await db.refresh(sleep_record)
    return sleep_record


@router.get("/sleep", response_model=PaginatedResponse[SleepRecordResponse], summary="List sleep records")
async def list_sleep_records(
    params: SleepRecordListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List sleep records with pagination."""
    query = select(SleepRecord).where(SleepRecord.user_id == current_user.id)

    if params.date_from:
        query = query.where(SleepRecord.date >= params.date_from)
    if params.date_to:
        query = query.where(SleepRecord.date <= params.date_to)
    if params.source:
        query = query.where(SleepRecord.source == params.source)
    if params.quality_rating:
        query = query.where(SleepRecord.quality_rating == params.quality_rating)

    query = query.order_by(SleepRecord.date.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/sleep/today", response_model=Optional[SleepRecordResponse], summary="Get today's sleep record")
async def get_today_sleep(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get today's sleep record if exists."""
    today = date.today()
    result = await db.execute(
        select(SleepRecord)
        .where(SleepRecord.user_id == current_user.id, SleepRecord.date == today)
    )
    return result.scalar_one_or_none()


@router.put("/sleep/{record_id}", response_model=SleepRecordResponse, summary="Update sleep record")
async def update_sleep_record(
    record_id: UUID,
    request: SleepRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a sleep record."""
    result = await db.execute(
        select(SleepRecord).where(
            SleepRecord.id == record_id,
            SleepRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep record not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/sleep/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete sleep record")
async def delete_sleep_record(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a sleep record."""
    result = await db.execute(
        select(SleepRecord).where(
            SleepRecord.id == record_id,
            SleepRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep record not found")

    await db.delete(record)
    await db.commit()


# Nutrition Records
@router.post("/nutrition", response_model=NutritionRecordResponse, status_code=status.HTTP_201_CREATED, summary="Create nutrition record")
async def create_nutrition_record(
    request: NutritionRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a nutrition/food record."""
    nutrition_record = NutritionRecord(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(nutrition_record)
    await db.commit()
    await db.refresh(nutrition_record)
    return nutrition_record


@router.get("/nutrition", response_model=PaginatedResponse[NutritionRecordResponse], summary="List nutrition records")
async def list_nutrition_records(
    params: NutritionRecordListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List nutrition records with pagination."""
    query = select(NutritionRecord).where(NutritionRecord.user_id == current_user.id)

    if params.date_from:
        query = query.where(NutritionRecord.date >= params.date_from)
    if params.date_to:
        query = query.where(NutritionRecord.date <= params.date_to)
    if params.meal_type:
        query = query.where(NutritionRecord.meal_type == params.meal_type)
    if params.source:
        query = query.where(NutritionRecord.source == params.source)

    query = query.order_by(NutritionRecord.timestamp.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/nutrition/today", response_model=List[NutritionRecordResponse], summary="Get today's nutrition records")
async def get_today_nutrition(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get today's nutrition records."""
    today = date.today()
    result = await db.execute(
        select(NutritionRecord)
        .where(NutritionRecord.user_id == current_user.id, NutritionRecord.date == today)
        .order_by(NutritionRecord.timestamp)
    )
    return result.scalars().all()


@router.get("/nutrition/summary/daily", response_model=List[DailyNutritionSummaryResponse], summary="Get daily nutrition summaries")
async def get_daily_nutrition_summaries(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get daily nutrition summaries for a date range."""
    result = await db.execute(
        select(DailyNutritionSummary)
        .where(
            DailyNutritionSummary.user_id == current_user.id,
            DailyNutritionSummary.date >= start_date,
            DailyNutritionSummary.date <= end_date,
        )
        .order_by(DailyNutritionSummary.date)
    )
    return result.scalars().all()


@router.put("/nutrition/{record_id}", response_model=NutritionRecordResponse, summary="Update nutrition record")
async def update_nutrition_record(
    record_id: UUID,
    request: NutritionRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a nutrition record."""
    result = await db.execute(
        select(NutritionRecord).where(
            NutritionRecord.id == record_id,
            NutritionRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition record not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/nutrition/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete nutrition record")
async def delete_nutrition_record(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a nutrition record."""
    result = await db.execute(
        select(NutritionRecord).where(
            NutritionRecord.id == record_id,
            NutritionRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition record not found")

    await db.delete(record)
    await db.commit()


# Physical Activity Records
@router.post("/activity", response_model=PhysicalActivityResponse, status_code=status.HTTP_201_CREATED, summary="Create physical activity record")
async def create_physical_activity(
    request: PhysicalActivityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a physical activity record."""
    activity = PhysicalActivity(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


@router.get("/activity", response_model=PaginatedResponse[PhysicalActivityResponse], summary="List physical activity records")
async def list_physical_activities(
    params: PhysicalActivityListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List physical activity records with pagination."""
    query = select(PhysicalActivity).where(PhysicalActivity.user_id == current_user.id)

    if params.date_from:
        query = query.where(PhysicalActivity.date >= params.date_from)
    if params.date_to:
        query = query.where(PhysicalActivity.date <= params.date_to)
    if params.activity_type:
        query = query.where(PhysicalActivity.activity_type == params.activity_type)
    if params.source:
        query = query.where(PhysicalActivity.source == params.source)
    if params.intensity:
        query = query.where(PhysicalActivity.intensity == params.intensity)

    query = query.order_by(PhysicalActivity.start_time.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/activity/summary/daily", response_model=List[DailyPhysicalActivitySummaryResponse], summary="Get daily physical activity summaries")
async def get_daily_activity_summaries(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get daily physical activity summaries for a date range."""
    result = await db.execute(
        select(DailyPhysicalActivitySummary)
        .where(
            DailyPhysicalActivitySummary.user_id == current_user.id,
            DailyPhysicalActivitySummary.date >= start_date,
            DailyPhysicalActivitySummary.date <= end_date,
        )
        .order_by(DailyPhysicalActivitySummary.date)
    )
    return result.scalars().all()


@router.put("/activity/{record_id}", response_model=PhysicalActivityResponse, summary="Update physical activity record")
async def update_physical_activity(
    record_id: UUID,
    request: PhysicalActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a physical activity record."""
    result = await db.execute(
        select(PhysicalActivity).where(
            PhysicalActivity.id == record_id,
            PhysicalActivity.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical activity record not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/activity/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete physical activity record")
async def delete_physical_activity(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a physical activity record."""
    result = await db.execute(
        select(PhysicalActivity).where(
            PhysicalActivity.id == record_id,
            PhysicalActivity.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical activity record not found")

    await db.delete(record)
    await db.commit()


# Hydration Records
@router.post("/hydration", response_model=HydrationRecordResponse, status_code=status.HTTP_201_CREATED, summary="Create hydration record")
async def create_hydration_record(
    request: HydrationRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a hydration record."""
    hydration_record = HydrationRecord(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(hydration_record)
    await db.commit()
    await db.refresh(hydration_record)
    return hydration_record


@router.get("/hydration", response_model=PaginatedResponse[HydrationRecordResponse], summary="List hydration records")
async def list_hydration_records(
    params: HydrationRecordListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List hydration records with pagination."""
    query = select(HydrationRecord).where(HydrationRecord.user_id == current_user.id)

    if params.date_from:
        query = query.where(HydrationRecord.date >= params.date_from)
    if params.date_to:
        query = query.where(HydrationRecord.date <= params.date_to)
    if params.beverage_type:
        query = query.where(HydrationRecord.beverage_type == params.beverage_type)

    query = query.order_by(HydrationRecord.timestamp.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/hydration/today", response_model=List[HydrationRecordResponse], summary="Get today's hydration records")
async def get_today_hydration(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get today's hydration records."""
    today = date.today()
    result = await db.execute(
        select(HydrationRecord)
        .where(HydrationRecord.user_id == current_user.id, HydrationRecord.date == today)
        .order_by(HydrationRecord.timestamp)
    )
    return result.scalars().all()


@router.get("/hydration/summary/daily", response_model=List[DailyHydrationSummaryResponse], summary="Get daily hydration summaries")
async def get_daily_hydration_summaries(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get daily hydration summaries for a date range."""
    result = await db.execute(
        select(DailyHydrationSummary)
        .where(
            DailyHydrationSummary.user_id == current_user.id,
            DailyHydrationSummary.date >= start_date,
            DailyHydrationSummary.date <= end_date,
        )
        .order_by(DailyHydrationSummary.date)
    )
    return result.scalars().all()


@router.put("/hydration/{record_id}", response_model=HydrationRecordResponse, summary="Update hydration record")
async def update_hydration_record(
    record_id: UUID,
    request: HydrationRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a hydration record."""
    result = await db.execute(
        select(HydrationRecord).where(
            HydrationRecord.id == record_id,
            HydrationRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hydration record not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/hydration/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete hydration record")
async def delete_hydration_record(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a hydration record."""
    result = await db.execute(
        select(HydrationRecord).where(
            HydrationRecord.id == record_id,
            HydrationRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hydration record not found")

    await db.delete(record)
    await db.commit()


# Combined Today's Summary
@router.get("/today/summary", summary="Get today's complete health summary")
async def get_today_health_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get today's complete health summary across all domains."""
    today = date.today()

    # Sleep
    sleep_result = await db.execute(
        select(SleepRecord).where(SleepRecord.user_id == current_user.id, SleepRecord.date == today)
    )
    sleep = sleep_result.scalar_one_or_none()

    # Nutrition
    nutrition_result = await db.execute(
        select(NutritionRecord).where(NutritionRecord.user_id == current_user.id, NutritionRecord.date == today)
    )
    nutrition = nutrition_result.scalars().all()

    # Physical Activity
    activity_result = await db.execute(
        select(PhysicalActivity).where(PhysicalActivity.user_id == current_user.id, PhysicalActivity.date == today)
    )
    activities = activity_result.scalars().all()

    # Hydration
    hydration_result = await db.execute(
        select(HydrationRecord).where(HydrationRecord.user_id == current_user.id, HydrationRecord.date == today)
    )
    hydration = hydration_result.scalars().all()

    # Calculate totals
    total_calories = sum(n.calories or 0 for n in nutrition)
    total_protein = sum(n.protein_g or 0 for n in nutrition)
    total_carbs = sum(n.carbs_g or 0 for n in nutrition)
    total_fat = sum(n.fat_g or 0 for n in nutrition)
    total_fiber = sum(n.fiber_g or 0 for n in nutrition)

    total_activity_minutes = sum(a.duration_minutes for a in activities)
    total_calories_burned = sum(a.calories_burned or 0 for a in activities)
    total_steps = sum(a.steps or 0 for a in activities)

    total_hydration_ml = sum(h.amount_ml for h in hydration)

    return {
        "date": today,
        "sleep": {
            "total_sleep_minutes": sleep.total_sleep_minutes if sleep else None,
            "quality_rating": sleep.quality_rating.value if sleep and sleep.quality_rating else None,
            "bedtime": sleep.bedtime if sleep else None,
            "wake_time": sleep.wake_time if sleep else None,
        },
        "nutrition": {
            "meals_count": len(nutrition),
            "total_calories": total_calories,
            "total_protein_g": total_protein,
            "total_carbs_g": total_carbs,
            "total_fat_g": total_fat,
            "total_fiber_g": total_fiber,
            "by_meal": {
                meal.value: [n.model_dump() for n in nutrition if n.meal_type == meal]
                for meal in set(n.meal_type for n in nutrition)
            },
        },
        "activity": {
            "sessions_count": len(activities),
            "total_minutes": total_activity_minutes,
            "total_calories_burned": total_calories_burned,
            "total_steps": total_steps,
            "by_type": {
                a.activity_type.value: a.duration_minutes for a in activities
            },
        },
        "hydration": {
            "total_ml": total_hydration_ml,
            "by_beverage": {
                h.beverage_type: sum(h2.amount_ml for h2 in hydration if h2.beverage_type == h.beverage_type)
                for h in hydration
            },
        },
    }

# Daily steps (imported from a phone health export)
from pydantic import BaseModel as PydModel, Field
from app.models.physical import DailyStepCount


class StepDayIn(PydModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    steps: int = Field(ge=0, le=200000)
    source: str = "apple_health_export"


class StepsImportIn(PydModel):
    items: List[StepDayIn] = Field(max_length=400)


@router.post("/steps/import", summary="Import daily step totals")
async def import_steps(
    request: StepsImportIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    n = 0
    for it in request.items:
        day = date.fromisoformat(it.date)
        res = await db.execute(
            select(DailyStepCount).where(DailyStepCount.user_id == current_user.id, DailyStepCount.date == day)
        )
        row = res.scalar_one_or_none()
        if row:
            row.steps = it.steps
            row.source = it.source
        else:
            db.add(DailyStepCount(user_id=current_user.id, date=day, steps=it.steps, source=it.source))
        n += 1
    await db.commit()
    return {"imported": n}


@router.get("/steps", summary="List daily step totals")
async def list_steps(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    q = select(DailyStepCount).where(DailyStepCount.user_id == current_user.id)
    if date_from:
        q = q.where(DailyStepCount.date >= date_from)
    if date_to:
        q = q.where(DailyStepCount.date <= date_to)
    rows = (await db.execute(q.order_by(DailyStepCount.date.desc()))).scalars().all()
    return [{"date": r.date.isoformat(), "steps": r.steps, "source": r.source} for r in rows]
