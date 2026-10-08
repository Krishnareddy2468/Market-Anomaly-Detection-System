"""
Dashboard Service
=================
Business logic for dashboard metrics and visualizations.
"""

from datetime import datetime, timedelta
from typing import List

from app.models.schemas import (
    DashboardMetrics,
    MetricTrends,
    AlertsTrend,
    SeverityDistribution,
)
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class DashboardService:
    """Service for dashboard-related business logic."""
    
    def __init__(
        self,
        alert_repo: AlertRepository,
        transaction_repo: TransactionRepository,
        feedback_repo: FeedbackRepository,
    ):
        self.alert_repo = alert_repo
        self.transaction_repo = transaction_repo
        self.feedback_repo = feedback_repo
    
    async def get_metrics(self) -> DashboardMetrics:
        """
        Get dashboard overview metrics.
        
        Aggregates:
        - Total processed transactions
        - Active alert count
        - High-risk alert count
        - False positive rate
        - Trend percentages vs previous period
        """
        logger.info("Fetching dashboard metrics")

        now = datetime.utcnow()
        current_24h_start = now - timedelta(hours=24)
        previous_24h_start = now - timedelta(hours=48)
        current_7d_start = now - timedelta(days=7)
        previous_7d_start = now - timedelta(days=14)

        total_transactions = await self.transaction_repo.get_total_count()
        active_alerts = await self.alert_repo.get_active_count()
        high_risk_alerts = await self.alert_repo.get_high_risk_count(min_score=70.0)

        feedback_totals = await self.feedback_repo.get_summary_stats(days=36500)
        fp_total = feedback_totals.get("false_positives", 0)
        resolution_total = feedback_totals.get("total", 0)
        false_positive_rate = (
            (fp_total / resolution_total) * 100 if resolution_total else 0.0
        )

        current_alerts = await self.alert_repo.get_count_in_range(current_24h_start, now)
        previous_alerts = await self.alert_repo.get_count_in_range(previous_24h_start, current_24h_start)

        current_txn = await self.transaction_repo.get_count_in_range(current_24h_start, now)
        previous_txn = await self.transaction_repo.get_count_in_range(previous_24h_start, current_24h_start)

        current_feedback = await self.feedback_repo.get_counts_in_range(current_7d_start, now)
        previous_feedback = await self.feedback_repo.get_counts_in_range(previous_7d_start, current_7d_start)
        current_fp_rate = (
            (current_feedback["false_positives"] / current_feedback["total"]) * 100
            if current_feedback["total"]
            else 0.0
        )
        previous_fp_rate = (
            (previous_feedback["false_positives"] / previous_feedback["total"]) * 100
            if previous_feedback["total"]
            else 0.0
        )

        return DashboardMetrics(
            total_transactions=total_transactions,
            active_alerts=active_alerts,
            high_risk_alerts=high_risk_alerts,
            false_positive_rate=round(false_positive_rate, 2),
            trends=MetricTrends(
                alerts_change_pct=self._pct_change(current_alerts, previous_alerts),
                false_positive_change_pct=self._pct_change(current_fp_rate, previous_fp_rate),
                transactions_change_pct=self._pct_change(current_txn, previous_txn),
            ),
        )
    
    async def get_alerts_trend(self, range: str = "24h") -> AlertsTrend:
        """
        Get alerts trend data for charting.
        
        Returns hourly/daily alert counts based on range.
        """
        logger.info("Fetching alerts trend", range=range)

        if range == "24h":
            raw = await self.alert_repo.get_trend_data(hours=24, bucket="hour")
            timestamps = [row["hour"].strftime("%H:%M") for row in raw]
            values = [row["count"] for row in raw]
        elif range == "7d":
            # Daily buckets so each point aggregates a full day's alerts.
            raw = await self.alert_repo.get_trend_data(hours=24 * 7, bucket="day")
            timestamps = [row["hour"].strftime("%a %d") for row in raw]
            values = [row["count"] for row in raw]
        else:  # 30d
            raw = await self.alert_repo.get_trend_data(hours=24 * 30, bucket="day")
            timestamps = [row["hour"].strftime("%b %d") for row in raw]
            values = [row["count"] for row in raw]

        return AlertsTrend(timestamps=timestamps, values=values)
    
    async def get_severity_distribution(self) -> List[SeverityDistribution]:
        """
        Get alert distribution by severity.
        
        For donut/pie chart visualization.
        """
        logger.info("Fetching severity distribution")

        raw_counts = await self.alert_repo.get_count_by_severity()
        counts = {
            (key.value if hasattr(key, "value") else str(key)): value
            for key, value in raw_counts.items()
        }
        return [
            SeverityDistribution(
                name="Critical",
                value=counts.get("CRITICAL", 0),
                color="hsl(0, 84%, 50%)",
            ),
            SeverityDistribution(
                name="High",
                value=counts.get("HIGH", 0),
                color="hsl(0, 84%, 60%)",
            ),
            SeverityDistribution(
                name="Medium",
                value=counts.get("MEDIUM", 0),
                color="hsl(54, 92%, 50%)",
            ),
            SeverityDistribution(
                name="Low",
                value=counts.get("LOW", 0),
                color="hsl(120, 73%, 55%)",
            ),
        ]

    def _pct_change(self, current: float, previous: float) -> float:
        """Calculate percentage delta with zero-safe fallback."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
