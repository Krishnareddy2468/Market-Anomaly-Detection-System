"""
Dashboard API Routes
====================
Endpoints for dashboard overview data including metrics, trends, and distributions.
"""

from fastapi import APIRouter, Depends, Query
from typing import Literal

from app.models.schemas import (
    DashboardMetricsResponse,
    AlertsTrendResponse,
    SeverityDistributionResponse,
)
from app.services.dashboard_service import DashboardService
from app.api.dependencies import get_dashboard_service

router = APIRouter()


@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    service: DashboardService = Depends(get_dashboard_service),
):
    """
    Get dashboard overview metrics.
    
    Returns KPIs including:
    - Total transactions processed
    - Active alerts count
    - High-risk alerts count
    - False positive rate
    - Trend percentages
    """
    metrics = await service.get_metrics()
    return DashboardMetricsResponse(data=metrics)


@router.get("/alerts-trend", response_model=AlertsTrendResponse)
async def get_alerts_trend(
    range: Literal["24h", "7d", "30d"] = Query(default="24h", description="Time range for trend data"),
    service: DashboardService = Depends(get_dashboard_service),
):
    """
    Get alerts trend data over time.
    
    Returns timestamps and corresponding alert counts for charting.
    """
    trend = await service.get_alerts_trend(range)
    return AlertsTrendResponse(data=trend)


@router.get("/severity-distribution", response_model=SeverityDistributionResponse)
async def get_severity_distribution(
    service: DashboardService = Depends(get_dashboard_service),
):
    """
    Get alert severity distribution.
    
    Returns breakdown of alerts by severity level (Critical, High, Medium, Low).
    """
    distribution = await service.get_severity_distribution()
    return SeverityDistributionResponse(data=distribution)
