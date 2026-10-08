# Market Anomaly & Fraud Detection System

> Real-time, ML-powered transaction monitoring that scores every transaction for fraud risk in **under 25 ms** — and gets smarter from analyst feedback.

A full-stack fraud detection platform: a **Python / FastAPI** detection engine (the core) behind a **Next.js** analyst dashboard. Instead of brittle "flag anything over ₹X" rules, it asks a better question — *does this look normal for **this** entity?* — using three independent detection layers combined into a single composite risk score.

---

## Why

Rule-based fraud systems drown analysts in false positives (industry average **70–80%**). Fraudsters learn fixed thresholds in days, and legitimate customers get frozen. This system blends statistical rules, per-entity behavioral baselines, and an unsupervised ML model so that **when all three agree, you can trust the alert** — and every analyst decision feeds back into the model.

---

## How it works

Every transaction flows through three detectors whose scores are combined by weight and confidence into a composite **0–100** risk score.

```
Transaction
     │
     ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  STATISTICAL │  │  BEHAVIORAL  │  │   ML MODEL   │
│   (25% wt)   │  │   (35% wt)   │  │   (40% wt)   │
│ Z-scores     │  │ Spend vs own │  │ Isolation    │
│ Velocity     │  │ history, new │  │ Forest       │
│ Thresholds   │  │ dest/channel │  │ (unsupervised│
│ Time rules   │  │ frequency    │  │  anomaly)    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       └─────────────────┼─────────────────┘
                         ▼
             Composite Risk Score (0–100)
                         │
          ≥90 CRITICAL · ≥70 HIGH · ≥50 MEDIUM · <50 LOW
                         │
                   Alert raised ──▶ Analyst investigates
                         │
            Marks FRAUD / FALSE POSITIVE ──▶ feedback stored ──▶ model retrains
```

- **Statistical** — obvious outliers: large amounts, rapid-fire velocity, odd-hour (midnight–5 AM) activity, geo/device risk.
- **Behavioral** — deviation from the entity's *own* baseline: spend spikes, first-time destinations, new channels, dormant-account reactivation.
- **ML (Isolation Forest)** — multi-dimensional anomalies no single rule would catch. Unsupervised, so it needs no labelled data to start; a heuristic fallback keeps scoring alive if the model artifact is missing.

---

## Tech stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16 · React 18 · TypeScript · Tailwind CSS · TanStack Query & Table · Recharts · Radix UI |
| **API** | FastAPI (async) · Pydantic v2 · structured logging (structlog) |
| **ML / Data** | scikit-learn (Isolation Forest) · pandas · NumPy · joblib |
| **Database** | PostgreSQL · SQLAlchemy 2 (async / asyncpg) · Alembic migrations |

---

## Project structure

```
.
├── app/                    # Next.js App Router (pages, layout, mock /api routes)
├── components/             # React UI: pages, charts, tables, cards, badges
├── lib/                    # API client, React Query hooks, services, types
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app factory + routes
│   │   ├── config.py           # pydantic-settings configuration
│   │   ├── api/routes/         # dashboard, alerts, investigations, analytics, feedback, detection
│   │   ├── detection/
│   │   │   ├── engine.py           # orchestrates features → detectors → scoring
│   │   │   ├── detectors/          # statistical, behavioral, ml
│   │   │   ├── features/           # feature engineering
│   │   │   ├── scoring/            # risk scorer / normalizer
│   │   │   └── train_model.py      # train & persist the Isolation Forest artifact
│   │   ├── db/                 # models, session, repositories, seeder
│   │   └── services/           # business logic per domain
│   ├── alembic/            # database migrations
│   ├── scripts/smoke_test.py   # end-to-end API verification
│   └── models/             # trained ML artifact (fraud_detector.joblib)
└── docs/                   # step-by-step build & deployment guides
```

---

## Getting started

### Prerequisites
- **Node.js** 18+ and **Python** 3.9+
- **PostgreSQL** 14+ (local install or Docker)

### 1. Database

