# Step 7 — Deployment & Production Design

> **Scope:** How the system moves from local build to hosted, reliable, demo-ready product.  
> **Status:** 🔒 DESIGNED  
> **Last updated:** 2026-02-10  

---

## 7.1 Deployment Philosophy

This is a **personal, industry-style product** — not a hyperscale enterprise system. The design is intentionally scoped for a solo developer who wants to demonstrate production-grade thinking.

### Design Goals

| Goal | Meaning |
|------|---------|
| **Simple first** | One deployable system before microservices |
| **Predictable behavior** | Same code, same config → same result |
| **Easy redeployments** | Push to main → auto-deploy |
| **Clear failure modes** | Fail loudly with structured errors, never silently |

### Key Principle

> **One deployable system first, modular later.**

Premature microservice decomposition is a bigger risk than a well-structured monolith. The backend is designed as a modular monolith that can be split when — and only when — there's a reason to.

---

## 7.2 Deployment Architecture (MVP)

```
┌─────────────────────────────────┐
│         Browser (User)          │
└────────────┬────────────────────┘
             │ HTTPS
             ▼
┌─────────────────────────────────┐
│   Frontend (Next.js)            │
│   Hosted: Vercel / Netlify      │
│   CDN-backed, globally cached   │
└────────────┬────────────────────┘
             │ HTTPS (API calls)
             ▼
┌─────────────────────────────────┐
│   Backend API (FastAPI)         │
│   Hosted: AWS / Render / Railway│
│   Single service, Docker-based  │
│                                 │
│   ┌───────────────────────────┐ │
│   │ Detection & Scoring Engine│ │
│   │ (Internal module)         │ │
│   └───────────────────────────┘ │
└────────────┬────────────────────┘
             │ asyncpg (TCP/5432)
             ▼
┌─────────────────────────────────┐
│   PostgreSQL Database           │
│   Hosted: AWS RDS               │
│   Persistent, independent       │
└─────────────────────────────────┘
```

### MVP Deployment Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| Frontend & Backend | **Separate deployments** | Independent scaling, different hosting optimisations |
| ML Detection | **Inside backend service** | No separate ML serving needed at MVP; reduces infra complexity |
| Database | **Single instance** | One PostgreSQL on AWS RDS; read replicas added later if needed |
| Message queue | **Not needed yet** | Synchronous request-response is sufficient at demo scale |

---

## 7.3 Hosting Strategy

### Frontend Hosting

| Option | Recommended | Why |
|--------|:-----------:|-----|
| **Vercel** | ✅ Primary | Built for Next.js; zero-config deploy; global CDN; free tier |
| **Netlify** | ✅ Alternative | Similar capabilities; excellent for static + SSR |
| AWS Amplify | ⬜ Optional | More setup; better if already invested in AWS |

**Deploy command:** `git push` → Vercel auto-deploys from `main` branch.

### Backend Hosting

| Option | Recommended | Why |
|--------|:-----------:|-----|
| **AWS (EC2 / ECS / App Runner)** | ✅ Primary | User's chosen cloud; pairs with RDS; free tier available |
| **Render** | ✅ Alternative | Simple Docker deployment; automatic restarts; free tier |
| **Railway** | ✅ Alternative | One-click PostgreSQL + backend; developer-friendly |
| **Fly.io** | ⬜ Optional | Edge deployment; more complex setup |

**Deploy method:** Docker container → push to registry → deploy service.

### Database Hosting

| Option | Recommended | Why |
|--------|:-----------:|-----|
| **AWS RDS (PostgreSQL)** | ✅ Primary | User's chosen deployment target; managed backups; Multi-AZ available |
| Render Managed PostgreSQL | ✅ Alternative | Simpler if backend is also on Render |
| Railway PostgreSQL | ✅ Alternative | One-click setup |

> **Design Rule:** Database must persist independently of backend restarts. The backend is stateless; the database is the source of truth.

---

## 7.4 Environment Separation

Three logical environments, same codebase:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    LOCAL     │    │   STAGING   │    │ PRODUCTION  │
│              │    │             │    │             │
│  Developer   │    │  Demo &     │    │  Public     │
│  machine     │    │  testing    │    │  showcase   │
│              │    │             │    │             │
│  PostgreSQL  │    │  Cloud DB   │    │  AWS RDS    │
│  (local)     │    │  (free)     │    │  (managed)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                  Same codebase
                  Different .env
