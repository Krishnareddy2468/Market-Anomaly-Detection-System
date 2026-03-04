"""
Alert Service
=============
Business logic for alert management, filtering, and status transitions.
"""

from typing import List

from app.models.schemas import (
    Alert,
    AlertDetail,
    AlertFilters,
    AlertsResult,
    PaginationInfo,
    Transaction,
    FeatureDeviation,
)
from app.models.enums import AlertStatus, RiskLevel
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feature_snapshot_repository import FeatureSnapshotRepository
from app.db.repositories.model_score_repository import ModelScoreRepository
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
        feature_repo: FeatureSnapshotRepository,
        model_score_repo: ModelScoreRepository,
    ):
        self.alert_repo = alert_repo
        self.transaction_repo = transaction_repo
        self.feature_repo = feature_repo
        self.model_score_repo = model_score_repo

    async def get_alerts(self, filters: AlertFilters) -> AlertsResult:
        """
        Get paginated list of alerts with filtering.
        
        Business rules:
        - Default sort by timestamp descending (newest first)
        - ACTIVE and INVESTIGATING alerts prioritized
        - Search matches alert_id and entity
        """
        logger.info("Fetching alerts", filters=filters.model_dump())

        offset = (filters.page - 1) * filters.limit
        alert_rows, total = await self.alert_repo.get_list(
            severity=filters.severity,
            status=filters.status,
            search=filters.search,
            offset=offset,
            limit=filters.limit,
        )

        page_alerts = [
            Alert(
                alert_id=row.alert_id,
                timestamp=row.detection_time,
                entity=row.entity,
                entity_type=row.entity_type,
                risk_score=row.risk_score,
                severity=row.severity,
                status=row.status,
            )
            for row in alert_rows
        ]

        total_pages = (total + filters.limit - 1) // filters.limit if total else 0

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

        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundError(f"Alert {alert_id} not found")

        transaction = None
        feature_deviations: List[FeatureDeviation] = []

        if alert.transaction_id:
            txn = await self.transaction_repo.get_by_db_id(alert.transaction_id)
            if txn:
                transaction = Transaction(
                    transaction_id=txn.transaction_id,
                    amount=txn.amount,
                    currency=txn.currency,
                    timestamp=txn.timestamp,
                    source_account=txn.source_account,
                    destination_account=txn.destination_account,
                    channel=txn.channel,
                    ip_address=txn.ip_address,
                    device_fingerprint=txn.device_fingerprint,
                )

                feature_rows = await self.feature_repo.get_by_transaction(
                    txn.id,
                    alert.detection_run_id,
                )
                feature_rows.sort(
                    key=lambda row: abs(float(row.feature_value)),
                    reverse=True,
                )
                feature_deviations = [
                    FeatureDeviation(
                        feature=row.feature_name,
                        deviation=f"{row.feature_value:.2f}",
                        risk_level=self._risk_level_from_value(row.feature_value),
                        value=row.feature_value,
                        baseline=None,
                    )
                    for row in feature_rows[:6]
                ]

        model_scores = await self.model_score_repo.get_scores_for_alert(alert.id)
        historical_scores = [score.normalized_score for score in model_scores[:10]]
        if not historical_scores:
            historical_scores = [alert.risk_score]

        return AlertDetail(
            alert_id=alert_id,
            timestamp=alert.detection_time,
            entity=alert.entity,
            entity_type=alert.entity_type,
            risk_score=alert.risk_score,
            severity=alert.severity,
            status=alert.status,
            description=alert.description,
            transaction=transaction,
            feature_deviations=feature_deviations,
            historical_scores=historical_scores,
        )
    
    async def update_status(self, alert_id: str, new_status: AlertStatus) -> bool:
        """
        Update alert status with validation.
        
        Enforces valid state transitions.
        """
        logger.info("Updating alert status", alert_id=alert_id, new_status=new_status)

        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundError(f"Alert {alert_id} not found")

        current_status = alert.status

        # Validate transition
        if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
            raise BusinessRuleViolation(
                f"Invalid status transition: {current_status} → {new_status}"
            )

        updated = await self.alert_repo.update_status(alert_id, new_status)
        if not updated:
            raise NotFoundError(f"Alert {alert_id} not found")

        logger.info(
            "Alert status updated",
            alert_id=alert_id,
            old_status=current_status,
            new_status=new_status,
        )

        return True

    def _risk_level_from_value(self, value: float) -> RiskLevel:
        """Map feature magnitude to display risk level."""
        absolute = abs(float(value))
        if absolute >= 80:
            return RiskLevel.VERY_HIGH
        if absolute >= 50:
            return RiskLevel.HIGH
        if absolute >= 20:
            return RiskLevel.MEDIUM
        if absolute >= 5:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL
