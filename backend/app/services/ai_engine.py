"""
AI Intelligence Engine - Core AI services for pattern detection, recommendations, and reports.
"""
from app.models.knowledge import WeeklySurvey
import json
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from openai import AsyncOpenAI

from app.core.config import settings
from app.models.user import User
from app.models.goals import Goal, GoalProgress
from app.models.digital import DigitalActivity, DailyDigitalSummary
from app.models.physical import (
    SleepRecord, NutritionRecord, PhysicalActivity,
    DailyNutritionSummary, DailyPhysicalActivitySummary, HydrationRecord, DailyHydrationSummary
)
from app.models.ai import AIObservation, DetectedPattern, Recommendation, WeeklyReport
from app.models.knowledge import KnowledgeArticle

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """Assembled user context for AI processing."""
    user: User
    profile: Dict[str, Any]
    goals: List[Dict[str, Any]]
    recent_digital: List[Dict[str, Any]]
    recent_sleep: List[Dict[str, Any]]
    recent_nutrition: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    recent_hydration: List[Dict[str, Any]]
    weekly_surveys: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    previous_recommendations: List[Dict[str, Any]]


class AIEngine:
    """Core AI engine for Know Thyself."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.NVIDIA_API_KEY,
            base_url=settings.NVIDIA_BASE_URL,
        )
        self.model = settings.NVIDIA_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS

    async def assemble_user_context(
        self,
        user_id: UUID,
        db: AsyncSession,
        days_back: int = 30,
    ) -> UserContext:
        """Assemble comprehensive user context for AI processing."""
        # Get user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        # Get profile
        from app.models.user import UserProfile
        profile_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profile = profile_result.scalar_one_or_none()

        # Get active goals
        goals_result = await db.execute(
            select(Goal).where(Goal.user_id == user_id, Goal.status == "active")
        )
        goals = goals_result.scalars().all()

        # Get recent digital activity summaries
        start_date = date.today() - timedelta(days=days_back)
        digital_result = await db.execute(
            select(DailyDigitalSummary)
            .where(DailyDigitalSummary.user_id == user_id, DailyDigitalSummary.date >= start_date)
            .order_by(DailyDigitalSummary.date.desc())
        )
        digital_summaries = digital_result.scalars().all()

        # Get recent sleep records
        sleep_result = await db.execute(
            select(SleepRecord)
            .where(SleepRecord.user_id == user_id, SleepRecord.date >= start_date)
            .order_by(SleepRecord.date.desc())
        )
        sleep_records = sleep_result.scalars().all()

        # Get recent nutrition summaries
        nutrition_result = await db.execute(
            select(DailyNutritionSummary)
            .where(DailyNutritionSummary.user_id == user_id, DailyNutritionSummary.date >= start_date)
            .order_by(DailyNutritionSummary.date.desc())
        )
        nutrition_summaries = nutrition_result.scalars().all()

        # Get recent physical activity summaries
        activity_result = await db.execute(
            select(DailyPhysicalActivitySummary)
            .where(DailyPhysicalActivitySummary.user_id == user_id, DailyPhysicalActivitySummary.date >= start_date)
            .order_by(DailyPhysicalActivitySummary.date.desc())
        )
        activity_summaries = activity_result.scalars().all()

        # Get recent hydration summaries
        hydration_result = await db.execute(
            select(DailyHydrationSummary)
            .where(DailyHydrationSummary.user_id == user_id, DailyHydrationSummary.date >= start_date)
            .order_by(DailyHydrationSummary.date.desc())
        )
        hydration_summaries = hydration_result.scalars().all()

        # Get weekly surveys
        survey_result = await db.execute(
            select(WeeklySurvey)
            .where(WeeklySurvey.user_id == user_id)
            .order_by(WeeklySurvey.week_start.desc())
            .limit(8)
        )
        surveys = survey_result.scalars().all()

        # Get detected patterns
        pattern_result = await db.execute(
            select(DetectedPattern)
            .where(DetectedPattern.user_id == user_id, DetectedPattern.is_active == True)
        )
        patterns = pattern_result.scalars().all()

        # Get previous recommendations
        rec_result = await db.execute(
            select(Recommendation)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
            .limit(20)
        )
        recommendations = rec_result.scalars().all()

        return UserContext(
            user=user,
            profile=self._serialize_profile(profile),
            goals=[self._serialize_goal(g) for g in goals],
            recent_digital=[self._serialize_digital_summary(d) for d in digital_summaries],
            recent_sleep=[self._serialize_sleep(s) for s in sleep_records],
            recent_nutrition=[self._serialize_nutrition_summary(n) for n in nutrition_summaries],
            recent_activity=[self._serialize_activity_summary(a) for a in activity_summaries],
            recent_hydration=[self._serialize_hydration_summary(h) for h in hydration_summaries],
            weekly_surveys=[self._serialize_survey(s) for s in surveys],
            patterns=[self._serialize_pattern(p) for p in patterns],
            previous_recommendations=[self._serialize_recommendation(r) for r in recommendations],
        )

    def _serialize_profile(self, profile) -> Dict[str, Any]:
        if not profile:
            return {}
        return {
            "age": self._calculate_age(profile.date_of_birth) if profile.date_of_birth else None,
            "gender": profile.gender.value if profile.gender else None,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "activity_level": profile.activity_level.value if profile.activity_level else None,
            "dietary_preference": profile.dietary_preference.value if profile.dietary_preference else None,
            "dietary_restrictions": profile.dietary_restrictions,
            "allergies": profile.allergies,
            "medical_conditions": profile.medical_conditions,
            "occupation": profile.occupation,
            "work_schedule": profile.work_schedule,
            "typical_wake_time": profile.typical_wake_time,
            "typical_bed_time": profile.typical_bed_time,
        }

    def _calculate_age(self, dob: date) -> int:
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def _serialize_goal(self, goal: Goal) -> Dict[str, Any]:
        return {
            "id": str(goal.id),
            "title": goal.title,
            "category": goal.category.value,
            "target_value": goal.target_value,
            "target_unit": goal.target_unit.value,
            "current_value": goal.current_value,
            "progress_percentage": goal.progress_percentage,
            "status": goal.status.value,
            "streak_days": goal.streak_days,
            "priority": goal.priority,
        }

    def _serialize_digital_summary(self, summary: DailyDigitalSummary) -> Dict[str, Any]:
        return {
            "date": summary.date.isoformat(),
            "total_seconds": summary.total_seconds,
            "active_seconds": summary.active_seconds,
            "category_breakdown": summary.category_breakdown,
            "productive_seconds": summary.productive_seconds,
            "unproductive_seconds": summary.unproductive_seconds,
            "session_count": summary.session_count,
        }

    def _serialize_sleep(self, sleep: SleepRecord) -> Dict[str, Any]:
        return {
            "date": sleep.date.isoformat(),
            "total_sleep_minutes": sleep.total_sleep_minutes,
            "quality_rating": sleep.quality_rating.value if sleep.quality_rating else None,
            "bedtime": sleep.bedtime.isoformat() if sleep.bedtime else None,
            "wake_time": sleep.wake_time.isoformat() if sleep.wake_time else None,
            "screen_time_before_bed": sleep.screen_time_before_bed_minutes,
        }

    def _serialize_nutrition_summary(self, summary: DailyNutritionSummary) -> Dict[str, Any]:
        return {
            "date": summary.date.isoformat(),
            "total_calories": summary.total_calories,
            "total_protein_g": summary.total_protein_g,
            "total_carbs_g": summary.total_carbs_g,
            "total_fat_g": summary.total_fat_g,
            "total_fiber_g": summary.total_fiber_g,
            "meals_count": summary.meals_count,
        }

    def _serialize_activity_summary(self, summary: DailyPhysicalActivitySummary) -> Dict[str, Any]:
        return {
            "date": summary.date.isoformat(),
            "total_duration_minutes": summary.total_duration_minutes,
            "total_calories_burned": summary.total_calories_burned,
            "total_steps": summary.total_steps,
            "activity_breakdown": summary.activity_breakdown,
            "mvpa_minutes": summary.mvpa_minutes,
        }

    def _serialize_hydration_summary(self, summary: DailyHydrationSummary) -> Dict[str, Any]:
        return {
            "date": summary.date.isoformat(),
            "total_ml": summary.total_ml,
            "goal_ml": summary.goal_ml,
            "goal_met": summary.goal_met,
        }

    def _serialize_survey(self, survey: WeeklySurvey) -> Dict[str, Any]:
        return {
            "week_start": survey.week_start.isoformat(),
            "nutrition_score": survey.nutrition_score,
            "sleep_score": survey.sleep_score,
            "activity_score": survey.activity_score,
            "stress_score": survey.stress_score,
            "digital_wellbeing_score": survey.digital_wellbeing_score,
            "overall_wellbeing_score": survey.overall_wellbeing_score,
        }

    def _serialize_pattern(self, pattern: DetectedPattern) -> Dict[str, Any]:
        return {
            "category": pattern.pattern_category.value,
            "name": pattern.pattern_name,
            "description": pattern.description,
            "strength": pattern.strength.value,
            "direction": pattern.direction,
            "consistency_score": pattern.consistency_score,
        }

    def _serialize_recommendation(self, rec: Recommendation) -> Dict[str, Any]:
        return {
            "id": str(rec.id),
            "type": rec.recommendation_type.value,
            "title": rec.title,
            "status": rec.status.value,
            "user_response": rec.user_response,
            "completed_at": rec.completed_at.isoformat() if rec.completed_at else None,
        }

    async def detect_patterns(
        self,
        context: UserContext,
    ) -> List[Dict[str, Any]]:
        """Detect patterns in user data using AI."""
        prompt = self._build_pattern_detection_prompt(context)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_pattern_detection_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("patterns", [])

        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
            return []

    def _get_pattern_detection_system_prompt(self) -> str:
        return """You are an expert lifestyle pattern detection AI. Analyze user data across digital activity, sleep, nutrition, physical activity, and hydration to identify meaningful patterns.