```

### What Changes Between Environments

| Setting | Local | Staging | Production |
|---------|-------|---------|------------|
| `DATABASE_URL` | `localhost:5432` | Cloud DB URL | RDS endpoint |
| `CORS_ORIGINS` | `localhost:3000` | Staging frontend URL | Production URL |
| `DEBUG` | `true` | `true` | `false` |
| `LOG_FORMAT` | `console` | `json` | `json` |
| `WORKERS` | `1` | `2` | `4` |
| `SECRET_KEY` | Dev key | Staging key | **Strong random key** |

### What NEVER Changes

- Application code
- Database schema
- API contracts
- Detection logic

---

## 7.5 Configuration Management

> **Design Rule:** Changing behavior should not require redeploying code.

### All Configuration Is Externalised

Every tunable parameter lives in environment variables, not in code:

| Category | Config Keys | Example Values |
|----------|------------|----------------|
| **Thresholds** | `RISK_THRESHOLD_HIGH`, `RISK_THRESHOLD_MEDIUM` | `0.80`, `0.50` |
| **Weights** | Detector weights (future: env vars) | `0.25`, `0.35`, `0.40` |
| **Severity cutoffs** | Mapped from thresholds | Derived from above |
| **Database** | `DATABASE_URL`, `DATABASE_POOL_SIZE` | Connection string |
| **Rate limits** | `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS` | `100`, `60` |
| **Logging** | `LOG_LEVEL`, `LOG_FORMAT` | `INFO`, `json` |

### Configuration Hierarchy

```
1. Environment variables (highest priority — set on host)
2. .env file (local development override)
3. Code defaults (fallback — defined in config.py)
```

### Operational Examples

```bash
# Raise alert threshold without redeploying:
export RISK_THRESHOLD_HIGH=0.85
# → Restart backend → fewer CRITICAL alerts

# Increase connection pool for higher load:
export DATABASE_POOL_SIZE=20
# → Restart backend → more concurrent DB connections

# Switch to structured logging for production:
export LOG_FORMAT=json
# → Restart backend → logs parseable by CloudWatch/Datadog
```

---

## 7.6 Scalability Design (Future-Ready)

> **Design Principle:** Scale when needed, not prematurely.

The system is designed to scale but does not require it at MVP.

### Horizontal Scaling (Backend)

The backend is **stateless** — all state lives in PostgreSQL. This means:

```
                    ┌──────────────────┐
                    │  Load Balancer   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Backend  │   │ Backend  │   │ Backend  │
        │ Instance │   │ Instance │   │ Instance │
        │    #1    │   │    #2    │   │    #3    │
        └────┬─────┘   └────┬─────┘   └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │   (shared)       │
                    └──────────────────┘
```

- Add more backend instances behind a load balancer
- Connection pool settings prevent database overload
- `pool_pre_ping` handles instance restarts gracefully

### Vertical Scaling

For ML-heavy workloads, increase instance CPU/RAM rather than adding instances:

| Workload | Scaling Strategy |
|----------|-----------------|
| API serving | Horizontal (more instances) |
| ML detection | Vertical (bigger instance) |
| Database queries | Read replicas (later) |

### Future Modularisation Path

When the system outgrows a monolith:

```
Current (MVP):                    Future (if needed):
┌──────────────────┐              ┌──────────────────┐
│  Single Backend  │              │   API Service    │
│  ├── API         │              └────────┬─────────┘
│  ├── Detection   │                       │
│  ├── Scoring     │              ┌────────▼─────────┐
│  └── Analytics   │              │ Detection Service│
└──────────────────┘              └────────┬─────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │Analytics Service │
                                  └──────────────────┘
```

**Split trigger:** When detection latency impacts API response times, extract the detection engine into its own service with an async queue.

---

## 7.7 Performance & Latency Expectations

### Targets (Demo-Appropriate)

| Operation | Target | Acceptable |
|-----------|--------|------------|
| API response (single resource) | < 200 ms | < 500 ms |
| Dashboard initial load | < 1 second | < 2 seconds |
| Alert list (paginated) | < 150 ms | < 300 ms |
| Detection scoring (per transaction) | < 1 second | < 3 seconds |
| Investigation context load | < 500 ms | < 1 second |

### Optimisation Strategies

| Strategy | Where Applied | Impact |
|----------|--------------|--------|
| **Pre-aggregated metrics** | `metrics_snapshots` table | Dashboard loads from snapshots, not live queries |
| **Paginated queries** | Alert lists, feedback history | Bounded response sizes |
| **Database indexes** | All query-heavy columns | Sub-100ms query execution |
| **Connection pooling** | `asyncpg` pool (10+20) | No connection creation overhead per request |
| **Async I/O** | FastAPI + asyncpg throughout | Non-blocking request handling |

### What We Do NOT Do (By Design)

| Anti-Pattern | Why We Avoid It |
|-------------|----------------|
| Redis caching | Adds infra complexity; DB indexes are sufficient at demo scale |
| CDN for API | API is behind auth; CDN caching inappropriate |
| Materialized views | PostgreSQL standard views + indexes are sufficient |
| Background workers | Synchronous detection is fast enough at MVP volume |

---

## 7.8 Reliability & Failure Handling

> **Design Rule:** A system that fails loudly is better than one that fails silently.

### Failure Scenarios & Responses

| Failure | Detection | Response | User Experience |
|---------|-----------|----------|-----------------|
| **Backend crash** | Health check fails | Container auto-restarts (hosting platform) | Brief downtime; request retried |
| **Database unavailable** | Connection timeout | 503 with structured error; backend stays up | "Service temporarily unavailable" |
| **Model scoring failure** | Exception caught | Fallback: alert created with severity = "NEEDS_REVIEW" | Alert still appears; analyst reviews manually |
| **Partial data ingestion** | Validation error | 422 with field-level errors; transaction rolled back | Clear error message; no partial state |
| **Rate limit exceeded** | Middleware counter | 429 with retry-after header | "Too many requests; try again in X seconds" |

### Health Check Endpoint

```
GET /health

