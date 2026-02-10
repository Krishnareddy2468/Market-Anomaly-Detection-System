"""
Model Score Repository
======================
Data access layer for model score record operations.
Supports versioned score storage and model comparison queries.
"""

from datetime import datetime
from typing import List, Optional, Dict

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelScoreRecordModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class ModelScoreRepository:
    """Repository for model score record database operations."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_scores_for_alert(
        self,
        alert_id: str,
    ) -> List[ModelScoreRecordModel]:
        """Get all model scores for an alert."""
        if not self.session:
            return []

        query = (
            select(ModelScoreRecordModel)
            .where(ModelScoreRecordModel.alert_id == alert_id)
            .order_by(ModelScoreRecordModel.scored_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_scores_by_model(
        self,
        model_name: str,
        model_version: Optional[str] = None,
        limit: int = 100,
    ) -> List[ModelScoreRecordModel]:
        """Get scores produced by a specific model (optionally a version)."""
        if not self.session:
            return []

        conditions = [ModelScoreRecordModel.model_name == model_name]
        if model_version:
            conditions.append(ModelScoreRecordModel.model_version == model_version)

        query = (
            select(ModelScoreRecordModel)
            .where(and_(*conditions))
            .order_by(ModelScoreRecordModel.scored_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_model_comparison(
        self,
        alert_id: str,
    ) -> Dict[str, dict]:
        """
        Get all model scores for an alert, keyed by model_name.

        Returns:
            {"statistical": {"raw": 72, "normalised": 68, ...}, ...}
        """
        if not self.session:
            return {}

        rows = await self.get_scores_for_alert(alert_id)
        return {
            row.model_name: {
                "model_version": row.model_version,
                "raw_score": row.raw_score,
                "normalized_score": row.normalized_score,
                "confidence": row.confidence,
                "weight": row.weight,
                "scored_at": row.scored_at.isoformat(),
            }
            for row in rows
        }

    async def get_model_performance_summary(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> dict:
        """Get aggregate performance stats for a model."""
        if not self.session:
            return {}

        conditions = [ModelScoreRecordModel.model_name == model_name]
        if model_version:
            conditions.append(ModelScoreRecordModel.model_version == model_version)

        query = (
            select(
                func.count(ModelScoreRecordModel.id).label("total_scores"),
                func.avg(ModelScoreRecordModel.normalized_score).label("avg_score"),
                func.min(ModelScoreRecordModel.normalized_score).label("min_score"),
                func.max(ModelScoreRecordModel.normalized_score).label("max_score"),
                func.avg(ModelScoreRecordModel.confidence).label("avg_confidence"),
            )
            .where(and_(*conditions))
        )
        result = await self.session.execute(query)
        row = result.one()

        return {
            "model_name": model_name,
            "model_version": model_version,
            "total_scores": row.total_scores or 0,
            "avg_score": round(float(row.avg_score or 0), 2),
            "min_score": round(float(row.min_score or 0), 2),
            "max_score": round(float(row.max_score or 0), 2),
            "avg_confidence": round(float(row.avg_confidence or 0), 2),
        }