Return a JSON object with a "patterns" array. Each pattern should have:
- category: one of [sleep_digital, activity_nutrition, stress_sleep, work_life_balance, consistency, goal_adherence, seasonal, weekly_rhythm, progress_trajectory, behavioral_cluster]
- name: descriptive name
- description: detailed explanation
- variables_involved: list of variables
- strength: one of [weak, moderate, strong, very_strong]
- direction: one of [positive, negative, complex]
- consistency_score: 0-1
- suggested_interventions: list of actionable suggestions
- related_goals: list of goal IDs this affects

Focus on patterns that are actionable and relevant to the user's goals. Distinguish correlation from causation."""

    def _build_pattern_detection_prompt(self, context: UserContext) -> str:
        return f"""Analyze this user's lifestyle data for patterns:

USER PROFILE:
{json.dumps(context.profile, indent=2)}

ACTIVE GOALS:
{json.dumps(context.goals, indent=2)}

RECENT DIGITAL ACTIVITY (last 30 days):
{json.dumps(context.recent_digital[:14], indent=2)}

RECENT SLEEP (last 30 days):
{json.dumps(context.recent_sleep[:14], indent=2)}

RECENT NUTRITION (last 30 days):
{json.dumps(context.recent_nutrition[:14], indent=2)}

RECENT PHYSICAL ACTIVITY (last 30 days):
{json.dumps(context.recent_activity[:14], indent=2)}

RECENT HYDRATION (last 30 days):
{json.dumps(context.recent_hydration[:14], indent=2)}

WEEKLY SURVEYS:
{json.dumps(context.weekly_surveys, indent=2)}

EXISTING PATTERNS:
{json.dumps(context.patterns, indent=2)}

PREVIOUS RECOMMENDATIONS:
{json.dumps(context.previous_recommendations[:10], indent=2)}

Identify NEW patterns not already in existing patterns. Focus on cross-domain patterns (e.g., digital activity affecting sleep, nutrition affecting energy for exercise)."""

    async def generate_recommendations(
        self,
        context: UserContext,
        observations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on observations and context."""
        prompt = self._build_recommendation_prompt(context, observations)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_recommendation_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=3000,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("recommendations", [])

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []

    def _get_recommendation_system_prompt(self) -> str:
        return """You are a personalized lifestyle coach AI. Generate specific, actionable, evidence-based recommendations.

Return a JSON object with a "recommendations" array. Each recommendation must have:
- type: one of [behavioral_change, routine_adjustment, goal_modification, environment_change, knowledge_acquisition, professional_referral, habit_formation, recovery_focus]
- priority: one of [low, medium, high, urgent]
- title: clear, specific title
- description: detailed explanation
- rationale: why this matters for THIS user
- evidence_summary: brief evidence backing
- evidence_sources: array of {{title, url, source_type}}
- specific_action: ONE concrete, small next step (not "exercise more" but "take a 15-min walk after lunch")
- action_category: domain (digital, sleep, nutrition, activity, hydration, mental)
- difficulty_level: 1-10
- estimated_time_minutes: integer
- frequency: e.g., "daily", "3x_week", "once"
- duration_weeks: integer
- success_criteria: how to measure success
- measurable_target: {{metric, target_value, unit}}
- suggested_start_date: YYYY-MM-DD
- suggested_time_of_day: HH:MM
- related_goal_ids: array of goal UUIDs

AVOID generic advice. Make recommendations specific to the user's actual data, goals, and context."""

    def _build_recommendation_prompt(self, context: UserContext, observations: List[Dict[str, Any]]) -> str:
        return f"""Generate personalized recommendations for this user:

USER PROFILE:
{json.dumps(context.profile, indent=2)}

ACTIVE GOALS:
{json.dumps(context.goals, indent=2)}

RECENT OBSERVATIONS:
{json.dumps(observations, indent=2)}

RECENT DATA SUMMARY:
- Digital: {len(context.recent_digital)} days, avg active: {sum(d['active_seconds'] for d in context.recent_digital)/max(len(context.recent_digital),1)/60:.0f} min/day
- Sleep: {len(context.recent_sleep)} nights, avg: {sum(s['total_sleep_minutes'] for s in context.recent_sleep)/max(len(context.recent_sleep),1):.0f} min
- Nutrition: {len(context.recent_nutrition)} days tracked
- Activity: {len(context.recent_activity)} days, avg MVPA: {sum(a['mvpa_minutes'] for a in context.recent_activity)/max(len(context.recent_activity),1):.0f} min
- Hydration: {len(context.recent_hydration)} days

PREVIOUS RECOMMENDATIONS (for learning):
{json.dumps(context.previous_recommendations[:5], indent=2)}

Generate 3-5 high-impact recommendations. Prioritize based on user's goals and biggest gaps."""

    async def generate_weekly_report(
        self,
        context: UserContext,
        week_start: date,
        week_end: date,
    ) -> Dict[str, Any]:
        """Generate a comprehensive weekly intelligence report."""
        prompt = self._build_weekly_report_prompt(context, week_start, week_end)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_weekly_report_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
            return {}

    def _get_weekly_report_system_prompt(self) -> str:
        return """You are an expert lifestyle analyst generating a weekly intelligence report.

Return a JSON object with these sections:
- week_at_a_glance: {{overall_progress, major_improvements, major_concerns, goal_completion, significant_changes}}
- digital_life: {{total_active_hours, category_breakdown, productive_vs_recreational, distraction_patterns, focus_performance, target_exceedances, week_over_week_comparison}}
- physical_wellbeing: {{activity_summary, sleep_summary, nutrition_summary, hydration_summary, routine_consistency, changes_from_previous_weeks}}
- personal_patterns: array of {{pattern, evidence, relevance_to_goals, significance}}
- missed_goals: array of {{goal, shortfall, deviation_timing, recurring_pattern, explanatory_factors}}
- recommendations: array of {{observation, relevance, proposed_change, why_it_helps, practical_action, measurable_target, evaluation_method}}
- long_term_consequences: array of {{pattern, potential_consequence, evidence_strength, sources}}
- next_week_action_plan: {{priorities[3-5], daily_actions, weekly_targets, reminders, measurement_criteria}}

Be specific, evidence-based, and actionable. Use the user's actual data. Distinguish established risks from uncertain possibilities."""

    def _build_weekly_report_prompt(self, context: UserContext, week_start: date, week_end: date) -> str:
        # Filter data for the specific week
        week_digital = [d for d in context.recent_digital if week_start <= date.fromisoformat(d["date"]) <= week_end]
        week_sleep = [s for s in context.recent_sleep if week_start <= date.fromisoformat(s["date"]) <= week_end]
        week_nutrition = [n for n in context.recent_nutrition if week_start <= date.fromisoformat(n["date"]) <= week_end]
        week_activity = [a for a in context.recent_activity if week_start <= date.fromisoformat(a["date"]) <= week_end]
        week_hydration = [h for h in context.recent_hydration if week_start <= date.fromisoformat(h["date"]) <= week_end]

        return f"""Generate weekly report for {week_start} to {week_end}:

USER PROFILE:
{json.dumps(context.profile, indent=2)}

ACTIVE GOALS:
{json.dumps(context.goals, indent=2)}

THIS WEEK'S DATA:
- Digital: {json.dumps(week_digital, indent=2)}
- Sleep: {json.dumps(week_sleep, indent=2)}
- Nutrition: {json.dumps(week_nutrition, indent=2)}
- Activity: {json.dumps(week_activity, indent=2)}
- Hydration: {json.dumps(week_hydration, indent=2)}

DETECTED PATTERNS:
{json.dumps(context.patterns, indent=2)}

PREVIOUS RECOMMENDATIONS & OUTCOMES:
{json.dumps(context.previous_recommendations[:10], indent=2)}

Generate comprehensive report following the specified structure."""


# Global AI engine instance
ai_engine = AIEngine()