# Know Thyself - Architecture Document

## Overview

Know Thyself is a personal intelligence platform that combines digital life tracking with physical/lifestyle intelligence into one unified system. The architecture follows a modern, scalable, and privacy-first approach.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Web App        │  Browser Ext.    │   Mobile App (Future)    │
│   (Next.js 14)   │  (Manifest V3)   │   (React Native)         │
└────────┬─────────┴────────┬─────────┴───────────┬──────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                              │
│                    (FastAPI / Nginx)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Auth Service  │ │  Core API       │ │  AI Service     │
│   (JWT/OAuth)   │ │  (FastAPI)      │ │  (Nemotron 3)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
├──────────────────────┬──────────────────────┬───────────────────┤
│  PostgreSQL + pgvector│     Redis          │   Object Storage  │
│  (Primary + Vector)   │  (Cache/Queue)     │   (Files/Images)  │
└──────────────────────┴──────────────────────┴───────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKGROUND WORKERS                            │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Aggregation │  AI Analysis │ Notifications│  Sync/Integrations │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Custom Design System
- **Animations**: Framer Motion
- **Charts**: Recharts
- **State**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Auth**: JWT (python-jose) + bcrypt

### Database
- **Primary**: PostgreSQL 15+
- **Vector**: pgvector extension
- **Cache/Queue**: Redis 7+
- **Search**: pgvector + GIN indexes

### AI/ML
- **LLM**: NVIDIA Nemotron 3 Ultra (via API)
- **Embeddings**: NV-EmbedQA-E5-V5
- **Vector Search**: pgvector (cosine similarity)
- **RAG**: Custom retrieval-augmented generation

### Infrastructure
- **Container**: Docker + Docker Compose
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry + Prometheus + Grafana
- **Logging**: Structlog (JSON)

## Database Schema Overview

### Core Entities

1. **Users & Profiles**
   - `users` - Authentication & authorization
   - `user_profiles` - Extended lifestyle profile
   - `health_history` - Medical conditions
   - `consent_records` - GDPR/Privacy compliance
   - `audit_logs` - Security audit trail

2. **Goals & Tasks**
   - `goals` - User-defined targets
   - `goal_progress` - Daily progress tracking
   - `tasks` - Actionable items
   - `focus_sessions` - Pomodoro/deep work sessions

3. **Digital Activity**
   - `digital_activities` - Raw browser events
   - `website_classifications` - User-defined categorization
   - `daily/weekly_digital_summaries` - Pre-aggregated analytics
   - `digital_wellbeing_thresholds` - Nudge triggers

4. **Physical Health**
   - `sleep_records` - Sleep tracking
   - `nutrition_records` - Food logging
   - `physical_activities` - Exercise logging
   - `hydration_records` - Water intake
   - Daily/weekly summary tables for each

5. **AI Intelligence**
   - `ai_observations` - Pattern detections
   - `detected_patterns` - Cross-domain correlations
   - `recommendations` - Personalized suggestions
   - `recommendation_effectiveness` - Outcome tracking
   - `weekly_reports` - Generated reports
   - `notifications` - Nudges & alerts
   - `push_subscriptions` - Web Push API

6. **Knowledge Base**
   - `knowledge_articles` - Evidence-based content
   - `evidence_sources` - Structured citations
   - `user_knowledge_interactions` - Engagement tracking
   - `personalized_knowledge_recommendations` - AI-curated
   - `weekly_surveys` - Lifestyle assessments
   - `survey_templates` - Conditional questionnaires

## API Design

### RESTful Conventions
- Resource-oriented URLs
- Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Consistent response envelopes
- Cursor-based pagination
- OpenAPI 3.0 specification

### Authentication
- JWT Access Tokens (15min) + Refresh Tokens (30 days)
- HttpOnly Secure Cookies option
- Role-based access (user, admin, researcher)
- Device/session management

### Rate Limiting
- 100 req/min per IP (configurable)
- Per-endpoint limits for expensive operations
- Webhook rate limits for integrations

## AI Architecture

### RAG Pipeline
```
User Query + Context
       │
       ▼
Context Assembly (User Profile + History + Goals)
       │
       ▼
Vector Search (pgvector) → Knowledge Base
       │
       ▼
Prompt Construction (System + Context + Query)
       │
       ▼
Nemotron 3 Ultra (Structured Output)
       │
       ▼
Response Validation → Structured JSON
```

### AI Capabilities
1. **Pattern Detection** - Cross-domain correlation analysis
2. **Recommendation Generation** - Personalized, evidence-based
3. **Weekly Report Generation** - Comprehensive intelligence
4. **Knowledge Curation** - Personalized content recommendations
5. **Effectiveness Evaluation** - Outcome measurement

### Privacy-First AI
- No user data sent to external training
- Local context assembly
- Structured, validated outputs
- Audit trail for all AI decisions

## Background Processing

### Celery Workers
1. **Aggregation Worker** - Hourly/daily/weekly rollups
2. **AI Worker** - Pattern detection, recommendations, reports
3. **Notification Worker** - Threshold checks, push/email delivery
4. **Integration Worker** - Third-party sync (Apple Health, Fitbit, etc.)
5. **Maintenance Worker** - Cleanup, backups, verification

### Scheduled Jobs (Celery Beat)
- Hourly: Digital activity aggregation
- Daily: Physical health summaries
- Weekly: AI reports, pattern detection
- 5min: Threshold checking (nudges)
- 1min: Notification delivery

## Security & Privacy

### Data Protection
- Encryption at rest (AES-256)
- TLS 1.3 in transit
- Field-level encryption for sensitive data
- Regular key rotation

### Access Control
- Row-level security (RLS) in PostgreSQL
- User-scoped queries only
- Admin actions audit logged
- Device/session revocation

### Privacy Compliance
- GDPR/CCPA ready
- Explicit consent management
- Data portability (export)
- Right to deletion
- Minimal data collection
- No third-party tracking

## Scalability Considerations

### Horizontal Scaling
- Stateless API pods
- Redis Cluster for sessions/cache
- Read replicas for analytics
- pgvector partitioning by user

### Performance Optimization
- Materialized views for dashboards
- Pre-aggregated summary tables
- Vector index tuning (HNSW/IVFFlat)
- CDN for static assets

### Monitoring
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Queue depths
- AI token usage/costs
- Database query performance

## Deployment Architecture

### Development
```yaml
# docker-compose.yml
services:
  postgres: ...
  redis: ...
  backend: ...
  frontend: ...
  celery-worker: ...
  celery-beat: ...
```

### Production (Kubernetes)
- Namespace separation
- Helm charts for each service
- Ingress with TLS termination
- Horizontal Pod Autoscaler
- Pod Disruption Budgets
- Network Policies

## Future Extensibility

### Plugin Architecture
- Custom integrations via webhooks
- User-defined data sources
- Custom AI prompts
- Export/import of configurations

### Mobile Support
- React Native app
- Offline-first sync
- Background tracking
- Push notifications

### Research Platform
- Anonymized dataset export
- Cohort analysis tools
- Longitudinal study support
- IRB compliance features