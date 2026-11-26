"""
Knowledge base models - Articles, Evidence Sources, Educational Content.
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


class KnowledgeCategory(str, enum.Enum):
    NUTRITION = "nutrition"
    SLEEP_RECOVERY = "sleep_recovery"
    PHYSICAL_ACTIVITY = "physical_activity"
    MENTAL_WELLBEING = "mental_wellbeing"
    DIGITAL_WELLBEING = "digital_wellbeing"
    GENERAL_LIFESTYLE = "general_lifestyle"
    HABIT_FORMATION = "habit_formation"
    GOAL_SETTING = "goal_setting"
    BEHAVIORAL_PSYCHOLOGY = "behavioral_psychology"


class EvidenceQuality(str, enum.Enum):
    HIGH = "high"           # Systematic reviews, meta-analyses, RCTs
    MODERATE = "moderate"   # Cohort studies, case-control studies
    LOW = "low"             # Cross-sectional, case reports, expert opinion
    EMERGING = "emerging"   # Preliminary research, preprints
    CONSENSUS = "consensus" # Clinical guidelines, position statements


class EvidenceSourceType(str, enum.Enum):
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


class KnowledgeArticle(BaseModel):
    """Knowledge base articles with evidence backing."""
    __tablename__ = "knowledge_articles"

    # Identification
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[KnowledgeCategory] = mapped_column(Enum(KnowledgeCategory), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Content
    summary: Mapped[str] = mapped_column(Text, nullable=False)  # 2-3 sentence summary
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Full article content (Markdown)
    key_takeaways: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    practical_tips: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Evidence
    evidence_quality: Mapped[EvidenceQuality] = mapped_column(Enum(EvidenceQuality), nullable=False)
    evidence_sources: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)  # [{"title": "...", "url": "...", "type": "...", "date": "..."}]
    primary_source_type: Mapped[EvidenceSourceType] = mapped_column(Enum(EvidenceSourceType), nullable=False)
    doi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pmid: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Applicability
    applicable_populations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # general, athletes, elderly, pregnant, children, etc.
    applicable_conditions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    limitations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contraindications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_verification_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_verification_due: Mapped[date] = mapped_column(Date, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reading_time_minutes: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=2, nullable=False)  # 1=beginner, 3=advanced

    # Engagement
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    share_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    related_articles: Mapped[List["KnowledgeArticle"]] = relationship(
        "KnowledgeArticle",
        secondary="knowledge_article_relations",
        primaryjoin="KnowledgeArticle.id==KnowledgeArticleRelation.article_id",
        secondaryjoin="KnowledgeArticle.id==KnowledgeArticleRelation.related_article_id",
        back_populates="related_articles_reverse",
    )
    related_articles_reverse: Mapped[List["KnowledgeArticle"]] = relationship(
        "KnowledgeArticle",
        secondary="knowledge_article_relations",
        primaryjoin="KnowledgeArticle.id==KnowledgeArticleRelation.related_article_id",
        secondaryjoin="KnowledgeArticle.id==KnowledgeArticleRelation.article_id",
        back_populates="related_articles",
    )

    __table_args__ = (
        Index("ix_knowledge_articles_category", "category"),
        Index("ix_knowledge_articles_published", "is_published"),
        Index("ix_knowledge_articles_verification", "next_verification_due"),
        CheckConstraint("reading_time_minutes > 0", name="ck_knowledge_reading_time_positive"),
        CheckConstraint("difficulty_level BETWEEN 1 AND 3", name="ck_knowledge_difficulty_range"),
    )


class KnowledgeArticleRelation(BaseModel):
    """Many-to-many relationship between knowledge articles."""
    __tablename__ = "knowledge_article_relations"

    article_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    related_article_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    relation_type: Mapped[str] = mapped_column(String(50), default="related", nullable=False)  # related, prerequisite, follow_up, alternative
    strength: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 0-1

    __table_args__ = (
        UniqueConstraint("article_id", "related_article_id", name="uq_knowledge_article_relation"),
    )


class EvidenceSource(BaseModel):
    """Structured evidence sources for knowledge base."""
    __tablename__ = "evidence_sources"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[EvidenceSourceType] = mapped_column(Enum(EvidenceSourceType), nullable=False)
    authors: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    publication: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pmid: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_findings: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    population: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    quality_rating: Mapped[EvidenceQuality] = mapped_column(Enum(EvidenceQuality), nullable=False)
    funding_sources: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    conflicts_of_interest: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_evidence_sources_type", "source_type"),
        Index("ix_evidence_sources_quality", "quality_rating"),
        Index("ix_evidence_sources_verified", "is_verified"),
    )


class UserKnowledgeInteraction(BaseModel):
    """Track user interactions with knowledge content."""
    __tablename__ = "user_knowledge_interactions"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    article_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_articles.id", ondelete="CASCADE"),
        nullable=False,
    )

    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # view, bookmark, share, rate_helpful, complete
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scroll_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-100
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_user_knowledge_interactions_user_id", "user_id"),
        Index("ix_user_knowledge_interactions_article_id", "article_id"),
        Index("ix_user_knowledge_interactions_type", "interaction_type"),
    )


class PersonalizedKnowledgeRecommendation(BaseModel):
    """AI-generated personalized knowledge recommendations."""
    __tablename__ = "personalized_knowledge_recommendations"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    article_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_articles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Reasoning
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0-1
    trigger_context: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # goal, pattern, observation, survey, manual

    # Status
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # AI metadata
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_personalized_knowledge_user_id", "user_id"),
        Index("ix_personalized_knowledge_article_id", "article_id"),
        Index("ix_personalized_knowledge_relevance", "relevance_score"),
        UniqueConstraint("user_id", "article_id", name="uq_personalized_knowledge"),
    )


class WeeklySurvey(BaseModel):
    """Weekly lifestyle survey responses."""
    __tablename__ = "weekly_surveys"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Survey version
    survey_version: Mapped[str] = mapped_column(String(20), nullable=False)

    # Responses (structured JSON)
    responses: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Computed scores
    nutrition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    sleep_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    activity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stress_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    digital_wellbeing_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_wellbeing_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    completion_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    skipped_sections: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="weekly_surveys")

    __table_args__ = (
        Index("ix_weekly_surveys_user_id", "user_id"),
        Index("ix_weekly_surveys_week_start", "week_start"),
        UniqueConstraint("user_id", "week_start", name="uq_weekly_survey"),
    )


class SurveyTemplate(BaseModel):
    """Survey templates with conditional logic."""
    __tablename__ = "survey_templates"

    version: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Structure
    sections: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    questions: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    conditional_logic: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    scoring_rules: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Metadata
    estimated_time_minutes: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_survey_templates_active", "is_active"),
    )