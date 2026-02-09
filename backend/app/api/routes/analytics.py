"""
Analytics API Routes
====================
Endpoints for model performance metrics and analytics.
"""

from fastapi import APIRouter, Depends, Query
from typing import Literal, Optional
from datetime import date

from app.models.schemas import (
    AnalyticsMetricsResponse,
    ModelPerformanceResponse,
    AlertVolumeResponse,
)
from app.services.analytics_service import AnalyticsService
from app.api.dependencies import get_analytics_service

router = APIRouter()


@router.get("/metrics", response_model=AnalyticsMetricsResponse)
async def get_analytics_metrics(
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get overall model performance metrics.
    
    Returns:
    - Precision
    - Recall
    - F1 Score
    - Daily alert volume
    """
    metrics = await service.get_metrics()
    return AnalyticsMetricsResponse(data=metrics)


@router.get("/model-performance", response_model=ModelPerformanceResponse)
async def get_model_performance(
    range: Literal["7d", "30d", "90d"] = Query(default="7d", description="Time range"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get model performance over time.
    
    Returns historical accuracy, precision, recall metrics.
    """
    performance = await service.get_model_performance(range)
    return ModelPerformanceResponse(data=performance)


@router.get("/alert-volume", response_model=AlertVolumeResponse)
async def get_alert_volume(
    range: Literal["7d", "30d", "90d"] = Query(default="7d", description="Time range"),
    group_by: Literal["day", "hour"] = Query(default="day", description="Grouping"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get alert volume statistics.
    
    Returns alert counts grouped by time period, with fraud vs total breakdown.
    """
    volume = await service.get_alert_volume(range, group_by)
    return AlertVolumeResponse(data=volume)


@router.get("/confusion-matrix")
async def get_confusion_matrix(
    start_date: Optional[date] = Query(default=None, description="Start date"),
    end_date: Optional[date] = Query(default=None, description="End date"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get confusion matrix data for model evaluation.
    
    Returns true positives, false positives, true negatives, false negatives.
    """
    matrix = await service.get_confusion_matrix(start_date, end_date)
    return {"data": matrix}


@router.get("/detection-rate")
async def get_detection_rate(
    range: Literal["7d", "30d", "90d"] = Query(default="7d", description="Time range"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get fraud detection rate over time.
    
    Shows percentage of actual frauds caught by the system.
    """
    rate = await service.get_detection_rate(range)
    return {"data": rate}
