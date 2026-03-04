"""
Analytics Service
=================
Business logic for model performance metrics and analytics.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple

from app.models.schemas import (
    AnalyticsMetrics,
    ModelPerformance,
    AlertVolume,
    ConfusionMatrix,
)
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.model_score_repository import ModelScoreRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and model performance metrics."""
    
    def __init__(
        self,
        alert_repo: AlertRepository,
        feedback_repo: FeedbackRepository,
        model_score_repo: ModelScoreRepository,
        transaction_repo: TransactionRepository,
    ):
        self.alert_repo = alert_repo
        self.feedback_repo = feedback_repo
        self.model_score_repo = model_score_repo
        self.transaction_repo = transaction_repo
    
    async def get_metrics(self) -> AnalyticsMetrics:
        """
        Get overall model performance metrics.
        
        Calculated from historical feedback data.
        """
        logger.info("Calculating analytics metrics")

        now = datetime.utcnow()
        start = now - timedelta(days=30)
        feedback = await self.feedback_repo.get_counts_in_range(start, now)
        alerts_30d = await self.alert_repo.get_count_in_range(start, now)

        tp = feedback["frauds"]
        fp = feedback["false_positives"]
        fn = max(0, alerts_30d - tp - fp)

        precision = (tp / (tp + fp) * 100) if (tp + fp) else 0.0
        recall = (tp / (tp + fn) * 100) if (tp + fn) else 0.0
        f1 = (
            (2 * precision * recall) / (precision + recall)
            if (precision + recall)
            else 0.0
        )

        return AnalyticsMetrics(
            precision=round(precision, 2),
            recall=round(recall, 2),
            f1_score=round(f1, 2),
            alert_volume_daily=round(alerts_30d / 30),
        )
    
    async def get_model_performance(self, range: str = "7d") -> ModelPerformance:
        """
        Get model performance over time.
        
        Shows accuracy progression across model versions.
        """
        logger.info("Fetching model performance", range=range)

        model_names = ["statistical", "behavioral", "ml_ensemble"]
        versions: List[str] = []
        accuracy: List[float] = []
        timestamps: List[datetime] = []

        for model in model_names:
            summary = await self.model_score_repo.get_model_performance_summary(model)
            versions.append(model)
            accuracy.append(summary.get("avg_score", 0.0))
            timestamps.append(datetime.utcnow())

        return ModelPerformance(
            versions=versions,
            accuracy=accuracy,
            timestamps=timestamps,
        )
    
    async def get_alert_volume(
        self,
        range: str = "7d",
        group_by: str = "day",
    ) -> AlertVolume:
        """
        Get alert volume statistics.
        
        Returns total alerts and confirmed frauds for charting.
        """
        logger.info("Fetching alert volume", range=range, group_by=group_by)

        windows = self._build_time_windows(range, group_by)
        labels: List[str] = []
        alerts: List[int] = []
        frauds: List[int] = []

        for start, end, label in windows:
            labels.append(label)
            alerts.append(await self.alert_repo.get_count_in_range(start, end))
            counts = await self.feedback_repo.get_counts_in_range(start, end)
            frauds.append(counts["frauds"])

        return AlertVolume(labels=labels, alerts=alerts, frauds=frauds)
    
    async def get_confusion_matrix(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> ConfusionMatrix:
        """
        Get confusion matrix for model evaluation.
        
        Based on feedback data where ground truth is known.
        """
        logger.info(
            "Calculating confusion matrix",
            start_date=start_date,
            end_date=end_date,
        )

        end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else datetime.utcnow()
        start_dt = (
            datetime.combine(start_date, datetime.min.time())
            if start_date
            else end_dt - timedelta(days=30)
        )
        feedback = await self.feedback_repo.get_counts_in_range(start_dt, end_dt)
        tp = feedback["frauds"]
        fp = feedback["false_positives"]

        alert_total = await self.alert_repo.get_count_in_range(start_dt, end_dt)
        fn = max(0, alert_total - tp - fp)

        txn_total = await self.transaction_repo.get_count_in_range(start_dt, end_dt)
        tn = max(0, txn_total - tp - fp - fn)

        return ConfusionMatrix(
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
        )
    
    async def get_detection_rate(self, range: str = "7d") -> dict:
        """
        Get fraud detection rate over time.
        
        Detection rate = TP / (TP + FN)
        """
        logger.info("Calculating detection rate", range=range)

        volume = await self.get_alert_volume(range=range, group_by="day")
        labels = volume.labels
        rates = [
            round((fraud / total) * 100, 2) if total else 0.0
            for total, fraud in zip(volume.alerts, volume.frauds)
        ]

        return {
            "labels": labels,
            "rates": rates,
            "average": round(sum(rates) / len(rates), 2) if rates else 0.0,
        }

    def _build_time_windows(
        self,
        range_value: str,
        group_by: str,
    ) -> List[Tuple[datetime, datetime, str]]:
        """Generate labeled time windows for analytics aggregation."""
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        windows: List[Tuple[datetime, datetime, str]] = []

        if group_by == "hour":
            hours = 24 if range_value == "7d" else 72
            for i in range(hours, 0, -1):
                start = now - timedelta(hours=i)
                end = start + timedelta(hours=1)
                windows.append((start, end, start.strftime("%m-%d %H:%M")))
            return windows

        if range_value == "7d":
            days = 7
        elif range_value == "30d":
            days = 30
        else:
            days = 90

        for i in range(days, 0, -1):
            start = (now - timedelta(days=i)).replace(hour=0)
            end = start + timedelta(days=1)
            windows.append((start, end, start.strftime("%Y-%m-%d")))
        return windows
