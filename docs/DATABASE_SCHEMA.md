# Know Thyself - Database Schema Documentation

## Overview

This document describes the complete database schema for Know Thyself, including all tables, relationships, indexes, and constraints. The schema is designed for PostgreSQL 15+ with pgvector extension.

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    users    │◄─────►│  user_profiles   │       │  health_history │
└──────┬──────┘       └──────────────────┘       └────────┬────────┘
       │                                                  │
       ▼                                                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐
│      goals       │ │    tasks     │ │  focus_sessions  │ │  digital_activities│
└────────┬─────────┘ └──────┬───────┘ └────────┬─────────┘ └────────┬─────────┘
         │                  │                   │                   │
         ▼                  ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  goal_progress   │ │              │ │                  │ │website_classif.  │
└──────────────────┘ └──────────────┘ └──────────────────┘ └──────────────────┘

         │                                                     │
         ▼                                                     ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  sleep_records   │ │nutrition_rec.│ │physical_activ.   │ │hydration_records │
└────────┬─────────┘ └──────┬───────┘ └────────┬─────────┘ └────────┬─────────┘
         │                  │                   │                   │
         ▼                  ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐
│daily_*_summaries │ │daily_nutr... │ │daily_phys...     │ │daily_hydr...     │
└──────────────────┘ └──────────────┘ └──────────────────┘ └──────────────────┘

         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI INTELLIGENCE LAYER                      │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│ ai_observations │ detected_patterns│ recommendations │ weekly_   │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              NOTIFICATIONS & KNOWLEDGE                          │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│  notifications  │push_subscriptions│knowledge_articles│evidence_ │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                              │
                              ▼
┌─────────────────┬─────────────────┬─────────────────┬───────────┤
│user_knowledge_i.│personalized_k...│ weekly_surveys   │survey_tem.│
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

---

## Table Definitions

### 1. Core User Tables

#### `users`
Primary authentication and account table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hash |
| full_name | VARCHAR(255) | NULLABLE | Display name |
| role | ENUM | NOT NULL, DEFAULT 'user' | user, admin, researcher |
| status | ENUM | NOT NULL, DEFAULT 'active' | active, inactive, suspended, deleted |
| is_verified | BOOLEAN | NOT NULL, DEFAULT false | Email verification |
| is_superuser | BOOLEAN | NOT NULL, DEFAULT false | Admin flag |
| last_login | TIMESTAMPTZ | NULLABLE | Last successful login |
| failed_login_attempts | INTEGER | NOT NULL, DEFAULT 0 | Brute force protection |
| locked_until | TIMESTAMPTZ | NULLABLE | Account lockout |
| email_verification_token | VARCHAR(255) | NULLABLE | Email verification |
| password_reset_token | VARCHAR(255) | NULLABLE | Password reset |
| password_reset_expires | TIMESTAMPTZ | NULLABLE | Reset token expiry |
| preferences | JSONB | NOT NULL, DEFAULT '{}' | User preferences |
| timezone | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | User timezone |
| locale | VARCHAR(10) | NOT NULL, DEFAULT 'en' | Language locale |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Record creation |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Record update |

**Indexes**: `ix_users_email` (unique), `ix_users_status`

#### `user_profiles`
Extended lifestyle and demographic information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, UNIQUE, NOT NULL | Owner |
| date_of_birth | DATE | NULLABLE | |
| gender | ENUM | NULLABLE | male, female, non_binary, prefer_not_to_say, other |
| height_cm | FLOAT | NULLABLE, CHECK > 0 | |
| weight_kg | FLOAT | NULLABLE, CHECK > 0 | |
| activity_level | ENUM | NULLABLE | sedentary, lightly_active, moderately_active, very_active, extra_active |
| dietary_preference | ENUM | NULLABLE | omnivore, vegetarian, vegan, pescatarian, keto, paleo, mediterranean, gluten_free, dairy_free, other, no_preference |
| dietary_restrictions | JSONB | DEFAULT '[]' | Array of strings |
| allergies | JSONB | DEFAULT '[]' | |
| medical_conditions | JSONB | DEFAULT '[]' | |
| medications | JSONB | DEFAULT '[]' | |
| supplements | JSONB | DEFAULT '[]' | |
| occupation | VARCHAR(100) | NULLABLE | |
| work_schedule | VARCHAR(50) | NULLABLE | 9-5, shift, flexible, etc. |
| typical_wake_time | VARCHAR(5) | NULLABLE | HH:MM format |
| typical_bed_time | VARCHAR(5) | NULLABLE | HH:MM format |
| typical_work_hours | JSONB | NULLABLE | {start, end, days[]} |
| timezone | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | |
| avatar_url | VARCHAR(500) | NULLABLE | |
| bio | TEXT | NULLABLE | |
| emergency_contact | JSONB | NULLABLE | |
| health_provider | VARCHAR(255) | NULLABLE | |
| health_insurance | VARCHAR(255) | NULLABLE | |
| onboarding_completed | BOOLEAN | DEFAULT false | |
| onboarding_step | INTEGER | DEFAULT 0 | |
| profile_completeness | FLOAT | DEFAULT 0.0 | 0-100% |

**Indexes**: `ix_user_profiles_user_id` (unique)

#### `health_history`
User-reported medical history with audit trail.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| condition_name | VARCHAR(255) | NOT NULL | |
| condition_category | VARCHAR(100) | NOT NULL | chronic, acute, mental, etc. |
| diagnosed_date | DATE | NULLABLE | |
| resolved_date | DATE | NULLABLE | |
| is_active | BOOLEAN | DEFAULT true | |
| severity | VARCHAR(50) | NULLABLE | mild, moderate, severe |
| notes | TEXT | NULLABLE | |
| diagnosed_by | VARCHAR(255) | NULLABLE | |
| icd_code | VARCHAR(20) | NULLABLE | ICD-10 code |
| source | VARCHAR(50) | DEFAULT 'user_reported' | user_reported, imported, verified |

**Indexes**: `ix_health_history_user_id`, `ix_health_history_condition`, `ix_health_history_active`

#### `consent_records`
GDPR/CCPA compliant consent tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| consent_type | VARCHAR(100) | NOT NULL | data_collection, analytics, marketing, ai_processing, third_party_sharing, push_notifications, browser_tracking |
| consent_given | BOOLEAN | DEFAULT false | |
| consent_version | VARCHAR(20) | NOT NULL | |
| consent_text | TEXT | NOT NULL | Full consent text |
| ip_address | VARCHAR(45) | NULLABLE | |
| user_agent | TEXT | NULLABLE | |
| withdrawn_at | TIMESTAMPTZ | NULLABLE | |
| withdrawal_reason | TEXT | NULLABLE | |

**Constraints**: UNIQUE(user_id, consent_type, consent_version)

#### `audit_logs`
Security and compliance audit trail.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NULLABLE | NULL for system actions |
| action | VARCHAR(100) | NOT NULL | login, logout, data_export, delete_account, etc. |
| resource_type | VARCHAR(100) | NOT NULL | user, goal, health_record, etc. |
| resource_id | VARCHAR(100) | NULLABLE | |
| old_values | JSONB | NULLABLE | |
| new_values | JSONB | NULLABLE | |
| ip_address | VARCHAR(45) | NULLABLE | |
| user_agent | TEXT | NULLABLE | |
| success | BOOLEAN | DEFAULT true | |
| error_message | TEXT | NULLABLE | |

