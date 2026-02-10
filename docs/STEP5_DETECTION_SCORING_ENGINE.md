# Step 5 — Detection & Scoring Engine: Intelligence Architecture

> **Scope:** How the system *thinks* — not how it's coded.  
> **Status:** 🔒 DESIGNED  
> **Last updated:** 2026-02-10  

---

## 5.1 Role of the Detection & Scoring Engine

The engine is the brain of the system. It answers four critical questions for every transaction that enters the pipeline:

| # | Question | Output |
|---|----------|--------|
| 1 | **Is this behavior unusual?** | Boolean signal per detector |
| 2 | **How unusual is it?** | Normalised risk score ∈ [0, 1] |
| 3 | **Why is it unusual?** | Explainability artifact per alert |
| 4 | **Is it important enough to alert a human?** | Alert trigger decision |

### Engine Properties

| Property | Meaning |
|----------|---------|
| **Modular** | Each detector is independently deployable and replaceable |
| **Explainable** | Every score can be traced back to specific features and detectors |
| **Extensible** | New detection layers can be added without modifying existing ones |
| **Safe against false positives** | Built-in suppression, adaptive thresholds, feedback loops |

---

## 5.2 Design Philosophy

### Core Principle

> **No single model decides fraud. Signals are combined.**

This is the foundational rule. It means:

- Multiple detectors run **in parallel** on every transaction
- Each detector produces a **normalised score** in [0, 1]
- Scores are **fused** into a single composite risk score
- **Thresholds** — not models — decide whether to alert

### Why This Matters

| Single-model approach | Multi-signal approach (ours) |
|---|---|
| One model failure = missed fraud | Redundancy across layers |
| Hard to explain decisions | Each layer contributes interpretable signals |
| Retraining breaks everything | Individual detectors retrained independently |
| Brittle against novel attacks | Diverse detection surfaces |

---

## 5.3 Detection Layers

The engine uses three logical detection layers, each specialised for a different class of anomaly.

```
┌─────────────────────────────────────────────────────┐
│                   TRANSACTION                        │
└──────────┬──────────────┬──────────────┬────────────┘
           │              │              │
           ▼              ▼              ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │  LAYER 1     │ │  LAYER 2     │ │  LAYER 3     │
   │  Statistical │ │  Behavioral  │ │  ML-Based    │
   │  Detection   │ │  Detection   │ │  Detection   │
   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
          │                │                │
          ▼                ▼                ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │  Score: 0–1  │ │  Score: 0–1  │ │  Score: 0–1  │
   │  + Reasons   │ │  + Reasons   │ │  + Reasons   │
   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
          │                │                │
          └────────┬───────┴────────┬───────┘
                   ▼                │
          ┌────────────────┐       │
          │ COMPOSITE RISK │◄──────┘
          │    SCORER      │
          └───────┬────────┘
                  ▼
          ┌────────────────┐
          │ ALERT DECISION │
          └────────────────┘
```

---

### Layer 1: Statistical Detection

**Purpose:** Fast baseline anomaly detection — catch extreme deviations that don't need context.

| Aspect | Detail |
|--------|--------|
| **Signals** | Amount deviation (Z-score), frequency deviation, time-of-day deviation |
| **Baseline** | Global distribution statistics (mean, std, percentiles) |
| **Characteristics** | Deterministic, interpretable, low latency |
| **Strength** | Catches obvious outliers immediately |
| **Weakness** | Blind to entity-specific patterns |

**How it thinks:**  
"This transaction is 4.2 standard deviations above the global average amount. That alone is statistically extreme."

**Explainability output:**
```
Signal: amount_zscore = 4.2 (threshold: 3.0)
Reason: "Transaction amount $48,500 exceeds 99.9th percentile of all transactions"
```

---

### Layer 2: Behavioral Detection

**Purpose:** Detect changes relative to the *same entity's* past behavior — not the global population.

| Aspect | Detail |
|--------|--------|
| **Signals** | Deviation from user baseline, velocity shifts, pattern changes |
| **Baseline** | Per-entity historical profile (rolling windows) |
| **Characteristics** | Personalised, context-aware |
| **Strength** | Catches low-and-slow fraud, account takeover, gradual escalation |
| **Weakness** | Requires history; cold-start for new entities |

