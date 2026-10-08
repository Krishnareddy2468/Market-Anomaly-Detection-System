# Step 6 — Alert & Investigation System: Operational Architecture

> **Scope:** How anomalies become operations — alerts, investigations, feedback, and continuous improvement.  
> **Status:** 🔒 DESIGNED  
> **Last updated:** 2026-02-10  

---

## 6.1 Why This Step Matters

> **Industry reality: Models do not stop fraud. Operations do.**

The detection engine (Step 5) produces risk signals. This step defines how those signals become **human-actionable operations** — and how human decisions flow back to improve the system.

A good operational system does four things:

| # | Responsibility | Failure Mode If Missing |
|---|---------------|------------------------|
| 1 | Sends the **right alerts** | Analysts drown in noise |
| 2 | To the **right humans** | Critical fraud sits in wrong queue |
| 3 | At the **right time** | SLA breaches, delayed response |
| 4 | **Learns from decisions** | Same mistakes repeated forever |

---

## 6.2 Alert Lifecycle (End-to-End)

### Finite State Machine

Every alert follows a strict, forward-only lifecycle:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ CREATED  │────▶│  ACTIVE  │────▶│IN_REVIEW │────▶│ RESOLVED │────▶│  CLOSED  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
  Detection       Queued for       Analyst is       Decision         Archived &
  engine           analyst         investigating    recorded         auditable
  created it       attention                                         
```

### State Definitions

| State | Who Triggers | What Happens | Exit Condition |
|-------|-------------|-------------|----------------|
| **CREATED** | Detection engine | Alert record inserted into `alerts` table | Automatic → ACTIVE |
| **ACTIVE** | System (automatic) | Alert enters analyst queue, prioritised by severity | Analyst picks it up |
| **IN_REVIEW** | Analyst | Context auto-loaded; investigation begins | Analyst submits decision |
| **RESOLVED** | Analyst | Decision (FRAUD / FALSE_POSITIVE) recorded in `feedback` | Review period expires or supervisor approves |
| **CLOSED** | System / Supervisor | Alert archived; feedback consumed for learning | Terminal state |

### State Transition Rules

```
CREATED ──────► ACTIVE         (automatic, immediate)
ACTIVE ───────► IN_REVIEW      (analyst claims alert)
IN_REVIEW ────► RESOLVED       (analyst submits decision)
RESOLVED ─────► CLOSED         (after review period or supervisor sign-off)
IN_REVIEW ────► ACTIVE         (analyst releases — only valid backward transition)
```

### Design Rule

> **Alerts move forward only** — with one exception: an analyst may release an IN_REVIEW alert back to ACTIVE (unclaim). No other backward transitions are permitted.

### State Transition Audit

Every transition creates a row in the `investigations` table:

```
InvestigationModel(
    alert_id = "ALT-1042",
    action = "STATUS_CHANGED",
    old_status = "ACTIVE",
    new_status = "IN_REVIEW",
    analyst_id = "analyst-001",
    created_at = "2026-02-10T10:15:00Z"
)
```

**Nothing is lost. Every transition is permanent, timestamped, and attributed.**

---

## 6.3 Alert Prioritisation Strategy

### Priority Inputs

The system uses four signals to determine alert priority:

| Signal | Weight | Rationale |
|--------|--------|-----------|
| **Severity** | Primary | CRITICAL > HIGH > MEDIUM > LOW |
| **Risk score** | Secondary | Within same severity, higher score = higher priority |
| **Entity risk history** | Modifier | Entities with prior confirmed fraud get boosted |
| **Alert age** | Escalation | Older alerts rise in priority (SLA pressure) |

### Priority Buckets

```
┌─────────────────────────────────────────────────────┐
│                  ANALYST QUEUE                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  🔴 IMMEDIATE (P1)                                  │
│  ├── CRITICAL severity alerts                        │
│  ├── HIGH severity + entity with fraud history       │
│  └── Any alert approaching SLA breach                │
│                                                      │
│  🟠 SCHEDULED (P2)                                  │
│  ├── HIGH severity (standard)                        │
│  ├── MEDIUM severity + multi-detector agreement      │
│  └── Escalated alerts from P3                        │
│                                                      │
│  🟢 BACKGROUND (P3)                                 │
│  ├── MEDIUM severity (single detector)               │
│  ├── LOW severity (monitoring only)                  │
│  └── Alerts with decreasing risk on re-evaluation    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Priority Calculation (Conceptual)