**Indexes**: `ix_audit_logs_user_id`, `ix_audit_logs_action`, `ix_audit_logs_resource`, `ix_audit_logs_created_at`

---

### 2. Goals & Productivity Tables

#### `goals`
User-defined targets across all life domains.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | |
| category | ENUM | NOT NULL | digital_wellbeing, physical_activity, nutrition, sleep, study, work, personal_routine, mental_wellbeing, hydration, general_lifestyle |
| frequency | ENUM | DEFAULT 'daily' | daily, weekly, monthly, custom |
| status | ENUM | DEFAULT 'active' | active, paused, completed, archived, failed |
| target_value | FLOAT | NOT NULL, CHECK >= 0 | |
| target_unit | ENUM | NOT NULL | minutes, hours, count, steps, calories, grams, milliliters, liters, kg, percentage, score, boolean |
| baseline_value | FLOAT | NULLABLE, CHECK >= 0 | Starting value |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NULLABLE | |
| target_days_per_week | INTEGER | NULLABLE, CHECK 1-7 | For custom frequency |
| reminder_enabled | BOOLEAN | DEFAULT true | |
| reminder_time | TIME | NULLABLE | |
| reminder_days | JSONB | DEFAULT '[]' | Array of 0-6 (Mon-Sun) |
| current_value | FLOAT | DEFAULT 0, CHECK >= 0 | |
| progress_percentage | FLOAT | DEFAULT 0, CHECK 0-100 | |
| streak_days | INTEGER | DEFAULT 0 | Current streak |
| longest_streak | INTEGER | DEFAULT 0 | Best streak |
| last_completed_date | DATE | NULLABLE | |
| ai_generated | BOOLEAN | DEFAULT false | |
| ai_reasoning | TEXT | NULLABLE | |
| difficulty_rating | INTEGER | NULLABLE, CHECK 1-10 | |
| priority | INTEGER | DEFAULT 1, CHECK 1-3 | 1=high, 3=low |
| tags | JSONB | DEFAULT '[]' | |
| metadata | JSONB | DEFAULT '{}' | Extensible |

**Indexes**: `ix_goals_user_id`, `ix_goals_category`, `ix_goals_status`, `ix_goals_dates`

#### `goal_progress`
Daily progress tracking for goals.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| goal_id | UUID | FK→goals.id, NOT NULL | |
| date | DATE | NOT NULL | |
| value | FLOAT | NOT NULL, CHECK >= 0 | Actual value |
| target_value | FLOAT | NOT NULL, CHECK >= 0 | Target for this date |
| achieved | BOOLEAN | DEFAULT false | |
| notes | TEXT | NULLABLE | |
| source | VARCHAR(50) | DEFAULT 'manual' | manual, auto, imported |
| metadata | JSONB | DEFAULT '{}' | |

**Constraints**: UNIQUE(goal_id, date)

#### `tasks`
Actionable items linked to goals.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| goal_id | UUID | FK→goals.id, NULLABLE | Optional link |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | |
| category | ENUM | DEFAULT 'personal' | work, study, personal, health, admin, creative, learning, social, other |
| priority | ENUM | DEFAULT 'medium' | low, medium, high, urgent |
| status | ENUM | DEFAULT 'pending' | pending, in_progress, completed, cancelled, overdue |
| scheduled_date | DATE | NULLABLE | |
| scheduled_time | TIME | NULLABLE | |
| due_date | DATE | NULLABLE | |
| due_time | TIME | NULLABLE | |
| estimated_duration_minutes | INTEGER | NULLABLE, CHECK > 0 | |
| actual_duration_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| is_recurring | BOOLEAN | DEFAULT false | |
| recurrence_rule | VARCHAR(100) | NULLABLE | RRULE format |
| recurrence_end_date | DATE | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| completion_notes | TEXT | NULLABLE | |

**Indexes**: `ix_tasks_user_id`, `ix_tasks_goal_id`, `ix_tasks_status`, `ix_tasks_scheduled_date`, `ix_tasks_due_date`

#### `focus_sessions`
Pomodoro/deep work sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| task_id | UUID | FK→tasks.id, NULLABLE | |
| goal_id | UUID | FK→goals.id, NULLABLE | |
| status | ENUM | DEFAULT 'planned' | planned, active, paused, completed, interrupted, cancelled |
| planned_duration_minutes | INTEGER | NOT NULL, CHECK > 0 | |
| actual_duration_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| planned_start | TIMESTAMPTZ | NULLABLE | |
| actual_start | TIMESTAMPTZ | NULLABLE | |
| actual_end | TIMESTAMPTZ | NULLABLE | |
| interruption_count | INTEGER | DEFAULT 0 | |
| interruption_details | JSONB | DEFAULT '[]' | [{time, duration, reason}] |
| total_interruption_minutes | INTEGER | DEFAULT 0 | |
| focus_quality_rating | INTEGER | NULLABLE, CHECK 1-10 | |
| productivity_rating | INTEGER | NULLABLE, CHECK 1-10 | |
| notes | TEXT | NULLABLE | |
| environment_type | VARCHAR(50) | NULLABLE | home, office, library, cafe |
| noise_level | VARCHAR(20) | NULLABLE | quiet, moderate, noisy |
| device_used | VARCHAR(100) | NULLABLE | |

**Indexes**: `ix_focus_sessions_user_id`, `ix_focus_sessions_task_id`, `ix_focus_sessions_status`, `ix_focus_sessions_actual_start`

---

### 3. Digital Activity Tables

#### `digital_activities`
Raw browser activity events from extension.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| session_id | VARCHAR(100) | NULLABLE, INDEX | Browser session ID |
| source | ENUM | DEFAULT 'browser_extension' | browser_extension, desktop_app, mobile_app, manual, imported |
| url | TEXT | NOT NULL | Full URL |
| domain | VARCHAR(255) | NOT NULL, INDEX | example.com |
| subdomain | VARCHAR(255) | NULLABLE | app.example.com |
| title | TEXT | NULLABLE | Page title |
| favicon_url | TEXT | NULLABLE | |
| category | ENUM | DEFAULT 'unclassified' | work, study, learning, communication, research, entertainment, social_media, gaming, shopping, news, finance, health, productivity, development, design, writing, reading, video, music, distraction, unclassified |
| subcategory | VARCHAR(100) | NULLABLE | |
| is_productive | BOOLEAN | NULLABLE | User/AI classified |
| user_classified | BOOLEAN | DEFAULT false | |
| confidence_score | FLOAT | NULLABLE, CHECK 0-1 | AI classification confidence |
| start_time | TIMESTAMPTZ | NOT NULL, INDEX | |
| end_time | TIMESTAMPTZ | NOT NULL, INDEX | |
| duration_seconds | INTEGER | NOT NULL, CHECK > 0 | Total duration |
| active_seconds | INTEGER | NOT NULL, CHECK >= 0 | Active interaction |
| idle_seconds | INTEGER | DEFAULT 0, CHECK >= 0 | |
| tab_switches | INTEGER | DEFAULT 0, CHECK >= 0 | |
| scroll_count | INTEGER | DEFAULT 0, CHECK >= 0 | |
| click_count | INTEGER | DEFAULT 0, CHECK >= 0 | |
| keystroke_count | INTEGER | DEFAULT 0, CHECK >= 0 | |
| is_fullscreen | BOOLEAN | DEFAULT false | |
| is_incognito | BOOLEAN | DEFAULT false | |
| window_id | INTEGER | NULLABLE | |
| tab_id | INTEGER | NULLABLE | |
| device_type | VARCHAR(50) | NULLABLE | desktop, laptop, tablet, mobile |
| os | VARCHAR(50) | NULLABLE | |
| browser | VARCHAR(50) | NULLABLE | |
| screen_resolution | VARCHAR(20) | NULLABLE | |
| referrer_url | TEXT | NULLABLE | |
| metadata | JSONB | DEFAULT '{}' | Extensible |

