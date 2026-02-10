"""
Database Models (SQLAlchemy)
============================
Step 4 — Complete database schema for the fraud detection system.

Design Principles:
  • Immutability: Transactions and scores are append-only
  • Auditability: Every decision is traceable from transaction → feedback
  • Time-aware: All records carry created_at (and updated_at where mutable)
  • Model-agnostic: Scores are versioned per model+version, not overwritten
  • Separation: Detection ≠ Investigation ≠ Feedback

Entity Relationship:
  Transaction
      ↓
  FeatureSnapshot (per detection run)
      ↓
  Alert
      ↓
  ModelScoreRecord (per model per alert)
      ↓
  Investigation (append-only audit trail)
      ↓
  Feedback / Learning Signal
"""

from datetime import datetime
from typing import Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    String,
    Float,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    Index,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import (
    AlertSeverity,
    AlertStatus,
    EntityType,
    FeedbackDecision,
    FeatureCategory,
    InvestigationAction,
    MetricScope,
    MetricPeriod,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uuid() -> str:
    """Generate a UUID4 primary key value."""
    return str(uuid.uuid4())


# ===================================================================
# 1. TRANSACTION  — append-only, immutable
# ===================================================================

class TransactionModel(Base):
    """
    Immutable record of a single financial / trading event.

    Design rules:
      • Never altered after ingestion.
      • Always timestamped at ingestion (created_at) and event (timestamp).
      • Ground truth input to every downstream entity.
    """

    __tablename__ = "transactions"

    # --- Identity ---
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )
    transaction_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True,
        comment="Business-facing transaction identifier"
    )

    # --- Monetary details ---
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # --- Time & channel ---
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True,
        comment="Original event timestamp"
    )
    channel: Mapped[Optional[str]] = mapped_column(
        String(50), comment="Transaction channel (API, WEB, POS, ATM, etc.)"
    )

    # --- Entity involved ---
    entity_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Originating entity (user/account/device ID)"
    )
    entity_type: Mapped[EntityType] = mapped_column(
        SQLEnum(EntityType), nullable=False
    )
    source_account: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    destination_account: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )

    # --- Context (IP, geo, device) ---
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(100))
    geo_country: Mapped[Optional[str]] = mapped_column(
        String(3), comment="ISO 3166-1 alpha-2 country code"
    )
    geo_city: Mapped[Optional[str]] = mapped_column(String(100))
    geo_lat: Mapped[Optional[float]] = mapped_column(Float)
    geo_lon: Mapped[Optional[float]] = mapped_column(Float)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512))

    # --- Ingestion timestamp (immutable) ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
        comment="Record ingestion time — never updated"
    )

    # --- Relationships ---
    feature_snapshots: Mapped[List["FeatureSnapshotModel"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )
    alerts: Mapped[List["AlertModel"]] = relationship(
        back_populates="transaction"
    )

    __table_args__ = (
        Index("ix_txn_entity_time", "entity_id", "timestamp"),
        Index("ix_txn_source_dest", "source_account", "destination_account"),
        Index("ix_txn_amount_time", "timestamp", "amount"),
    )


# ===================================================================
# 2. FEATURE SNAPSHOT  — per transaction, per detection run
# ===================================================================

class FeatureSnapshotModel(Base):
    """
    Derived features captured at the moment of detection.

    Design rules:
      • Stored per transaction per detection_run_id for reproducibility.
      • Flexible name/value pairs with a category for filtering.
      • Never updated — insert a new snapshot for a re-run.
    """

    __tablename__ = "feature_snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )

    # --- References ---
    transaction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id"), nullable=False, index=True
    )
    detection_run_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True,
        comment="Groups features belonging to the same detection run"
    )

    # --- Feature data ---
    feature_name: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Human-readable feature name, e.g. amount_zscore"
    )
    feature_value: Mapped[float] = mapped_column(Float, nullable=False)
    feature_category: Mapped[FeatureCategory] = mapped_column(
        SQLEnum(FeatureCategory), nullable=False
    )
    feature_description: Mapped[Optional[str]] = mapped_column(
        String(255), comment="Optional explanation of the feature"
    )

    # --- Model context ---
    model_version: Mapped[Optional[str]] = mapped_column(
        String(20), comment="Model version that produced / used this feature"
    )

    # --- Timestamp (immutable) ---
    computed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
        comment="When this feature was computed"
    )

    # --- Relationship ---
    transaction: Mapped["TransactionModel"] = relationship(
        back_populates="feature_snapshots"
    )

    __table_args__ = (
        Index("ix_feat_txn_run", "transaction_id", "detection_run_id"),
        Index("ix_feat_name_cat", "feature_name", "feature_category"),
    )


