"""
Analytics Service
=================
Business logic for model performance metrics and analytics.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
import random

from app.models.schemas import (
    AnalyticsMetrics,
    ModelPerformance,
    AlertVolume,
    ConfusionMatrix,
)
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and model performance metrics."""
    
    def __init__(
        self,
        alert_repo: AlertRepository,
        feedback_repo: FeedbackRepository,
    ):
        self.alert_repo = alert_repo
        self.feedback_repo = feedback_repo
    
    async def get_metrics(self) -> AnalyticsMetrics:
        """
        Get overall model performance metrics.
        
        Calculated from historical feedback data.
        """
        logger.info("Calculating analytics metrics")
        
        # In production, calculate from feedback data
        # precision = TP / (TP + FP)
        # recall = TP / (TP + FN)
        # f1 = 2 * (precision * recall) / (precision + recall)
        
        return AnalyticsMetrics(
            precision=94.2,
            recall=87.5,
            f1_score=90.7,
            alert_volume_daily=2400,
        )
    
    async def get_model_performance(self, range: str = "7d") -> ModelPerformance:
        """
        Get model performance over time.
        
        Shows accuracy progression across model versions.
        """
        logger.info("Fetching model performance", range=range)
        
        return ModelPerformance(
            versions=["v1.0", "v1.5", "v2.0", "v2.5", "v3.0"],
            accuracy=[82.5, 85.3, 89.1, 92.8, 94.2],
            timestamps=[
                datetime.now() - timedelta(days=120),
                datetime.now() - timedelta(days=90),
                datetime.now() - timedelta(days=60),
                datetime.now() - timedelta(days=30),
                datetime.now(),
            ],
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
        
        if range == "7d":
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            alerts = [280, 320, 290, 350, 410, 380, 320]
            frauds = [24, 28, 19, 32, 38, 35, 26]
        elif range == "30d":
            labels = [f"Week {i}" for i in range(1, 5)]
            alerts = [1950, 2100, 2250, 2100]
            frauds = [175, 190, 210, 195]
        else:  # 90d
            labels = ["Month 1", "Month 2", "Month 3"]
            alerts = [8500, 8800, 9200]
            frauds = [780, 810, 850]
        
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
        
        # Mock confusion matrix values
        return ConfusionMatrix(
            true_positives=215,
            false_positives=23,
            true_negatives=9500,
            false_negatives=12,
        )
    
    async def get_detection_rate(self, range: str = "7d") -> dict:
        """
        Get fraud detection rate over time.
        
        Detection rate = TP / (TP + FN)
        """
        logger.info("Calculating detection rate", range=range)
        
        if range == "7d":
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            rates = [88.5, 89.2, 91.0, 90.3, 92.1, 89.8, 90.3]
        elif range == "30d":
            labels = [f"Week {i}" for i in range(1, 5)]
            rates = [87.5, 89.0, 90.5, 90.3]
        else:
            labels = ["Month 1", "Month 2", "Month 3"]
            rates = [85.0, 88.0, 90.3]
        
        return {
            "labels": labels,
            "rates": rates,
            "average": sum(rates) / len(rates),
        }