**Indexes**: 
- `ix_digital_activities_user_id`
- `ix_digital_activities_domain`
- `ix_digital_activities_category`
- `ix_digital_activities_start_time`
- `ix_digital_activities_user_date` (user_id, start_time)
- CHECK constraints for duration validity

#### `website_classifications`
User-defined categorization rules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| domain | VARCHAR(255) | NOT NULL, INDEX | |
| subdomain | VARCHAR(255) | NULLABLE | |
| url_pattern | TEXT | NULLABLE | Regex for specific paths |
| category | ENUM | NOT NULL | Same as digital_activities |
| subcategory | VARCHAR(100) | NULLABLE | |
| is_productive | BOOLEAN | NULLABLE | |
| priority | INTEGER | DEFAULT 0 | Higher = more specific |
| notes | TEXT | NULLABLE | |
| auto_created | BOOLEAN | DEFAULT false | |

**Constraints**: UNIQUE(user_id, domain, subdomain, url_pattern)

#### `daily_digital_summaries`
Pre-aggregated daily analytics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| total_seconds | INTEGER | DEFAULT 0 | |
| active_seconds | INTEGER | DEFAULT 0 | |
| idle_seconds | INTEGER | DEFAULT 0 | |
| category_breakdown | JSONB | DEFAULT '{}' | {category: seconds} |
| top_domains | JSONB | DEFAULT '[]' | [{domain, seconds, category}] |
| productive_seconds | INTEGER | DEFAULT 0 | |
| unproductive_seconds | INTEGER | DEFAULT 0 | |
| neutral_seconds | INTEGER | DEFAULT 0 | |
| session_count | INTEGER | DEFAULT 0 | |
| avg_session_seconds | FLOAT | DEFAULT 0 | |
| longest_session_seconds | INTEGER | DEFAULT 0 | |
| total_tab_switches | INTEGER | DEFAULT 0 | |
| total_interruptions | INTEGER | DEFAULT 0 | |
| hourly_distribution | JSONB | DEFAULT '{}' | {hour: seconds} |
| day_part_distribution | JSONB | DEFAULT '{}' | morning, afternoon, evening, night |
| data_completeness | FLOAT | DEFAULT 1.0 | 0-1 |
| sources | JSONB | DEFAULT '[]' | ['browser_extension', ...] |

**Constraints**: UNIQUE(user_id, date)

#### `weekly_digital_summaries`
Pre-aggregated weekly analytics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| week_start | DATE | NOT NULL, INDEX | Monday |
| week_end | DATE | NOT NULL | Sunday |
| total_seconds | INTEGER | DEFAULT 0 | |
| active_seconds | INTEGER | DEFAULT 0 | |
| daily_average_seconds | FLOAT | DEFAULT 0 | |
| trend_vs_previous_week | FLOAT | NULLABLE | Percentage change |
| category_breakdown | JSONB | DEFAULT '{}' | |
| category_trends | JSONB | DEFAULT '{}' | {category: pct_change} |
| goals_met | INTEGER | DEFAULT 0 | |
| goals_total | INTEGER | DEFAULT 0 | |
| focus_sessions_count | INTEGER | DEFAULT 0 | |
| focus_sessions_total_minutes | INTEGER | DEFAULT 0 | |
| avg_focus_quality | FLOAT | NULLABLE | |
| data_completeness | FLOAT | DEFAULT 1.0 | |

**Constraints**: UNIQUE(user_id, week_start)

#### `digital_wellbeing_thresholds`
User-defined nudge triggers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | NULLABLE | |
| metric | VARCHAR(50) | NOT NULL | total_screen_time, social_media_time, etc. |
| category | ENUM | NULLABLE | digital_activities.category |
| domain | VARCHAR(255) | NULLABLE | Specific domain |
| threshold_value | FLOAT | NOT NULL | |
| threshold_unit | VARCHAR(20) | DEFAULT 'seconds' | seconds, minutes, hours, count |
| comparison | VARCHAR(10) | DEFAULT 'gte' | gte, lte, gt, lt, eq |
| window_type | VARCHAR(20) | DEFAULT 'daily' | daily, weekly, session |
| window_start | VARCHAR(5) | NULLABLE | HH:MM |
| window_end | VARCHAR(5) | NULLABLE | HH:MM |
| days_of_week | JSONB | DEFAULT '[]' | Empty = all days |
| nudge_enabled | BOOLEAN | DEFAULT true | |
| nudge_message | TEXT | NULLABLE | Custom message |
| nudge_severity | VARCHAR(20) | DEFAULT 'info' | info, warning, critical |
| cooldown_minutes | INTEGER | DEFAULT 60 | |
| max_nudges_per_day | INTEGER | DEFAULT 3 | |
| is_active | BOOLEAN | DEFAULT true | |
| last_triggered | TIMESTAMPTZ | NULLABLE | |
| trigger_count_today | INTEGER | DEFAULT 0 | |
| trigger_count_total | INTEGER | DEFAULT 0 | |

---

### 4. Physical Health Tables

