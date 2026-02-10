"""
Metrics Snapshot Repository
===========================
Data access layer for pre-computed dashboard metrics.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MetricsSnapshotModel
from app.models.enums import MetricScope, MetricPeriod
from app.core.logging import get_logger

logger = get_logger(__name__)


class MetricsSnapshotRepository:
    """Repository for aggregated metrics snapshot operations."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_latest(
        self,
        scope: MetricScope = MetricScope.GLOBAL,
        scope_value: Optional[str] = None,
        period: MetricPeriod = MetricPeriod.DAILY,
    ) -> Optional[MetricsSnapshotModel]:
        """Get the most recent metrics snapshot for a given scope."""
        if not self.session:
            return None

        conditions = [
            MetricsSnapshotModel.scope == scope,
            MetricsSnapshotModel.period == period,
        ]
        if scope_value:
            conditions.append(MetricsSnapshotModel.scope_value == scope_value)

        query = (
            select(MetricsSnapshotModel)
            .where(and_(*conditions))
            .order_by(MetricsSnapshotModel.window_start.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_time_series(
        self,
        scope: MetricScope = MetricScope.GLOBAL,
        scope_value: Optional[str] = None,
        period: MetricPeriod = MetricPeriod.HOURLY,
        hours: int = 24,
    ) -> List[MetricsSnapshotModel]:
        """Get a chronological series of metrics snapshots."""
        if not self.session:
            return []

        since = datetime.utcnow() - timedelta(hours=hours)
        conditions = [
            MetricsSnapshotModel.scope == scope,
            MetricsSnapshotModel.period == period,
            MetricsSnapshotModel.window_start >= since,
        ]
        if scope_value:
            conditions.append(MetricsSnapshotModel.scope_value == scope_value)

        query = (
            select(MetricsSnapshotModel)
            .where(and_(*conditions))
            .order_by(MetricsSnapshotModel.window_start.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def prune_old_snapshots(
        self,
        retention_days: int = 90,
    ) -> int:
        """
        Remove snapshots older than the retention window.

        Returns the number of rows deleted.
        """
        if not self.session:
            return 0

        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        stmt = (
            delete(MetricsSnapshotModel)
            .where(MetricsSnapshotModel.window_start < cutoff)
        )
        result = await self.session.execute(stmt)
        logger.info(
            "Pruned old metrics snapshots",
            deleted=result.rowcount,
            cutoff=cutoff.isoformat(),
        )
        return result.rowcount
