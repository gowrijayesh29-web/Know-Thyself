# Know Thyself - API Specification

## Overview

RESTful API for Know Thyself personal intelligence platform. All endpoints are prefixed with `/api/v1`.

**Base URL**: `https://api.knowthyself.app/api/v1` (production) / `http://localhost:8000/api/v1` (development)

**Authentication**: JWT Bearer tokens in Authorization header
```
Authorization: Bearer <access_token>
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... }
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### Error Response
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": [
    {"field": "email", "message": "Invalid email format", "code": "value_error.email"}
  ],
  "request_id": "req_abc123"
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTHENTICATION_ERROR | 401 | Invalid/expired token |
| AUTHORIZATION_ERROR | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource doesn't exist |
| VALIDATION_ERROR | 422 | Request body invalid |
| CONFLICT | 409 | Resource already exists |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
| EXTERNAL_SERVICE_ERROR | 502 | Upstream service failed |
| AI_SERVICE_ERROR | 503 | AI processing failed |

## Authentication Endpoints

### POST /auth/login
User login with email/password.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "remember_me": false
}
```

**Response** (200):
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

### POST /auth/register
Create new account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "timezone": "America/New_York",
  "locale": "en",
  "accept_terms": true,
  "marketing_consent": false
}
```

**Response** (201): Same as login

### POST /auth/refresh
Refresh access token.

**Request**:
```json
{
  "refresh_token": "eyJ..."
}
```

### POST /auth/logout
Invalidate tokens (clears cookies).

### GET /auth/me
Get current user profile.

### POST /auth/password/reset
Request password reset email.

### POST /auth/password/reset/confirm
Confirm password reset with token.

### POST /auth/password/change
Change password (authenticated).

---

## User Endpoints

### GET /users/profile
Get current user's extended profile.

### PUT /users/profile
Update profile.

### GET /users/profile/completeness
Get profile completeness score.

### GET /users/health-history
List health history (paginated).

### POST /users/health-history
Add health history entry.

### GET /users/health-history/{id}
Get specific entry.

### PUT /users/health-history/{id}
Update entry.

### DELETE /users/health-history/{id}
Delete entry.

### GET /users/consents
List consent records.

### POST /users/consents
Record consent.

### GET /users/audit-logs (admin)
List audit logs (paginated).

### DELETE /users/account
Soft delete account.

---

## Goals Endpoints

### GET /goals
List goals with filters.

**Query Params**:
- `page`, `page_size`
- `category` (enum)
- `status` (enum)
- `start_date_from`, `start_date_to`

### POST /goals
Create goal.

**Request**:
```json
{
  "title": "Sleep 8 hours",
  "description": "Consistent sleep schedule",
  "category": "sleep",
  "frequency": "daily",
  "target_value": 8,
  "target_unit": "hours",
  "baseline_value": 6.5,
  "start_date": "2024-01-15",
  "end_date": "2024-04-15",
  "reminder_enabled": true,
  "reminder_time": "22:00",
  "reminder_days": [0,1,2,3,4,5,6],
  "difficulty_rating": 4,
  "priority": 1,
  "tags": ["health", "sleep"]
}
```

### GET /goals/{id}
Get goal with progress history.

### PUT /goals/{id}
Update goal.

### DELETE /goals/{id}
Delete goal.

### POST /goals/{id}/progress
Add progress entry.

### GET /goals/{id}/progress
List progress (paginated).

### PUT /goals/progress/{id}
Update progress entry.

### GET /goals/tasks
List tasks (paginated, filters: status, category, priority, dates, goal_id).

### POST /goals/tasks
Create task.

### PUT /goals/tasks/{id}
Update task.

### DELETE /goals/tasks/{id}
Delete task.

### GET /goals/focus-sessions
List focus sessions (paginated, filters).

### POST /goals/focus-sessions
Create focus session.

### PUT /goals/focus-sessions/{id}
Update focus session.

### POST /goals/focus-sessions/{id}/start
Start session.

### POST /goals/focus-sessions/{id}/complete
Complete session.

---

## Digital Activity Endpoints

### POST /digital/activities
Create single activity (usually from extension batch).

### POST /digital/activities/batch
Batch create activities (extension sync).

**Request**:
```json
{
  "activities": [
    {
      "session_id": "sess_abc123",
      "source": "browser_extension",
      "url": "https://github.com/user/repo",
      "domain": "github.com",
      "subdomain": null,
      "title": "Repository",
      "category": "work",
      "start_time": "2024-01-15T10:00:00Z",
      "end_time": "2024-01-15T11:30:00Z",
      "duration_seconds": 5400,
      "active_seconds": 4800,
      "idle_seconds": 600,
      "tab_switches": 5,
      "scroll_count": 50,
      "click_count": 20,
      "keystroke_count": 1000
    }
  ]
}
```

### GET /digital/activities
List activities (paginated, filters: category, domain, date range, session_id).

### GET /digital/activities/summary/daily
Daily summaries for date range.

**Query**: `start_date`, `end_date` (required)

### GET /digital/activities/summary/weekly
Weekly summaries for week range.

**Query**: `week_start_from`, `week_start_to` (required)

### GET /digital/activities/today
Today's real-time stats.

### POST /digital/classifications
Create website classification.

### GET /digital/classifications
List user's classifications.

### PUT /digital/classifications/{id}
Update classification.

### DELETE /digital/classifications/{id}
Delete classification.

### POST /digital/thresholds
Create wellbeing threshold.

### GET /digital/thresholds
List thresholds.

### PUT /digital/thresholds/{id}
Update threshold.

### DELETE /digital/thresholds/{id}
Delete threshold.

---

## Physical Health Endpoints

### Sleep

#### POST /physical/sleep
Create sleep record.

#### GET /physical/sleep
List sleep records (paginated, filters: date range, source, quality).

#### GET /physical/sleep/today
Today's sleep record.

#### PUT /physical/sleep/{id}
Update sleep record.

#### DELETE /physical/sleep/{id}
Delete sleep record.

### Nutrition

#### POST /physical/nutrition
Create nutrition record.

#### GET /physical/nutrition
List records (paginated, filters: date range, meal_type, source).

#### GET /physical/nutrition/today
Today's meals.

#### GET /physical/nutrition/summary/daily
Daily summaries for date range.

#### PUT /physical/nutrition/{id}
Update record.

#### DELETE /physical/nutrition/{id}
Delete record.

### Physical Activity

#### POST /physical/activity
Create activity record.

#### GET /physical/activity
List records (paginated, filters).

#### GET /physical/activity/summary/daily
Daily summaries for date range.

#### PUT /physical/activity/{id}
Update record.

#### DELETE /physical/activity/{id}
Delete record.

### Hydration

#### POST /physical/hydration
Create hydration record.

#### GET /physical/hydration
List records (paginated, filters).

#### GET /physical/hydration/today
Today's hydration.

#### GET /physical/hydration/summary/daily
Daily summaries for date range.

#### PUT /physical/hydration/{id}
Update record.

#### DELETE /physical/hydration/{id}
Delete record.

### Combined

#### GET /physical/today/summary
Today's complete health snapshot.

---

## AI Intelligence Endpoints

### Observations

#### GET /ai/observations
List observations (paginated, filters: type, severity, read status, date range).

#### GET /ai/observations/unread-count
Get unread count.

#### PUT /ai/observations/{id}/read
Mark as read.

#### PUT /ai/observations/{id}/dismiss
Dismiss observation.

#### PUT /ai/observations/{id}/feedback
Provide feedback (helpful, not_helpful, inaccurate, already_known).

### Patterns

#### GET /ai/patterns
List detected patterns (paginated, filters).

#### PUT /ai/patterns/{id}/acknowledge
Acknowledge pattern.

### Recommendations

#### GET /ai/recommendations
List recommendations (paginated, filters).

#### GET /ai/recommendations/pending
Get pending recommendations.

#### PUT /ai/recommendations/{id}/accept
Accept recommendation.

#### PUT /ai/recommendations/{id}/decline
Decline (with optional reason).

#### PUT /ai/recommendations/{id}/complete
Mark complete.

### Effectiveness

#### POST /ai/recommendations/{id}/effectiveness
Record effectiveness evaluation.

#### GET /ai/recommendations/{id}/effectiveness
Get effectiveness history.

### Weekly Reports

#### GET /ai/reports/weekly
List reports (paginated, filters).

#### GET /ai/reports/weekly/latest
Get latest report.

#### GET /ai/reports/weekly/{week_start}
Get report for specific week.

#### PUT /ai/reports/weekly/{id}/read
Mark as read.

### Notifications

#### GET /ai/notifications
List notifications (paginated, filters).

#### GET /ai/notifications/unread-count
Get unread count.

#### PUT /ai/notifications/{id}/read
Mark read.

#### PUT /ai/notifications/{id}/dismiss
Dismiss.

#### PUT /ai/notifications/{id}/snooze
Snooze (minutes parameter).

### Push Subscriptions

#### POST /ai/push-subscriptions
Register push subscription.

#### GET /ai/push-subscriptions
List subscriptions.

#### DELETE /ai/push-subscriptions/{id}
Remove subscription.

---

## Knowledge Base Endpoints

### Articles

#### GET /knowledge/articles
List articles (paginated, filters: category, subcategory, tag, evidence_quality, featured, difficulty, search).

#### GET /knowledge/articles/featured
Get featured articles (limit parameter).

#### GET /knowledge/articles/{id}
Get article by ID (increments view count).

#### GET /knowledge/articles/slug/{slug}
Get article by slug.

#### POST /knowledge/articles/{id}/interact
Record interaction.

**Request**:
```json
{
  "interaction_type": "view",
  "time_spent_seconds": 120,
  "scroll_percentage": 75,
  "completed": true,
  "rating": 5,
  "feedback": "Very helpful!"
}
```

#### GET /knowledge/articles/{id}/interactions
Get user's interactions with article.

### Personalized Recommendations

#### GET /knowledge/recommendations
Get personalized recommendations (paginated, filters).

#### PUT /knowledge/recommendations/{id}/read
Mark as read.

#### PUT /knowledge/recommendations/{id}/dismiss
Dismiss.

### Weekly Surveys

#### POST /knowledge/surveys/weekly
Submit weekly survey.

#### GET /knowledge/surveys/weekly
List surveys (paginated, filters).

#### GET /knowledge/surveys/weekly/latest
Get latest survey.

#### GET /knowledge/surveys/weekly/{week_start}
Get survey for specific week.

### Survey Templates (Admin)

#### GET /knowledge/survey-templates
List templates (paginated, admin only).

#### GET /knowledge/survey-templates/active
Get active template.

### Evidence Sources

#### GET /knowledge/evidence-sources
List sources (paginated, filters).

---

## Notification Preferences

### GET /notifications/preferences
Get user's notification preferences.

### PUT /notifications/preferences
Update preferences.

**Request**:
```json
{
  "enabled": true,
  "channels": ["in_app", "push"],
  "quiet_hours": {"start": "22:00", "end": "07:00"},
  "frequency_limits": {"max_per_hour": 3, "max_per_day": 10},
  "categories": {
    "nudges": true,
    "reminders": true,
    "achievements": true,
    "warnings": true,
    "insights": true,
    "weekly_reports": true,
    "goal_deadlines": true
  }
}
```

### GET /notifications/vapid-public-key
Get VAPID public key for push.

### POST /notifications/test
Send test notification.

### GET /notifications/stats
Get notification statistics (period days parameter).

---

## Health Check

### GET /health
Service health status.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## Rate Limits

| Endpoint Category | Limit |
|-------------------|-------|
| Authentication | 10/min |
| Data Read | 100/min |
| Data Write | 30/min |
| AI Generation | 10/min |
| Batch Operations | 5/min |
| File Upload | 5/min |

Headers returned:
- `X-RateLimit-Limit`: Max requests
- `X-RateLimit-Remaining`: Remaining in window
- `X-RateLimit-Reset`: Unix timestamp

---

## Webhooks

### Notification Events
Configure webhook URLs in settings to receive real-time events.

**Events**:
- `notification.created`
- `notification.read`
- `goal.achieved`
- `threshold.crossed`
- `report.generated`
- `recommendation.created`

**Payload**:
```json
{
  "event": "goal.achieved",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "uuid",
  "data": { "goal_id": "uuid", "title": "10k steps" }
}
```

---

## SDKs & Client Libraries

### JavaScript/TypeScript
```bash
npm install @knowthyself/sdk
```

```typescript
import { KnowThyself } from '@knowthyself/sdk';

const client = new KnowThyself({ 
  baseUrl: 'https://api.knowthyself.app',
  accessToken: '...'
});

const goals = await client.goals.list({ status: 'active' });
const report = await client.reports.getLatest();
```

### Python
```bash
pip install knowthyself-sdk
```

```python
from knowthyself import KnowThyself

client = KnowThyself(base_url="https://api.knowthyself.app", token="...")
goals = client.goals.list(status="active")
```

---

## Versioning

- URL versioning: `/api/v1/`
- Header: `Accept: application/vnd.knowthyself.v1+json`
- Deprecation notice: 6 months advance
- Sunset header on deprecated endpoints

---

## Changelog

### v1.0.0 (2024-11-24)
- Initial release
- Full CRUD for all entities
- AI intelligence endpoints
- Browser extension sync
- Knowledge base
- Weekly reports
- Push notifications