#### `sleep_records`
Sleep tracking with multi-source support.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| source | ENUM | DEFAULT 'manual' | manual, wearable, phone_app, smart_mattress, imported, estimated |
| device_id | VARCHAR(100) | NULLABLE | |
| bedtime | TIMESTAMPTZ | NOT NULL | When went to bed |
| sleep_start | TIMESTAMPTZ | NOT NULL | Actual sleep onset |
| sleep_end | TIMESTAMPTZ | NOT NULL | Actual wake |
| wake_time | TIMESTAMPTZ | NOT NULL | Got out of bed |
| time_in_bed_minutes | INTEGER | NOT NULL, CHECK >= 0 | |
| total_sleep_minutes | INTEGER | NOT NULL, CHECK >= 0 | |
| deep_sleep_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| light_sleep_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| rem_sleep_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| awake_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| sleep_latency_minutes | INTEGER | NULLABLE, CHECK >= 0 | Time to fall asleep |
| wake_after_sleep_onset_minutes | INTEGER | NULLABLE, CHECK >= 0 | WASO |
| quality_rating | ENUM | NULLABLE | very_poor, poor, fair, good, excellent |
| quality_score | INTEGER | NULLABLE, CHECK 0-100 | |
| restfulness_rating | INTEGER | NULLABLE, CHECK 1-10 | Subjective |
| wake_count | INTEGER | DEFAULT 0 | |
| interruption_details | JSONB | DEFAULT '[]' | [{time, duration}] |
| room_temperature | FLOAT | NULLABLE | Celsius |
| noise_level | VARCHAR(20) | NULLABLE | quiet, moderate, loud |
| light_level | VARCHAR(20) | NULLABLE | dark, dim, bright |
| screen_time_before_bed_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| caffeine_after_noon | BOOLEAN | DEFAULT false | |
| alcohol_before_bed | BOOLEAN | DEFAULT false | |
| exercise_before_bed | BOOLEAN | DEFAULT false | |
| meal_before_bed_minutes | INTEGER | NULLABLE, CHECK >= 0 | |
| notes | TEXT | NULLABLE | |
| tags | JSONB | DEFAULT '[]' | |
| metadata | JSONB | DEFAULT '{}' | |

**Constraints**: 
- UNIQUE(user_id, date, sleep_start)
- CHECK total_sleep_minutes <= time_in_bed_minutes

#### `nutrition_records`
Food logging with detailed nutrition.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| meal_type | ENUM | DEFAULT 'other' | breakfast, brunch, lunch, snack, dinner, late_night, other |
| source | ENUM | DEFAULT 'manual' | manual, barcode_scan, recipe, restaurant, meal_plan, imported, ai_estimated |
| timestamp | TIMESTAMPTZ | NOT NULL, INDEX | |
| food_name | VARCHAR(255) | NOT NULL | |
| brand | VARCHAR(255) | NULLABLE | |
| barcode | VARCHAR(50) | NULLABLE | |
| food_database_id | VARCHAR(100) | NULLABLE | USDA, OpenFoodFacts ID |
| quantity | FLOAT | NOT NULL, CHECK > 0 | |
| unit | VARCHAR(50) | NOT NULL | grams, ml, pieces, cups, etc. |
| serving_size | FLOAT | NULLABLE, CHECK > 0 | |
| serving_unit | VARCHAR(50) | NULLABLE | |
| calories | FLOAT | NULLABLE, CHECK >= 0 | |
| protein_g | FLOAT | NULLABLE, CHECK >= 0 | |
| carbs_g | FLOAT | NULLABLE, CHECK >= 0 | |
| fat_g | FLOAT | NULLABLE, CHECK >= 0 | |
| fiber_g | FLOAT | NULLABLE, CHECK >= 0 | |
| sugar_g | FLOAT | NULLABLE, CHECK >= 0 | |
| added_sugar_g | FLOAT | NULLABLE, CHECK >= 0 | |
| sodium_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| potassium_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| calcium_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| iron_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| vitamin_c_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| vitamin_d_iu | FLOAT | NULLABLE, CHECK >= 0 | |
| vitamin_b12_mcg | FLOAT | NULLABLE, CHECK >= 0 | |
| magnesium_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| zinc_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| omega3_g | FLOAT | NULLABLE, CHECK >= 0 | |
| cholesterol_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| saturated_fat_g | FLOAT | NULLABLE, CHECK >= 0 | |
| trans_fat_g | FLOAT | NULLABLE, CHECK >= 0 | |
| processing_level | VARCHAR(50) | NULLABLE | unprocessed, minimally, processed, ultra_processed |
| nutriscore | VARCHAR(1) | NULLABLE | A, B, C, D, E |
| health_stars | FLOAT | NULLABLE, CHECK 0.5-5 | |
| notes | TEXT | NULLABLE | |
| photo_url | TEXT | NULLABLE | |
| recipe_id | VARCHAR(100) | NULLABLE | |
| metadata | JSONB | DEFAULT '{}' | |

#### `daily_nutrition_summaries`
Pre-aggregated daily nutrition.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| total_calories | FLOAT | NULLABLE | |
| total_protein_g | FLOAT | NULLABLE | |
| total_carbs_g | FLOAT | NULLABLE | |
| total_fat_g | FLOAT | NULLABLE | |
| total_fiber_g | FLOAT | NULLABLE | |
| total_sugar_g | FLOAT | NULLABLE | |
| total_added_sugar_g | FLOAT | NULLABLE | |
| total_sodium_mg | FLOAT | NULLABLE | |
| meals_count | INTEGER | DEFAULT 0 | |
| meal_breakdown | JSONB | DEFAULT '{}' | {meal_type: {calories, protein...}} |
| food_groups | JSONB | DEFAULT '{}' | {group: servings} |
| avg_nutriscore | VARCHAR(1) | NULLABLE | |
| ultra_processed_percentage | FLOAT | NULLABLE | |
| dietary_variety_score | FLOAT | NULLABLE | 0-100 |
| water_from_food_ml | FLOAT | NULLABLE | |
| data_completeness | FLOAT | DEFAULT 1.0 | |
| sources | JSONB | DEFAULT '[]' | |
| estimated_values | BOOLEAN | DEFAULT false | |

**Constraints**: UNIQUE(user_id, date)

#### `physical_activities`
Exercise and movement tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| activity_type | ENUM | NOT NULL | walking, running, cycling, swimming, weight_training, bodyweight, yoga, pilates, hiit, crossfit, rowing, elliptical, stair_climbing, hiking, sports, dance, martial_arts, stretching, mobility, other |
| source | ENUM | DEFAULT 'manual' | manual, wearable, phone_app, gym_equipment, imported, ai_estimated |
| device_id | VARCHAR(100) | NULLABLE | |
| start_time | TIMESTAMPTZ | NOT NULL, INDEX | |
| end_time | TIMESTAMPTZ | NOT NULL | |
| duration_minutes | INTEGER | NOT NULL, CHECK > 0 | |
| intensity | ENUM | NULLABLE | very_light, light, moderate, vigorous, very_vigorous |
| avg_heart_rate | INTEGER | NULLABLE, CHECK 30-220 | |
| max_heart_rate | INTEGER | NULLABLE, CHECK 30-220 | |
| heart_rate_zones | JSONB | NULLABLE | {zone: minutes} |
| calories_burned | FLOAT | NULLABLE, CHECK >= 0 | |
| distance_km | FLOAT | NULLABLE, CHECK >= 0 | |
| steps | INTEGER | NULLABLE, CHECK >= 0 | |
| pace_min_per_km | FLOAT | NULLABLE, CHECK >= 0 | |
| elevation_gain_m | FLOAT | NULLABLE, CHECK >= 0 | |
| sets | INTEGER | NULLABLE, CHECK >= 0 | |
| reps | INTEGER | NULLABLE, CHECK >= 0 | |
| weight_kg | FLOAT | NULLABLE, CHECK >= 0 | |
| volume_kg | FLOAT | NULLABLE, CHECK >= 0 | sets * reps * weight |
| muscle_groups | JSONB | DEFAULT '[]' | |
| rpe | INTEGER | NULLABLE, CHECK 1-10 | Rate of Perceived Exertion |
| enjoyment_rating | INTEGER | NULLABLE, CHECK 1-10 | |
| location | VARCHAR(100) | NULLABLE | gym, home, outdoors, pool |
| weather | VARCHAR(50) | NULLABLE | |
| temperature_c | FLOAT | NULLABLE | |
| social | BOOLEAN | DEFAULT false | Group activity |
| recovery_rating | INTEGER | NULLABLE, CHECK 1-10 | Next day |
| soreness_level | INTEGER | NULLABLE, CHECK 1-10 | Next day |
| notes | TEXT | NULLABLE | |
| tags | JSONB | DEFAULT '[]' | |
| metadata | JSONB | DEFAULT '{}' | |