```
Priority Score = 
    (Severity Weight × 0.40) +
    (Normalised Risk Score × 0.30) +
    (Entity History Factor × 0.15) +
    (Age Pressure Factor × 0.15)
```

The **Age Pressure Factor** increases linearly as an alert approaches its SLA deadline, ensuring no alert is permanently buried.

---

## 6.4 Investigation Workflow (Analyst View)

### The 5-Step Investigation Flow

```
Step 1          Step 2              Step 3           Step 4            Step 5
┌─────────┐    ┌──────────────┐    ┌────────────┐   ┌─────────────┐  ┌────────────┐
│ Alert   │───▶│ Context      │───▶│ Evidence   │──▶│ Decision    │─▶│ Feedback   │
│ Opened  │    │ Auto-Loaded  │    │ Reviewed   │   │ Recorded    │  │ Submitted  │
└─────────┘    └──────────────┘    └────────────┘   └─────────────┘  └────────────┘
  Analyst       System provides     Analyst          Analyst selects   System
  clicks        everything          evaluates        FRAUD / FP /      captures
  the alert     needed              the evidence     UNCERTAIN         the signal
```

### Step 2: Context Auto-Loading (Critical Design)

> **Design Rule: Analysts should never re-collect data the system already knows.**

When an analyst opens an alert, the system automatically presents:

| Context Panel | Source | Purpose |
|--------------|--------|---------|
| **Transaction details** | `transactions` table | Amount, time, channel, accounts |
| **Feature contributions** | `feature_snapshots` table | Which features drove the score |
| **Detector breakdown** | `model_score_records` table | Per-model scores and agreement |
| **Entity history** | `transactions` + `alerts` (filtered) | Past behavior and prior alerts |
| **Geo & device info** | `transactions` table | IP, location, device fingerprint |
| **Similar past cases** | `alerts` + `feedback` (similarity query) | How similar alerts were resolved |

This context is assembled from the database — **no manual lookup required**.

### Step 4: Analyst Decision Options

| Decision | Meaning | System Response |
|----------|---------|----------------|
| **FRAUD** | True positive — this is real fraud | Reinforces model confidence; may trigger downstream actions |
| **FALSE_POSITIVE** | Model overreach — not actually fraud | Triggers threshold/weight adjustment consideration |
| **UNCERTAIN** | Boundary case — needs escalation or more data | Alert stays in queue for senior review |

### Analyst Inputs Per Decision

| Field | Required? | Purpose |
|-------|-----------|---------|
| **Decision** | ✅ Always | The label |
| **Notes** | ✅ For FRAUD decisions | Explain what confirmed it |
| **Confidence** | Optional | Analyst's certainty (0–1) |

---

## 6.5 Decision Validation Rules

Before the system accepts a decision, it enforces integrity rules:

### Pre-Conditions (All Must Pass)

| Rule | Check | Failure Response |
|------|-------|-----------------|
| **State check** | Alert must be IN_REVIEW | `400: Alert is not under review` |
| **Ownership check** | Submitting analyst must be the one who claimed it | `403: Alert assigned to different analyst` |
| **Valid decision** | Decision must be FRAUD, FALSE_POSITIVE, or UNCERTAIN | `422: Invalid decision value` |
| **Notes for fraud** | FRAUD decisions require non-empty notes | `422: Notes required for fraud decisions` |
| **No duplicate resolution** | Alert must not already be RESOLVED or CLOSED | `409: Alert already resolved` |

### Validation Flow

