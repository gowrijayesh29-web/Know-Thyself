"""
Knowledge base schemas - Articles, Evidence Sources, Surveys, Educational Content.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, HttpUrl

from app.schemas.base import IDTimestampSchema, PaginationParams
from app.models.knowledge import KnowledgeCategory, EvidenceQuality, EvidenceSourceType


# Enums for API
class KnowledgeCategoryStr(str, Enum):
    NUTRITION = "nutrition"
    SLEEP_RECOVERY = "sleep_recovery"
    PHYSICAL_ACTIVITY = "physical_activity"
    MENTAL_WELLBEING = "mental_wellbeing"
    DIGITAL_WELLBEING = "digital_wellbeing"
    GENERAL_LIFESTYLE = "general_lifestyle"
    HABIT_FORMATION = "habit_formation"
    GOAL_SETTING = "goal_setting"
    BEHAVIORAL_PSYCHOLOGY = "behavioral_psychology"


class EvidenceQualityStr(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    EMERGING = "emerging"
    CONSENSUS = "consensus"


class EvidenceSourceTypeStr(str, Enum):
    PEER_REVIEWED_JOURNAL = "peer_reviewed_journal"
    CLINICAL_GUIDELINE = "clinical_guideline"
    GOVERNMENT_HEALTH_AGENCY = "government_health_agency"
    MEDICAL_INSTITUTION = "medical_institution"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    RCT = "randomized_controlled_trial"
    COHORT_STUDY = "cohort_study"
    CASE_CONTROL_STUDY = "case_control_study"
    EXPERT_CONSENSUS = "expert_consensus"
    REPUTABLE_ORGANIZATION = "reputable_organization"


# Knowledge Article schemas
class KnowledgeArticleBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    subtitle: Optional[str] = None
    category: KnowledgeCategoryStr
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    summary: str
    content: str
    key_takeaways: List[str] = Field(default_factory=list)
    practical_tips: List[str] = Field(default_factory=list)
    evidence_quality: EvidenceQualityStr
    evidence_sources: List[Dict[str, Any]] = Field(default_factory=list)
    primary_source_type: EvidenceSourceTypeStr
    doi: Optional[str] = Field(None, max_length=100)
    pmid: Optional[str] = Field(None, max_length=20)
    applicable_populations: List[str] = Field(default_factory=list)
    applicable_conditions: List[str] = Field(default_factory=list)
    limitations: Optional[str] = None
    contraindications: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    reviewer: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[date] = None
    last_verification_date: date
    next_verification_due: date
    version: int = Field(default=1, ge=1)
    is_published: bool = True
    is_featured: bool = False
    reading_time_minutes: int = Field(default=5, ge=1)
    difficulty_level: int = Field(default=2, ge=1, le=3)


class KnowledgeArticleCreate(KnowledgeArticleBase):
    pass


class KnowledgeArticleUpdate(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    subtitle: Optional[str] = None
    category: Optional[KnowledgeCategoryStr] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    key_takeaways: Optional[List[str]] = None
    practical_tips: Optional[List[str]] = None
    evidence_quality: Optional[EvidenceQualityStr] = None
    evidence_sources: Optional[List[Dict[str, Any]]] = None
    primary_source_type: Optional[EvidenceSourceTypeStr] = None
    doi: Optional[str] = Field(None, max_length=100)
    pmid: Optional[str] = Field(None, max_length=20)
    applicable_populations: Optional[List[str]] = None
    applicable_conditions: Optional[List[str]] = None
    limitations: Optional[str] = None
    contraindications: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    reviewer: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[date] = None
    last_verification_date: Optional[date] = None
    next_verification_due: Optional[date] = None
    version: Optional[int] = Field(None, ge=1)
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    reading_time_minutes: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[int] = Field(None, ge=1, le=3)


class KnowledgeArticleResponse(IDTimestampSchema, KnowledgeArticleBase):
    view_count: int
    helpful_count: int
    share_count: int


class KnowledgeArticleListParams(PaginationParams):
    category: Optional[KnowledgeCategoryStr] = None
    subcategory: Optional[str] = None
    tag: Optional[str] = None
    evidence_quality: Optional[EvidenceQualityStr] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    search: Optional[str] = None
    difficulty_level: Optional[int] = None


# Evidence Source schemas
class EvidenceSourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    source_type: EvidenceSourceTypeStr
    authors: List[str] = Field(default_factory=list)
    publication: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[date] = None
    url: Optional[HttpUrl] = None
    doi: Optional[str] = Field(None, max_length=100)
    pmid: Optional[str] = Field(None, max_length=20)
    abstract: Optional[str] = None
    key_findings: List[str] = Field(default_factory=list)
    methodology: Optional[str] = None
    sample_size: Optional[int] = Field(None, ge=1)
    population: Optional[str] = Field(None, max_length=255)
    quality_rating: EvidenceQualityStr
    funding_sources: List[str] = Field(default_factory=list)
    conflicts_of_interest: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class EvidenceSourceCreate(EvidenceSourceBase):
    pass


class EvidenceSourceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    source_type: Optional[EvidenceSourceTypeStr] = None
    authors: Optional[List[str]] = None
    publication: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[date] = None
    url: Optional[HttpUrl] = None
    doi: Optional[str] = Field(None, max_length=100)
    pmid: Optional[str] = Field(None, max_length=20)
    abstract: Optional[str] = None
    key_findings: Optional[List[str]] = None
    methodology: Optional[str] = None
    sample_size: Optional[int] = Field(None, ge=1)
    population: Optional[str] = Field(None, max_length=255)
    quality_rating: Optional[EvidenceQualityStr] = None
    funding_sources: Optional[List[str]] = None
    conflicts_of_interest: Optional[str] = None
    tags: Optional[List[str]] = None
    is_verified: Optional[bool] = None


class EvidenceSourceResponse(IDTimestampSchema, EvidenceSourceBase):
    is_verified: bool
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None


class EvidenceSourceListParams(PaginationParams):
    source_type: Optional[EvidenceSourceTypeStr] = None
    quality_rating: Optional[EvidenceQualityStr] = None
    is_verified: Optional[bool] = None
    search: Optional[str] = None


# User Knowledge Interaction schemas
class UserKnowledgeInteractionBase(BaseModel):
    article_id: UUID
    interaction_type: str = Field(..., pattern="^(view|bookmark|share|rate_helpful|complete)$")
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    scroll_percentage: Optional[int] = Field(None, ge=0, le=100)
    completed: bool = False
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None


class UserKnowledgeInteractionCreate(UserKnowledgeInteractionBase):
    pass


class UserKnowledgeInteractionResponse(IDTimestampSchema, UserKnowledgeInteractionBase):
    user_id: UUID


# Personalized Knowledge Recommendation schemas
class PersonalizedKnowledgeRecommendationBase(BaseModel):
    article_id: UUID
    reason: str
    relevance_score: float = Field(default=0.0, ge=0, le=1)
    trigger_context: Optional[str] = Field(None, max_length=100)
    is_dismissed: bool = False
    is_read: bool = False


class PersonalizedKnowledgeRecommendationCreate(PersonalizedKnowledgeRecommendationBase):
    pass


class PersonalizedKnowledgeRecommendationUpdate(BaseModel):
    is_dismissed: Optional[bool] = None
    is_read: Optional[bool] = None


class PersonalizedKnowledgeRecommendationResponse(IDTimestampSchema, PersonalizedKnowledgeRecommendationBase):
    user_id: UUID
    read_at: Optional[datetime] = None
    model_version: str
    generated_at: datetime


class PersonalizedKnowledgeRecommendationListParams(PaginationParams):
    is_dismissed: Optional[bool] = None
    is_read: Optional[bool] = None
    trigger_context: Optional[str] = None


# Weekly Survey schemas
class WeeklySurveyBase(BaseModel):
    week_start: date
    week_end: date
    survey_version: str = Field(..., max_length=20)
    responses: Dict[str, Any] = Field(default_factory=dict)
    completion_time_seconds: Optional[int] = Field(None, ge=0)
    is_complete: bool = True
    skipped_sections: List[str] = Field(default_factory=list)


class WeeklySurveyCreate(WeeklySurveyBase):
    pass


class WeeklySurveyUpdate(BaseModel):
    responses: Optional[Dict[str, Any]] = None
    completion_time_seconds: Optional[int] = Field(None, ge=0)
    is_complete: Optional[bool] = None
    skipped_sections: Optional[List[str]] = None


class WeeklySurveyResponse(IDTimestampSchema, WeeklySurveyBase):
    user_id: UUID
    submitted_at: datetime
    nutrition_score: Optional[float] = None
    sleep_score: Optional[float] = None
    activity_score: Optional[float] = None
    stress_score: Optional[float] = None
    digital_wellbeing_score: Optional[float] = None
    overall_wellbeing_score: Optional[float] = None


class WeeklySurveyListParams(PaginationParams):
    week_start_from: Optional[date] = None
    week_start_to: Optional[date] = None
    survey_version: Optional[str] = None
    is_complete: Optional[bool] = None


# Survey Template schemas
class SurveyTemplateBase(BaseModel):
    version: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    conditional_logic: List[Dict[str, Any]] = Field(default_factory=list)
    scoring_rules: Dict[str, Any] = Field(default_factory=dict)
    estimated_time_minutes: int = Field(default=2, ge=1)
    created_by: Optional[str] = Field(None, max_length=100)
    validated: bool = False


class SurveyTemplateCreate(SurveyTemplateBase):
    pass


class SurveyTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sections: Optional[List[Dict[str, Any]]] = None
    questions: Optional[List[Dict[str, Any]]] = None
    conditional_logic: Optional[List[Dict[str, Any]]] = None
    scoring_rules: Optional[Dict[str, Any]] = None
    estimated_time_minutes: Optional[int] = Field(None, ge=1)
    validated: Optional[bool] = None


class SurveyTemplateResponse(IDTimestampSchema, SurveyTemplateBase):
    pass


class SurveyTemplateListParams(PaginationParams):
    is_active: Optional[bool] = None
    validated: Optional[bool] = None