**Constraints**: CHECK rpe BETWEEN 1 AND 10

#### `daily_physical_activity_summaries`
Pre-aggregated daily activity.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| total_duration_minutes | INTEGER | DEFAULT 0 | |
| total_calories_burned | FLOAT | NULLABLE | |
| total_steps | INTEGER | NULLABLE | |
| total_distance_km | FLOAT | NULLABLE | |
| activity_breakdown | JSONB | DEFAULT '{}' | {type: minutes} |
| intensity_breakdown | JSONB | DEFAULT '{}' | {intensity: minutes} |
| session_count | INTEGER | DEFAULT 0 | |
| strength_sessions | INTEGER | DEFAULT 0 | |
| cardio_sessions | INTEGER | DEFAULT 0 | |
| flexibility_sessions | INTEGER | DEFAULT 0 | |
| avg_heart_rate | INTEGER | NULLABLE | |
| max_heart_rate | INTEGER | NULLABLE | |
| active_minutes | INTEGER | DEFAULT 0 | Moderate+ intensity |
| mvpa_minutes | INTEGER | DEFAULT 0 | Moderate-to-Vigorous |
| step_goal_met | BOOLEAN | DEFAULT false | |
| activity_goal_met | BOOLEAN | DEFAULT false | |
| sedentary_hours | FLOAT | NULLABLE | |
| prolonged_sedentary_bouts | INTEGER | DEFAULT 0 | >60 min bouts |
| data_completeness | FLOAT | DEFAULT 1.0 | |
| sources | JSONB | DEFAULT '[]' | |

**Constraints**: UNIQUE(user_id, date)

#### `hydration_records`
Water and fluid intake tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| timestamp | TIMESTAMPTZ | NOT NULL, INDEX | |
| source | ENUM | DEFAULT 'manual' | manual, smart_bottle, app, imported, estimated |
| amount_ml | INTEGER | NOT NULL, CHECK > 0 | |
| beverage_type | VARCHAR(50) | DEFAULT 'water' | water, tea, coffee, juice, soda, alcohol, sports_drink, other |
| hydration_index | FLOAT | NULLABLE | Net hydration (water=1.0, coffee=0.8, alcohol=-0.5) |
| caffeine_mg | INTEGER | NULLABLE, CHECK >= 0 | |
| sugar_g | FLOAT | NULLABLE, CHECK >= 0 | |
| electrolytes_mg | FLOAT | NULLABLE, CHECK >= 0 | |
| meal_related | BOOLEAN | DEFAULT false | |
| exercise_related | BOOLEAN | DEFAULT false | |
| notes | TEXT | NULLABLE | |
| metadata | JSONB | DEFAULT '{}' | |

#### `daily_hydration_summaries`
Pre-aggregated daily hydration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| date | DATE | NOT NULL, INDEX | |
| total_ml | INTEGER | DEFAULT 0 | |
| net_hydration_ml | FLOAT | NULLABLE | Adjusted for diuretics |
| beverage_breakdown | JSONB | DEFAULT '{}' | {type: ml} |
| first_drink_time | TIME | NULLABLE | |
| last_drink_time | TIME | NULLABLE | |
| hourly_distribution | JSONB | DEFAULT '{}' | {hour: ml} |
| goal_ml | INTEGER | NULLABLE | |
| goal_met | BOOLEAN | DEFAULT false | |
| total_caffeine_mg | INTEGER | DEFAULT 0 | |
| total_sugar_g | FLOAT | NULLABLE | |
| water_percentage | FLOAT | NULLABLE | |
| data_completeness | FLOAT | DEFAULT 1.0 | |
| sources | JSONB | DEFAULT '[]' | |

**Constraints**: UNIQUE(user_id, date)

---

### 5. AI Intelligence Tables

#### `ai_observations`
AI-detected patterns and insights.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| observation_type | ENUM | NOT NULL | pattern_detected, anomaly_detected, goal_progress, goal_at_risk, threshold_crossed, correlation_found, trend_change, milestone_reached, behavioral_insight, health_indicator |
| severity | ENUM | DEFAULT 'info' | info, low, medium, high, critical |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NOT NULL | |
| detailed_analysis | TEXT | NULLABLE | |
| related_domains | JSONB | DEFAULT '[]' | ['digital', 'sleep', 'nutrition', ...] |
| related_goal_ids | JSONB | DEFAULT '[]' | Array of UUIDs |
| related_record_ids | JSONB | DEFAULT '[]' | [{type: 'sleep_records', ids: [...]}] |
| evidence_summary | TEXT | NULLABLE | |
| supporting_data | JSONB | DEFAULT '{}' | Raw data points |
| confidence_score | FLOAT | DEFAULT 0, CHECK 0-1 | |
| evidence_quality | VARCHAR(50) | NULLABLE | strong, moderate, weak |
| observation_period_start | DATE | NOT NULL | |
| observation_period_end | DATE | NOT NULL | |
| detected_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| is_read | BOOLEAN | DEFAULT false | |
| is_dismissed | BOOLEAN | DEFAULT false | |
| is_actionable | BOOLEAN | DEFAULT true | |
| user_feedback | VARCHAR(20) | NULLABLE | helpful, not_helpful, inaccurate, already_known |
| model_version | VARCHAR(50) | NOT NULL | |
| prompt_version | VARCHAR(50) | NOT NULL | |
| generation_metadata | JSONB | DEFAULT '{}' | |

**Indexes**: `ix_ai_observations_user_id`, `ix_ai_observations_type`, `ix_ai_observations_severity`, `ix_ai_observations_period`, `ix_ai_observations_detected_at`, `ix_ai_observations_unread` (user_id, is_read)

