"""
Enumerations
============
Centralized enum definitions for the application.
"""

from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertStatus(str, Enum):
    """Alert status values."""
    ACTIVE = "ACTIVE"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class InvestigationDecision(str, Enum):
    """Investigation decision types."""
    FRAUD = "FRAUD"
    LEGITIMATE = "LEGITIMATE"
    REVIEW = "REVIEW"


class FeedbackDecision(str, Enum):
    """Feedback decision for resolved alerts."""
    FRAUD = "FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class EntityType(str, Enum):
    """Entity types that can trigger alerts."""
    USER = "USER"
    ACCOUNT = "ACCOUNT"
    TRANSACTION = "TRANSACTION"
    DEVICE = "DEVICE"


class RiskLevel(str, Enum):
    """Risk level classification."""
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class TimeRange(str, Enum):
    """Time range options for queries."""
    HOURS_24 = "24h"
    DAYS_7 = "7d"
    DAYS_30 = "30d"
    DAYS_90 = "90d"
    ALL = "all"