```
Decision Submitted
        │
        ▼
┌─────────────────┐     NO
│ Alert IN_REVIEW? │────────► 400 Error
└───────┬─────────┘
        │ YES
        ▼
┌─────────────────┐     NO
│ Correct analyst? │────────► 403 Error
└───────┬─────────┘
        │ YES
        ▼
┌─────────────────┐     NO
│ Valid decision?  │────────► 422 Error
└───────┬─────────┘
        │ YES
        ▼
┌─────────────────┐     NO
│ Notes if FRAUD?  │────────► 422 Error
└───────┬─────────┘
        │ YES
        ▼
┌─────────────────┐     NO
│ Not duplicate?   │────────► 409 Error
└───────┬─────────┘
        │ YES
        ▼
   ✅ Accept Decision
   • Create feedback record
   • Update alert status → RESOLVED
   • Log investigation entry
```

---

## 6.6 Human-in-the-Loop Learning Design

> **Design Rule: Feedback is data. Treat it like gold.**

Human decisions are not just outcomes — they are **training signals** that improve the system over time.

### Feedback Types and Their Meaning

| Decision | System Interpretation | Learning Signal |
|----------|----------------------|-----------------|
| **FRAUD** | True positive — detection was correct | Positive reinforcement for contributing detectors |
| **FALSE_POSITIVE** | Model overreach — detection was wrong | Negative signal — detectors need adjustment |
| **UNCERTAIN** | Boundary case | Weak signal — may indicate threshold is near-optimal |

### How Feedback Is Used

```
┌──────────────┐
│   FEEDBACK   │
│   RECORD     │
└──────┬───────┘
       │
       ├──► Threshold Tuning
       │    "If FP rate > 30%, raise alert threshold by 5%"
       │
       ├──► Weight Adjustment
       │    "Detector X produced 70% of false positives → reduce its weight"
       │
       ├──► Model Retraining Dataset
       │    "Labelled feedback becomes supervised training data"
       │    (tracked via used_for_training flag in feedback table)
       │
       └──► Feature Refinement
            "Feature Y contributed to most FPs → review its computation"
```

### Training Data Pipeline

```
feedback table
    │
    │  WHERE used_for_training = FALSE
    │
    ▼
┌──────────────────────┐
│  Training Batch      │
│  • Batch ID assigned │
│  • Labels extracted  │
│  • Features joined   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Model Retrained     │
│  • New version       │
│  • A/B tested        │
│  • Deployed if better│
└──────────┬───────────┘
           │
           ▼
   feedback.used_for_training = TRUE
   feedback.training_batch_id = <batch_id>
```

---

## 6.7 False Positive Management (System Level)

### Root Cause Dimensions

When a false positive occurs, the system investigates *why* across four dimensions:

| Dimension | Question | Example |
|-----------|----------|---------|
| **Feature noise** | Was a feature value misleading? | Geo-IP wrongly flagged due to VPN |
| **Threshold too low** | Was the alerting threshold too aggressive? | Threshold at 0.45 catches too many edge cases |
| **Context missing** | Did the system lack information that would have prevented the alert? | Payroll day not accounted for in baseline |
| **Model disagreement** | Did only one detector flag it? | ML said anomaly, statistical + behavioral said normal |

### Reduction Strategies

| Strategy | Mechanism | Impact |
|----------|-----------|--------|
| **Per-entity thresholds** | High-volume entities get a higher baseline | Reduces retail noise by ~40% |
| **Context-aware suppression** | Known legitimate patterns (payroll, batch processing) are whitelisted | Eliminates predictable false positives |
| **Alert deduplication** | Same entity + same pattern within time window = single alert | Reduces alert volume during storms |
| **Analyst-driven suppression** | Analysts can flag patterns as "known safe" | Creates supervised suppression rules |
| **Multi-detector agreement** | Single-detector flags are downweighted | Higher confidence = fewer false positives |

### False Positive Rate Tracking