#### `detected_patterns`
Cross-domain correlations with statistical backing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| pattern_category | ENUM | NOT NULL | sleep_digital, activity_nutrition, stress_sleep, work_life_balance, consistency, goal_adherence, seasonal, weekly_rhythm, progress_trajectory, behavioral_cluster |
| pattern_name | VARCHAR(255) | NOT NULL | |
| description | TEXT | NOT NULL | |
| variables_involved | JSONB | DEFAULT '[]' | ['sleep_duration', 'screen_time_before_bed'] |
| correlation_coefficient | FLOAT | NULLABLE, CHECK -1 to 1 | |
| p_value | FLOAT | NULLABLE, CHECK 0-1 | |
| strength | ENUM | NOT NULL | weak, moderate, strong, very_strong |
| direction | VARCHAR(20) | NULLABLE | positive, negative, complex |
| first_detected | DATE | NOT NULL | |
| last_confirmed | DATE | NOT NULL | |
| detection_count | INTEGER | DEFAULT 1 | |
| consistency_score | FLOAT | DEFAULT 0, CHECK 0-1 | |
| supporting_observations | JSONB | DEFAULT '[]' | |
| sample_size | INTEGER | DEFAULT 0 | |
| date_range_start | DATE | NOT NULL | |
| date_range_end | DATE | NOT NULL | |
| is_actionable | BOOLEAN | DEFAULT true | |
| suggested_interventions | JSONB | DEFAULT '[]' | |
| related_goal_ids | JSONB | DEFAULT '[]' | |
| is_active | BOOLEAN | DEFAULT true | |
| user_acknowledged | BOOLEAN | DEFAULT false | |
| user_feedback | VARCHAR(20) | NULLABLE | helpful, not_helpful, inaccurate, already_known |
| model_version | VARCHAR(50) | NOT NULL | |
| detection_method | VARCHAR(100) | NOT NULL | statistical, ml, rule_based |
| metadata | JSONB | DEFAULT '{}' | |

**Indexes**: `ix_detected_patterns_user_id`, `ix_detected_patterns_category`, `ix_detected_patterns_active`, `ix_detected_patterns_strength`

#### `recommendations`
Personalized AI-generated suggestions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| observation_id | UUID | FK→ai_observations.id, NULLABLE | |
| pattern_id | UUID | FK→detected_patterns.id, NULLABLE | |
| recommendation_type | ENUM | NOT NULL | behavioral_change, routine_adjustment, goal_modification, environment_change, knowledge_acquisition, professional_referral, habit_formation, recovery_focus |
| priority | ENUM | DEFAULT 'medium' | low, medium, high, urgent |
| status | ENUM | DEFAULT 'pending' | pending, accepted, declined, in_progress, completed, failed, expired, superseded |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NOT NULL | |
| rationale | TEXT | NOT NULL | Why this matters |
| evidence_summary | TEXT | NULLABLE | |
| evidence_sources | JSONB | DEFAULT '[]' | [{title, url, source}] |
| specific_action | TEXT | NOT NULL | Concrete next step |
| action_category | VARCHAR(50) | NOT NULL | digital, sleep, nutrition, activity, etc. |
| difficulty_level | INTEGER | DEFAULT 3, CHECK 1-10 | |
| estimated_time_minutes | INTEGER | NULLABLE, CHECK > 0 | |
| frequency | VARCHAR(50) | NULLABLE | daily, 3x_week, once, etc. |
| duration_weeks | INTEGER | NULLABLE, CHECK > 0 | |
| success_criteria | TEXT | NOT NULL | How to measure |
| measurable_target | JSONB | NULLABLE | {metric, target, unit} |
| baseline_value | FLOAT | NULLABLE | |
| target_value | FLOAT | NULLABLE | |
| suggested_start_date | DATE | NULLABLE | |
| suggested_time_of_day | VARCHAR(5) | NULLABLE | HH:MM |
| reminder_enabled | BOOLEAN | DEFAULT true | |
| reminder_schedule | JSONB | NULLABLE | |
| related_goal_ids | JSONB | DEFAULT '[]' | |
| prerequisite_recommendations | JSONB | DEFAULT '[]' | |
| conflicting_recommendations | JSONB | DEFAULT '[]' | |
| user_response | VARCHAR(20) | NULLABLE | accepted, declined, deferred, modified |
| user_notes | TEXT | NULLABLE | |
| user_modified_action | TEXT | NULLABLE | |
| responded_at | TIMESTAMPTZ | NULLABLE | |
| started_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| model_version | VARCHAR(50) | NOT NULL | |
| prompt_version | VARCHAR(50) | NOT NULL | |
| confidence_score | FLOAT | DEFAULT 0, CHECK 0-1 | |
| generation_metadata | JSONB | DEFAULT '{}' | |

**Indexes**: `ix_recommendations_user_id`, `ix_recommendations_status`, `ix_recommendations_priority`, `ix_recommendations_type`, `ix_recommendations_suggested_start`

#### `recommendation_effectiveness`
Outcome tracking for recommendations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| recommendation_id | UUID | FK→recommendations.id, NOT NULL | |
| evaluation_period_start | DATE | NOT NULL | |
| evaluation_period_end | DATE | NOT NULL | |
| adherence_rate | FLOAT | NULLABLE, CHECK 0-1 | |
| completion_rate | FLOAT | NULLABLE, CHECK 0-1 | |
| progress_towards_target | FLOAT | NULLABLE, CHECK >= 0 | |
| outcome | VARCHAR(50) | NULLABLE | improved, no_change, worsened, mixed |
| outcome_details | TEXT | NULLABLE | |
| measured_improvement | FLOAT | NULLABLE | Percentage |
| statistical_significance | FLOAT | NULLABLE, CHECK 0-1 | |
| unintended_consequences | JSONB | DEFAULT '[]' | |
| positive_spillovers | JSONB | DEFAULT '[]' | |
| user_satisfaction | INTEGER | NULLABLE, CHECK 1-10 | |
| user_feedback | TEXT | NULLABLE | |
| would_recommend | BOOLEAN | NULLABLE | |
| suggested_adjustments | JSONB | DEFAULT '[]' | |
| continue_recommendation | BOOLEAN | NULLABLE | |
| evaluation_method | VARCHAR(50) | DEFAULT 'automated' | |
| data_completeness | FLOAT | DEFAULT 1.0, CHECK 0-1 | |
| metadata | JSONB | DEFAULT '{}' | |

**Constraints**: UNIQUE(recommendation_id, evaluation_period_start, evaluation_period_end)

#### `weekly_reports`
Comprehensive weekly intelligence reports.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| week_start | DATE | NOT NULL, INDEX | Monday |
| week_end | DATE | NOT NULL | Sunday |
| status | ENUM | DEFAULT 'generating' | generating, completed, failed, archived |
| report_data | JSONB | DEFAULT '{}' | Full structured report |
| week_at_a_glance | JSONB | DEFAULT '{}' | Summary |
| digital_life | JSONB | DEFAULT '{}' | |
| physical_wellbeing | JSONB | DEFAULT '{}' | |
| personal_patterns | JSONB | DEFAULT '{}' | |
| missed_goals | JSONB | DEFAULT '{}' | |
| recommendations | JSONB | DEFAULT '[]' | |
| long_term_consequences | JSONB | DEFAULT '[]' | |
| next_week_action_plan | JSONB | DEFAULT '{}' | |
| generated_at | TIMESTAMPTZ | NULLABLE | |
| generation_duration_seconds | FLOAT | NULLABLE | |
| model_version | VARCHAR(50) | NOT NULL | |
| prompt_version | VARCHAR(50) | NOT NULL | |
| data_completeness | FLOAT | DEFAULT 1.0, CHECK 0-1 | |
| sources_used | JSONB | DEFAULT '[]' | |
| is_read | BOOLEAN | DEFAULT false | |
| read_at | TIMESTAMPTZ | NULLABLE | |
| user_rating | INTEGER | NULLABLE, CHECK 1-10 | |
| user_feedback | TEXT | NULLABLE | |
| shared | BOOLEAN | DEFAULT false | |

