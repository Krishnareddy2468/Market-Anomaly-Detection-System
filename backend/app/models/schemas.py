"""
Pydantic Schemas
================
API request/response schemas that define the contract between frontend and backend.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import (
    AlertSeverity,
    AlertStatus,
    InvestigationDecision,
    FeedbackDecision,
    EntityType,
    RiskLevel,
)


# =============================================================================
# Base Schemas
# =============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PaginationInfo(BaseSchema):
    """Pagination metadata."""
    page: int = Field(..., ge=1)
    total_pages: int = Field(..., ge=0)
    total_records: int = Field(..., ge=0)
    has_next: bool = False
    has_previous: bool = False


class ErrorResponse(BaseSchema):
    """Standard error response."""
    error_code: str
    message: str
    details: Optional[dict] = None


# =============================================================================
# Alert Schemas
# =============================================================================

class Alert(BaseSchema):
    """Alert summary for list views."""
    alert_id: str
    timestamp: datetime
    entity: str
    entity_type: Optional[EntityType] = None
    risk_score: float = Field(..., ge=0, le=100)
    severity: AlertSeverity
    status: AlertStatus


class AlertDetail(BaseSchema):
    """Detailed alert information."""
    alert_id: str
    timestamp: datetime
    entity: str
    entity_type: EntityType
    risk_score: float
    severity: AlertSeverity
    status: AlertStatus
    description: Optional[str] = None
    transaction: Optional["Transaction"] = None
    feature_deviations: List["FeatureDeviation"] = []
    historical_scores: List[float] = []


class AlertFilters(BaseSchema):
    """Alert filtering parameters."""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    search: Optional[str] = None


class AlertsResult(BaseSchema):
    """Internal result for alert queries."""
    alerts: List[Alert]
    pagination: PaginationInfo


class AlertsListResponse(BaseSchema):
    """API response for alerts list."""
    data: List[Alert]
    pagination: PaginationInfo


class AlertDetailResponse(BaseSchema):
    """API response for alert detail."""
    data: AlertDetail


# =============================================================================
# Transaction Schemas
# =============================================================================

class Transaction(BaseSchema):
    """Transaction details."""
    transaction_id: str
    amount: float
    currency: str = "USD"
    timestamp: datetime
    source_account: str
    destination_account: str
    channel: Optional[str] = None
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None


class FeatureDeviation(BaseSchema):
    """Feature deviation from normal behavior."""
    feature: str
    deviation: str
    risk_level: RiskLevel
    value: Optional[float] = None
    baseline: Optional[float] = None


# =============================================================================
# Dashboard Schemas
# =============================================================================

class DashboardMetrics(BaseSchema):
    """Dashboard overview metrics."""
    total_transactions: int
    active_alerts: int
    high_risk_alerts: int
    false_positive_rate: float
    trends: "MetricTrends"


class MetricTrends(BaseSchema):
    """Trend percentages for metrics."""
    alerts_change_pct: float
    false_positive_change_pct: float
    transactions_change_pct: Optional[float] = None


class AlertsTrend(BaseSchema):
    """Time-series data for alerts trend chart."""
    timestamps: List[str]
    values: List[int]


class SeverityDistribution(BaseSchema):
    """Severity distribution for donut chart."""
    name: str
    value: int
    color: str


class DashboardMetricsResponse(BaseSchema):
    """API response for dashboard metrics."""
    data: DashboardMetrics


class AlertsTrendResponse(BaseSchema):
    """API response for alerts trend."""
    data: AlertsTrend


class SeverityDistributionResponse(BaseSchema):
    """API response for severity distribution."""
    data: List[SeverityDistribution]


# =============================================================================
# Investigation Schemas
# =============================================================================

class Investigation(BaseSchema):
    """Investigation context for an alert."""
    alert_id: str
    entity: str
    status: AlertStatus
    risk_score: float
    transaction: Optional[Transaction] = None
    feature_deviations: List[FeatureDeviation] = []
    historical_behavior: List[dict] = []
    notes: List["InvestigationNote"] = []


class InvestigationNote(BaseSchema):
    """Note added during investigation."""
    note_id: str
    content: str
    analyst_id: str
    timestamp: datetime


class InvestigationDecisionRequest(BaseSchema):
    """Request to submit investigation decision."""
    decision: InvestigationDecision
    notes: Optional[str] = None
    analyst_id: Optional[str] = "system"


class InvestigationNoteRequest(BaseSchema):
    """Request to add investigation note."""
    content: str = Field(..., min_length=1, max_length=1000)
    analyst_id: Optional[str] = "system"


class InvestigationDecisionResult(BaseSchema):
    """Internal result for decision submission."""
    success: bool
    new_status: AlertStatus


class InvestigationDetailResponse(BaseSchema):
    """API response for investigation detail."""
    data: Investigation


class InvestigationDecisionResponse(BaseSchema):
    """API response for decision submission."""
    success: bool
    alert_id: str
    updated_status: AlertStatus
    message: str


# =============================================================================
# Analytics Schemas
# =============================================================================

class AnalyticsMetrics(BaseSchema):
    """Model performance metrics."""
    precision: float = Field(..., ge=0, le=100)
    recall: float = Field(..., ge=0, le=100)
    f1_score: float = Field(..., ge=0, le=100)
    alert_volume_daily: int


class ModelPerformance(BaseSchema):
    """Historical model performance."""
    versions: List[str]
    accuracy: List[float]
    timestamps: List[datetime]


class AlertVolume(BaseSchema):
    """Alert volume statistics."""
    labels: List[str]  # Time labels (days/hours)
    alerts: List[int]   # Total alerts
    frauds: List[int]   # Confirmed frauds


class ConfusionMatrix(BaseSchema):
    """Confusion matrix data."""
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int


class AnalyticsMetricsResponse(BaseSchema):
    """API response for analytics metrics."""
    data: AnalyticsMetrics


class ModelPerformanceResponse(BaseSchema):
    """API response for model performance."""
    data: ModelPerformance


class AlertVolumeResponse(BaseSchema):
    """API response for alert volume."""
    data: AlertVolume


# =============================================================================
# Feedback Schemas
# =============================================================================

class Feedback(BaseSchema):
    """Resolved alert feedback record."""
    feedback_id: str
    alert_id: str
    entity: str
    decision: FeedbackDecision
    notes: Optional[str] = None
    resolved_at: datetime
    analyst: str


class FeedbackFilters(BaseSchema):
    """Feedback filtering parameters."""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    decision: Optional[FeedbackDecision] = None
    analyst: Optional[str] = None
    range: str = "30d"


class FeedbackSummary(BaseSchema):
    """Summary statistics for feedback."""
    total_resolutions: int
    confirmed_frauds: int
    false_positives: int
    resolution_rate: float


class FeedbackResult(BaseSchema):
    """Internal result for feedback queries."""
    feedback: List[Feedback]
    pagination: PaginationInfo
    summary: FeedbackSummary


class FeedbackListResponse(BaseSchema):
    """API response for feedback list."""
    data: List[Feedback]
    pagination: PaginationInfo
    summary: FeedbackSummary


# =============================================================================
# Forward References Update
# =============================================================================

AlertDetail.model_rebuild()
Investigation.model_rebuild()
DashboardMetrics.model_rebuild()