```bash
# Example with Docker
docker run -d --name mads-postgres \
  -e POSTGRES_USER=fraud -e POSTGRES_PASSWORD=fraud -e POSTGRES_DB=fraud_detection \
  -p 5432:5432 postgres:16
```

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env                 # then edit DATABASE_URL / SECRET_KEY
export DATABASE_URL="postgresql+asyncpg://fraud:fraud@localhost:5432/fraud_detection"

alembic upgrade head                 # create the schema (prod-safe)
python -m app.db.seed                # optional: load demo data

uvicorn app.main:app --reload --port 8000
```

API docs (when `DEBUG=true`): <http://localhost:8000/docs> · Health: <http://localhost:8000/health>

> In `development`, the app also auto-creates tables on startup. In `staging`/`production` the schema is owned by Alembic — run `alembic upgrade head` as a deploy step.

### 3. Frontend (Next.js)

```bash
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev        # http://localhost:3000
```

> **Data source:** when `NEXT_PUBLIC_API_BASE_URL` points at the FastAPI backend, the dashboard uses live data. If it's unset, the app falls back to the **mock** `app/api/*` routes so the frontend can be demoed standalone.

### 4. Train the model (optional)

```bash
cd backend
python -m app.detection.train_model --dataset data/fraud_transactions.csv
# → writes models/fraud_detector.joblib (Isolation Forest + threshold + metrics)
```

---

## Dashboard

| Page | Purpose |
|---|---|
| **Dashboard** | KPI cards, alerts-trend chart, severity breakdown, live ML scanner |
| **Alerts** | Filterable, paginated alert table with risk scores and severity badges |
| **Investigation** | Transaction details, feature deviations, history, decision buttons |
| **Analytics** | Precision / recall / F1, alert-volume trends, confusion matrix |
| **Feedback** | Resolution history — confirmed frauds vs. false positives |
| **Settings** | Alert thresholds, notifications, API key management |

---

## API overview

Base: `http://localhost:8000`

| Method & Endpoint | Description |
|---|---|
| `POST /api/detection/evaluate` | Score a transaction in real time (<25 ms) |
| `GET  /api/dashboard/metrics` | KPIs — transactions, active alerts, FP rate |
| `GET  /api/dashboard/alerts-trend` · `/severity-distribution` | Trend & severity data |
| `GET  /api/alerts` · `/api/alerts/{id}` | List / detail (severity, status, search, pagination) |
| `PATCH /api/alerts/{id}/status` | Transition alert status (state-machine enforced) |
| `GET  /api/investigations/{id}` · `/history` | Investigation context & audit trail |
| `POST /api/investigations/{id}/decision` | Submit analyst verdict → feedback loop |
| `GET  /api/analytics/*` | model-performance, alert-volume, confusion-matrix, detection-rate |
| `GET  /api/feedback` · `/summary` | Resolution history and aggregates |

Full OpenAPI spec is served at `/docs`.

---

## Testing

```bash
# Backend API smoke test against a running server + seeded DB
cd backend
BASE_URL=http://127.0.0.1:8000 python scripts/smoke_test.py

# Frontend
npm run typecheck     # tsc --noEmit (also mapped to `npm run lint`)
npm run build         # production build
```

---

## Database migrations

```bash
cd backend
alembic upgrade head                        # apply latest
alembic revision --autogenerate -m "msg"    # create a migration from model changes
alembic downgrade -1                         # roll back one
```

---

## Roadmap

Realistic next steps that build on what's already here:

- **Close the feedback loop** — retrain the model on accumulated analyst labels (the feedback data is already captured; `used_for_training` tracks what's been consumed).
- **Per-feature explanations** — surface which features drove each score in the Investigation view (the engine already returns explanations per detector).
- **Auth & roles** — add authentication and basic role-based access for analysts vs. admins.
- **CSV export** — export filtered alerts and feedback history from the dashboard.
- **Alert notifications** — email/webhook on CRITICAL alerts.
- **Live refresh** — push new alerts to the dashboard instead of polling.
- **Deployment** — containerize and deploy (e.g. AWS ECS + RDS).

---

## License

This project is provided as-is for demonstration and educational purposes.

**Author:** Krishna Reddy
