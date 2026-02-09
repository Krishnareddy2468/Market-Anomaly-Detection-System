"""
Database Models (SQLAlchemy)
============================
Database table definitions for the fraud detection system.
"""

from datetime import datetime
from typing import Optional, List
import uuid

from sqlalchemy import (
    String,
    Float,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.models.enums import AlertSeverity, AlertStatus, FeedbackDecision, EntityType


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class TransactionModel(Base):
    """Immutable transaction records."""
    
    __tablename__ = "transactions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    transaction_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Parties
    source_account: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    destination_account: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Context
    channel: Mapped[Optional[str]] = mapped_column(String(50))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(100))
    geo_location: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Scoring (from detection engine)
    risk_score: Mapped[Optional[float]] = mapped_column(Float)
    model_version: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    alerts: Mapped[List["AlertModel"]] = relationship(back_populates="transaction")
    
    __table_args__ = (
        Index("ix_transactions_source_dest", "source_account", "destination_account"),
        Index("ix_transactions_time_score", "timestamp", "risk_score"),
    )


class AlertModel(Base):
    """Append-only alert records."""
    
    __tablename__ = "alerts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    alert_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    
    # Alert details
    entity: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[EntityType] = mapped_column(SQLEnum(EntityType), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(SQLEnum(AlertSeverity), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(SQLEnum(AlertStatus), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Foreign keys
    transaction_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("transactions.id"), nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transaction: Mapped[Optional["TransactionModel"]] = relationship(back_populates="alerts")
    investigations: Mapped[List["InvestigationModel"]] = relationship(back_populates="alert")
    feedback: Mapped[Optional["FeedbackModel"]] = relationship(back_populates="alert", uselist=False)
    
    __table_args__ = (
        Index("ix_alerts_status_severity", "status", "severity"),
        Index("ix_alerts_created", "created_at"),
    )


class InvestigationModel(Base):
    """Investigation actions and notes (append-only audit trail)."""
    
    __tablename__ = "investigations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # Reference
    alert_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alerts.id"), nullable=False, index=True
    )
    
    # Action
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_status: Mapped[Optional[str]] = mapped_column(String(20))
    new_status: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Analyst
    analyst_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    alert: Mapped["AlertModel"] = relationship(back_populates="investigations")


class FeedbackModel(Base):
    """Final decisions for resolved alerts (for ML training)."""
    
    __tablename__ = "feedback"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    feedback_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    
    # Reference
    alert_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alerts.id"), nullable=False, unique=True, index=True
    )
    
    # Decision
    decision: Mapped[FeedbackDecision] = mapped_column(SQLEnum(FeedbackDecision), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Analyst
    analyst_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    alert: Mapped["AlertModel"] = relationship(back_populates="feedback")


class FeatureModel(Base):
    """Computed features for transactions (for ML input)."""
    
    __tablename__ = "features"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # Reference
    transaction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id"), nullable=False, index=True
    )
    
    # Feature data (stored as JSON-like columns for common features)
    amount_zscore: Mapped[Optional[float]] = mapped_column(Float)
    time_deviation: Mapped[Optional[float]] = mapped_column(Float)
    frequency_score: Mapped[Optional[float]] = mapped_column(Float)
    geo_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    device_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    velocity_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Model metadata
    model_version: Mapped[Optional[str]] = mapped_column(String(20))
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MetricsSnapshotModel(Base):
    """Aggregated metrics snapshots for analytics."""
    
    __tablename__ = "metrics_snapshots"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # Time bucket
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(10), nullable=False)  # 'hourly', 'daily'
    
    # Counts
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    total_alerts: Mapped[int] = mapped_column(Integer, default=0)
    critical_alerts: Mapped[int] = mapped_column(Integer, default=0)
    high_alerts: Mapped[int] = mapped_column(Integer, default=0)
    medium_alerts: Mapped[int] = mapped_column(Integer, default=0)
    low_alerts: Mapped[int] = mapped_column(Integer, default=0)
    
    # Resolutions
    resolved_alerts: Mapped[int] = mapped_column(Integer, default=0)
    confirmed_frauds: Mapped[int] = mapped_column(Integer, default=0)
    false_positives: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance
    avg_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    precision: Mapped[Optional[float]] = mapped_column(Float)
    recall: Mapped[Optional[float]] = mapped_column(Float)