# ===================================================================
# 3. ALERT  — append-only creation, mutable status only
# ===================================================================

class AlertModel(Base):
    """
    A detection outcome that crossed a risk threshold.

    Design rules:
      • Score history is preserved in ModelScoreRecord, not here.
      • Status may evolve; all transitions logged in Investigation.
      • updated_at tracks the latest status mutation.
    """

    __tablename__ = "alerts"

    # --- Identity ---
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )
    alert_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True,
        comment="Business-facing alert ID, e.g. ALT-001"
    )

    # --- Core detection data ---
    entity: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Entity display label (User #42521, Account #8839)"
    )
    entity_type: Mapped[EntityType] = mapped_column(
        SQLEnum(EntityType), nullable=False
    )
    risk_score: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Composite risk score at detection time (0–100)"
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        SQLEnum(AlertSeverity), nullable=False, index=True
    )
    status: Mapped[AlertStatus] = mapped_column(
        SQLEnum(AlertStatus), nullable=False, index=True,
        default=AlertStatus.ACTIVE
    )
    description: Mapped[Optional[str]] = mapped_column(Text)

    # --- References ---
    transaction_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("transactions.id"), nullable=True, index=True,
        comment="Primary triggering transaction"
    )
    detection_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), index=True,
        comment="Links to feature snapshots from the same run"
    )

    # --- Timestamps ---
    detection_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow,
        comment="Exact moment the detection engine flagged this"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
        comment="Row insertion time"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
        nullable=False, comment="Last status mutation"
    )

    # --- Relationships ---
    transaction: Mapped[Optional["TransactionModel"]] = relationship(
        back_populates="alerts"
    )
    model_scores: Mapped[List["ModelScoreRecordModel"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )
    investigations: Mapped[List["InvestigationModel"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )
    feedback: Mapped[Optional["FeedbackModel"]] = relationship(
        back_populates="alert", uselist=False
    )

    __table_args__ = (
        Index("ix_alert_status_severity", "status", "severity"),
        Index("ix_alert_detection_time", "detection_time"),
        Index("ix_alert_entity_time", "entity", "detection_time"),
    )


# ===================================================================
# 4. MODEL SCORE RECORD  — per model, per alert, versioned
# ===================================================================

class ModelScoreRecordModel(Base):
    """
    Individual model output for an alert.

    Design rules:
      • Never overwrite — create a new row for a new model version.
      • Supports composite scoring: multiple models feed one alert.
      • Stores both raw and normalised scores for transparency.
    """

    __tablename__ = "model_score_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )

    # --- References ---
    alert_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alerts.id"), nullable=False, index=True
    )
    detection_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), index=True,
        comment="Same detection run as the alert & features"
    )

    # --- Model identity ---
    model_name: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="e.g. statistical, behavioral, ml_ensemble"
    )
    model_version: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="Semantic version of the model"
    )

    # --- Scores ---
    raw_score: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Unprocessed model output"
    )
    normalized_score: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Score normalised to 0–100 scale"
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0,
        comment="Model's confidence in its score (0–1)"
    )
    weight: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0,
        comment="Weight used in composite scoring"
    )

    # --- Explainability ---
    explanations: Mapped[Optional[str]] = mapped_column(
        Text, comment="JSON array of explanation strings"
    )

    # --- Timestamp (immutable) ---
    scored_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # --- Relationship ---
    alert: Mapped["AlertModel"] = relationship(back_populates="model_scores")

    __table_args__ = (
        Index("ix_score_alert_model", "alert_id", "model_name"),
        UniqueConstraint(
            "alert_id", "model_name", "model_version",
            name="uq_score_per_model_version"
        ),
    )


# ===================================================================
# 5. INVESTIGATION  — append-only audit trail
# ===================================================================

class InvestigationModel(Base):
    """
    Human analysis actions on an alert (append-only audit log).

    Design rules:
      • One alert → many investigation entries (timeline).
      • Every status change, note, or decision is a separate row.
      • Rows are never modified after creation.
    """

    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )

    # --- Reference ---
    alert_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alerts.id"), nullable=False, index=True
    )

    # --- Action detail ---
    action: Mapped[InvestigationAction] = mapped_column(
        SQLEnum(InvestigationAction), nullable=False,
        comment="Type of investigation action"
    )
    old_status: Mapped[Optional[str]] = mapped_column(String(20))
    new_status: Mapped[Optional[str]] = mapped_column(String(20))
    decision: Mapped[Optional[str]] = mapped_column(
        String(20), comment="FRAUD / LEGITIMATE / REVIEW (for DECISION_SUBMITTED)"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # --- Analyst ---
    analyst_id: Mapped[Optional[str]] = mapped_column(
        String(100), index=True
    )
    analyst_name: Mapped[Optional[str]] = mapped_column(String(200))

    # --- Timestamp (immutable) ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True,
        comment="When this action was recorded"
    )

    # --- Relationship ---
    alert: Mapped["AlertModel"] = relationship(back_populates="investigations")

    __table_args__ = (
        Index("ix_inv_alert_time", "alert_id", "created_at"),
        Index("ix_inv_analyst_time", "analyst_id", "created_at"),
    )


