# Know Thyself - Dependencies & Integration List

## Backend Dependencies (Python)

### Core Framework
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| fastapi | 0.109.0 | Web framework | MIT |
| uvicorn[standard] | 0.27.0 | ASGI server | BSD-3 |
| gunicorn | 21.2.0 | WSGI HTTP server | MIT |
| pydantic | 2.5.3 | Data validation | MIT |
| pydantic-settings | 2.1.0 | Settings management | MIT |

### Database
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| sqlalchemy | 2.0.25 | ORM | MIT |
| alembic | 1.13.1 | Migrations | MIT |
| asyncpg | 0.29.0 | Async PostgreSQL driver | Apache-2.0 |
| psycopg2-binary | 2.9.9 | Sync PostgreSQL driver | LGPL-3.0 |
| pgvector | 0.2.3 | Vector similarity search | PostgreSQL |

### Authentication & Security
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| python-jose[cryptography] | 3.3.0 | JWT handling | MIT |
| passlib[bcrypt] | 1.7.4 | Password hashing | BSD |
| python-dotenv | 1.0.0 | Environment variables | BSD |
| cryptography | 41.0.7 | Encryption | Apache-2.0/BSD |

### AI & ML
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| openai | 1.3.7 | Nemotron API client | Apache-2.0 |
| numpy | 1.26.3 | Numerical computing | BSD-3 |
| scikit-learn | 1.3.2 | ML utilities | BSD-3 |

### Background Processing
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| celery | 5.3.6 | Distributed task queue | BSD-3 |
| redis | 5.0.1 | Redis client | MIT |
| flower | 2.0.1 | Celery monitoring | BSD-3 |

### HTTP & Data
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| httpx | 0.26.0 | Async HTTP client | MIT |
| aiohttp | 3.9.1 | Async HTTP server/client | Apache-2.0 |
| pandas | 2.1.4 | Data manipulation | BSD-3 |
| python-dateutil | 2.8.2 | Date utilities | Apache-2.0 |

### Monitoring & Testing
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| structlog | 24.1.0 | Structured logging | Apache-2.0/MIT |
| sentry-sdk | 1.39.1 | Error tracking | BSD-3 |
| pytest | 7.4.4 | Testing | MIT |
| pytest-asyncio | 0.23.3 | Async testing | Apache-2.0 |
| pytest-cov | 4.1.0 | Coverage reporting | MIT |

### Utilities
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| python-slugify | 8.0.1 | URL slugs | MIT |
| email-validator | 2.1.0.post1 | Email validation | MIT |

---

## Frontend Dependencies (Node.js)

### Core Framework
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| next | 14.2.0 | React framework | MIT |
| react | 18.3.0 | UI library | MIT |
| react-dom | 18.3.0 | DOM renderer | MIT |

### State & Data
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| zustand | 4.5.0 | State management | MIT |
| @tanstack/react-query | 5.28.0 | Server state | MIT |
| @tanstack/react-query-devtools | 5.28.0 | DevTools | MIT |
| axios | 1.7.0 | HTTP client | MIT |

### Forms & Validation
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| react-hook-form | 7.51.0 | Form handling | MIT |
| @hookform/resolvers | 3.3.4 | Validation resolvers | MIT |
| zod | 3.23.0 | Schema validation | MIT |

### UI & Animation
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| framer-motion | 11.0.0 | Animations | MIT |
| recharts | 2.12.0 | Charts | MIT |
| lucide-react | 0.363.0 | Icons | ISC |
| clsx | 2.1.0 | Class names | MIT |
| tailwind-merge | 2.2.0 | Tailwind merging | MIT |

### Utilities
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| date-fns | 3.6.0 | Date formatting | MIT |
| react-hot-toast | 2.4.1 | Toasts | MIT |
| socket.io-client | 4.7.0 | WebSockets | MIT |
| web-push | 3.6.0 | Push notifications | Apache-2.0 |