**How it thinks:**  
"This user normally transacts $200–$500 on weekdays via the app. Today they sent $12,000 via API at 3 AM to a new destination. That's unusual *for them*."

**Explainability output:**
```
Signal: amount_deviation_from_baseline = 24x
Signal: new_channel = true (first API transaction)
Signal: unusual_hour = true (03:00 vs typical 09:00–18:00)
Reason: "Entity ENT-1042 deviated from personal baseline across 3 dimensions"
```

---

### Layer 3: ML-Based Anomaly Detection

**Purpose:** Discover novel and non-obvious anomalies that rule-based systems miss.

| Aspect | Detail |
|--------|--------|
| **Signals** | Multi-feature patterns, cross-feature interactions |
| **Characteristics** | Probabilistic, non-linear, model-agnostic |
| **Strength** | Catches unknown fraud patterns, multi-dimensional anomalies |
| **Weakness** | Less interpretable, requires periodic retraining |

**How it thinks:**  
"Looking at all 15 features together, this transaction falls in a region of feature space where only 0.3% of past transactions existed. It's a statistical outlier in the multi-dimensional sense, even if no single feature is extreme."

**Explainability output:**
```
Signal: isolation_score = 0.87 (anomaly threshold: 0.65)
Signal: top_contributing_features = [velocity_score, geo_risk, amount_pct_change]
Reason: "Rare multi-dimensional pattern detected — combination of features is unusual"
```

**Model-agnostic design:** The ML layer is a *slot*, not a specific algorithm. It can host Isolation Forest, Autoencoders, or any future model. The interface is fixed; the internals are swappable.

---

## 5.4 Score Normalisation Strategy

### The Problem

Different detectors produce different score ranges:

| Detector | Raw Output | Range |
|----------|-----------|-------|
| Statistical | Z-scores | (-∞, +∞) |
| Behavioral | Deviation multiples | [0, +∞) |
| ML | Isolation/probability scores | [0, 1] or arbitrary |

### The Solution

All detector outputs are **normalised to [0, 1]** before fusion.

```
Raw Score → Normaliser → Normalised Score ∈ [0, 1]
```

| Normalisation Method | When Used |
|---------------------|-----------|
| **Sigmoid** | Unbounded scores (Z-scores) — compresses extreme values |
| **Min-Max** | Bounded scores with known range |
| **Percentile** | When distribution shape is unknown — rank-based |
| **Clamp + Linear** | When domain bounds are well-understood |

### Why This Matters

| Without normalisation | With normalisation |
|---|---|
| Statistical Z-score of 5.0 dominates ML score of 0.8 | Both contribute proportionally |
| Thresholds are model-specific | One threshold works across all detectors |
| Adding a new detector breaks scoring | New detectors plug in seamlessly |

---

## 5.5 Composite Risk Scoring

### Purpose

Produce **one number** the system can act on.

### Conceptual Formula

```
Final Risk Score = (Statistical × W₁) + (Behavioral × W₂) + (ML × W₃)

where W₁ + W₂ + W₃ = 1.0
```

### Default Weights

| Detector | Weight | Rationale |
|----------|--------|-----------|
| Statistical | 0.25 | Fast but shallow — good first filter |
| Behavioral | 0.35 | Strongest signal for known entities |
| ML | 0.40 | Best at catching novel patterns |

### Weight Design Rules

| Rule | Rationale |
|------|-----------|
| **Weights are configuration, not code** | Tunable without deployment |
| **Weights are versioned** | Every weight change is tracked in `model_score_records` |
| **Weights sum to 1.0** | Ensures score stays in [0, 1] after fusion |
| **Weights are adjustable per entity type** | Trading accounts may weight ML higher than retail |

### Score Fusion Diagram

```
Statistical Score: 0.72 ──┐
                          │  × 0.25 = 0.180
                          │
Behavioral Score: 0.88 ───┤  × 0.35 = 0.308
                          │
ML Score: 0.64 ───────────┤  × 0.40 = 0.256
                          │
                          ▼
              Composite: 0.744 → MEDIUM severity
```

---

## 5.6 Severity Classification

