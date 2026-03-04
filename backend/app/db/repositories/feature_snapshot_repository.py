"""
Feature Snapshot Repository
===========================
Data access layer for feature snapshot operations.
Supports reproducibility and explainability queries.
"""

from typing import List, Optional, Dict
import uuid
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FeatureSnapshotModel
from app.models.enums import FeatureCategory
from app.core.logging import get_logger

logger = get_logger(__name__)


class FeatureSnapshotRepository:
    """Repository for feature snapshot database operations."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_by_transaction(
        self,
        transaction_id: str,
        detection_run_id: Optional[str] = None,
    ) -> List[FeatureSnapshotModel]:
        """
        Get feature snapshots for a transaction.

        If detection_run_id is given, only return features from that run.
        """
        if not self.session:
            return []

        conditions = [FeatureSnapshotModel.transaction_id == transaction_id]
        if detection_run_id:
            conditions.append(
                FeatureSnapshotModel.detection_run_id == detection_run_id
            )

        query = (
            select(FeatureSnapshotModel)
            .where(and_(*conditions))
            .order_by(
                FeatureSnapshotModel.feature_category,
                FeatureSnapshotModel.feature_name,
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_as_dict(
        self,
        transaction_id: str,
        detection_run_id: str,
    ) -> Dict[str, float]:
        """
        Reconstruct the feature vector as a flat dict.

        Useful for reproducing the exact features that a model saw.
        """
        snapshots = await self.get_by_transaction(
            transaction_id, detection_run_id
        )
        return {s.feature_name: s.feature_value for s in snapshots}

    async def get_by_category(
        self,
        transaction_id: str,
        category: FeatureCategory,
        detection_run_id: Optional[str] = None,
    ) -> List[FeatureSnapshotModel]:
        """Get features filtered by category."""
        if not self.session:
            return []

        conditions = [
            FeatureSnapshotModel.transaction_id == transaction_id,
            FeatureSnapshotModel.feature_category == category,
        ]
        if detection_run_id:
            conditions.append(
                FeatureSnapshotModel.detection_run_id == detection_run_id
            )

        query = (
            select(FeatureSnapshotModel)
            .where(and_(*conditions))
            .order_by(FeatureSnapshotModel.feature_name)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_detection_run_ids(
        self,
        transaction_id: str,
    ) -> List[str]:
        """Get all detection run IDs for a transaction (for history)."""
        if not self.session:
            return []

        query = (
            select(FeatureSnapshotModel.detection_run_id)
            .where(FeatureSnapshotModel.transaction_id == transaction_id)
            .distinct()
            .order_by(FeatureSnapshotModel.computed_at.desc())
        )
        result = await self.session.execute(query)
        return [row[0] for row in result.all()]

    async def count_features_per_category(
        self,
        detection_run_id: str,
    ) -> Dict[str, int]:
        """Count features per category for a detection run."""
        if not self.session:
            return {}

        query = (
            select(
                FeatureSnapshotModel.feature_category,
                func.count(FeatureSnapshotModel.id),
            )
            .where(FeatureSnapshotModel.detection_run_id == detection_run_id)
            .group_by(FeatureSnapshotModel.feature_category)
        )
        result = await self.session.execute(query)
        return {row[0].value: row[1] for row in result.all()}

    async def create_many(
        self,
        transaction_id: str,
        detection_run_id: str,
        features: Dict[str, float],
        model_version: str = "1.0.0",
    ) -> int:
        """Persist numeric feature values for a detection run."""
        if not self.session:
            return 0

        rows: List[FeatureSnapshotModel] = []
        for feature_name, feature_value in features.items():
            rows.append(
                FeatureSnapshotModel(
                    id=str(uuid.uuid4()),
                    transaction_id=transaction_id,
                    detection_run_id=detection_run_id,
                    feature_name=feature_name,
                    feature_value=float(feature_value),
                    feature_category=self._infer_category(feature_name),
                    model_version=model_version,
                    computed_at=datetime.utcnow(),
                )
            )
        self.session.add_all(rows)
        await self.session.flush()
        return len(rows)

    def _infer_category(self, feature_name: str) -> FeatureCategory:
        """Infer feature category from naming conventions."""
        name = feature_name.lower()
        if "zscore" in name or "pct" in name or "amount" in name:
            return FeatureCategory.STATISTICAL
        if "hour" in name or "day" in name or "weekend" in name or "time" in name:
            return FeatureCategory.TEMPORAL
        if "geo" in name or "location" in name:
            return FeatureCategory.GEOGRAPHIC
        if "device" in name:
            return FeatureCategory.DEVICE
        if "frequency" in name or "destination" in name or "channel" in name or "history" in name:
            return FeatureCategory.BEHAVIORAL
        return FeatureCategory.CONTEXTUAL