```
Daily FP Rate = (FALSE_POSITIVE decisions) / (Total decisions) × 100

Target: FP Rate < 25%
Warning: FP Rate 25–35%
Critical: FP Rate > 35% → automatic threshold adjustment triggered
```

---

## 6.8 SLA & Operational Controls

### SLA Definitions

| Severity | Response SLA | Resolution SLA | Escalation |
|----------|-------------|----------------|------------|
| 🔴 **CRITICAL** | 15 minutes | 2 hours | Auto-escalate to supervisor after 15m |
| 🟠 **HIGH** | 1 hour | 8 hours | Auto-escalate after 1h |
| 🟡 **MEDIUM** | 4 hours | 24 hours | Auto-escalate after 4h |
| 🟢 **LOW** | End of day | 72 hours | Batch review acceptable |

### System Responsibilities

| Responsibility | Implementation |
|---------------|----------------|
| **Track alert age** | `detection_time` vs current time |
| **SLA countdown** | Computed field: `sla_remaining = sla_deadline - now()` |
| **Escalate overdue** | Alerts approaching SLA deadline get priority boost |
| **Surface breaches** | Dashboard widget: "X alerts breaching SLA" |
| **Report compliance** | Metrics snapshot: SLA compliance rate per period |

### SLA Pressure Visualization

```
Alert Age Timeline:
├─── 0 min ────────── 15 min ────────── 1 hour ────────── 4 hours ───►
│                        │                  │                  │
│    CRITICAL            │                  │                  │
│    ████████████████████ SLA BREACH        │                  │
│                                           │                  │
│    HIGH                                   │                  │
│    ██████████████████████████████████████████ SLA BREACH     │
│                                                              │
│    MEDIUM                                                    │
│    ██████████████████████████████████████████████████████████████
```

---

## 6.9 Audit & Traceability

> **Design Rule: If it can't be audited, it's not production-ready.**

### The 5 Audit Questions

Every closed alert must answer these questions with traceable evidence:

| # | Question | Data Source |
|---|----------|-------------|
| 1 | **What triggered it?** | `transactions` → `feature_snapshots` → `alerts` |
| 2 | **Which models contributed?** | `model_score_records` (per-model, versioned) |
| 3 | **Who reviewed it?** | `investigations` (analyst_id, analyst_name) |
| 4 | **What was decided?** | `feedback` (decision, notes, confidence) |
| 5 | **When was it closed?** | `investigations` + `feedback.resolved_at` |

### Complete Audit Trail Example

```
ALERT: ALT-1042 (CRITICAL, Risk Score: 92.3)
│
├── TRIGGER
│   Transaction: TXN-10181 | $48,500 | 03:15 AM | API channel
│   Entity: User #42521 (Account ACC-8039)
│
├── DETECTION (Run: dr-7a3f...)
│   Features computed: 10 features across 5 categories
│   ├── amount_zscore: 4.2 (STATISTICAL)
│   ├── frequency_deviation: 2.8 (BEHAVIORAL)
│   ├── geo_risk_score: 0.91 (GEOGRAPHIC)
│   └── ... (7 more)
│
├── SCORING
│   ├── Statistical:  0.72 (v1.0.0, confidence: 0.89)
│   ├── Behavioral:   0.88 (v1.0.0, confidence: 0.94)
│   └── ML Ensemble:  0.95 (v3.0.0, confidence: 0.87)
│   Composite: 0.923 → CRITICAL
│
├── INVESTIGATION TIMELINE
│   ├── 10:15:00  CREATED → ACTIVE
│   ├── 10:17:23  ACTIVE → IN_REVIEW (analyst: Sarah Chen)
│   ├── 10:22:45  NOTE: "Confirmed geo mismatch — user's
│   │                     known location is NYC, transaction
│   │                     originated from Lagos, Nigeria"
│   ├── 10:28:12  NOTE: "Destination account flagged in 2
│   │                     previous confirmed fraud cases"
│   └── 10:31:05  DECISION: FRAUD (confidence: 0.95)
│
├── FEEDBACK
│   Decision: FRAUD
│   Analyst: Sarah Chen (analyst-001)
│   Confidence: 0.95
│   Notes: "Geo mismatch + previously flagged destination"
│   Resolved at: 10:31:05
│   Used for training: FALSE (pending next batch)
│
└── RESOLUTION
    Total investigation time: 13 minutes 42 seconds
    SLA status: WITHIN SLA (CRITICAL = 15 minute SLA)
```