The composite risk score is mapped to human-friendly severity labels.

| Risk Score | Severity | Colour | Analyst Action |
|------------|----------|--------|----------------|
| ≥ 0.80 | **CRITICAL** | 🔴 Red | Immediate investigation required |
| 0.70 – 0.79 | **HIGH** | 🟠 Orange | Investigate within 1 hour |
| 0.50 – 0.69 | **MEDIUM** | 🟡 Yellow | Review in daily triage |
| < 0.50 | **LOW** | 🟢 Green | Monitor only (no alert by default) |

### Purpose

- **Reduce analyst cognitive load** — don't make humans interpret raw scores
- **Enable alert prioritisation** — CRITICAL before HIGH before MEDIUM
- **Support SLA definitions** — "all CRITICAL alerts investigated within 15 minutes"

### Design Rule

> Severity thresholds are **configurable** via environment variables, not hardcoded.

```
RISK_THRESHOLD_HIGH=0.80
RISK_THRESHOLD_MEDIUM=0.50
RISK_THRESHOLD_LOW=0.20
```

---

## 5.7 Alert Triggering Logic

**Not every anomaly becomes an alert.** The system applies three gates before creating an alert:

```
                    Composite Risk Score
                           │
                           ▼
                ┌──────────────────────┐
          NO    │  Score > threshold?   │
       ◄────────│                      │
                └──────────┬───────────┘
                           │ YES
                           ▼
                ┌──────────────────────┐
          NO    │  Entity NOT already  │
       ◄────────│  under investigation?│
                └──────────┬───────────┘
                           │ YES
                           ▼
                ┌──────────────────────┐
          NO    │  Rate limit not      │
       ◄────────│  exceeded?           │
                └──────────┬───────────┘
                           │ YES
                           ▼
                   ┌──────────────┐
                   │ CREATE ALERT │
                   └──────────────┘
```

### Gate 1: Threshold Check
Only scores above the operational threshold produce alerts. LOW scores are logged but never alert.

### Gate 2: Duplicate Suppression
If the same entity already has an ACTIVE or INVESTIGATING alert, a new alert is **not** created. Instead, the existing alert's score may be updated.

### Gate 3: Rate Limiting
Maximum N alerts per entity per time window. Prevents alert storms from a single noisy entity.

---

## 5.8 Explainability Design

> **Design Rule:** Every alert must answer three questions for the analyst.

### The Three Questions

| Question | Explainability Artifact |
|----------|----------------------|
| **Why was it flagged?** | Feature deviation list — which features contributed most |
| **Which detectors agreed?** | Detector contribution breakdown with individual scores |
| **How does it compare to normal?** | Historical baseline comparison |

### Explainability Artifact Structure

For every alert, the system produces:

```
Explainability Package:
├── Feature Contributions
│   ├── amount_zscore: 4.2 (STATISTICAL — HIGH contribution)
│   ├── frequency_deviation: 2.8 (BEHAVIORAL — MEDIUM contribution)
│   ├── geo_risk_score: 0.91 (CONTEXTUAL — HIGH contribution)
│   └── ... (all features ranked by contribution)
│
├── Detector Agreement
│   ├── Statistical: 0.72 (flagged: YES)
│   ├── Behavioral: 0.88 (flagged: YES)
│   └── ML: 0.64 (flagged: YES)
│   └── Agreement: 3/3 detectors agree → HIGH confidence
│
└── Baseline Comparison
    ├── Entity avg amount: $450 → This transaction: $48,500
    ├── Entity typical hour: 09:00–18:00 → This transaction: 03:15
    └── Entity usual channel: MOBILE → This transaction: API
```

### Analyst Trust

Explainability is not a nice-to-have — it's a **trust mechanism**:

- Analysts who understand *why* make faster decisions
- Analysts who trust the system provide better feedback
- Better feedback → better retraining → fewer false positives

---

## 5.9 False Positive Control

> **Design Rule:** False positives are system failures, not analyst problems.

### Preventative Measures (Before Alert)

