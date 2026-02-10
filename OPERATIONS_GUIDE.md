# Market Anomaly Detection System — Operations Guide

> Everything you need to run, manage, and operate the system locally.

---

## Table of Contents

- [Quick Start (TL;DR)](#quick-start-tldr)
- [Prerequisites](#prerequisites)
- [1. PostgreSQL Database](#1-postgresql-database)
- [2. Backend (FastAPI)](#2-backend-fastapi)
- [3. Frontend (Next.js)](#3-frontend-nextjs)
- [4. Running All 3 Services](#4-running-all-3-services)
- [5. Database Operations](#5-database-operations)
- [6. Database Seeding](#6-database-seeding)
- [7. API Documentation & Testing](#7-api-documentation--testing)
- [8. Git & GitHub](#8-git--github)
- [9. Environment Configuration](#9-environment-configuration)
- [10. Troubleshooting](#10-troubleshooting)

---

## Quick Start (TL;DR)

Open **3 terminal tabs** and run:

```bash
# Tab 1 — PostgreSQL (usually already running)
brew services start postgresql@16

# Tab 2 — Backend
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Tab 3 — Frontend
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System"
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

---

## Prerequisites

| Tool | Version | Check Command |
|------|---------|---------------|
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Python | 3.9+ | `python3 --version` |
| PostgreSQL | 16 | `/opt/homebrew/opt/postgresql@16/bin/psql --version` |
| Homebrew | Latest | `brew --version` |

---

## 1. PostgreSQL Database

### Start / Stop / Status

```bash
# Check if running
brew services list | grep postgresql

# Start (runs in background, auto-starts at login)
brew services start postgresql@16

# Stop
brew services stop postgresql@16

# Restart
brew services restart postgresql@16
```

### Connect to Database

```bash
# Using full path (always works)
/opt/homebrew/opt/postgresql@16/bin/psql -d fraud_detection

# Using short command (after restarting terminal)
psql -d fraud_detection
```

You'll see a `fraud_detection=#` prompt. Type SQL commands here.

### Essential psql Commands

| Command | What It Does |
|---------|-------------|
| `\dt` | List all tables |
| `\d table_name` | Show table structure (columns, types, indexes) |
| `\d+ table_name` | Show table with extra detail (storage, description) |
| `\di` | List all indexes |
| `\l` | List all databases |
| `\du` | List all database users |
| `\x` | Toggle expanded display (for wide rows) |
| `\timing` | Toggle query execution time display |
| `\q` | Quit psql |

### Common SQL Queries

```sql
-- Count all records
SELECT 'transactions' AS entity, COUNT(*) FROM transactions
UNION ALL SELECT 'feature_snapshots', COUNT(*) FROM feature_snapshots
UNION ALL SELECT 'alerts', COUNT(*) FROM alerts
UNION ALL SELECT 'model_score_records', COUNT(*) FROM model_score_records
UNION ALL SELECT 'investigations', COUNT(*) FROM investigations
UNION ALL SELECT 'feedback', COUNT(*) FROM feedback
UNION ALL SELECT 'metrics_snapshots', COUNT(*) FROM metrics_snapshots
ORDER BY entity;

-- View recent alerts
SELECT alert_id, severity, status, risk_score, detection_time
FROM alerts
ORDER BY detection_time DESC
LIMIT 10;

-- View high-risk alerts
SELECT alert_id, entity, risk_score, severity, status
FROM alerts
WHERE risk_score >= 80
ORDER BY risk_score DESC;

-- Full alert traceability (alert → transaction → feedback)
SELECT
    f.feedback_id,
    f.decision,
    a.alert_id,
    a.risk_score,
    a.severity,
    t.transaction_id,
    t.amount,
    t.source_account
FROM feedback f
JOIN alerts a ON f.alert_id = a.id
JOIN transactions t ON a.transaction_id = t.id
LIMIT 10;

-- Alert severity distribution
SELECT severity, COUNT(*) as count
FROM alerts
GROUP BY severity
ORDER BY count DESC;

-- Model score comparison for an alert
SELECT alert_id, model_name, model_version, normalized_score, confidence
FROM model_score_records
ORDER BY alert_id, model_name
LIMIT 20;
```

### Database Management

```bash
# Create a new database
/opt/homebrew/opt/postgresql@16/bin/createdb my_database

# Delete a database (CAREFUL — this is permanent!)
/opt/homebrew/opt/postgresql@16/bin/dropdb my_database

# Reset fraud_detection database (drop + recreate + seed)
/opt/homebrew/opt/postgresql@16/bin/dropdb fraud_detection
/opt/homebrew/opt/postgresql@16/bin/createdb fraud_detection
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
python3 -m app.db.seed
```


# Create a new database
/opt/homebrew/opt/postgresql@16/bin/createdb my_new_db

# Delete a database (CAREFUL!)
/opt/homebrew/opt/postgresql@16/bin/dropdb my_new_db

# Re-seed your data (from project directory)
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
python3 -m app.db.seed
---

## 2. Backend (FastAPI)

### First-Time Setup

```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"

# Create virtual environment (one-time)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
cp .env.example .env
```

### Run Backend

```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| Flag | Purpose |
|------|---------|
| `--reload` | Auto-restart on code changes (dev only) |
| `--host 0.0.0.0` | Accept connections from any IP |
| `--port 8000` | Listen on port 8000 |

### Stop Backend

Press `Ctrl + C` in the terminal.

### Run on a Different Port

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Check Backend Health

```bash
curl http://localhost:8000/health
```

---

## 3. Frontend (Next.js)

### First-Time Setup

```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System"

# Install dependencies (one-time)
npm install
```

### Run Frontend

```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System"
npm run dev
```

### Stop Frontend

Press `Ctrl + C` in the terminal.

### Build for Production

```bash
npm run build
npm start
```

---

## 4. Running All 3 Services

### Startup Order (Important!)

```
1. PostgreSQL  →  2. Backend  →  3. Frontend
   (database)      (API)          (UI)
```

### Step-by-Step

**Terminal Tab 1 — Database:**
```bash
brew services start postgresql@16
# Verify it's running:
brew services list | grep postgresql
```

**Terminal Tab 2 — Backend:**
```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal Tab 3 — Frontend:**
```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System"
npm run dev
```

### Shutdown Order (Reverse)

```bash
# 1. Stop Frontend: Ctrl+C in Tab 3
# 2. Stop Backend:  Ctrl+C in Tab 2
# 3. Stop PostgreSQL (optional — it's fine to leave running):
brew services stop postgresql@16
```

### Verify Everything Is Running

| Check | Command / URL |
|-------|--------------|
| PostgreSQL | `brew services list \| grep postgresql` → should show `started` |
| Backend | Open http://localhost:8000/docs → Swagger UI loads |
| Frontend | Open http://localhost:3000 → Dashboard loads |
| DB connection | `curl http://localhost:8000/health` → `{"status": "healthy"}` |

---

## 5. Database Operations

### View Table Structure

```bash
# Connect to database
/opt/homebrew/opt/postgresql@16/bin/psql -d fraud_detection

# Inside psql:
\dt                    -- list all 7 tables
\d transactions        -- show transaction columns
\d alerts              -- show alert columns
\d feature_snapshots   -- show feature snapshot columns
\d model_score_records -- show model score columns
\d investigations      -- show investigation columns
\d feedback            -- show feedback columns
\d metrics_snapshots   -- show metrics columns
\di                    -- list all indexes
```

### Export Data to CSV

```sql
-- Inside psql, export alerts to CSV:
\copy (SELECT * FROM alerts ORDER BY detection_time DESC) TO '/tmp/alerts_export.csv' WITH CSV HEADER;

-- Export feedback:
\copy (SELECT * FROM feedback) TO '/tmp/feedback_export.csv' WITH CSV HEADER;
```

### Clear All Data (Keep Tables)

```sql
-- Inside psql (CAREFUL — deletes all data!):
TRUNCATE transactions, feature_snapshots, alerts, model_score_records, investigations, feedback, metrics_snapshots CASCADE;
```

---

## 6. Database Seeding

### Seed with Synthetic Data

```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
python3 -m app.db.seed
```

This creates:

| Entity | Records |
|--------|---------|
| Transactions | 200 |
| Feature Snapshots | 2,000 |
| Alerts | ~50 |
| Model Score Records | ~150 |
| Investigations | ~46 |
| Feedback | ~19 |
| Metrics Snapshots | 48 |

### Re-Seed (Clear + Seed)

```bash
# Connect and clear data first
/opt/homebrew/opt/postgresql@16/bin/psql -d fraud_detection -c "TRUNCATE transactions, feature_snapshots, alerts, model_score_records, investigations, feedback, metrics_snapshots CASCADE;"

# Then seed
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
python3 -m app.db.seed
```

---

## 7. API Documentation & Testing

### Swagger UI (Interactive)

Open http://localhost:8000/docs in your browser (backend must be running).

You can:
- Browse all API endpoints
- Try out requests directly
- See request/response schemas

### Test API with curl

```bash
# Health check
curl http://localhost:8000/health

# Get dashboard metrics
curl http://localhost:8000/api/v1/dashboard/metrics

# Get alerts (paginated)
curl "http://localhost:8000/api/v1/alerts?page=1&limit=10"

# Get alerts filtered by severity
curl "http://localhost:8000/api/v1/alerts?severity=CRITICAL"

# Get single alert
curl http://localhost:8000/api/v1/alerts/ALT-1000

# Get dashboard trends
curl http://localhost:8000/api/v1/dashboard/trends
```

---

## 8. Git & GitHub

### Common Git Commands

```bash
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System"

# Check status
git status

# Stage all changes
git add .

# Commit with message
git commit -m "Your commit message here"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main

# View recent commits
git log -n 5 --oneline
```

### What's Excluded from Git (.gitignore)

| Excluded | Why |
|----------|-----|
| `backend/venv/` | Virtual environment — recreated via `pip install` |
| `backend/.env` | Contains local secrets — use `.env.example` as template |
| `node_modules/` | npm packages — recreated via `npm install` |
| `.next/` | Next.js build cache |
| `__pycache__/` | Python bytecode cache |
| `*.db` | SQLite files (not used, but excluded as precaution) |
| `.DS_Store` | macOS system files |

---

## 9. Environment Configuration

### Backend (.env)

Location: `backend/.env`

Key settings:

```bash
# Database connection
DATABASE_URL=postgresql+asyncpg://krishnareddy@localhost:5432/fraud_detection

# Detection thresholds (change without redeploying)
RISK_THRESHOLD_HIGH=80.0
RISK_THRESHOLD_MEDIUM=50.0
RISK_THRESHOLD_LOW=20.0

# Logging
LOG_LEVEL=INFO          # DEBUG for verbose, WARNING for quiet
LOG_FORMAT=console      # 'json' for production

# Debug mode
DEBUG=true              # false for production
```

### Frontend

API URL configured in Next.js — points to `http://localhost:8000` during development.

---

## 10. Troubleshooting

### PostgreSQL Won't Start

```bash
# Check if another PostgreSQL is using port 5432
lsof -i :5432

# Restart the service
brew services restart postgresql@16

# Check logs
cat /opt/homebrew/var/log/postgresql@16.log
```

### Backend Won't Start

```bash
# Make sure you're in the right directory
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"

# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Reinstall dependencies if packages are missing
pip install -r requirements.txt

# Check if port 8000 is already in use
lsof -i :8000

# Kill process using port 8000 (if needed)
kill -9 $(lsof -t -i:8000)
```

### Frontend Won't Start

```bash
# Make sure you're in the root project directory
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System"

# Reinstall node modules
rm -rf node_modules
npm install

# Check if port 3000 is already in use
lsof -i :3000
```

### Database Connection Error

```bash
# Verify PostgreSQL is running
brew services list | grep postgresql

# Verify the database exists
/opt/homebrew/opt/postgresql@16/bin/psql -l | grep fraud_detection

# Recreate database if missing
/opt/homebrew/opt/postgresql@16/bin/createdb fraud_detection

# Re-seed data
cd "/Users/krishnareddy/ my Projects/Market-Anomaly-Detection-System/backend"
source venv/bin/activate
python3 -m app.db.seed
```

### "Module not found" Errors

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall all packages
pip install -r requirements.txt

# If greenlet error:
pip install greenlet
```

### Port Already in Use

```bash
# Find what's using a port
lsof -i :8000    # backend
lsof -i :3000    # frontend
lsof -i :5432    # postgresql

# Kill the process
kill -9 <PID>
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| **Start PostgreSQL** | `brew services start postgresql@16` |
| **Stop PostgreSQL** | `brew services stop postgresql@16` |
| **Start Backend** | `source venv/bin/activate && uvicorn app.main:app --reload --port 8000` |
| **Stop Backend** | `Ctrl + C` |
| **Start Frontend** | `npm run dev` |
| **Stop Frontend** | `Ctrl + C` |
| **Open Database** | `/opt/homebrew/opt/postgresql@16/bin/psql -d fraud_detection` |
| **Seed Data** | `python3 -m app.db.seed` |
| **API Docs** | http://localhost:8000/docs |
| **Dashboard** | http://localhost:3000 |
| **Git Push** | `git add . && git commit -m "msg" && git push origin main` |