---

## 6.10 Continuous Improvement Loop

### The Feedback Loop

```
┌─────────────┐     ┌─────────────┐     ┌───────────────┐     ┌─────────────┐
│  Detection  │────▶│   Alert     │────▶│ Investigation │────▶│  Feedback   │
│  Engine     │     │  Created    │     │  Completed    │     │  Captured   │
└─────────────┘     └─────────────┘     └───────────────┘     └──────┬──────┘
      ▲                                                              │
      │                                                              │
      │         ┌──────────────────────────────────────┐             │
      └─────────│  Model & Threshold Updates           │◄────────────┘
                │  • Retrained models                  │
                │  • Adjusted weights                  │
                │  • Tuned thresholds                  │
                │  • New suppression rules             │
                └──────────────────────────────────────┘
```

### Improvement Triggers

| Trigger | Signal | Response |
|---------|--------|----------|
| **Precision drop** | Confirmed fraud rate among alerts falls below 60% | Review detector weights; retrain ML |
| **False positive spike** | FP rate exceeds 35% for 3 consecutive days | Raise thresholds; add suppression rules |
| **New fraud pattern** | Cluster of confirmed frauds with novel feature profile | Feature engineering review; model update |
| **Analyst feedback trend** | Consistent notes mentioning same root cause | Add new feature or context signal |
| **Volume anomaly** | Alert volume ±50% without business explanation | Investigate detection pipeline health |

### Improvement Cadence

| Review | Frequency | Scope |
|--------|-----------|-------|
| **Threshold review** | Weekly | Are thresholds producing acceptable FP rates? |
| **Weight review** | Bi-weekly | Are detector weights balanced per precision? |
| **Model retraining** | When triggered by drift | Full ML model retraining with new labels |
| **Feature review** | Monthly | Are features still informative? Any new ones needed? |
| **System health** | Daily (automated) | Score distributions, volume, latency |

---

## Alignment with Previous Steps

### Step 4 (Database) ↔ Step 6 (Operations) Mapping

| Operational Concept | Database Entity | Key Fields |
|--------------------|----------------|------------|
| Alert lifecycle states | `alerts` | `status`, `updated_at` |
| State transition audit | `investigations` | `action`, `old_status`, `new_status` |
| Analyst decisions | `feedback` | `decision`, `confidence`, `notes` |
| SLA tracking | `alerts` | `detection_time` vs system clock |
| Training signal pipeline | `feedback` | `used_for_training`, `training_batch_id` |
| Dashboard metrics | `metrics_snapshots` | `resolved_alerts`, `false_positives`, `precision` |

### Step 5 (Detection) ↔ Step 6 (Operations) Mapping

| Detection Output | Operational Use |
|-----------------|----------------|
| Composite risk score | Alert prioritisation (§6.3) |
| Severity classification | SLA assignment (§6.8) |
| Explainability artifacts | Investigation context (§6.4) |
| Per-detector scores | Audit trail (§6.9) |
| Feature contributions | Analyst decision support (§6.4) |
| False positive signals | Threshold tuning (§6.7) |

---

> 🔒 **STEP 6 COMPLETE**  
> The system now has a documented operational architecture:  
> ✔ Alert lifecycle (5-state FSM with audit)  
> ✔ Priority-based analyst queues  
> ✔ 5-step investigation workflow  
> ✔ Decision validation rules  
> ✔ Human-in-the-loop learning pipeline  
> ✔ False positive management strategy  
> ✔ SLA definitions and escalation  
> ✔ Audit-grade traceability  
> ✔ Continuous improvement loop  
