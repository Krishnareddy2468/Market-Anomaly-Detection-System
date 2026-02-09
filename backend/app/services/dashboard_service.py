"""
Dashboard Service
=================
Business logic for dashboard metrics and visualizations.
"""

from datetime import datetime, timedelta
from typing import List
import random

from app.models.schemas import (
    DashboardMetrics,
    MetricTrends,
    AlertsTrend,
    SeverityDistribution,
)
from app.db.repositories.alert_repository import AlertRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class DashboardService:
    """Service for dashboard-related business logic."""
    
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo
    
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
        
        # In production, these would come from the database
        # For MVP, using mock data
        return DashboardMetrics(
            total_transactions=2_456_789,
            active_alerts=142,
            high_risk_alerts=28,
            false_positive_rate=2.3,
            trends=MetricTrends(
                alerts_change_pct=8.2,
                false_positive_change_pct=-0.5,
                transactions_change_pct=12.5,
            ),
        )
    
    async def get_alerts_trend(self, range: str = "24h") -> AlertsTrend:
        """
        Get alerts trend data for charting.
        
        Returns hourly/daily alert counts based on range.
        """
        logger.info("Fetching alerts trend", range=range)
        
        if range == "24h":
            # Hourly data
            timestamps = [f"{h:02d}:00" for h in range(0, 24, 2)]
            values = [
                random.randint(20, 40),  # Early morning low
                random.randint(25, 45),
                random.randint(30, 50),
                random.randint(40, 60),  # Morning increase
                random.randint(50, 70),
                random.randint(60, 85),  # Peak hours
                random.randint(70, 95),
                random.randint(75, 90),
                random.randint(80, 100), # Afternoon peak
                random.randint(70, 85),
                random.randint(55, 70),  # Evening decline
                random.randint(35, 50),  # Night
            ]
        elif range == "7d":
            timestamps = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            values = [
                random.randint(200, 300),
                random.randint(250, 350),
                random.randint(220, 320),
                random.randint(280, 380),
                random.randint(350, 450),  # Friday peak
                random.randint(300, 400),
                random.randint(250, 350),
            ]
        else:  # 30d
            timestamps = [f"Day {i}" for i in range(1, 31)]
            values = [random.randint(180, 400) for _ in range(30)]
        
        return AlertsTrend(timestamps=timestamps, values=values)
    
    async def get_severity_distribution(self) -> List[SeverityDistribution]:
        """
        Get alert distribution by severity.
        
        For donut/pie chart visualization.
        """
        logger.info("Fetching severity distribution")
        
        # Mock distribution
        return [
            SeverityDistribution(name="Critical", value=15, color="hsl(0, 84%, 50%)"),
            SeverityDistribution(name="High", value=35, color="hsl(0, 84%, 60%)"),
            SeverityDistribution(name="Medium", value=45, color="hsl(54, 92%, 50%)"),
            SeverityDistribution(name="Low", value=25, color="hsl(120, 73%, 55%)"),
        ]