Response:
{
    "status": "healthy",
    "database": "connected",
    "uptime_seconds": 14523,
    "version": "1.0.0"
}
```

### Structured Error Responses

Every error returns a consistent structure:

```json
{
    "error": {
        "type": "DatabaseUnavailable",
        "message": "Cannot connect to database",
        "request_id": "req-7a3f-...",
        "timestamp": "2026-02-10T10:30:00Z"
    }
}
```

### Graceful Degradation Priority

```
Full system operational
        │
        ▼ (database slow)
Dashboard serves cached/snapshot data
        │
        ▼ (detection engine fails)
Alerts created with fallback severity
        │
        ▼ (database down)
API returns 503 with structured error
Health check returns "unhealthy"
```

---

## 7.9 Observability (Lightweight)

### What to Monitor

| Metric | Source | Why |
|--------|--------|-----|
| **API request rate** | Middleware counter | Volume baseline; detect traffic anomalies |
| **Error rate** | Middleware counter | Detect system degradation |
| **Response latency (p50, p95, p99)** | Middleware timer | Performance regression detection |
| **Alert creation volume** | Metrics snapshot | Detect detection engine anomalies |
| **Investigation resolution time** | Computed from timestamps | Operational efficiency tracking |
| **False positive rate** | Computed from feedback | Model quality signal |
| **Database connection pool** | SQLAlchemy pool stats | Resource exhaustion early warning |

### Observability Stack (MVP)

```
Application Code
      │
      ├──► Structured Logs (structlog → JSON)
      │         └──► CloudWatch Logs (AWS) / stdout (local)
      │
      ├──► In-Memory Metrics (MetricsCollector)
      │         └──► /metrics endpoint (Prometheus-compatible)
      │
      └──► Health Check (/health)
                └──► Uptime monitoring (UptimeRobot / AWS health checks)
```

### Log Structure

Every request produces a structured log entry:

```json
{
    "timestamp": "2026-02-10T10:30:00Z",
    "level": "info",
    "event": "request_completed",
    "request_id": "req-7a3f-...",
    "method": "GET",
    "path": "/api/v1/alerts",
    "status": 200,
    "duration_ms": 45,
    "user_agent": "Next.js/14"
}
```

### Why This Matters for Demos

> "Detect anomalies in the anomaly detector."

Being able to show observability in a demo proves production thinking:
- "Here's my request rate over the last hour"
- "Here's my p95 latency — consistently under 200ms"
- "Here's my false positive rate trending downward after feedback"

---

## 7.10 Security (Personal Project Level)

### What We Include

| Control | Implementation | Purpose |
|---------|---------------|---------|
| **Input validation** | Pydantic schemas on all endpoints | Reject malformed requests at the API boundary |
| **Rate limiting** | Middleware-based per-IP | Prevent abuse and accidental overload |
| **Structured errors** | Never expose stack traces in production | No internal leak in error responses |
| **Environment secrets** | All secrets via env vars; never in code | Credentials never committed to git |
| **CORS** | Whitelist specific frontend origins | Prevent unauthorized cross-origin requests |
| **Read-only demo mode** | Conceptual: demo accounts with limited writes | Safe for live demonstrations |
| **No real data** | Synthetic seed data only | No PII or sensitive financial data exposed |

### What We Exclude (For Now)

| Control | Why Not Yet |
|---------|------------|
| OAuth / SSO | Adds auth service dependency; out of scope for MVP |
| JWT auth | Planned for future; currently using API key / session |
| Complex IAM | Single-user system; role-based access not needed |
| Encryption at rest | Handled by AWS RDS; not application-level |
| Penetration testing | Not appropriate for demo project |

### Design Rule

> **Security proportional to project scope.** Demonstrate awareness of what's needed, implement what's appropriate.

---

## 7.11 Demo & Portfolio Readiness

### What the Final System Demonstrates

A live visitor or interviewer can:

| Action | What It Proves |
|--------|---------------|
| **Open dashboard** | Real-time metrics, responsive design, data visualization |
| **Browse alerts** | Paginated, filtered, sortable — production-grade UI |
| **Click into an alert** | Context auto-loads: transaction, features, detector scores |
| **Review investigation** | Full audit trail with analyst actions and timestamps |
| **See metrics** | Model performance, false positive rates, resolution times |
| **Explain any decision** | Traceability from alert → features → detectors → transaction |

### Interview-Ready Architecture Walkthrough

```
"I designed and built an end-to-end anomaly detection platform 
with three detection layers, composite risk scoring, human-in-the-loop 
feedback, and adaptive thresholds — following production-grade 
architectural principles."