# ===================================================================
# 6. FEEDBACK / LEARNING SIGNAL  — immutable
# ===================================================================

class FeedbackModel(Base):
    """
    Final labelled outcome for a resolved alert.

    Design rules:
      • One alert → exactly one feedback record.
      • Immutable after creation — preserved for ML training.
      • `used_for_training` tracks whether the signal was consumed.
    """

    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )
    feedback_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True,
        comment="Business-facing feedback ID"
    )

    # --- Reference ---
    alert_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alerts.id"),
        nullable=False, unique=True, index=True
    )

    # --- Decision ---
    decision: Mapped[FeedbackDecision] = mapped_column(
        SQLEnum(FeedbackDecision), nullable=False
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float, comment="Analyst confidence (0–1)"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # --- Analyst ---
    analyst_id: Mapped[Optional[str]] = mapped_column(
        String(100), index=True
    )
    analyst_name: Mapped[Optional[str]] = mapped_column(String(200))

    # --- ML training ---
    used_for_training: Mapped[bool] = mapped_column(
        Boolean, default=False,
        comment="Whether this signal has been consumed for retraining"
    )
    training_batch_id: Mapped[Optional[str]] = mapped_column(
        String(36), comment="ID of the training batch that used this"
    )

    # --- Timestamps (immutable) ---
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow,
        comment="When the analyst submitted the final label"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
        comment="Row insertion time"
    )

    # --- Relationship ---
    alert: Mapped["AlertModel"] = relationship(back_populates="feedback")

    __table_args__ = (
        Index("ix_feedback_decision_time", "decision", "resolved_at"),
        Index("ix_feedback_analyst", "analyst_id", "resolved_at"),
        Index("ix_feedback_training", "used_for_training"),
    )


# ===================================================================
# 7. AGGREGATED METRICS  — rolling window snapshots
# ===================================================================

class MetricsSnapshotModel(Base):
    """
    Pre-computed KPIs for fast dashboard rendering.

    Design rules:
      • Computed offline (not real-time queries).
      • Scoped: global, per-model, per-severity, per-entity-type.
      • Old windows can be pruned by the retention policy.
    """

    __tablename__ = "metrics_snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )

    # --- Time bucket ---
    window_start: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True,
        comment="Start of the aggregation window"
    )
    window_end: Mapped[datetime] = mapped_column(
        DateTime, nullable=False,
        comment="End of the aggregation window"
    )
    period: Mapped[MetricPeriod] = mapped_column(
        SQLEnum(MetricPeriod), nullable=False
    )

    # --- Scope ---
    scope: Mapped[MetricScope] = mapped_column(
        SQLEnum(MetricScope), nullable=False, default=MetricScope.GLOBAL
    )
    scope_value: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Qualifier when scope is MODEL/SEVERITY/ENTITY_TYPE"
    )

    # --- Volume counts ---
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    total_alerts: Mapped[int] = mapped_column(Integer, default=0)
    critical_alerts: Mapped[int] = mapped_column(Integer, default=0)
    high_alerts: Mapped[int] = mapped_column(Integer, default=0)
    medium_alerts: Mapped[int] = mapped_column(Integer, default=0)
    low_alerts: Mapped[int] = mapped_column(Integer, default=0)

    # --- Resolution counts ---
    resolved_alerts: Mapped[int] = mapped_column(Integer, default=0)
    confirmed_frauds: Mapped[int] = mapped_column(Integer, default=0)
    false_positives: Mapped[int] = mapped_column(Integer, default=0)

    # --- Performance metrics ---
    avg_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    precision: Mapped[Optional[float]] = mapped_column(Float)
    recall: Mapped[Optional[float]] = mapped_column(Float)
    f1_score: Mapped[Optional[float]] = mapped_column(Float)
    avg_resolution_time_sec: Mapped[Optional[float]] = mapped_column(
        Float, comment="Average seconds from alert → resolution"
    )

    # --- Timestamp ---
    computed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
        comment="When this snapshot was generated"
    )

    __table_args__ = (
        Index("ix_metrics_window", "window_start", "period"),
        Index("ix_metrics_scope", "scope", "scope_value", "window_start"),
        UniqueConstraint(
            "window_start", "period", "scope", "scope_value",
            name="uq_metrics_window_scope"
        ),
    )
