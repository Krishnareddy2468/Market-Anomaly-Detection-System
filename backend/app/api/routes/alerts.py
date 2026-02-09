"""
Alerts API Routes
=================
Endpoints for alert management including listing, filtering, and detail views.
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException
from typing import Optional

from app.models.schemas import (
    AlertsListResponse,
    AlertDetailResponse,
    AlertFilters,
    AlertSeverity,
    AlertStatus,
)
from app.services.alert_service import AlertService
from app.api.dependencies import get_alert_service
from app.core.errors import NotFoundError

router = APIRouter()


@router.get("", response_model=AlertsListResponse)
async def get_alerts(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    severity: Optional[AlertSeverity] = Query(default=None, description="Filter by severity"),
    status: Optional[AlertStatus] = Query(default=None, description="Filter by status"),
    search: Optional[str] = Query(default=None, max_length=100, description="Search by ID or entity"),
    service: AlertService = Depends(get_alert_service),
):
    """
    List alerts with filtering and pagination.
    
    Supports filtering by:
    - Severity (CRITICAL, HIGH, MEDIUM, LOW)
    - Status (ACTIVE, INVESTIGATING, RESOLVED, FALSE_POSITIVE)
    - Search term (Alert ID or Entity)
    """
    filters = AlertFilters(
        page=page,
        limit=limit,
        severity=severity,
        status=status,
        search=search,
    )
    
    result = await service.get_alerts(filters)
    return AlertsListResponse(
        data=result.alerts,
        pagination=result.pagination,
    )


@router.get("/{alert_id}", response_model=AlertDetailResponse)
async def get_alert_detail(
    alert_id: str = Path(..., description="Alert ID"),
    service: AlertService = Depends(get_alert_service),
):
    """
    Get detailed information for a specific alert.
    
    Includes:
    - Alert summary
    - Associated transaction details
    - Feature deviations
    - Historical context
    """
    try:
        alert = await service.get_alert_detail(alert_id)
        return AlertDetailResponse(data=alert)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{alert_id}/status")
async def update_alert_status(
    alert_id: str = Path(..., description="Alert ID"),
    status: AlertStatus = Query(..., description="New status"),
    service: AlertService = Depends(get_alert_service),
):
    """
    Update an alert's status.
    
    Valid transitions:
    - ACTIVE → INVESTIGATING
    - INVESTIGATING → RESOLVED / FALSE_POSITIVE
    - Any status → ACTIVE (reopen)
    """
    try:
        result = await service.update_status(alert_id, status)
        return {"success": True, "alert_id": alert_id, "new_status": status}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
