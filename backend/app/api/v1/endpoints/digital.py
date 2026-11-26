"""
Digital Activity Tracking endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, timedelta

from app.core.dependencies import get_db_session, get_current_user, get_pagination_params
from app.models.digital import (
    DigitalActivity,
    WebsiteClassification,
    DailyDigitalSummary,
    WeeklyDigitalSummary,
    DigitalWellbeingThreshold,
)
from app.models.user import User
from app.schemas.digital import (
    DigitalActivityCreate,
    DigitalActivityBatchCreate,
    DigitalActivityUpdate,
    DigitalActivityResponse,
    DigitalActivityListParams,
    WebsiteClassificationBase,
    WebsiteClassificationCreate,
    WebsiteClassificationUpdate,
    WebsiteClassificationResponse,
    DailyDigitalSummaryResponse,
    WeeklyDigitalSummaryResponse,
    DigitalWellbeingThresholdBase,
    DigitalWellbeingThresholdCreate,
    DigitalWellbeingThresholdUpdate,
    DigitalWellbeingThresholdResponse,
)
from app.schemas.base import PaginatedResponse, paginate


router = APIRouter()


# Digital Activity - Batch ingest (for browser extension)
@router.post("/activities/batch", response_model=List[DigitalActivityResponse], status_code=status.HTTP_201_CREATED, summary="Batch create digital activities")
async def batch_create_digital_activities(
    request: DigitalActivityBatchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Batch create digital activity records (for browser extension sync)."""
    activities = []
    for activity_data in request.activities:
        # Apply user's website classifications
        classification = await get_website_classification(current_user.id, activity_data.domain, activity_data.subdomain, db)
        if classification:
            activity_data.category = classification.category
            activity_data.subcategory = classification.subcategory
            activity_data.is_productive = classification.is_productive
            activity_data.user_classified = True

        activity = DigitalActivity(
            user_id=current_user.id,
            **activity_data.model_dump(),
        )
        activities.append(activity)

    db.add_all(activities)
    await db.commit()

    # Refresh all
    for activity in activities:
        await db.refresh(activity)

    return activities


