"""
Investigation Service
=====================
Business logic for fraud investigations and decision submission.
"""

from typing import List, Optional

from app.models.schemas import (
    Investigation,
    InvestigationNote,
    InvestigationDecisionResult,
    Transaction,
    FeatureDeviation,
)
from app.models.enums import (
    AlertStatus,
    FeedbackDecision,
    InvestigationDecision,
    InvestigationAction,
    RiskLevel,
)
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feature_snapshot_repository import FeatureSnapshotRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.investigation_repository import InvestigationRepository
from app.db.repositories.model_score_repository import ModelScoreRepository
from app.core.errors import NotFoundError, BusinessRuleViolation
from app.core.logging import get_logger

logger = get_logger(__name__)


class InvestigationService:
    """Service for investigation business logic."""
    
    # Decision to status mapping
    DECISION_STATUS_MAP = {
        InvestigationDecision.FRAUD: AlertStatus.RESOLVED,
        InvestigationDecision.LEGITIMATE: AlertStatus.FALSE_POSITIVE,
        InvestigationDecision.REVIEW: AlertStatus.INVESTIGATING,
    }

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
        feedback_repo: FeedbackRepository,
        feature_repo: FeatureSnapshotRepository,
        model_score_repo: ModelScoreRepository,
        investigation_repo: InvestigationRepository,
    ):
        self.alert_repo = alert_repo
        self.transaction_repo = transaction_repo
        self.feedback_repo = feedback_repo
        self.feature_repo = feature_repo
        self.model_score_repo = model_score_repo
        self.investigation_repo = investigation_repo
    
    async def get_investigation(self, alert_id: str) -> Investigation:
        """
        Get comprehensive investigation context for an alert.
        
        Includes:
        - Alert summary
        - Associated transaction
        - Feature deviations (what triggered the alert)
        - Historical behavior patterns
        - Investigation notes
        """
        logger.info("Fetching investigation", alert_id=alert_id)

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

                features = await self.feature_repo.get_by_transaction(
                    txn.id,
                    alert.detection_run_id,
                )
                features.sort(
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
                    for row in features[:8]
                ]

        score_rows = await self.model_score_repo.get_scores_for_alert(alert.id)
        historical_behavior = [
            {
                "date": row.scored_at.isoformat(),
                "score": row.normalized_score,
                "model": row.model_name,
            }
            for row in score_rows
        ]

        history_rows = await self.investigation_repo.get_history(alert.id)
        notes = [
            InvestigationNote(
                note_id=row.id,
                content=row.notes,
                analyst_id=row.analyst_id or "system",
                timestamp=row.created_at,
            )
            for row in history_rows
            if row.action == InvestigationAction.NOTE_ADDED and row.notes
        ]

        return Investigation(
            alert_id=alert_id,
            entity=alert.entity,
            status=alert.status,
            risk_score=alert.risk_score,
            transaction=transaction,
            feature_deviations=feature_deviations,
            historical_behavior=historical_behavior,
            notes=notes,
        )
    
    async def submit_decision(
        self,
        alert_id: str,
        decision: InvestigationDecision,
        notes: Optional[str] = None,
        analyst_id: Optional[str] = None,
    ) -> InvestigationDecisionResult:
        """
        Submit investigation decision.
        
        Process:
        1. Validate alert exists and is in investigable state
        2. Update alert status based on decision
        3. Record feedback for ML training loop
        4. Create audit trail entry
        """
        logger.info(
            "Submitting investigation decision",
            alert_id=alert_id,
            decision=decision,
            analyst_id=analyst_id,
        )

        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundError(f"Alert {alert_id} not found")

        new_status = self.DECISION_STATUS_MAP[decision]

        if new_status != alert.status and new_status not in self.VALID_TRANSITIONS.get(alert.status, []):
            raise BusinessRuleViolation(
                f"Invalid status transition: {alert.status} → {new_status}"
            )

        updated = await self.alert_repo.update_status(alert_id, new_status)
        if not updated:
            raise NotFoundError(f"Alert {alert_id} not found")

        await self.investigation_repo.create_entry(
            alert_id=alert.id,
            action=InvestigationAction.STATUS_CHANGED,
            old_status=alert.status.value,
            new_status=new_status.value,
            analyst_id=analyst_id,
            analyst_name=analyst_id,
        )
        await self.investigation_repo.create_entry(
            alert_id=alert.id,
            action=InvestigationAction.DECISION_SUBMITTED,
            old_status=alert.status.value,
            new_status=new_status.value,
            decision=decision.value,
            notes=notes,
            analyst_id=analyst_id,
            analyst_name=analyst_id,
        )

        if decision in (InvestigationDecision.FRAUD, InvestigationDecision.LEGITIMATE):
            existing = await self.feedback_repo.get_by_alert(alert.id)
            if not existing:
                feedback_decision = (
                    FeedbackDecision.FRAUD
                    if decision == InvestigationDecision.FRAUD
                    else FeedbackDecision.FALSE_POSITIVE
                )
                await self.feedback_repo.create_feedback(
                    alert_id=alert.id,
                    decision=feedback_decision,
                    notes=notes,
                    analyst_id=analyst_id,
                    analyst_name=analyst_id,
                )

        logger.info(
            "Decision recorded",
            alert_id=alert_id,
            decision=decision,
            new_status=new_status,
        )
        
        return InvestigationDecisionResult(
            success=True,
            new_status=new_status,
        )
    
    async def add_note(
        self,
        alert_id: str,
        note: str,
        analyst_id: Optional[str] = None,
    ) -> None:
        """
        Add a note to an investigation.
        
        Notes are append-only for audit purposes.
        """
        logger.info("Adding investigation note", alert_id=alert_id)

        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundError(f"Alert {alert_id} not found")

        note_row = await self.investigation_repo.create_entry(
            alert_id=alert.id,
            action=InvestigationAction.NOTE_ADDED,
            notes=note,
            analyst_id=analyst_id or "system",
            analyst_name=analyst_id or "system",
        )
        logger.info("Note added", alert_id=alert_id, note_id=note_row.id if note_row else None)
    
    async def get_history(self, alert_id: str) -> List[dict]:
        """
        Get complete investigation history.
        
        Returns timeline of all actions taken on this alert.
        """
        logger.info("Fetching investigation history", alert_id=alert_id)

        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundError(f"Alert {alert_id} not found")

        rows = await self.investigation_repo.get_history(alert.id)
        return [
            {
                "timestamp": row.created_at.isoformat(),
                "action": row.action.value,
                "from_status": row.old_status,
                "to_status": row.new_status,
                "decision": row.decision,
                "analyst": row.analyst_id,
                "content": row.notes,
            }
            for row in rows
        ]

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