**Constraints**: UNIQUE(user_id, week_start)

#### `notifications`
Multi-channel alerting system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| notification_type | ENUM | NOT NULL | nudge, reminder, achievement, warning, insight, weekly_report, goal_deadline, threshold_crossed, pattern_detected, recommendation, system |
| priority | ENUM | DEFAULT 'normal' | low, normal, high, urgent |
| status | ENUM | DEFAULT 'pending' | pending, sent, delivered, read, dismissed, snoozed, failed |
| title | VARCHAR(255) | NOT NULL | |
| message | TEXT | NOT NULL | |
| action_text | VARCHAR(100) | NULLABLE | |
| action_url | TEXT | NULLABLE | |
| related_entity_type | VARCHAR(50) | NULLABLE | goal, recommendation, threshold, report |
| related_entity_id | UUID | NULLABLE | |
| threshold_id | UUID | NULLABLE | FK→digital_wellbeing_thresholds |
| channels | JSONB | DEFAULT '[]' | ['in_app', 'push', 'email'] |
| sent_at | TIMESTAMPTZ | NULLABLE | |
| delivered_at | TIMESTAMPTZ | NULLABLE | |
| read_at | TIMESTAMPTZ | NULLABLE | |
| dismissed_at | TIMESTAMPTZ | NULLABLE | |
| snoozed_until | TIMESTAMPTZ | NULLABLE | |
| clicked | BOOLEAN | DEFAULT false | |
| clicked_at | TIMESTAMPTZ | NULLABLE | |
| action_taken | VARCHAR(50) | NULLABLE | |
| nudge_context | JSONB | NULLABLE | |
| nudge_effectiveness | JSONB | NULLABLE | |
| scheduled_for | TIMESTAMPTZ | NULLABLE | |
| expires_at | TIMESTAMPTZ | NULLABLE | |
| recurring | BOOLEAN | DEFAULT false | |
| recurrence_rule | VARCHAR(100) | NULLABLE | RRULE |
| metadata | JSONB | DEFAULT '{}' | |

**Indexes**: `ix_notifications_user_id`, `ix_notifications_status`, `ix_notifications_type`, `ix_notifications_scheduled_for`, `ix_notifications_user_unread`

#### `push_subscriptions`
Web Push API subscriptions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| endpoint | TEXT | NOT NULL | |
| p256dh_key | VARCHAR(100) | NOT NULL | |
| auth_key | VARCHAR(100) | NOT NULL | |
| user_agent | TEXT | NULLABLE | |
| is_active | BOOLEAN | DEFAULT true | |
| last_used | TIMESTAMPTZ | NULLABLE | |

**Constraints**: UNIQUE(user_id, endpoint)

---

### 6. Knowledge Base Tables

#### `knowledge_articles`
Evidence-based educational content.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| slug | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | URL-friendly |
| title | VARCHAR(500) | NOT NULL | |
| subtitle | TEXT | NULLABLE | |
| category | ENUM | NOT NULL | nutrition, sleep_recovery, physical_activity, mental_wellbeing, digital_wellbeing, general_lifestyle, habit_formation, goal_setting, behavioral_psychology |
| subcategory | VARCHAR(100) | NULLABLE, INDEX | |
| tags | JSONB | DEFAULT '[]' | |
| summary | TEXT | NOT NULL | 2-3 sentence summary |
| content | TEXT | NOT NULL | Full Markdown content |
| key_takeaways | JSONB | DEFAULT '[]' | |
| practical_tips | JSONB | DEFAULT '[]' | |
| evidence_quality | ENUM | NOT NULL | high, moderate, low, emerging, consensus |
| evidence_sources | JSONB | DEFAULT '[]' | [{title, url, type, date}] |
| primary_source_type | ENUM | NOT NULL | peer_reviewed_journal, clinical_guideline, government_health_agency, medical_institution, systematic_review, meta_analysis, rct, cohort_study, case_control_study, expert_consensus, reputable_organization |
| doi | VARCHAR(100) | NULLABLE | |
| pmid | VARCHAR(20) | NULLABLE | PubMed ID |
| applicable_populations | JSONB | DEFAULT '[]' | general, athletes, elderly, pregnant, children |
| applicable_conditions | JSONB | DEFAULT '[]' | |
| limitations | TEXT | NULLABLE | |
| contraindications | TEXT | NULLABLE | |
| author | VARCHAR(255) | NULLABLE | |
| reviewer | VARCHAR(255) | NULLABLE | |
| publication_date | DATE | NULLABLE | |
| last_verification_date | DATE | NOT NULL | |
| next_verification_due | DATE | NOT NULL | |
| version | INTEGER | DEFAULT 1 | |
| is_published | BOOLEAN | DEFAULT true | |
| is_featured | BOOLEAN | DEFAULT false | |
| reading_time_minutes | INTEGER | DEFAULT 5, CHECK > 0 | |
| difficulty_level | INTEGER | DEFAULT 2, CHECK 1-3 | 1=beginner, 3=advanced |
| view_count | INTEGER | DEFAULT 0 | |
| helpful_count | INTEGER | DEFAULT 0 | |
| share_count | INTEGER | DEFAULT 0 | |

**Indexes**: `ix_knowledge_articles_category`, `ix_knowledge_articles_published`, `ix_knowledge_articles_verification`

#### `knowledge_article_relations`
Many-to-many article relationships.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| article_id | UUID | FK→knowledge_articles.id, NOT NULL | |
| related_article_id | UUID | FK→knowledge_articles.id, NOT NULL | |
| relation_type | VARCHAR(50) | DEFAULT 'related' | related, prerequisite, follow_up, alternative |
| strength | FLOAT | DEFAULT 1.0, CHECK 0-1 | |

**Constraints**: UNIQUE(article_id, related_article_id)

#### `evidence_sources`
Structured citation database.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| title | VARCHAR(500) | NOT NULL | |
| source_type | ENUM | NOT NULL | peer_reviewed_journal, clinical_guideline, government_health_agency, medical_institution, systematic_review, meta_analysis, rct, cohort_study, case_control_study, expert_consensus, reputable_organization |
| authors | JSONB | DEFAULT '[]' | |
| publication | VARCHAR(255) | NULLABLE | Journal name |
| publication_date | DATE | NULLABLE | |
| url | TEXT | NULLABLE | |
| doi | VARCHAR(100) | NULLABLE | |
| pmid | VARCHAR(20) | NULLABLE | |
| abstract | TEXT | NULLABLE | |
| key_findings | JSONB | DEFAULT '[]' | |
| methodology | TEXT | NULLABLE | |
| sample_size | INTEGER | NULLABLE, CHECK > 0 | |
| population | VARCHAR(255) | NULLABLE | |
| quality_rating | ENUM | NOT NULL | high, moderate, low, emerging, consensus |
| funding_sources | JSONB | DEFAULT '[]' | |
| conflicts_of_interest | TEXT | NULLABLE | |
| tags | JSONB | DEFAULT '[]' | |
| is_verified | BOOLEAN | DEFAULT false | |
| verified_by | VARCHAR(255) | NULLABLE | |
| verified_at | TIMESTAMPTZ | NULLABLE | |

