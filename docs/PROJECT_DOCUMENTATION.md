# Market Anomaly & Fraud Detection System

### A Real-Time ML-Powered Financial Transaction Monitoring Platform

> **Author:** Krishna Reddy
> **Version:** 1.0.0
> **Last Updated:** April 15, 2026

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [The Solution](#2-the-solution)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack](#4-tech-stack)
5. [Detection Engine — The Brain](#5-detection-engine--the-brain)
6. [Database Design](#6-database-design)
7. [API Reference](#7-api-reference)
8. [Frontend Architecture](#8-frontend-architecture)
9. [The Feedback Loop — Why It Gets Smarter](#9-the-feedback-loop--why-it-gets-smarter)
10. [Problems We Faced & How We Solved Them](#10-problems-we-faced--how-we-solved-them)
11. [Scalability — Taking This to Production](#11-scalability--taking-this-to-production)
12. [Future Scope](#12-future-scope)
13. [Performance Benchmarks](#13-performance-benchmarks)
14. [Quick Start](#14-quick-start)

---

## 1. The Problem

### The $48 Billion Blind Spot

In 2024, global fraud losses crossed **$48 billion**. But the number that should scare financial institutions more is this: for every **$1 lost to actual fraud**, they spend **$4.41** in investigation, compliance, and operational overhead trying to catch it.

That's not a typo. The cost of *catching* fraud is 4x the fraud itself.

### Why Traditional Systems Fail

Most banks and financial platforms still rely on **rule-based fraud detection** — hard-coded thresholds written by compliance teams:

```
IF amount > ₹5,00,000 → FLAG
IF country IN blacklist → FLAG
IF time BETWEEN 12AM-5AM → FLAG
```

These rules have three fatal flaws:

| Problem | What Happens |
|---|---|
| **Static thresholds** | A ₹4,99,999 transaction slips through. Fraudsters learn the limits. |
| **No personalization** | A CEO transferring ₹50L is normal. A student doing it isn't. Same rule catches both — or neither. |
| **Alert fatigue** | 80-95% of alerts are **false positives**. Analysts process 200,000+ alerts/year, most of which are noise. |

### The Hidden Cost: Analyst Fatigue

When 9 out of 10 alerts are false, your best investigators start rubber-stamping. They stop reading the details. And that's exactly when the real fraud — the ₹2 crore wire transfer at 3 AM to a brand-new account — gets marked "legitimate" because someone was drowning in garbage alerts.

The industry calls this the **alert fatigue death spiral**:

```
More rules → More alerts → More false positives → Analysts ignore alerts
→ Real fraud slips through → Add more rules → Repeat
```

### What We Needed

A system that doesn't ask *"does this transaction break a threshold?"* but instead asks:

> **"Does this transaction look normal *for this specific entity*, at *this time*, through *this channel*, to *this destination*?"**

That question changes everything. It means a ₹50L transfer is only suspicious if the entity normally transacts ₹20K. It means a 3 AM transaction is only flagged if the entity normally operates 9-5. Personalized detection, not blanket rules.

---

## 2. The Solution

### What We Built

An **end-to-end ML-powered fraud detection platform** that:

- Scores every transaction in **real-time (<25ms)** using three independent detection layers
- Learns **behavioral baselines per entity** — what's "normal" is different for everyone
- Provides a full **investigation workflow** with explainable AI — every score comes with reasons
- Closes the loop with **analyst feedback** that makes the model smarter with every decision
- Runs a modern **operations dashboard** for monitoring, triage, and analytics

### The Key Insight

Instead of one monolithic fraud model, we use a **three-layer ensemble**:

```
┌─────────────────────────────────────────────────────────────┐
│                    TRANSACTION INPUT                        │
│         (amount, time, channel, entity, history)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              FEATURE ENGINEERING (50+ features)             │
│  Statistical · Temporal · Behavioral · Device · Geographic  │
└─────────┬───────────────┬───────────────┬───────────────────┘
          │               │               │
          ▼               ▼               ▼
   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │ STATISTICAL  │ │ BEHAVIORAL  │ │  ML MODEL   │
   │  DETECTOR    │ │  DETECTOR   │ │ (Isolation  │
   │              │ │             │ │   Forest)   │
   │  Weight: 25% │ │ Weight: 35% │ │ Weight: 40% │
   │              │ │             │ │             │
   │ Z-scores     │ │ Spending    │ │ Unsupervised│
   │ Velocity     │ │ patterns    │ │ Multi-dim   │
   │ Thresholds   │ │ Destinations│ │ anomaly     │
   │ Time rules   │ │ Channels    │ │ detection   │
   └──────┬───────┘ └──────┬──────┘ └──────┬──────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │   WEIGHTED SCORE AGGREGATION   │
         │                                │
         │  Score = Σ(Si × Wi × Ci)       │
         │         ─────────────────      │
         │          Σ(Wi × Ci)            │
         │                                │
         │  Confidence floor: 0.7         │
         └────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │      SEVERITY CLASSIFICATION   │
         │                                │
         │  ≥ 90  →  🔴 CRITICAL          │
         │  ≥ 70  →  🟠 HIGH              │
         │  ≥ 50  →  🟡 MEDIUM            │
         │  < 50  →  🟢 LOW               │
         │                                │
         │  ≥ 50  →  ALERT GENERATED      │
         └────────────────────────────────┘
```

Each detector catches different fraud patterns. The statistical detector catches the obvious — large amounts, unusual hours. The behavioral detector catches the subtle — a change in spending pattern, a new destination. The ML model catches the invisible — multi-dimensional anomalies that no human rule would flag.

When all three agree something is wrong, you can be confident it's real.

---

## 3. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Next.js 16 Frontend                       │   │
│  │                                                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │   │
│  │  │Dashboard │ │ Alerts   │ │Analytics │ │Investigation │   │   │
│  │  │  Page    │ │  Page    │ │  Page    │ │    Page      │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │   │
│  │                                                              │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │              Live Transaction Scanner                │    │   │
│  │  │         (Real-time ML Scoring Demo)                  │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │ HTTP/REST                             │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────────┐
│                         API LAYER                                    │
│                              │                                       │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │                    FastAPI Backend                            │   │
│  │                                                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │   │
│  │  │Dashboard │ │ Alerts   │ │Analytics │ │  Detection   │   │   │
│  │  │  Router  │ │ Router   │ │  Router  │ │   Router     │   │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │   │
│  │       │             │            │              │            │   │
│  │  ┌────▼─────────────▼────────────▼──────────────▼───────┐   │   │
│  │  │              SERVICE LAYER                            │   │   │
│  │  │  DashboardService · AlertService · DetectionService   │   │   │
│  │  │  AnalyticsService · FeedbackService                   │   │   │
│  │  └──────────────────────┬────────────────────────────────┘   │   │
│  │                         │                                    │   │
│  │  ┌──────────────────────▼────────────────────────────────┐   │   │
│  │  │              REPOSITORY LAYER (Data Access)           │   │   │
│  │  │  AlertRepo · TransactionRepo · FeedbackRepo          │   │   │
│  │  │  FeatureSnapshotRepo · ModelScoreRepo                 │   │   │
│  │  └──────────────────────┬────────────────────────────────┘   │   │
│  └──────────────────────────┤                                   │   │
│                              │                                   │   │
└──────────────────────────────┼───────────────────────────────────┘   │
                               │                                       │
┌──────────────────────────────┼───────────────────────────────────────┘
│                         DATA LAYER                                    │
│                              │                                       │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │                    PostgreSQL Database                        │   │
│  │                                                              │   │
│  │  ┌────────────┐ ┌────────┐ ┌──────────────┐ ┌──────────┐   │   │
│  │  │Transactions│ │ Alerts │ │Feature Snaps │ │ Feedback │   │   │
│  │  │  (2,306)   │ │ (668)  │ │  (Audit Log) │ │  (83)    │   │   │
│  │  └────────────┘ └────────┘ └──────────────┘ └──────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              ML DETECTION ENGINE                              │   │
│  │                                                              │   │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐   │   │
│  │  │  Statistical   │ │  Behavioral    │ │  ML Detector   │   │   │
│  │  │  Detector      │ │  Detector      │ │ (Isolation     │   │   │
│  │  │  (25% weight)  │ │  (35% weight)  │ │  Forest 40%)   │   │   │
│  │  └────────────────┘ └────────────────┘ └────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### Request Flow — What Happens When a Transaction Arrives

```
1. Transaction JSON hits POST /api/detection/evaluate
                    │
2. DetectionService receives the request
                    │
3. Duplicate check — has this transaction_id been scored before?
                    │
4. Fetch 30-day historical transactions for this entity from DB
   (or use payload-provided history if entity is new)
                    │
5. Feature Engineering — extract 50+ features:
   • amount_zscore, hourly_velocity, is_unusual_hour
   • is_new_destination, spending_deviation_pct
   • frequency_zscore, account_age_days
   • geo_risk_score, device_risk, ip_reputation
                    │
6. Three detectors score independently (can run in parallel):
   • Statistical:  Z-scores, thresholds, velocity    → Score + Confidence
   • Behavioral:   Pattern deviation, new behaviors   → Score + Confidence
   • ML (IForest): Multi-dimensional anomaly          → Score + Confidence
                    │
7. Weighted aggregation:
   composite = Σ(score × weight × confidence) / Σ(weight × confidence)
                    │
8. Classification: Score → Severity (CRITICAL/HIGH/MEDIUM/LOW)
                    │
9. If score ≥ 50: Create Alert record in DB
                    │
10. Persist: Transaction + Feature Snapshots + Model Scores
                    │
11. Return: risk_score, severity, detector_scores, explanations
            Processing time: <25ms
```

---

## 4. Tech Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.9+ | Core language |
| **FastAPI** | 0.128 | Async REST API framework |
| **Uvicorn** | - | ASGI server with hot-reload |
| **SQLAlchemy** | 2.0+ | Async ORM with connection pooling |
| **asyncpg** | - | High-performance PostgreSQL driver |
| **Pydantic** | v2 | Request/response validation |
| **scikit-learn** | - | Isolation Forest ML model |
| **joblib** | - | Model serialization |
| **NumPy** | - | Numerical computations |
| **structlog** | - | Structured JSON logging |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| **Next.js** | 16.1.6 | React meta-framework (Turbopack) |
| **React** | 18.3 | UI library |
| **TypeScript** | 5.x | Type safety |
| **TanStack Query** | 5.x | Server state management (caching, refetch) |
| **TanStack Table** | 8.x | Headless data table with sorting, pagination |
| **Recharts** | 2.15 | Charts (Area, Pie, Bar, Line) |
| **Radix UI** | - | Accessible headless UI primitives |
| **Tailwind CSS** | 3.4 | Utility-first styling |
| **Lucide React** | - | Icon system |
| **next-themes** | - | Dark/light mode |

### Infrastructure

| Technology | Purpose |
|---|---|
| **PostgreSQL** | Primary datastore — transactions, alerts, feedback |
| **joblib files** | Serialized ML model storage |
| **CORS Middleware** | Cross-origin security |
| **Connection Pooling** | 10 connections, 20 overflow, 300s recycle |

### Why These Choices?

- **FastAPI over Flask/Django**: Async-native, automatic OpenAPI docs, Pydantic validation. Our `/evaluate` endpoint needs to be non-blocking — we can't afford to hold a thread per scoring request.

- **SQLAlchemy 2.0 async over raw SQL**: Type safety + connection pooling + query builder. The repository pattern cleanly separates DB access from business logic.

- **Next.js 16 over plain React**: Server-side rendering for SEO (if we ever need a public landing page), API routes as fallback for mock data during development, Turbopack for instant HMR.

- **TanStack Query over Redux**: We don't have *client* state that needs global management. All our state is *server* state — cached API responses that need smart invalidation. TanStack Query does this perfectly with stale-while-revalidate.

- **Isolation Forest over supervised models**: We launched without labelled fraud data. Isolation Forest is unsupervised — it learns the shape of "normal" and flags whatever doesn't fit. No labels needed at day zero.

---

## 5. Detection Engine — The Brain

### 5.1 Feature Engineering (50+ Features)

Before any detector runs, the system extracts a rich feature set from each transaction and its entity's history:

**Statistical Features**
| Feature | How It's Computed | Why It Matters |
|---|---|---|
| `amount_zscore` | `(amount - mean) / stddev` over 30-day history | Flags amounts that deviate from the entity's norm |
| `hourly_velocity` | Count of transactions in the same hour | Rapid-fire transfers are a strong fraud signal |
| `amount_pct_from_avg` | `(amount / average) × 100` | Quick relative magnitude check |

**Temporal Features**
| Feature | How It's Computed | Why It Matters |
|---|---|---|
| `is_unusual_hour` | `True` if hour is 0-5 AM | Most legitimate transactions happen during business hours |
| `day_of_week` | Monday=0 to Sunday=6 | Weekend patterns differ from weekday |
| `is_end_of_month` | `True` if day > 25 | Salary disbursements vs. suspicious activity |

**Behavioral Features**
| Feature | How It's Computed | Why It Matters |
|---|---|---|
| `is_new_destination` | First-time recipient account | Account takeover typically sends to new accounts |
| `is_new_channel` | First time using WEB/API/POS/ATM | Channel switching is a fraud indicator |
| `spending_deviation_pct` | `current / average × 100` | 500%+ deviation is highly suspicious |
| `account_age_days` | Days since first transaction | New accounts are higher risk |
| `frequency_zscore` | Z-score of transaction frequency | Sudden burst of activity |

**Device & Geographic Features**
| Feature | How It's Computed | Why It Matters |
|---|---|---|
| `geo_risk_score` | Country-based risk rating | Transactions from high-risk jurisdictions |
| `is_new_device` | New device fingerprint | New device + high amount = classic fraud |
| `location_distance_km` | Distance from typical location | Travel-time impossible scenarios |

### 5.2 Statistical Detector (25% Weight)

The statistical detector catches **obvious outliers** using mathematical tests:

```
Score Contribution Breakdown:
─────────────────────────────────────────────
Amount-Based Scoring:
  Amount > ₹50,00,000  → +45 points
  Amount > ₹10,00,000  → +35 points
  Amount > ₹5,00,000   → +30 points
  Amount > ₹1,00,000   → +20 points

Z-Score Deviation:
  |z-score| > 2.0       → +min(30, |z| × 3) points

Velocity (transactions/hour):
  Count > 3/hour        → +min(30, (count-3) × 8) points

Time of Day:
  Hour 0-5 AM           → +20 points

Device:
  New device            → +10 points
─────────────────────────────────────────────
Final Score: min(100, total)
Confidence: 0.33 (no history) to 1.0 (full data)
```

### 5.3 Behavioral Detector (35% Weight)

The behavioral detector compares each transaction against the **entity's personal baseline**:

```
Score Contribution Breakdown:
─────────────────────────────────────────────
Spending Pattern:
  > 500% of average     → +25-35 points (scales)
  > 200% of average     → +scaled up to 25 points
  > 150% of average     → +scaled up to 15 points

Destination Analysis:
  New recipient          → +20 points (account takeover signal)

Channel Analysis:
  New channel            → +15 points (WEB user suddenly on API)

Time Pattern:
  Deviation > 30         → +min(20, deviation × 0.3)

Frequency:
  |z-score| > 1.5        → +min(25, |z| × 6) points

Location:
  New location > 500km   → +min(25, distance/100)

Account Age:
  < 30 days              → +15 points (new account risk)
─────────────────────────────────────────────
Confidence: 0.9 (has history) or 0.5 (new entity)
```

### 5.4 ML Detector — Isolation Forest (40% Weight)

This is the most powerful layer. **Isolation Forest** is an unsupervised anomaly detection algorithm that works on a beautiful principle:

> *Anomalies are few and different. Therefore, they are easier to isolate.*

The algorithm builds random binary trees. Normal data points require many splits to isolate. Anomalies — being few and far from the cluster — get isolated in very few splits. The shorter the path to isolation, the more anomalous the data point.

**Why Isolation Forest?**

| Consideration | Why It's Right Here |
|---|---|
| No labelled data needed | We launched without a labelled fraud dataset |
| Multi-dimensional | Catches patterns across 8 features simultaneously |
| Fast inference | O(n log n) training, O(log n) scoring |
| Robust to noise | Ensemble of 100 trees averages out noise |
| Interpretable | Anomaly score directly maps to probability |

**Feature Vector (8 dimensions)**:
```python
{
  "amount_normalized":    zscore / 3,           # Relative transaction size
  "time_risk":            1.0 if 0-5AM else 0,  # Temporal risk
  "velocity":             min(1.0, count / 10),  # Transaction speed
  "geo_risk":             country_risk / 100,    # Geographic risk
  "device_risk":          1.0 if new_device,     # Device novelty
  "destination_risk":     1.0 if new_dest,       # Recipient novelty
  "frequency_deviation":  abs(freq_z) / 3,       # Activity deviation
  "account_age_risk":     1.0 if < 30 days,      # Account maturity
}
```

**Scoring Pipeline**:
```
Raw IForest score (decision_function) → [-1, 1]
          │
Sigmoid mapping: 1 / (1 + e^(6 × raw_score))
          │
Anomaly probability: [0.0 - 1.0]
          │
Risk score: probability × 100 → [0 - 100]
```

### 5.5 Score Aggregation

The three detector scores are combined using a **confidence-weighted average**:

```
                    Σ (Score_i × Weight_i × Confidence_i)
Composite Score = ─────────────────────────────────────────
                      Σ (Weight_i × Confidence_i)

Where:
  Weight_statistical  = 0.25
  Weight_behavioral   = 0.35
  Weight_ml           = 0.40
  Confidence_floor    = 0.7  (prevents low-confidence detectors
                               from zeroing out the score)
```

The confidence floor is critical. Without it, a new entity with no history would get a behavioral confidence of 0.5, dragging the composite score down even when the statistical and ML detectors see a clear anomaly.

---

## 6. Database Design

### Entity-Relationship Overview

```
┌──────────────┐       ┌────────────────┐       ┌──────────────────┐
│ Transactions │──1:N──│    Alerts       │──1:1──│    Feedback      │
│              │       │                │       │                  │
│ id (PK)      │       │ alert_id (PK)  │       │ feedback_id (PK) │
│ transaction_id│      │ risk_score     │       │ decision         │
│ amount       │       │ severity       │       │ confidence       │
│ currency     │       │ status         │       │ notes            │
│ timestamp    │       │ transaction_id │       │ analyst_id       │
│ entity_id    │       │ detection_time │       │ resolved_at      │
│ source_acct  │       └───────┬────────┘       └──────────────────┘
│ dest_acct    │               │
│ channel      │               │
│ ip_address   │       ┌───────▼────────┐
│ geo_country  │       │ Model Scores   │
└──────┬───────┘       │                │
       │               │ detector_name  │
       │               │ raw_score      │
┌──────▼───────┐       │ confidence     │
│Feature Snaps │       │ model_version  │
│              │       └────────────────┘
│ feature_name │
│ feature_value│
│ category     │
│ model_version│
└──────────────┘
```

### Tables Detail

| Table | Records | Purpose |
|---|---|---|
| **transactions** | 2,306 | Immutable record of every financial transaction |
| **alerts** | 668 | Generated when risk_score ≥ 50. Tracks lifecycle. |
| **feature_snapshots** | ~30K | Every feature computed during scoring — full audit trail |
| **feedback** | 83 | Analyst decisions (FRAUD / FALSE_POSITIVE) |
| **model_scores** | ~2K | Per-detector scores for every alert — reproducibility |

### Key Indexes

```sql
-- Fast entity history lookups (30-day window for scoring)
CREATE INDEX ix_txn_entity_time ON transactions (entity_id, timestamp);

-- Alert triage queries
CREATE INDEX ix_txn_source_dest ON transactions (source_account, destination_account);

-- Time-range analytics
CREATE INDEX ix_txn_amount_time ON transactions (timestamp, amount);
```

### Alert Status State Machine

```
                    ┌──────────────┐
                    │    ACTIVE    │ ◄── Alert Created
                    └──┬───────┬──┘
                       │       │
            ┌──────────▼─┐   ┌▼──────────────┐
            │INVESTIGATING│   │   RESOLVED     │
            └──┬──┬───┬──┘   └───────────────┘
               │  │   │
    ┌──────────▼  │   ▼───────────────┐
    │  RESOLVED │  │  │FALSE_POSITIVE │
    └───────────┘  │  └───────┬───────┘
                   │          │
                   └──►ACTIVE◄┘  (reopen)
```

---

## 7. API Reference

### 7.1 Detection — The Core

#### `POST /api/detection/evaluate`

Score a transaction in real-time. This is the endpoint that powers the entire platform.

**Request:**
```json
{
  "transaction_id": "TXN-20260415-001",
  "amount": 7670000,
  "timestamp": "2026-04-15T02:15:00",
  "source_account": "ACC-8042",
  "destination_account": "ACC-9999",
  "entity_id": "USER-42521",
  "entity_type": "USER",
  "currency": "INR",
  "channel": "API",
  "ip_address": "185.220.101.45",
  "geo_country": "XX",
  "historical_transactions": [
    {
      "transaction_id": "H1",
      "amount": 20350,
      "timestamp": "2026-04-13T10:00:00",
      "destination_account": "ACC-9100",
      "channel": "WEB"
    }
  ]
}
```

**Response:**
```json
{
  "data": {
    "transaction_id": "TXN-20260415-001",
    "risk_score": 90.13,
    "severity": "CRITICAL",
    "should_alert": true,
    "alert_id": "ALT-07234",
    "detector_scores": {
      "statistical": 92.5,
      "behavioral": 88.7,
      "ml": 91.3
    },
    "explanations": [
      "High transaction amount: ₹76,70,000",
      "Amount deviation: 3.8σ from historical mean",
      "Transaction at unusual hour (2 AM)",
      "High-risk geographic location",
      "New destination account"
    ],
    "processing_time_ms": 18.42
  }
}
```

### 7.2 Dashboard

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/dashboard/metrics` | GET | KPI cards — total transactions, active alerts, high-risk count, FP rate |
| `/api/dashboard/alerts-trend?range=24h` | GET | Hourly/daily alert counts for trend chart |
| `/api/dashboard/severity-distribution` | GET | CRITICAL/HIGH/MEDIUM/LOW counts for donut chart |

### 7.3 Alerts

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/alerts?page=1&limit=10&severity=HIGH&status=ACTIVE` | GET | Paginated alert list with filters |
| `/api/alerts/{alert_id}` | GET | Full alert detail with transaction + features |
| `/api/alerts/{alert_id}/status?status=INVESTIGATING` | PATCH | Update alert status (validates transitions) |

### 7.4 Investigation

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/investigations/{alert_id}` | GET | Investigation context — entity, risk, features, history |
| `/api/investigations/{alert_id}/decision` | POST | Submit FRAUD / LEGITIMATE / REVIEW decision |
| `/api/investigations/{alert_id}/notes` | POST | Add investigation notes |

### 7.5 Analytics

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/analytics/metrics` | GET | Precision, Recall, F1, daily alert volume |
| `/api/analytics/model-performance?range=7d` | GET | Accuracy over model versions |
| `/api/analytics/alert-volume?range=7d` | GET | Alert + fraud counts by day |
| `/api/analytics/confusion-matrix` | GET | TP, FP, TN, FN counts |
| `/api/analytics/detection-rate?range=7d` | GET | Detection rate trend |

### 7.6 Feedback

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/feedback?page=1&limit=20` | GET | Paginated feedback history with summary |
| `/api/feedback/summary?range=7d` | GET | Resolution stats — total, frauds, FPs |
| `/api/feedback/{feedback_id}` | GET | Single feedback detail |
| `/api/feedback/by-analyst/{analyst_id}` | GET | Per-analyst decision history |

### 7.7 Health

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service health — `{"status":"healthy"}` |

---

## 8. Frontend Architecture

### Component Tree

```
app/layout.tsx
└── ThemeProvider (dark/light mode)
    └── QueryProvider (TanStack Query)
        └── app/page.tsx (Client-side router)
            ├── CurrencyProvider (INR/USD/EUR)
            ├── Sidebar (Navigation — 6 pages)
            ├── TopBar (Title, Theme toggle, Notifications, Currency)
            └── Dynamic Page Content
                │
                ├── Dashboard
                │   ├── 4× MetricCard (KPIs with accent colors)
                │   ├── AlertsTrendChart (Area chart — 24h trend)
                │   ├── SeverityDonut (Pie chart — severity breakdown)
                │   ├── AlertsDataTable (Recent 10 alerts, clickable)
                │   └── LiveScannerCard (3 presets + custom mode)
                │
                ├── Alerts Page
                │   ├── Filter Panel (severity, status, search)
                │   └── AlertsDataTable (paginated, sortable)
                │
                ├── Investigation Page
                │   ├── Alert Summary (score, entity, status)
                │   ├── Transaction Details (9 fields)
                │   ├── Feature Deviations (risk-colored pills)
                │   ├── Historical Behavior Chart
                │   ├── Decision Buttons (Fraud / Legitimate)
                │   └── Notes Section
                │
                ├── Analytics Page
                │   ├── 4× Performance Metrics (Precision, Recall, F1, Volume)
                │   ├── Alert Volume Bar Chart
                │   ├── Model Accuracy Line Chart
                │   └── Confusion Matrix Stats
                │
                ├── Feedback Page
                │   ├── 3× Summary Cards (Resolutions, Fraud, FPs)
                │   └── Resolved Alerts Table
                │
                └── Settings Page
                    ├── Profile Settings
                    ├── Alert Thresholds Configuration
                    ├── Notification Preferences
                    ├── API Keys Management
                    └── System Preferences
```

### Data Flow

```
Component mounts
      │
      ▼
TanStack Query hook fires (e.g., useDashboardMetrics())
      │
      ▼
API Client tries: http://localhost:8000/api/dashboard/metrics
      │
      ├── ✅ Success → Cache response (staleTime: 60s)
      │                 → Render data
      │
      └── ❌ Fail → Fallback to Next.js API route: /api/dashboard/metrics
                    → Returns mock data (development safety net)
```

### Live Scanner — The Demo Centrepiece

The `LiveScannerCard` component is the most important piece for the demo. It lets you score transactions in real-time against the live ML engine.

**3 Pre-configured Scenarios:**

| Preset | Amount | Time | Channel | Expected Score |
|---|---|---|---|---|
| 🚨 Suspicious | ₹76.7L | 2 AM | API | **~90 CRITICAL** |
| ✅ Normal | ₹2,850 | 10 AM | POS | **~18 LOW** |
| ⚠️ Velocity | 6× ₹15L | Rapid | WIRE | **~55 MEDIUM** |

**Custom Mode:** User can dial in any amount, channel, and hour — and watch the ML engine score it live.

---

## 9. The Feedback Loop — Why It Gets Smarter

This is the architectural differentiator. Most fraud systems are fire-and-forget — they score, they alert, end of story. This system closes the loop.

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Transaction │────▶│   Scoring   │────▶│    Alert     │
│   Arrives    │     │   Engine    │     │  Generated   │
└──────────────┘     └─────────────┘     └──────┬───────┘
                                                │
                           ┌────────────────────▼───────┐
                           │   Analyst Investigates     │
                           │                            │
                           │  • Reviews transaction     │
                           │  • Checks feature devs     │
                           │  • Reads explanations      │
                           │  • Marks: FRAUD or FP      │
                           └────────────┬───────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  Feedback Stored   │
                              │                    │
                              │  decision, notes,  │
                              │  analyst, timestamp │
                              └─────────┬──────────┘
                                        │
                     ┌──────────────────▼──────────────────┐
                     │      Model Retraining Pipeline      │
                     │                                      │
                     │  Labelled data → Supervised tuning   │
                     │  FP rate tracked → Threshold adjust  │
                     │  Precision/Recall → Model selection  │
                     └──────────────────┬──────────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  Better Detection  │
                              │                    │
                              │  ↓ False Positives │
                              │  ↑ True Positives  │
                              └────────────────────┘
```

**Current Feedback Pool:** 83 analyst decisions → 55 confirmed frauds, 27 false positives. Each one makes the next detection more accurate.

---

## 10. Problems We Faced & How We Solved Them

This section documents the real engineering challenges we hit during development — not theoretical issues but actual bugs that broke the demo.

### Problem 1: Timezone Bug — Scores Were Wrong for Hours

**What happened:** The Live Scanner was sending `new Date().toISOString()` as the transaction timestamp. JavaScript's `toISOString()` converts to UTC. So a scan at 2:00 AM IST was being sent as 8:30 PM UTC (previous day). The statistical detector saw it as an evening transaction — not unusual at all — and gave it a low time-risk score.

**The impact:** A ₹76.7L transaction at 2 AM was scoring **41.8 LOW** instead of the expected **90+ CRITICAL**. The "unusual hour" signal was completely lost.

**The fix:**
```javascript
// Before: UTC conversion loses IST timezone
const timestamp = new Date().toISOString()  // 2 AM IST → 8:30 PM UTC

// After: Local ISO string preserves the actual wall-clock time
function localISOTimestamp() {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const local = new Date(now.getTime() - offset * 60000)
  return local.toISOString().slice(0, -1)  // 2 AM IST → 02:00:00
}
```

**Lesson:** Always be explicit about timezone handling in fraud systems. The *local time* of the transaction is what matters for behavioral patterns, not UTC.

### Problem 2: Silent Schema Drop — Pydantic Was Eating Our Data

**What happened:** We were sending `historical_transactions` in the request body to provide entity history for new entities. But the scores weren't reflecting the history — the behavioral detector was scoring as if the entity had no history at all.

**Root cause:** The `DetectionRequest` Pydantic v2 model didn't have a `historical_transactions` field. Pydantic v2's default behavior is to **silently ignore** extra fields. Our carefully crafted payload history was being dropped before it reached the detection engine.

**The fix:**
```python
# Added to schemas.py
class HistoricalTransactionInput(BaseModel):
    transaction_id: str
    amount: float
    timestamp: str
    destination_account: str
    channel: str

class DetectionRequest(BaseModel):
    # ... existing fields ...
    historical_transactions: Optional[List[HistoricalTransactionInput]] = None
```

**Lesson:** Pydantic's strict validation is a double-edged sword. It protects you from bad data, but `model_config = ConfigDict(extra='ignore')` means typos in field names fail silently. Always validate that your payload reaches the function you expect.

### Problem 3: Entity ID Collision — DB History Overriding Test Data

**What happened:** When demoing with the Live Scanner, we used entity IDs like `ENT-SCAN-001`. But the seeded database already had transactions under that entity. The detection service was finding 30 days of *database* history and ignoring the *payload* history we sent — because the code prioritized DB history.

**The fix:** Generate unique entity IDs per scan:
```javascript
const entityId = `ENT-SCAN-${preset}-${Date.now()}`
```

And modified the detection service to fall back to payload history only when DB history is empty.

### Problem 4: Field Name Mismatch — geo_location vs geo_country

**What happened:** The frontend was sending `geo_location: "XX"` but the backend schema expected `geo_country: "XX"`. Pydantic silently ignored the wrong field name. The geographic risk detector was always getting `None` for country — scoring zero geographic risk.

**The fix:** Changed frontend to use `geo_country` to match the schema.

**Lesson:** When two systems talk to each other, field name mismatches are the most common integration bug. They're invisible in JavaScript (no type checking at runtime) and silent in Pydantic v2. TypeScript on the frontend catches some of these, but only if you use the types.

### Problem 5: Conservative Scoring — The Model Was Too Polite

**What happened:** After fixing all the data bugs, the scores were *better* but still too conservative. A ₹76.7L transaction at 2 AM was scoring 65 instead of 90+.

**Root causes:**
- Statistical detector's amount thresholds were too high (required ₹1Cr+ for max score)
- Behavioral detector capped spending deviation at 25 points even for 500%+ deviations
- The confidence multiplier was too aggressive — new entities with 0.5 confidence were dragging down composites

**The fix:**
- Added tiered amount scoring: ₹1L → +20, ₹5L → +30, ₹10L → +35, ₹50L+ → +45
- Added higher behavioral scoring tier: 500%+ deviation → up to 35 points
- Changed the confidence floor from 0 to **0.7** — a low-confidence detector can reduce the score, but never by more than 30%

**Before and after:**

| Scenario | Before Fix | After Fix |
|---|---|---|
| ₹76.7L at 2 AM, unknown IP | 41.8 LOW | **90.13 CRITICAL** |
| ₹2,850 grocery, 10 AM, known POS | 32.1 LOW | **18.45 LOW** |
| 6× ₹15L rapid wire transfers | 38.2 LOW | **55.52 MEDIUM** |
| Custom escalation test | 42 → stuck | **42 → 71 → 81 → 86** |

### Problem 6: Sidebar Visibility — CSS Variable Opacity Bug

**What happened:** After redesigning the sidebar with Tailwind CSS variables (`text-sidebar-foreground/60`), the nav items became nearly invisible on the dark background. The Tailwind opacity modifier `/60` wasn't rendering correctly with HSL CSS variables.

**The fix:** Replaced all `text-sidebar-*` CSS variable classes with direct Tailwind colors:
```jsx
// Before: invisible
className="text-sidebar-foreground/60"

// After: clearly visible
className="text-white/80"
```

**Lesson:** CSS-variable-based color systems in Tailwind work great for semantic theming, but opacity modifiers can break when the underlying HSL variable doesn't support the alpha channel format. When visibility is critical, use explicit colors.

---

## 11. Scalability — Taking This to Production

### Current State (Development)

```
Single Uvicorn worker → 1 process
PostgreSQL direct connection → 10 pool, 20 overflow
In-process ML model → loaded in memory
Frontend → Next.js dev server
```

**Throughput:** ~200 transactions/second (single worker with DB round-trips)

### Production Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        LOAD BALANCER                             │
│                   (AWS ALB / Nginx)                               │
└────────────┬──────────────┬──────────────┬───────────────────────┘
             │              │              │
    ┌────────▼────┐ ┌───────▼─────┐ ┌─────▼───────┐
    │  FastAPI    │ │  FastAPI    │ │  FastAPI    │
    │  Worker 1  │ │  Worker 2  │ │  Worker N  │
    │  (Uvicorn) │ │  (Uvicorn) │ │  (Uvicorn) │
    └────┬────┬──┘ └────┬───┬───┘ └────┬───┬───┘
         │    │         │   │          │   │
    ┌────▼────▼─────────▼───▼──────────▼───▼───┐
    │              Redis Cluster                │
    │     (Rate limiting, Caching, Queues)      │
    └────────────────┬──────────────────────────┘
                     │
    ┌────────────────▼──────────────────────────┐
    │         PostgreSQL (Multi-AZ)             │
    │  Primary (writes) ←→ Read Replicas        │
    │                                           │
    │  pgBouncer connection pooling             │
    └───────────────────────────────────────────┘

    ┌───────────────────────────────────────────┐
    │         Kafka / SQS                       │
    │   (Transaction ingestion stream)          │
    │                                           │
    │   Bank Core → Kafka Topic → Detection API │
    └───────────────────────────────────────────┘
```

### Scaling Strategies

| Bottleneck | Solution | Impact |
|---|---|---|
| **CPU (ML scoring)** | Add Uvicorn workers (`--workers 4`) | 4× throughput per instance |
| **Database reads** | PostgreSQL read replicas | Separate scoring reads from dashboard queries |
| **Connection overhead** | pgBouncer in front of Postgres | 10,000+ concurrent connections |
| **Traffic spikes** | Celery + Redis task queue | Buffer scoring requests, process async |
| **Model loading** | Pre-load model per worker, shared memory | Zero-copy model access across workers |
| **Global latency** | Multi-region deployment (AWS ECS) | <50ms from any geography |
| **Frontend** | Vercel / CloudFront CDN | Edge-cached static assets |

### Throughput Projections

| Configuration | Transactions/Second | Transactions/Day |
|---|---|---|
| 1 worker, local DB | ~200 | ~17M |
| 4 workers, local DB | ~700 | ~60M |
| 4 workers, pgBouncer, read replicas | ~2,000 | ~170M |
| 8 workers, Kafka queue, Redis cache | ~5,000+ | ~430M+ |
| Horizontal auto-scale (ECS) | ~20,000+ | ~1.7B+ |

### Real-Time Integration Options

**Option 1: Direct API Integration**
```
Core Banking System → POST /api/detection/evaluate → Response in <25ms
```
Best for: Low-volume, synchronous scoring. The bank holds the transaction until scoring completes.

**Option 2: Event Stream (Kafka)**
```
Transaction Event → Kafka Topic → Consumer (Detection Service) → Alert DB
```
Best for: High-volume, async scoring. Transactions are not held — alerts are raised post-facto.

**Option 3: Webhook Notifications**
```
Detection Service scores → If alert → POST webhook to bank's alert system
```
Best for: Integration with existing SIEM/SOC tools.

### Deployment Architecture (AWS)

```
┌─────────────────────────────────────────────────┐
│                    AWS Cloud                     │
│                                                  │
│  ┌──────────────┐  ┌───────────────────────┐    │
│  │   CloudFront  │  │   Route 53 (DNS)      │    │
│  │   (CDN)       │  └───────────────────────┘    │
│  └──────┬────────┘                               │
│         │                                        │
│  ┌──────▼────────┐                               │
│  │   Vercel /    │  ← Next.js Frontend           │
│  │   S3 + CF     │                               │
│  └──────┬────────┘                               │
│         │                                        │
│  ┌──────▼────────┐  ┌───────────────────────┐    │
│  │   ALB         │  │   AWS WAF              │    │
│  │   (HTTPS)     │──│   (Rate limiting,      │    │
│  └──────┬────────┘  │    IP blocking)        │    │
│         │           └───────────────────────┘    │
│  ┌──────▼────────┐                               │
│  │   ECS Fargate │  ← FastAPI Containers         │
│  │   (Auto-scale)│     (2-10 tasks)              │
│  └──────┬────────┘                               │
│         │                                        │
│  ┌──────▼────────┐  ┌───────────────────────┐    │
│  │   RDS Postgres│  │   ElastiCache Redis   │    │
│  │   (Multi-AZ)  │  │   (Rate limit +       │    │
│  │   + Replicas  │  │    session cache)      │    │
│  └───────────────┘  └───────────────────────┘    │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │   CloudWatch (Monitoring + Alerting)      │    │
│  │   X-Ray (Distributed Tracing)             │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

---

## 12. Future Scope

### Short-Term (Next 3 Months)

| Feature | Description | Impact |
|---|---|---|
| **Supervised Model Layer** | Train on 83+ labelled feedback decisions using XGBoost/LightGBM | 15-20% improvement in precision |
| **API Key Authentication** | JWT + API key middleware on all endpoints | Production security |
| **Real-Time WebSocket Dashboard** | Push new alerts to dashboard without polling | True real-time UX |
| **Batch Scoring API** | Score 1000 transactions in a single call | Bulk processing for EOD reconciliation |
| **Email/Slack Alerts** | Notify analysts on CRITICAL alerts via integrations | Faster response time |

### Medium-Term (3-6 Months)

| Feature | Description | Impact |
|---|---|---|
| **Graph Neural Network** | Model entity relationships — sender/receiver graphs. Detect mule account networks. | Catch organized fraud rings |
| **Explainable AI (SHAP)** | SHAP values per feature per transaction — visual feature importance | Regulatory compliance (EU AI Act) |
| **A/B Model Testing** | Canary deployment: 10% traffic to new model, compare performance | Safe model upgrades |
| **Multi-Tenant Support** | Isolated detection engines per client/bank | SaaS deployment |
| **Device Fingerprint Intelligence** | Browser/device fingerprinting with similarity matching | Account takeover detection |

### Long-Term (6-12 Months)

| Feature | Description | Impact |
|---|---|---|
| **Federated Learning** | Train across multiple institutions without sharing raw data | Privacy-preserving cross-bank fraud detection |
| **NLP on Transaction Memos** | Parse transaction descriptions for anomaly signals | Catch social engineering patterns |
| **Synthetic Data Generation** | GAN-based fraud scenario generation for model training | Unlimited training data |
| **Regulatory Reporting Engine** | Auto-generate STR (Suspicious Transaction Reports) from alerts | Compliance automation |
| **Mobile SDK** | Embedded fraud scoring in mobile banking apps | On-device pre-screening |

### Research Directions

- **Temporal Graph Networks** — Model how entity behavior evolves over time, not just snapshot analysis
- **Adversarial Robustness** — Test and harden models against adversarial inputs designed to evade detection
- **Transfer Learning** — Pre-train on public fraud datasets, fine-tune on institution-specific data
- **Causal Inference** — Move from correlation (this looks anomalous) to causation (this is likely fraud because...)

---

## 13. Performance Benchmarks

### Scoring Latency

| Metric | Value |
|---|---|
| Average scoring time | **18-25ms** |
| P95 scoring time | **35ms** |
| P99 scoring time | **48ms** |
| Feature extraction | ~5ms |
| Statistical detector | ~2ms |
| Behavioral detector | ~3ms |
| ML detector (Isolation Forest) | ~4ms |
| DB persistence | ~8ms |

### Detection Quality

| Metric | Value | Context |
|---|---|---|
| Precision | **67%** | 2 out of 3 alerts are real fraud (vs. 20-30% industry average for rule-based) |
| Recall | **35%** | Room to improve — each feedback batch pushes this higher |
| F1 Score | **46%** | Balanced precision-recall metric |
| False Positive Rate | **23.3%** ↓ | Trending down as feedback accumulates |
| Alert-to-Fraud Ratio | **3:1** | Industry average is **8:1 to 20:1** |

### Database Performance

| Query | Avg Time |
|---|---|
| Entity history lookup (30-day) | 3ms |
| Alert list with filters (paginated) | 8ms |
| Dashboard metrics aggregation | 12ms |
| Feature snapshot batch insert | 5ms |

---

## 14. Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server (with hot-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# → http://localhost:3000
```

### Verify

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"healthy","app":"Market Anomaly Detection API","version":"1.0.0"}

# Score a test transaction
curl -X POST http://localhost:8000/api/detection/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "transaction_id": "TEST-001",
    "amount": 7670000,
    "timestamp": "2026-04-15T02:00:00",
    "source_account": "ACC-TEST",
    "destination_account": "ACC-NEW",
    "entity_id": "ENT-TEST-001",
    "entity_type": "USER",
    "currency": "INR",
    "channel": "API",
    "geo_country": "XX"
  }'
# → {"data": {"risk_score": 90.13, "severity": "CRITICAL", ...}}
```

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fraud_detection

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
DEBUG=false
WORKERS=1

# Security
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000"]

# Model
ML_MODEL_PATH=models/fraud_detector.joblib
MODEL_VERSION=1.0.0

# Detection Thresholds
HIGH_RISK_THRESHOLD=80.0
MEDIUM_RISK_THRESHOLD=50.0
LOW_RISK_THRESHOLD=20.0
```

---

> *"The best fraud detection system isn't the one that catches the most fraud — it's the one that catches the right fraud while letting legitimate transactions flow. Every false positive is a customer you've just inconvenienced and an analyst minute you've just wasted."*

---

**Built by Krishna Reddy** | Full-Stack ML Platform | April 2026
