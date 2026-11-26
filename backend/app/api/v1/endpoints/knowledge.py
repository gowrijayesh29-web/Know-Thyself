"""
Knowledge Base endpoints - Articles, Evidence Sources, Surveys, Educational Content.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.dependencies import get_db_session, get_current_user, get_pagination_params
from app.models.knowledge import (
    KnowledgeArticle,
    EvidenceSource,
    UserKnowledgeInteraction,
    PersonalizedKnowledgeRecommendation,
    WeeklySurvey,
    SurveyTemplate,
)
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeArticleBase,
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    KnowledgeArticleResponse,
    KnowledgeArticleListParams,
    EvidenceSourceBase,
    EvidenceSourceCreate,
    EvidenceSourceUpdate,
    EvidenceSourceResponse,
    EvidenceSourceListParams,
    UserKnowledgeInteractionBase,
    UserKnowledgeInteractionCreate,
    UserKnowledgeInteractionResponse,
    PersonalizedKnowledgeRecommendationBase,
    PersonalizedKnowledgeRecommendationCreate,
    PersonalizedKnowledgeRecommendationUpdate,
    PersonalizedKnowledgeRecommendationResponse,
    PersonalizedKnowledgeRecommendationListParams,
    WeeklySurveyBase,
    WeeklySurveyCreate,
    WeeklySurveyUpdate,
    WeeklySurveyResponse,
    WeeklySurveyListParams,
    SurveyTemplateBase,
    SurveyTemplateCreate,
    SurveyTemplateUpdate,
    SurveyTemplateResponse,
    SurveyTemplateListParams,
)
from app.schemas.base import PaginatedResponse, paginate


router = APIRouter()


# Knowledge Articles
@router.get("/articles", response_model=PaginatedResponse[KnowledgeArticleResponse], summary="List knowledge articles")
async def list_knowledge_articles(
    params: KnowledgeArticleListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List knowledge articles with pagination and filtering."""
    query = select(KnowledgeArticle).where(KnowledgeArticle.is_published == True)

    if params.category:
        query = query.where(KnowledgeArticle.category == params.category)
    if params.subcategory:
        query = query.where(KnowledgeArticle.subcategory == params.subcategory)
    if params.tag:
        query = query.where(KnowledgeArticle.tags.contains([params.tag]))
    if params.evidence_quality:
        query = query.where(KnowledgeArticle.evidence_quality == params.evidence_quality)
    if params.is_featured is not None:
        query = query.where(KnowledgeArticle.is_featured == params.is_featured)
    if params.difficulty_level:
        query = query.where(KnowledgeArticle.difficulty_level == params.difficulty_level)
    if params.search:
        search_term = f"%{params.search}%"
        query = query.where(
            or_(
                KnowledgeArticle.title.ilike(search_term),
                KnowledgeArticle.summary.ilike(search_term),
                KnowledgeArticle.content.ilike(search_term),
            )
        )

    query = query.order_by(KnowledgeArticle.is_featured.desc(), KnowledgeArticle.view_count.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/articles/featured", response_model=List[KnowledgeArticleResponse], summary="Get featured articles")
async def get_featured_articles(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get featured knowledge articles."""
    result = await db.execute(
        select(KnowledgeArticle)
        .where(
            KnowledgeArticle.is_published == True,
            KnowledgeArticle.is_featured == True,
        )
        .order_by(KnowledgeArticle.view_count.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/articles/{article_id}", response_model=KnowledgeArticleResponse, summary="Get knowledge article")
async def get_knowledge_article(
    article_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get a knowledge article by ID."""
    result = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_published == True,
        )
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    # Increment view count
    article.view_count += 1
    await db.commit()

    return article


@router.get("/articles/slug/{slug}", response_model=KnowledgeArticleResponse, summary="Get knowledge article by slug")
async def get_knowledge_article_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get a knowledge article by slug."""
    result = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.slug == slug,
            KnowledgeArticle.is_published == True,
        )
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.view_count += 1
    await db.commit()

    return article


@router.post("/articles/{article_id}/interact", response_model=UserKnowledgeInteractionResponse, status_code=status.HTTP_201_CREATED, summary="Record article interaction")
async def record_article_interaction(
    article_id: UUID,
    request: UserKnowledgeInteractionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Record user interaction with a knowledge article."""
    # Verify article exists
    result = await db.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    interaction = UserKnowledgeInteraction(
        user_id=current_user.id,
        article_id=article_id,
        **request.model_dump(),
    )
    db.add(interaction)

    # Update article counters
    if request.interaction_type == "rate_helpful" and request.rating and request.rating >= 4:
        article.helpful_count += 1
    elif request.interaction_type == "share":
        article.share_count += 1

    await db.commit()
    await db.refresh(interaction)
    return interaction


@router.get("/articles/{article_id}/interactions", response_model=List[UserKnowledgeInteractionResponse], summary="Get user's article interactions")
async def get_article_interactions(
    article_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get user's interactions with a specific article."""
    result = await db.execute(
        select(UserKnowledgeInteraction)
        .where(
            UserKnowledgeInteraction.user_id == current_user.id,
            UserKnowledgeInteraction.article_id == article_id,
        )
        .order_by(UserKnowledgeInteraction.created_at.desc())
    )
    return result.scalars().all()


# Personalized Knowledge Recommendations
@router.get("/recommendations", response_model=PaginatedResponse[PersonalizedKnowledgeRecommendationResponse], summary="Get personalized knowledge recommendations")
async def get_personalized_recommendations(
    params: PersonalizedKnowledgeRecommendationListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get personalized knowledge recommendations for the user."""
    query = select(PersonalizedKnowledgeRecommendation).where(
        PersonalizedKnowledgeRecommendation.user_id == current_user.id
    )

    if params.is_dismissed is not None:
        query = query.where(PersonalizedKnowledgeRecommendation.is_dismissed == params.is_dismissed)
    if params.is_read is not None:
        query = query.where(PersonalizedKnowledgeRecommendation.is_read == params.is_read)
    if params.trigger_context:
        query = query.where(PersonalizedKnowledgeRecommendation.trigger_context == params.trigger_context)

    query = query.order_by(PersonalizedKnowledgeRecommendation.relevance_score.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.put("/recommendations/{recommendation_id}/read", response_model=PersonalizedKnowledgeRecommendationResponse, summary="Mark recommendation as read")
async def mark_recommendation_read(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Mark a personalized recommendation as read."""
    result = await db.execute(
        select(PersonalizedKnowledgeRecommendation).where(
            PersonalizedKnowledgeRecommendation.id == recommendation_id,
            PersonalizedKnowledgeRecommendation.user_id == current_user.id,
        )
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    recommendation.is_read = True
    recommendation.read_at = datetime.utcnow()
    await db.commit()
    await db.refresh(recommendation)
    return recommendation


@router.put("/recommendations/{recommendation_id}/dismiss", response_model=PersonalizedKnowledgeRecommendationResponse, summary="Dismiss recommendation")
async def dismiss_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Dismiss a personalized recommendation."""
    result = await db.execute(
        select(PersonalizedKnowledgeRecommendation).where(
            PersonalizedKnowledgeRecommendation.id == recommendation_id,
            PersonalizedKnowledgeRecommendation.user_id == current_user.id,
        )
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    recommendation.is_dismissed = True
    await db.commit()
    await db.refresh(recommendation)
    return recommendation


# Weekly Surveys
@router.post("/surveys/weekly", response_model=WeeklySurveyResponse, status_code=status.HTTP_201_CREATED, summary="Submit weekly survey")
async def submit_weekly_survey(
    request: WeeklySurveyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Submit weekly lifestyle survey."""
    # Check if survey for this week already exists
    existing = await db.execute(
        select(WeeklySurvey).where(
            WeeklySurvey.user_id == current_user.id,
            WeeklySurvey.week_start == request.week_start,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Survey for this week already submitted",
        )

    survey = WeeklySurvey(
        user_id=current_user.id,
        submitted_at=datetime.utcnow(),
        **request.model_dump(),
    )

    # Calculate scores from responses
    survey.nutrition_score = calculate_nutrition_score(request.responses)
    survey.sleep_score = calculate_sleep_score(request.responses)
    survey.activity_score = calculate_activity_score(request.responses)
    survey.stress_score = calculate_stress_score(request.responses)
    survey.digital_wellbeing_score = calculate_digital_wellbeing_score(request.responses)
    survey.overall_wellbeing_score = calculate_overall_score(
        survey.nutrition_score,
        survey.sleep_score,
        survey.activity_score,
        survey.stress_score,
        survey.digital_wellbeing_score,
    )

    db.add(survey)
    await db.commit()
    await db.refresh(survey)
    return survey


def calculate_nutrition_score(responses: dict) -> Optional[float]:
    """Calculate nutrition score from survey responses."""
    # Placeholder implementation
    return None


def calculate_sleep_score(responses: dict) -> Optional[float]:
    """Calculate sleep score from survey responses."""
    return None


def calculate_activity_score(responses: dict) -> Optional[float]:
    """Calculate activity score from survey responses."""
    return None


def calculate_stress_score(responses: dict) -> Optional[float]:
    """Calculate stress score from survey responses."""
    return None


def calculate_digital_wellbeing_score(responses: dict) -> Optional[float]:
    """Calculate digital wellbeing score from survey responses."""
    return None


def calculate_overall_score(*scores: Optional[float]) -> Optional[float]:
    """Calculate overall wellbeing score."""
    valid_scores = [s for s in scores if s is not None]
    if not valid_scores:
        return None
    return sum(valid_scores) / len(valid_scores)


@router.get("/surveys/weekly", response_model=PaginatedResponse[WeeklySurveyResponse], summary="List weekly surveys")
async def list_weekly_surveys(
    params: WeeklySurveyListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List weekly surveys with pagination."""
    query = select(WeeklySurvey).where(WeeklySurvey.user_id == current_user.id)

    if params.week_start_from:
        query = query.where(WeeklySurvey.week_start >= params.week_start_from)
    if params.week_start_to:
        query = query.where(WeeklySurvey.week_start <= params.week_start_to)
    if params.survey_version:
        query = query.where(WeeklySurvey.survey_version == params.survey_version)
    if params.is_complete is not None:
        query = query.where(WeeklySurvey.is_complete == params.is_complete)

    query = query.order_by(WeeklySurvey.week_start.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/surveys/weekly/latest", response_model=Optional[WeeklySurveyResponse], summary="Get latest weekly survey")
async def get_latest_weekly_survey(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the most recent weekly survey."""
    result = await db.execute(
        select(WeeklySurvey)
        .where(WeeklySurvey.user_id == current_user.id)
        .order_by(WeeklySurvey.week_start.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/surveys/weekly/{week_start}", response_model=WeeklySurveyResponse, summary="Get weekly survey by week")
async def get_weekly_survey(
    week_start: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get weekly survey for a specific week."""
    result = await db.execute(
        select(WeeklySurvey).where(
            WeeklySurvey.user_id == current_user.id,
            WeeklySurvey.week_start == week_start,
        )
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly survey not found")

    return survey


# Survey Templates (Admin)
@router.get("/survey-templates", response_model=PaginatedResponse[SurveyTemplateResponse], summary="List survey templates")
async def list_survey_templates(
    params: SurveyTemplateListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List survey templates (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    query = select(SurveyTemplate)

    if params.is_active is not None:
        query = query.where(SurveyTemplate.is_active == params.is_active)
    if params.validated is not None:
        query = query.where(SurveyTemplate.validated == params.validated)

    query = query.order_by(SurveyTemplate.version.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)


@router.get("/survey-templates/active", response_model=SurveyTemplateResponse, summary="Get active survey template")
async def get_active_survey_template(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the currently active survey template."""
    result = await db.execute(
        select(SurveyTemplate)
        .where(SurveyTemplate.is_active == True)
        .order_by(SurveyTemplate.version.desc())
        .limit(1)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active survey template")

    return template


# Evidence Sources (Admin)
@router.get("/evidence-sources", response_model=PaginatedResponse[EvidenceSourceResponse], summary="List evidence sources")
async def list_evidence_sources(
    params: EvidenceSourceListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List evidence sources."""
    query = select(EvidenceSource)

    if params.source_type:
        query = query.where(EvidenceSource.source_type == params.source_type)
    if params.quality_rating:
        query = query.where(EvidenceSource.quality_rating == params.quality_rating)
    if params.is_verified is not None:
        query = query.where(EvidenceSource.is_verified == params.is_verified)
    if params.search:
        search_term = f"%{params.search}%"
        query = query.where(
            or_(
                EvidenceSource.title.ilike(search_term),
                EvidenceSource.authors.any(search_term),
            )
        )

    query = query.order_by(EvidenceSource.publication_date.desc().nullslast())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return paginate(items, total, params)

# ===== Real weekly survey scoring (overrides the earlier placeholders) =====
def _num(responses: dict, key: str):
    try:
        return float(responses.get(key))
    except (TypeError, ValueError):
        return None


def calculate_nutrition_score(responses: dict) -> Optional[float]:
    parts = []
    for key in ("fruit_days", "veg_days", "protein_days"):
        v = _num(responses, key)
        if v is not None:
            parts.append(min(v, 7) / 7)
    for key in ("oily_days", "sugary_days", "skipped_days"):
        v = _num(responses, key)
        if v is not None:
            parts.append(1 - min(v, 7) / 7)
    w = {"low": 0.0, "ok": 0.7, "good": 1.0}.get(str(responses.get("water")))
    if w is not None:
        parts.append(w)
    return round(sum(parts) / len(parts) * 100, 1) if parts else None


def calculate_activity_score(responses: dict) -> Optional[float]:
    v = _num(responses, "exercise_days")
    return None if v is None else round(min(v, 5) / 5 * 100, 1)


def calculate_sleep_score(responses: dict) -> Optional[float]:
    v = _num(responses, "sleep_quality")
    return None if v is None else round((min(max(v, 1), 5) - 1) / 4 * 100, 1)


def calculate_stress_score(responses: dict) -> Optional[float]:
    v = _num(responses, "stress")
    return None if v is None else round((5 - min(max(v, 1), 5)) / 4 * 100, 1)