@router.post("/activities", response_model=DigitalActivityResponse, status_code=status.HTTP_201_CREATED, summary="Create digital activity")
async def create_digital_activity(
    request: DigitalActivityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a single digital activity record."""
    # Apply classification
    classification = await get_website_classification(current_user.id, request.domain, request.subdomain, db)
    if classification:
        request.category = classification.category
        request.subcategory = classification.subcategory
        request.is_productive = classification.is_productive
        request.user_classified = True

    activity = DigitalActivity(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def get_website_classification(
    user_id: UUID,
    domain: str,
    subdomain: Optional[str],
    db: AsyncSession,
) -> Optional[WebsiteClassification]:
    """Get user's classification for a website."""
    from app.models.digital import WebsiteClassification, DigitalActivityCategory

    query = select(WebsiteClassification).where(
        WebsiteClassification.user_id == user_id,
        WebsiteClassification.domain == domain,
    )

    if subdomain:
        query = query.where(
            (WebsiteClassification.subdomain == subdomain) | (WebsiteClassification.subdomain.is_(None))
        )
    else:
        query = query.where(WebsiteClassification.subdomain.is_(None))

    query = query.order_by(WebsiteClassification.priority.desc())
    result = await db.execute(query)
    return result.scalar_one_or_none()


@router.get("/activities", response_model=PaginatedResponse[DigitalActivityResponse], summary="List digital activities")
async def list_digital_activities(
    params: DigitalActivityListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List digital activities with pagination."""
    query = select(DigitalActivity).where(DigitalActivity.user_id == current_user.id)

    if params.category:
        query = query.where(DigitalActivity.category == params.category)
    if params.domain:
        query = query.where(DigitalActivity.domain == params.domain)
    if params.start_time_from:
        query = query.where(DigitalActivity.start_time >= params.start_time_from)
    if params.start_time_to:
        query = query.where(DigitalActivity.start_time <= params.start_time_to)
    if params.is_productive is not None:
        query = query.where(DigitalActivity.is_productive == params.is_productive)
    if params.session_id:
        query = query.where(DigitalActivity.session_id == params.session_id)

    query = query.order_by(desc(DigitalActivity.start_time))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/activities/summary/daily", response_model=List[DailyDigitalSummaryResponse], summary="Get daily digital summaries")
async def get_daily_digital_summaries(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get daily digital activity summaries for a date range."""
    result = await db.execute(
        select(DailyDigitalSummary)
        .where(
            DailyDigitalSummary.user_id == current_user.id,
            DailyDigitalSummary.date >= start_date,
            DailyDigitalSummary.date <= end_date,
        )
        .order_by(DailyDigitalSummary.date)
    )
    return result.scalars().all()


@router.get("/activities/summary/weekly", response_model=List[WeeklyDigitalSummaryResponse], summary="Get weekly digital summaries")
async def get_weekly_digital_summaries(
    week_start_from: date = Query(...),
    week_start_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get weekly digital activity summaries for a week range."""
    result = await db.execute(
        select(WeeklyDigitalSummary)
        .where(
            WeeklyDigitalSummary.user_id == current_user.id,
            WeeklyDigitalSummary.week_start >= week_start_from,
            WeeklyDigitalSummary.week_start <= week_start_to,
        )
        .order_by(WeeklyDigitalSummary.week_start)
    )
    return result.scalars().all()


@router.get("/activities/today", summary="Get today's digital activity stats")
async def get_today_digital_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get today's digital activity statistics."""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # Get today's activities
    result = await db.execute(
        select(DigitalActivity)
        .where(
            DigitalActivity.user_id == current_user.id,
            DigitalActivity.start_time >= start_of_day,
            DigitalActivity.start_time <= end_of_day,
        )
    )
    activities = result.scalars().all()

    # Calculate stats
    total_seconds = sum(a.duration_seconds for a in activities)
    active_seconds = sum(a.active_seconds for a in activities)
    category_breakdown = {}
    domain_breakdown = {}

    for a in activities:
        cat = a.category.value
        category_breakdown[cat] = category_breakdown.get(cat, 0) + a.active_seconds
        domain_breakdown[a.domain] = domain_breakdown.get(a.domain, 0) + a.active_seconds

    # Top domains
    top_domains = sorted(domain_breakdown.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "date": today,
        "total_seconds": total_seconds,
        "active_seconds": active_seconds,
        "idle_seconds": total_seconds - active_seconds,
        "session_count": len(activities),
        "category_breakdown": category_breakdown,
        "top_domains": [{"domain": d, "seconds": s} for d, s in top_domains],
        "productive_seconds": sum(a.active_seconds for a in activities if a.is_productive),
        "unproductive_seconds": sum(a.active_seconds for a in activities if a.is_productive == False),
    }


# Website Classifications
@router.post("/classifications", response_model=WebsiteClassificationResponse, status_code=status.HTTP_201_CREATED, summary="Create website classification")
async def create_website_classification(
    request: WebsiteClassificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a website classification rule."""
    classification = WebsiteClassification(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(classification)
    await db.commit()
    await db.refresh(classification)
    return classification


@router.get("/classifications", response_model=List[WebsiteClassificationResponse], summary="List website classifications")
async def list_website_classifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List user's website classifications."""
    result = await db.execute(
        select(WebsiteClassification)
        .where(WebsiteClassification.user_id == current_user.id)
        .order_by(WebsiteClassification.priority.desc())
    )
    return result.scalars().all()


@router.put("/classifications/{classification_id}", response_model=WebsiteClassificationResponse, summary="Update website classification")
async def update_website_classification(
    classification_id: UUID,
    request: WebsiteClassificationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a website classification."""
    result = await db.execute(
        select(WebsiteClassification).where(
            WebsiteClassification.id == classification_id,
            WebsiteClassification.user_id == current_user.id,
        )
    )
    classification = result.scalar_one_or_none()

    if not classification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classification not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(classification, field, value)

    await db.commit()
    await db.refresh(classification)
    return classification


@router.delete("/classifications/{classification_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete website classification")
async def delete_website_classification(
    classification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a website classification."""
    result = await db.execute(
        select(WebsiteClassification).where(
            WebsiteClassification.id == classification_id,
            WebsiteClassification.user_id == current_user.id,
        )
    )
    classification = result.scalar_one_or_none()

    if not classification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classification not found")

    await db.delete(classification)
    await db.commit()


# Digital Wellbeing Thresholds
@router.post("/thresholds", response_model=DigitalWellbeingThresholdResponse, status_code=status.HTTP_201_CREATED, summary="Create digital wellbeing threshold")
async def create_threshold(
    request: DigitalWellbeingThresholdCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a digital wellbeing threshold for nudges."""
    threshold = DigitalWellbeingThreshold(
        user_id=current_user.id,
        **request.model_dump(),
    )
    db.add(threshold)
    await db.commit()
    await db.refresh(threshold)
    return threshold


@router.get("/thresholds", response_model=List[DigitalWellbeingThresholdResponse], summary="List digital wellbeing thresholds")
async def list_thresholds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List user's digital wellbeing thresholds."""
    result = await db.execute(
        select(DigitalWellbeingThreshold)
        .where(DigitalWellbeingThreshold.user_id == current_user.id)
        .order_by(DigitalWellbeingThreshold.created_at.desc())
    )
    return result.scalars().all()


@router.put("/thresholds/{threshold_id}", response_model=DigitalWellbeingThresholdResponse, summary="Update digital wellbeing threshold")
async def update_threshold(
    threshold_id: UUID,
    request: DigitalWellbeingThresholdUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a digital wellbeing threshold."""
    result = await db.execute(
        select(DigitalWellbeingThreshold).where(
            DigitalWellbeingThreshold.id == threshold_id,
            DigitalWellbeingThreshold.user_id == current_user.id,
        )
    )
    threshold = result.scalar_one_or_none()

    if not threshold:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threshold not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(threshold, field, value)

    await db.commit()
    await db.refresh(threshold)
    return threshold


@router.delete("/thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete digital wellbeing threshold")
async def delete_threshold(
    threshold_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a digital wellbeing threshold."""
    result = await db.execute(
        select(DigitalWellbeingThreshold).where(
            DigitalWellbeingThreshold.id == threshold_id,
            DigitalWellbeingThreshold.user_id == current_user.id,
        )
    )
    threshold = result.scalar_one_or_none()

    if not threshold:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threshold not found")

    await db.delete(threshold)
    await db.commit()


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete digital activity")
async def delete_digital_activity(
    activity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete one digital activity record."""
    result = await db.execute(
        select(DigitalActivity).where(
            DigitalActivity.id == activity_id,
            DigitalActivity.user_id == current_user.id,
        )
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    await db.delete(activity)
    await db.commit()


# ===== AI for Digital (classify + insights) =====
import json as _json
import httpx as _hx
from datetime import timezone as _tz
from app.core.config import settings as _cfg
from app.models.digital import DigitalActivityCategory as _Cat

_CAT_VALUES = [c.value for c in _Cat]
_FENCE = chr(96) * 3


async def _nv_text(system: str, user: str, max_tokens: int = 3000) -> str:
    key = _cfg.NVIDIA_API_KEY
    if not key:
        raise HTTPException(status_code=503, detail="NVIDIA_API_KEY is not set in backend/.env")
    url = _cfg.NVIDIA_BASE_URL.rstrip("/") + "/chat/completions"
    hdr = {"Authorization": "Bearer " + key}
    body = {"model": _cfg.NVIDIA_MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.2, "max_tokens": max_tokens, "reasoning_effort": "none"}
    try:
        async with _hx.AsyncClient(timeout=100) as c:
            r = await c.post(url, headers=hdr, json=body)
            if r.status_code == 400:
                body.pop("reasoning_effort", None)
                body["max_tokens"] = 8000
                r = await c.post(url, headers=hdr, json=body)
    except _hx.HTTPError as e:
        raise HTTPException(status_code=502, detail="Could not reach NVIDIA: " + str(e))
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="NVIDIA returned %s: %s" % (r.status_code, r.text[:300]))
    text = (r.json()["choices"][0]["message"].get("content") or "").strip()
    if not text:
        raise HTTPException(status_code=502, detail="The AI returned no text. Try again.")
    return text


def _parse_json(text: str):
    t = text.replace(_FENCE + "json", "").replace(_FENCE, "").strip()
    starts = [i for i in (t.find("["), t.find("{")) if i >= 0]
    if not starts:
        return None
    s = min(starts)
    e = max(t.rfind("]"), t.rfind("}"))
    if e <= s:
        return None
    try:
        return _json.loads(t[s:e + 1])
    except Exception:
        return None


@router.post("/ai/classify", summary="AI-classify unclassified sites and apps")
async def ai_classify_activities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    since = datetime.now(_tz.utc) - timedelta(days=14)
    res = await db.execute(select(DigitalActivity).where(
        DigitalActivity.user_id == current_user.id,
        DigitalActivity.start_time >= since,
        DigitalActivity.category == _Cat.UNCLASSIFIED,
    ))
    rows = res.scalars().all()
    secs, titles = {}, {}
    for a in rows:
        secs[a.domain] = secs.get(a.domain, 0) + a.active_seconds
        if a.title and a.domain not in titles:
            titles[a.domain] = a.title[:60]
    top = sorted(secs, key=secs.get, reverse=True)[:30]
    if not top:
        return {"classified": [], "remaining": 0}
    cats = ", ".join(c for c in _CAT_VALUES if c != "unclassified")
    system = ("You classify websites and Windows desktop apps for a wellbeing app. Reply with ONLY a JSON array and no other text. "
        "One object per item: {\"name\": exact name given, \"category\": one of [" + cats + "], \"productive\": true, false or null (null = neutral), \"confidence\": 0 to 1}. "
        "Names ending in .exe are desktop apps. If you do not recognise an item, use category \"unclassified\" with confidence below 0.4. Never guess.")
    text = await _nv_text(system, _json.dumps([{"name": d, "example_title": titles.get(d, "")} for d in top]))
    data = _parse_json(text)
    if not isinstance(data, list):
        raise HTTPException(status_code=502, detail="The AI did not return a usable list. Try again.")
    picked = {}
    for d in data:
        if not isinstance(d, dict) or d.get("name") not in secs:
            continue
        cat = d.get("category")
        try:
            conf = float(d.get("confidence", 0.5))
        except (TypeError, ValueError):
            conf = 0.5
        if cat in _CAT_VALUES and cat != "unclassified" and conf >= 0.5:
            prod = d.get("productive")
            picked[d["name"]] = (cat, prod if isinstance(prod, bool) else None, conf)
    for a in rows:
        if a.domain in picked:
            cat, prod, conf = picked[a.domain]
            a.category = _Cat(cat)
            a.is_productive = prod
            a.confidence_score = conf
            a.subcategory = "ai"
    for name, (cat, prod, conf) in picked.items():
        ex = await db.execute(select(WebsiteClassification).where(
            WebsiteClassification.user_id == current_user.id,
            WebsiteClassification.domain == name,
            WebsiteClassification.subdomain.is_(None),
        ))
        if ex.scalars().first() is None:
            db.add(WebsiteClassification(user_id=current_user.id, domain=name, category=_Cat(cat), is_productive=prod, priority=0, auto_created=True, notes="Classified by AI"))
    await db.commit()
    return {"classified": [{"domain": n, "category": c, "productive": p, "confidence": round(f, 2)} for n, (c, p, f) in picked.items()], "remaining": len(top) - len(picked)}


@router.post("/ai/insights", summary="AI conclusions from the last 7 days of digital activity")
async def ai_digital_insights(
    tz_offset: int = Query(330, description="Minutes ahead of UTC for the user's local time"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    since = datetime.now(_tz.utc) - timedelta(days=7)
    res = await db.execute(select(DigitalActivity).where(
        DigitalActivity.user_id == current_user.id,
        DigitalActivity.start_time >= since,
    ))
    rows = res.scalars().all()
    if not rows:
        return {"stats": None, "insight": None, "message": "No activity in the last 7 days."}
    per_day, per_cat, per_dom, late_days = {}, {}, {}, {}
    prod = unprod = neutral = late = longest = 0
    for a in rows:
        loc = a.start_time + timedelta(minutes=tz_offset)
        d = loc.date().isoformat()
        s = a.active_seconds
        cat = a.category.value
        per_day[d] = per_day.get(d, 0) + s
        per_cat[cat] = per_cat.get(cat, 0) + s
        per_dom[a.domain] = per_dom.get(a.domain, 0) + s
        if a.is_productive is True:
            prod += s
        elif a.is_productive is False:
            unprod += s
        else:
            neutral += s
        if loc.hour >= 23 or loc.hour < 5:
            late += s
            late_days[d] = late_days.get(d, 0) + s
        longest = max(longest, s)
    total = prod + unprod + neutral
    m = lambda x: round(x / 60)
    stats = {
        "days_with_data": len(per_day),
        "total_minutes": m(total),
        "avg_minutes_per_day": m(total / max(1, len(per_day))),
        "minutes_by_day": {k: m(v) for k, v in sorted(per_day.items())},
        "minutes_by_category": {k: m(v) for k, v in sorted(per_cat.items(), key=lambda x: -x[1])},
        "top_sites_apps": [{"name": k, "minutes": m(v)} for k, v in sorted(per_dom.items(), key=lambda x: -x[1])[:6]],
        "productive_minutes": m(prod),
        "unproductive_minutes": m(unprod),
        "neutral_minutes": m(neutral),
        "unproductive_share_pct": round(unprod / (prod + unprod) * 100) if (prod + unprod) else None,
        "late_night_minutes_11pm_to_5am": m(late),
        "late_night_minutes_by_day": {k: m(v) for k, v in sorted(late_days.items())},
        "longest_single_session_minutes": m(longest),
        "unclassified_minutes": m(per_cat.get("unclassified", 0)),
    }
    system = ("You are the digital-wellbeing analyst inside KnowThyself. Use ONLY the JSON stats below, which cover the user's laptop only (browser and desktop apps) for the last 7 days. "
        "Reply with ONLY a JSON object: {\"summary\": 2-3 plain sentences with exact numbers, \"patterns\": up to 4 short strings, each naming a real pattern with a number (late-night use, distraction share, heavy days, top time sinks), \"action\": ONE concrete action for tomorrow}. "
        "If a pattern is not in the data, do not mention it. Do not give medical advice.\n\nSTATS:\n" + _json.dumps(stats))
    text = await _nv_text(system, "Analyse my digital activity.", 2000)
    data = _parse_json(text)
    if isinstance(data, dict) and data.get("summary"):
        insight = {"summary": str(data.get("summary")), "patterns": [str(p) for p in (data.get("patterns") or [])][:4], "action": str(data.get("action") or "")}
    else:
        insight = {"summary": text, "patterns": [], "action": ""}
    return {"stats": stats, "insight": insight, "model": _cfg.NVIDIA_MODEL}
