"""
Alert Service
=============
Business logic for alert management, filtering, and status transitions.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import random
import uuid

from app.models.schemas import (
    Alert,
    AlertDetail,
    AlertFilters,
    AlertsResult,
    PaginationInfo,
    Transaction,
    FeatureDeviation,
)
from app.models.enums import AlertSeverity, AlertStatus, EntityType, RiskLevel
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.core.errors import NotFoundError, BusinessRuleViolation
from app.core.logging import get_logger

logger = get_logger(__name__)


class AlertService:
    """Service for alert-related business logic."""
    
    # Valid status transitions
    VALID_TRANSITIONS = {
        AlertStatus.ACTIVE: [AlertStatus.INVESTIGATING, AlertStatus.RESOLVED],
        AlertStatus.INVESTIGATING: [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE, AlertStatus.ACTIVE],
        AlertStatus.RESOLVED: [AlertStatus.ACTIVE],
        AlertStatus.FALSE_POSITIVE: [AlertStatus.ACTIVE],
    }
    
    def __init__(
        self,
        alert_repo: AlertRepository,
        transaction_repo: TransactionRepository,
    ):
        self.alert_repo = alert_repo
        self.transaction_repo = transaction_repo
    
    async def get_alerts(self, filters: AlertFilters) -> AlertsResult:
        """
        Get paginated list of alerts with filtering.
        
        Business rules:
        - Default sort by timestamp descending (newest first)
        - ACTIVE and INVESTIGATING alerts prioritized
        - Search matches alert_id and entity
        """
        logger.info("Fetching alerts", filters=filters.model_dump())
        
        # For MVP, generate mock data
        all_alerts = self._generate_mock_alerts()
        
        # Apply filters
        filtered = all_alerts
        
        if filters.severity:
            filtered = [a for a in filtered if a.severity == filters.severity]
        
        if filters.status:
            filtered = [a for a in filtered if a.status == filters.status]
        
        if filters.search:
            search_lower = filters.search.lower()
            filtered = [
                a for a in filtered
                if search_lower in a.alert_id.lower() or search_lower in a.entity.lower()
            ]
        
        # Sort by timestamp descending
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Paginate
        total = len(filtered)
        start = (filters.page - 1) * filters.limit
        end = start + filters.limit
        page_alerts = filtered[start:end]
        
        total_pages = (total + filters.limit - 1) // filters.limit
        
        return AlertsResult(
            alerts=page_alerts,
            pagination=PaginationInfo(
                page=filters.page,
                total_pages=total_pages,
                total_records=total,
                has_next=filters.page < total_pages,
                has_previous=filters.page > 1,
            ),
        )
    
    async def get_alert_detail(self, alert_id: str) -> AlertDetail:
        """
        Get detailed alert information.
        
        Includes transaction details and feature deviations.
        """
        logger.info("Fetching alert detail", alert_id=alert_id)
        
        # Mock alert detail
        if not alert_id.startswith("ALT-"):
            raise NotFoundError(f"Alert {alert_id} not found")
        
        return AlertDetail(
            alert_id=alert_id,
            timestamp=datetime.now() - timedelta(minutes=random.randint(5, 120)),
            entity=f"User #{random.randint(10000, 99999)}",
            entity_type=EntityType.USER,
            risk_score=random.uniform(60, 98),
            severity=random.choice([AlertSeverity.HIGH, AlertSeverity.CRITICAL]),
            status=AlertStatus.ACTIVE,
            description="Unusual transaction pattern detected",
            transaction=Transaction(
                transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                amount=random.uniform(1000, 50000),
                currency="USD",
                timestamp=datetime.now() - timedelta(minutes=random.randint(10, 60)),
                source_account=f"ACC-{random.randint(10000, 99999)}",
                destination_account=f"ACC-{random.randint(10000, 99999)}",
                channel="API",
                ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            ),
            feature_deviations=[
                FeatureDeviation(
                    feature="Transaction Amount",
                    deviation="+340%",
                    risk_level=RiskLevel.VERY_HIGH,
                ),
                FeatureDeviation(
                    feature="Time of Day",
                    deviation="Unusual Pattern",
                    risk_level=RiskLevel.HIGH,
                ),
                FeatureDeviation(
                    feature="Frequency",
                    deviation="+8x Normal Rate",
                    risk_level=RiskLevel.HIGH,
                ),
                FeatureDeviation(
                    feature="Geographic Location",
                    deviation="New Country",
                    risk_level=RiskLevel.MEDIUM,
                ),
            ],
            historical_scores=[15, 18, 22, 25, 35, 94],
        )
    
    async def update_status(self, alert_id: str, new_status: AlertStatus) -> bool:
        """
        Update alert status with validation.
        
        Enforces valid state transitions.
        """
        logger.info("Updating alert status", alert_id=alert_id, new_status=new_status)
        
        # Get current status (mock)
        current_status = AlertStatus.ACTIVE
        
        # Validate transition
        if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
            raise BusinessRuleViolation(
                f"Invalid status transition: {current_status} → {new_status}"
            )
        
        # Update in repository (would be real DB call)
        # await self.alert_repo.update_status(alert_id, new_status)
        
        logger.info(
            "Alert status updated",
            alert_id=alert_id,
            old_status=current_status,
            new_status=new_status,
        )
        
        return True
    
    def _get_severity_from_score(self, score: float) -> AlertSeverity:
        """Determine severity from risk score."""
        if score >= 90:
            return AlertSeverity.CRITICAL
        elif score >= 70:
            return AlertSeverity.HIGH
        elif score >= 50:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _generate_mock_alerts(self) -> List[Alert]:
        """Generate mock alert data for MVP."""
        alerts = []
        statuses = [AlertStatus.ACTIVE] * 5 + [AlertStatus.INVESTIGATING] * 2 + [
            AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE
        ]
        
        for i in range(15):
            score = random.uniform(30, 98)
            alerts.append(Alert(
                alert_id=f"ALT-{str(i + 1).zfill(3)}",
                timestamp=datetime.now() - timedelta(minutes=random.randint(5, 300)),
                entity=random.choice([
                    f"User #{random.randint(10000, 99999)}",
                    f"Account #{random.randint(1000, 9999)}",
                    f"Transaction #{random.randint(100000, 999999)}",
                ]),
                entity_type=random.choice(list(EntityType)),
                risk_score=round(score, 1),
                severity=self._get_severity_from_score(score),
                status=random.choice(statuses),
            ))
        
        return alerts