### Development
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| typescript | 5.4.0 | Type checking | Apache-2.0 |
| tailwindcss | 3.4.0 | CSS framework | MIT |
| postcss | 8.4.38 | CSS processing | MIT |
| autoprefixer | 10.4.19 | CSS vendor prefixes | MIT |
| eslint | 8.57.0 | Linting | MIT |
| eslint-config-next | 14.2.0 | Next.js ESLint config | MIT |
| @typescript-eslint/eslint-plugin | 7.0.0 | TypeScript ESLint | MIT |
| @typescript-eslint/parser | 7.0.0 | TypeScript parser | MIT |

---

## External API Integrations

### Required for Production

| Service | Purpose | API Type | Auth | Cost Estimate |
|---------|---------|----------|------|---------------|
| **NVIDIA Nemotron 3 Ultra** | AI LLM + Embeddings | REST | API Key | $200-1000/mo |
| **PostgreSQL** | Primary Database | SQL | User/Pass | $200-500/mo (managed) |
| **Redis** | Cache, Queue, Sessions | TCP | Password | $100-200/mo (managed) |
| **Sentry** | Error Tracking | REST | DSN | $100-300/mo |
| **Email Service** (SendGrid/Mailgun) | Transactional Email | REST | API Key | $50-200/mo |
| **Push Notifications** (Web Push) | Browser Push | VAPID | Keys | Free (self-hosted) |

### Health Integrations (Optional but Recommended)

| Service | Data Types | API Type | Auth | Status |
|---------|------------|----------|------|--------|
| **Apple HealthKit** | Steps, Sleep, Heart Rate, Workouts, Nutrition | Native iOS | User Consent | Planned |
| **Google Fit** | Steps, Sleep, Heart Rate, Activity | REST | OAuth 2.0 | Planned |
| **Fitbit API** | Steps, Sleep, Heart Rate, Weight, HRV | REST | OAuth 2.0 | Planned |
| **Oura Ring API** | Sleep, Readiness, Activity, HRV | REST | Personal Access Token | Planned |
| **Garmin Connect** | Advanced Training Metrics | REST | OAuth 2.0 | Planned |
| **Strava** | Running, Cycling, Swimming | REST | OAuth 2.0 | Planned |
| **Cronometer** | Detailed Nutrition | REST | API Key | Future |
| **MyFitnessPal** | Nutrition Logging | REST | OAuth 2.0 | Future |

### Knowledge Base Sources

| Source | Access Method | Update Frequency | Cost |
|--------|---------------|------------------|------|
| PubMed/MEDLINE | E-utilities API | Daily | Free |
| ClinicalTrials.gov | API | Daily | Free |
| Cochrane Library | RSS/API | Weekly | Subscription |
| USPSTF Guidelines | Website/RSS | As Published | Free |
| NICE Guidelines | Website/API | As Published | Free |
| WHO Guidelines | Website | As Published | Free |
| CDC/NIH | Website/API | As Published | Free |
| Top Medical Journals | RSS/Email | Real-time | Subscription |

---

## Infrastructure Requirements

### Development
```yaml
# docker-compose.yml minimum
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: knowthyself
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redisdata:/data]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:<PASSWORD>@postgres:5432/knowthyself
      - REDIS_URL=redis://redis:6379/0
      - NVIDIA_API_KEY=${NVIDIA_API_KEY}
    depends_on: [postgres, redis]
    volumes: [./backend:/app]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes: [./frontend:/app, /app/node_modules]

  celery-worker:
    build: ./backend
    command: celery -A app.services.background_tasks worker --loglevel=info
    depends_on: [redis, postgres]
    volumes: [./backend:/app]

  celery-beat:
    build: ./backend
    command: celery -A app.services.background_tasks beat --loglevel=info
    depends_on: [redis]
    volumes: [./backend:/app]

volumes:
  pgdata:
  redisdata:
```

### Production (Kubernetes)

```yaml
# Key resource requirements
resources:
  backend:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
    replicas: 3-10 (HPA)
  
  frontend:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "500m"
    replicas: 3-20 (HPA)
  
  celery-worker:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
    replicas: 2-20 (HPA, queue-depth based)
  
  postgres:
    # Use managed service (RDS, Cloud SQL)
    instance: db.r6g.xlarge (4 vCPU, 32GB)
    storage: 500GB gp3
    backup: 30 days retention
  
  redis:
    # Use managed service (ElastiCache, Memorystore)
    node: cache.r6g.xlarge
    cluster: 3 shards
```