| Measure | How It Works |
|---------|-------------|
| **Adaptive thresholds** | Thresholds adjust based on rolling false positive rate |
| **Context awareness** | Known legitimate patterns (e.g., payroll cycles) are whitelisted |
| **Entity-specific baselines** | A high-volume trader and a retail user have different "normal" |
| **Multi-detector agreement** | Single-detector flags are downweighted; multi-detector agreement increases score |

### Corrective Measures (After Alert)

| Measure | How It Works |
|---------|-------------|
| **Analyst feedback loop** | `FALSE_POSITIVE` labels in the feedback table feed back into the system |
| **Threshold tuning** | If false positive rate > target, thresholds are raised automatically |
| **Weight adjustment** | Detector weights are rebalanced based on precision per detector |
| **Suppression rules** | Repeated false positives from same pattern are suppressed |

### Feedback Loop Diagram

```
Alert Created → Analyst Reviews → Feedback Submitted
                                        │
                    ┌───────────────────┬┘
                    ▼                   ▼
              FRAUD label         FALSE_POSITIVE label
                    │                   │
                    ▼                   ▼
            Reinforces model    Triggers adjustment:
            confidence          • Raise threshold?
                                • Reduce detector weight?
                                • Add suppression rule?
```

---

## 5.10 Drift & Adaptation

> **Reality:** Fraud evolves. The system must evolve with it.

### Types of Drift

| Drift Type | What Changes | Example |
|-----------|-------------|---------|
| **Data drift** | Input distribution shifts | Average transaction amount increases 3× due to inflation |
| **Behavior drift** | Entity behavior evolves | Users adopt a new payment channel |
| **Fraud strategy drift** | Attackers change tactics | Shift from high-value to many small transactions |

### Drift Detection Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| **Score distribution shift** | Median risk score moves significantly | Review normalisation parameters |
| **False positive spike** | FP rate exceeds target (e.g., >30%) | Raise thresholds, retune weights |
| **Precision degradation** | Confirmed fraud rate drops among alerts | Retrain ML layer |
| **Volume anomaly** | Alert volume changes ±50% without explanation | Investigate root cause |

### Adaptation Responses

```
Drift Detected
      │
      ├──► Minor drift → Adjust thresholds automatically
      │
      ├──► Moderate drift → Retune detector weights
      │                     (uses feedback signals from DB)
      │
      └──► Major drift → Trigger full model retraining
                          (uses labelled feedback as training data)
```

### Design Rule

> Retraining and threshold review are **reactions to measurable drift**, not calendar-scheduled events.

The `feedback` table's `used_for_training` flag ensures:
- Every label is consumed exactly once per training cycle
- Training batches are traceable via `training_batch_id`
- Old labels can be weighted differently from recent ones

---

## Summary: What the Engine Produces

For every transaction processed, the engine outputs:

| Output | Stored In | Retention |
|--------|-----------|-----------|
| Feature snapshot | `feature_snapshots` | Permanent (audit) |
| Per-detector scores | `model_score_records` | Permanent (versioned) |
| Composite risk score | `alerts.risk_score` | Permanent |
| Severity classification | `alerts.severity` | Permanent |
| Explainability artifacts | `model_score_records.explanations` | Permanent |
| Alert decision | `alerts` (if threshold crossed) | Permanent |

---

## Architecture Alignment

This detection & scoring design maps directly to the database schema from Step 4:

```
Transaction (Step 4)
    → FeatureSnapshot (Step 4) ← Feature extraction (Step 5, §5.3)
    → Alert (Step 4) ← Alert triggering logic (Step 5, §5.7)
        → ModelScoreRecord (Step 4) ← Per-detector scores (Step 5, §5.3–5.5)
        → Investigation (Step 4) ← Analyst workflow (Step 5, §5.8)
        → Feedback (Step 4) ← False positive control (Step 5, §5.9–5.10)
```

**Every design concept in Step 5 has a concrete storage location in Step 4.**

---

> 🔒 **STEP 5 COMPLETE**  
> The system now has a documented intelligence architecture:  
> ✔ Multi-layer detection logic  
> ✔ Score normalisation strategy  
> ✔ Composite scoring with versioned weights  
> ✔ Alert severity framework  
> ✔ Explainability-first design  
> ✔ False positive control (preventative + corrective)  
> ✔ Drift-aware adaptation strategy  