**Indexes**: `ix_evidence_sources_type`, `ix_evidence_sources_quality`, `ix_evidence_sources_verified`

#### `user_knowledge_interactions`
Engagement tracking for personalization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| article_id | UUID | FK→knowledge_articles.id, NOT NULL | |
| interaction_type | VARCHAR(50) | NOT NULL | view, bookmark, share, rate_helpful, complete |
| time_spent_seconds | INTEGER | NULLABLE, CHECK >= 0 | |
| scroll_percentage | INTEGER | NULLABLE, CHECK 0-100 | |
| completed | BOOLEAN | DEFAULT false | |
| rating | INTEGER | NULLABLE, CHECK 1-5 | |
| feedback | TEXT | NULLABLE | |

**Indexes**: `ix_user_knowledge_interactions_user_id`, `ix_user_knowledge_interactions_article_id`, `ix_user_knowledge_interactions_type`

#### `personalized_knowledge_recommendations`
AI-curated content for each user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| article_id | UUID | FK→knowledge_articles.id, NOT NULL | |
| reason | TEXT | NOT NULL | Why recommended |
| relevance_score | FLOAT | DEFAULT 0, CHECK 0-1 | |
| trigger_context | VARCHAR(100) | NULLABLE | goal, pattern, observation, survey, manual |
| is_dismissed | BOOLEAN | DEFAULT false | |
| is_read | BOOLEAN | DEFAULT false | |
| read_at | TIMESTAMPTZ | NULLABLE | |
| model_version | VARCHAR(50) | NOT NULL | |
| generated_at | TIMESTAMPTZ | DEFAULT now() | |

**Constraints**: UNIQUE(user_id, article_id)

#### `weekly_surveys`
Lifestyle assessment responses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→users.id, NOT NULL | |
| week_start | DATE | NOT NULL, INDEX | Monday |
| week_end | DATE | NOT NULL | Sunday |
| submitted_at | TIMESTAMPTZ | NOT NULL | |
| survey_version | VARCHAR(20) | NOT NULL | |
| responses | JSONB | DEFAULT '{}' | Structured answers |
| nutrition_score | FLOAT | NULLABLE, CHECK 0-100 | |
| sleep_score | FLOAT | NULLABLE, CHECK 0-100 | |
| activity_score | FLOAT | NULLABLE, CHECK 0-100 | |
| stress_score | FLOAT | NULLABLE, CHECK 0-100 | |
| digital_wellbeing_score | FLOAT | NULLABLE, CHECK 0-100 | |
| overall_wellbeing_score | FLOAT | NULLABLE, CHECK 0-100 | |
| completion_time_seconds | INTEGER | NULLABLE, CHECK >= 0 | |
| is_complete | BOOLEAN | DEFAULT true | |
| skipped_sections | JSONB | DEFAULT '[]' | |

**Constraints**: UNIQUE(user_id, week_start)

#### `survey_templates`
Conditional questionnaire definitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| version | VARCHAR(20) | UNIQUE, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | NULLABLE | |
| is_active | BOOLEAN | DEFAULT true | |
| sections | JSONB | DEFAULT '[]' | |
| questions | JSONB | DEFAULT '[]' | |
| conditional_logic | JSONB | DEFAULT '[]' | Skip logic |
| scoring_rules | JSONB | DEFAULT '{}' | |
| estimated_time_minutes | INTEGER | DEFAULT 2, CHECK > 0 | |
| created_by | VARCHAR(100) | NULLABLE | |
| validated | BOOLEAN | DEFAULT false | Psychometrically validated |

---

## Migration Strategy

### Initial Migration
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Versioning Strategy
- Each schema change gets a new migration
- Migrations are timestamped: `YYYYMMDD_HHMMSS_description.py`
- Down migrations must be tested
- Production deployments run migrations before code deploy

### Naming Conventions
- Tables: snake_case, plural (`digital_activities`)
- Columns: snake_case (`created_at`)
- Indexes: `ix_{table}_{column(s)}`
- Foreign keys: `fk_{table}_{referenced_table}`
- Unique constraints: `uq_{table}_{columns}`
- Check constraints: `ck_{table}_{condition}`
- Enums: `{table}_{column}_enum`

---

## Performance Considerations

### Partitioning Strategy
- `digital_activities`: Partition by `start_time` (monthly)
- `ai_observations`: Partition by `detected_at` (monthly)
- `notifications`: Partition by `created_at` (monthly)

### Key Indexes for Query Patterns
```sql
-- User-scoped time-range queries (most common)
CREATE INDEX ON digital_activities (user_id, start_time DESC);
CREATE INDEX ON sleep_records (user_id, date DESC);
CREATE INDEX ON nutrition_records (user_id, timestamp DESC);

-- Aggregation lookups
CREATE INDEX ON daily_digital_summaries (user_id, date DESC);
CREATE INDEX ON weekly_digital_summaries (user_id, week_start DESC);

-- AI queries
CREATE INDEX ON ai_observations (user_id, is_read, detected_at DESC);
CREATE INDEX ON recommendations (user_id, status, priority DESC);

-- Vector search (pgvector)
CREATE INDEX ON knowledge_articles USING hnsw (embedding vector_cosine_ops);
```

### Materialized Views (for Dashboard)
```sql
CREATE MATERIALIZED VIEW user_dashboard_summary AS
SELECT u.id as user_id,
       COUNT(DISTINCT d.date) as active_days_30,
       AVG(d.active_seconds) as avg_daily_screen_time,
       AVG(s.total_sleep_minutes) as avg_sleep,
       COUNT(DISTINCT g.id) as active_goals
FROM users u
LEFT JOIN daily_digital_summaries d ON d.user_id = u.id AND d.date >= CURRENT_DATE - 30
LEFT JOIN sleep_records s ON s.user_id = u.id AND s.date >= CURRENT_DATE - 30
LEFT JOIN goals g ON g.user_id = u.id AND g.status = 'active'
GROUP BY u.id;
```

---

## Backup & Recovery

### Backup Schedule
- Continuous: WAL archiving
- Daily: Full pg_dump (compressed)
- Weekly: Logical backup to cold storage
- Point-in-time recovery: 30 days

### Recovery Procedures
1. Restore from latest daily backup
2. Replay WAL segments to target time
3. Verify data integrity
4. Update application connections
5. Run integrity checks

---

## Compliance

### Data Retention
- Active user data: Indefinite
- Deleted user data: 30 days (soft delete), then purge
- Audit logs: 7 years
- Analytics aggregates: Indefinite
- AI training data: Never (opt-in only)

### GDPR Compliance
- Right to access: `/api/v1/users/me` + export endpoint
- Right to rectification: Profile update endpoints
- Right to erasure: `DELETE /api/v1/users/account`
- Right to portability: Export endpoint (JSON)
- Right to restrict: Consent management
- Data processing agreements: With all subprocessors