---

## Environment Variables

### Backend (.env)
```bash
# Application
APP_NAME="Know Thyself"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=true
SECRET_KEY="generate-with-openssl-rand-base64-32"
API_V1_STR="/api/v1"

# Database
POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_DB="knowthyself"

# Redis
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=""

# AI
NVIDIA_API_KEY="your-nvidia-api-key"
NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL="nvidia/nemotron-3-ultra"
EMBEDDING_MODEL="nvidia/nv-embedqa-e5-v5"

# Auth
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=30
ALGORITHM="HS256"

# CORS
CORS_ORIGINS='["http://localhost:3000","http://127.0.0.1:3000"]'

# Email (Optional)
SMTP_HOST="smtp.sendgrid.net"
SMTP_PORT=587
SMTP_USER="apikey"
SMTP_PASSWORD="your-sendgrid-key"
EMAILS_FROM_EMAIL="noreply@knowthyself.app"
EMAILS_FROM_NAME="Know Thyself"

# Push Notifications
VAPID_PUBLIC_KEY="generate-with-web-push-cli"
VAPID_PRIVATE_KEY="generate-with-web-push-cli"
VAPID_CLAIMS_SUB="mailto:admin@knowthyself.app"

# Browser Extension
EXTENSION_ID="your-chrome-extension-id"
EXTENSION_ORIGIN="chrome-extension://"

# File Upload
UPLOAD_DIR="./uploads"
MAX_UPLOAD_SIZE=10485760

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"

# Sentry (Optional)
SENTRY_DSN=""
SENTRY_TRACES_SAMPLE_RATE=0.1

# Feature Flags
ENABLE_BROWSER_EXTENSION=true
ENABLE_PUSH_NOTIFICATIONS=true
ENABLE_WEEKLY_REPORTS=true
ENABLE_AI_ANALYSIS=true
ENABLE_KNOWLEDGE_BASE=true
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="Know Thyself"
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_VAPID_PUBLIC_KEY=your-vapid-public-key
```

---

## Browser Extension Permissions

```json
{
  "permissions": [
    "tabs",
    "activeTab",
    "storage",
    "alarms",
    "idle",
    "notifications",
    "scripting"
  ],
  "host_permissions": ["<all_urls>"],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "run_at": "document_idle",
    "all_frames": false
  }],
  "action": {
    "default_popup": "popup.html",
    "default_title": "Know Thyself"
  }
}
```

---

## Development Setup Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # Edit with your values
npm run dev
```

### Browser Extension
```bash
cd browser-extension
# Load unpacked in Chrome: chrome://extensions/
# Select browser-extension folder
```

### Celery Workers
```bash
cd backend
celery -A app.services.background_tasks worker --loglevel=info
celery -A app.services.background_tasks beat --loglevel=info
```

---

## Testing Commands

```bash
# Backend tests
cd backend
pytest                    # All tests
pytest -v                 # Verbose
pytest --cov=app          # With coverage
pytest tests/test_auth.py # Specific module

# Frontend tests
cd frontend
npm run test              # Jest
npm run test:watch        # Watch mode
npm run test:coverage     # Coverage
npm run lint              # ESLint
npm run type-check        # TypeScript

# E2E tests
cd frontend
npm run test:e2e          # Playwright
```

---

## Deployment Checklist

### Pre-deployment
- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates configured
- [ ] DNS records pointing to load balancer
- [ ] Sentry DSN configured
- [ ] VAPID keys generated
- [ ] Email service tested
- [ ] Backup strategy verified
- [ ] Monitoring alerts configured
- [ ] Rate limits tuned

### Post-deployment
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Authentication flow working
- [ ] Browser extension syncing
- [ ] Push notifications delivering
- [ ] AI responses generating
- [ ] Weekly reports generating
- [ ] Data exports working
- [ ] Error rate < 1%
- [ ] Latency p95 < 200ms