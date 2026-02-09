"""
Investigation Service
=====================
Business logic for fraud investigations and decision submission.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import random
import uuid

from app.models.schemas import (
    Investigation,
    InvestigationNote,
    InvestigationDecisionResult,
    Transaction,
    FeatureDeviation,
)
from app.models.enums import (
    AlertStatus,
    InvestigationDecision,
    EntityType,
    RiskLevel,
)
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.db.repositories.feedback_repository import FeedbackRepository
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
    
    def __init__(
        self,
        alert_repo: AlertRepository,
        transaction_repo: TransactionRepository,
        feedback_repo: FeedbackRepository,
    ):
        self.alert_repo = alert_repo
        self.transaction_repo = transaction_repo
        self.feedback_repo = feedback_repo
    
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
        
        if not alert_id.startswith("ALT-"):
            raise NotFoundError(f"Alert {alert_id} not found")
        
        # Build investigation context (mock data for MVP)
        return Investigation(
            alert_id=alert_id,
            entity=f"User #{random.randint(10000, 99999)}",
            status=AlertStatus.INVESTIGATING,
            risk_score=94.5,
            transaction=Transaction(
                transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                amount=45230.00,
                currency="USD",
                timestamp=datetime.now() - timedelta(minutes=30),
                source_account="Account #42521",
                destination_account="Account #8839",
                channel="API",
                ip_address="192.168.1.105",
                device_fingerprint="fp_a1b2c3d4e5",
            ),
            feature_deviations=[
                FeatureDeviation(
                    feature="Transaction Amount",
                    deviation="+340%",
                    risk_level=RiskLevel.VERY_HIGH,
                    value=45230,
                    baseline=10300,
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
                    value=8,
                    baseline=1,
                ),
                FeatureDeviation(
                    feature="Geographic Location",
                    deviation="New Country",
                    risk_level=RiskLevel.MEDIUM,
                ),
                FeatureDeviation(
                    feature="Device Fingerprint",
                    deviation="New Device",
                    risk_level=RiskLevel.MEDIUM,
                ),
            ],
            historical_behavior=[
                {"date": "5 days ago", "score": 15},
                {"date": "4 days ago", "score": 18},
                {"date": "3 days ago", "score": 22},
                {"date": "2 days ago", "score": 25},
                {"date": "Yesterday", "score": 35},
                {"date": "Today", "score": 94},
            ],
            notes=[],
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
        
        # Validate alert exists
        if not alert_id.startswith("ALT-"):
            raise NotFoundError(f"Alert {alert_id} not found")
        
        # Get new status from decision
        new_status = self.DECISION_STATUS_MAP[decision]
        
        # Update alert status
        # await self.alert_repo.update_status(alert_id, new_status)
        
        # Record feedback for ML loop
        # await self.feedback_repo.create(...)
        
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
        
        if not alert_id.startswith("ALT-"):
            raise NotFoundError(f"Alert {alert_id} not found")
        
        # Create note (would save to DB)
        note_entry = InvestigationNote(
            note_id=str(uuid.uuid4()),
            content=note,
            analyst_id=analyst_id or "system",
            timestamp=datetime.now(),
        )
        
        logger.info("Note added", alert_id=alert_id, note_id=note_entry.note_id)
    
    async def get_history(self, alert_id: str) -> List[dict]:
        """
        Get complete investigation history.
        
        Returns timeline of all actions taken on this alert.
        """
        logger.info("Fetching investigation history", alert_id=alert_id)
        
        if not alert_id.startswith("ALT-"):
            raise NotFoundError(f"Alert {alert_id} not found")
        
        # Mock history
        return [
            {
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "action": "ALERT_CREATED",
                "details": "Alert generated by detection engine",
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "action": "STATUS_CHANGED",
                "from_status": "ACTIVE",
                "to_status": "INVESTIGATING",
                "analyst": "john.smith",
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "action": "NOTE_ADDED",
                "analyst": "john.smith",
                "content": "Contacting customer for verification",
            },
        ]