Key talking points:
├── "Multi-layer detection: statistical, behavioral, ML-based"
├── "PostgreSQL on AWS RDS with async connection pooling"
├── "Every alert is fully traceable and auditable"
├── "Analyst feedback feeds back into model retraining"
├── "Configurable thresholds and weights via environment variables"
└── "Structured logging, health checks, and observability built in"
```

### GitHub README Highlights

The repository should demonstrate:

| Section | Content |
|---------|---------|
| **Architecture diagram** | System overview (frontend → API → detection → DB) |
| **Tech stack** | Next.js, FastAPI, PostgreSQL, SQLAlchemy, scikit-learn |
| **Setup instructions** | Local development in 5 commands |
| **API documentation** | Auto-generated via FastAPI `/docs` |
| **Design documents** | Steps 5, 6, 7 in `docs/` — proves systematic thinking |
| **Live demo link** | Deployed URL (Vercel + AWS) |

---

## Deployment Checklist

### Pre-Deployment

- [ ] All environment variables documented in `.env.example`
- [ ] Database migrations tested (Alembic)
- [ ] Health check endpoint working
- [ ] CORS configured for production frontend URL
- [ ] Secrets rotated from development defaults
- [ ] Synthetic seed data loaded
- [ ] Structured logging enabled (`LOG_FORMAT=json`)

### Deployment Steps

```
1. Provision AWS RDS PostgreSQL instance
2. Set DATABASE_URL to RDS endpoint
3. Build Docker image for backend
4. Deploy backend to AWS (EC2/ECS/App Runner)
5. Run database migrations (alembic upgrade head)
6. Seed database (python -m app.db.seed)
7. Deploy frontend to Vercel (git push)
8. Configure frontend API URL to point to backend
9. Verify health check: GET /health → 200
10. Smoke test: Dashboard loads, alerts display
```

### Post-Deployment Verification

- [ ] `/health` returns `{"status": "healthy"}`
- [ ] Dashboard loads in < 2 seconds
- [ ] Alert list paginates correctly
- [ ] Investigation context loads completely
- [ ] Structured logs flowing to CloudWatch / stdout
- [ ] No stack traces in error responses

---

## Architecture Summary: All Steps Aligned

```
Step 1-3: Frontend (Next.js)
    ↓ HTTPS
Step 4: Database Schema (PostgreSQL on AWS RDS)
    ↑ asyncpg
Step 5: Detection & Scoring Engine (inside backend)
    ↕ uses
Step 6: Alert & Investigation Workflows (business logic)
    ↕ served by
Step 3: API Layer (FastAPI)
    ↕ deployed via
Step 7: THIS STEP — Deployment & Production Design
```

Every design decision flows through:

```
Code (Steps 3-4) → Intelligence (Step 5) → Operations (Step 6) → Production (Step 7)
```

---

> 🔒 **STEP 7 COMPLETE**  
> The system now has a documented production architecture:  
> ✔ Hosting strategy (Vercel + AWS)  
> ✔ Deployment architecture (frontend/backend/database)  
> ✔ Environment separation (local/staging/production)  
> ✔ Configuration management (all externalised)  
> ✔ Scalability plan (horizontal + future modularisation)  
> ✔ Performance targets with optimisation strategies  
> ✔ Reliability & failure handling (graceful degradation)  
> ✔ Observability (structured logs, metrics, health checks)  
> ✔ Security (proportional to scope)  
> ✔ Demo & portfolio readiness  
> ✔ Deployment checklist  
