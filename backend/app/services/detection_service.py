"""
Detection Service
=================
Orchestrates real-time detection workflow:
- Persist transaction
- Run detection engine
- Persist features
- Persist alerts + model scores when threshold is crossed
"""

from datetime import datetime, timezone
from typing import Any, Dict
import uuid

from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.core.errors import ConflictError
from app.core.logging import get_logger
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feature_snapshot_repository import FeatureSnapshotRepository
from app.db.repositories.model_score_repository import ModelScoreRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.detection.engine import DetectionEngine, TransactionInput
from app.models.enums import AlertStatus
from app.models.schemas import DetectionRequest, DetectionResultData

logger = get_logger(__name__)


class DetectionService:
    """Service for end-to-end scoring and persistence."""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        feature_repo: FeatureSnapshotRepository,
        alert_repo: AlertRepository,
        model_score_repo: ModelScoreRepository,
    ):
        self.transaction_repo = transaction_repo
        self.feature_repo = feature_repo
        self.alert_repo = alert_repo
        self.model_score_repo = model_score_repo
        self.engine = DetectionEngine(
            risk_threshold_alert=settings.RISK_THRESHOLD_MEDIUM,
        )

    async def evaluate(self, payload: DetectionRequest) -> DetectionResultData:
        """Evaluate one transaction and persist artifacts."""
        normalized_timestamp = self._normalize_timestamp(payload.timestamp)

        existing = await self.transaction_repo.get_by_id(payload.transaction_id)
        if existing:
            raise ConflictError(
                message=f"Transaction {payload.transaction_id} already exists",
                details={"transaction_id": payload.transaction_id},
            )

        historical_rows = await self.transaction_repo.get_historical_for_entity(
            payload.entity_id,
            days=30,
        )
        historical_transactions = [
            {
                "transaction_id": row.transaction_id,
                "amount": float(row.amount),
                "timestamp": row.timestamp,
                "destination_account": row.destination_account,
                "channel": row.channel,
                "device_fingerprint": row.device_fingerprint,
                "geo_country": row.geo_country,
            }
            for row in historical_rows
        ]

        try:
            transaction = await self.transaction_repo.create(
                transaction_id=payload.transaction_id,
                amount=payload.amount,
                timestamp=normalized_timestamp,
                source_account=payload.source_account,
                destination_account=payload.destination_account,
                entity_id=payload.entity_id,
                entity_type=payload.entity_type,
                currency=payload.currency,
                channel=payload.channel,
                ip_address=payload.ip_address,
                device_fingerprint=payload.device_fingerprint,
                geo_country=payload.geo_country,
            )
        except IntegrityError as exc:
            message = str(exc).lower()
            is_unique_violation = (
                "duplicate key value violates unique constraint" in message
                or "unique" in message
                or "23505" in message
            )
            if is_unique_violation:
                raise ConflictError(
                    message=f"Transaction {payload.transaction_id} already exists",
                    details={"transaction_id": payload.transaction_id},
                ) from exc
            raise
        if not transaction:
            raise RuntimeError("Failed to persist transaction")

        engine_input = TransactionInput(
            transaction_id=payload.transaction_id,
            amount=payload.amount,
            timestamp=normalized_timestamp,
            source_account=payload.source_account,
            destination_account=payload.destination_account,
            entity_id=payload.entity_id,
            currency=payload.currency,
            channel=payload.channel,
            ip_address=payload.ip_address,
            device_fingerprint=payload.device_fingerprint,
            geo_location=payload.geo_country,
            historical_transactions=historical_transactions,
        )
        output = await self.engine.process_transaction(engine_input)

        detection_run_id = str(uuid.uuid4())
        numeric_features = self._select_numeric_features(output.feature_values)
        await self.feature_repo.create_many(
            transaction_id=transaction.id,
            detection_run_id=detection_run_id,
            features=numeric_features,
            model_version="1.0.0",
        )

        alert_id = None
        if output.should_alert:
            alert = await self.alert_repo.create(
                entity=payload.entity_id,
                entity_type=payload.entity_type,
                risk_score=output.risk_score,
                severity=output.severity,
                status=AlertStatus.ACTIVE,
                description="; ".join(output.explanations[:4]) if output.explanations else None,
                transaction_id=transaction.id,
                detection_run_id=detection_run_id,
                detection_time=datetime.utcnow(),
            )
            if alert:
                alert_id = alert.alert_id
                await self.model_score_repo.create_many(
                    alert_id=alert.id,
                    detection_run_id=detection_run_id,
                    detector_scores=output.detector_scores,
                    model_version="1.0.0",
                )

        logger.info(
            "Detection evaluation complete",
            transaction_id=payload.transaction_id,
            should_alert=output.should_alert,
            alert_id=alert_id,
            risk_score=output.risk_score,
        )
        return DetectionResultData(
            transaction_id=output.transaction_id,
            risk_score=output.risk_score,
            severity=output.severity,
            should_alert=output.should_alert,
            alert_id=alert_id,
            detector_scores=output.detector_scores,
            explanations=output.explanations,
            processing_time_ms=output.processing_time_ms,
        )

    def _select_numeric_features(self, feature_values: Dict[str, Any]) -> Dict[str, float]:
        """Keep only numeric/bool feature values for storage."""
        result: Dict[str, float] = {}
        for key, value in feature_values.items():
            if isinstance(value, bool):
                result[key] = 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                result[key] = float(value)
        return result

    def _normalize_timestamp(self, value: datetime) -> datetime:
        """Convert incoming timestamps to naive UTC for DB/storage consistency."""
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)
