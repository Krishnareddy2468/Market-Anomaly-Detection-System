"""
Feedback API Routes
===================
Endpoints for feedback history and analyst decision tracking.
"""

from fastapi import APIRouter, Depends, Query, Path
from typing import Optional, Literal

from app.models.schemas import (
    FeedbackListResponse,
    FeedbackFilters,
    FeedbackDecision,
)
from app.services.feedback_service import FeedbackService
from app.api.dependencies import get_feedback_service

router = APIRouter()


@router.get("", response_model=FeedbackListResponse)
async def get_feedback_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    decision: Optional[FeedbackDecision] = Query(default=None, description="Filter by decision"),
    analyst: Optional[str] = Query(default=None, description="Filter by analyst"),
    range: Literal["7d", "30d", "90d", "all"] = Query(default="30d", description="Time range"),
    service: FeedbackService = Depends(get_feedback_service),
):
    """
    Get feedback/resolution history.
    
    Returns list of resolved alerts with:
    - Decision made (FRAUD / FALSE_POSITIVE)
    - Analyst notes
    - Resolution timestamp
    - Analyst name
    """
    filters = FeedbackFilters(
        page=page,
        limit=limit,
        decision=decision,
        analyst=analyst,
        range=range,
    )
    
    result = await service.get_feedback_history(filters)
    return FeedbackListResponse(
        data=result.feedback,
        pagination=result.pagination,
        summary=result.summary,
    )


@router.get("/summary")
async def get_feedback_summary(
    range: Literal["7d", "30d", "90d"] = Query(default="7d", description="Time range"),
    service: FeedbackService = Depends(get_feedback_service),
):
    """
    Get summary statistics for feedback.
    
    Returns:
    - Total resolutions
    - Confirmed frauds
    - False positives
    - Resolution rate
    """
    summary = await service.get_summary(range)
    return {"data": summary}


@router.get("/{feedback_id}")
async def get_feedback_detail(
    feedback_id: str = Path(..., description="Feedback ID"),
    service: FeedbackService = Depends(get_feedback_service),
):
    """
    Get detailed feedback record.
    
    Returns complete feedback information including original alert context.
    """
    feedback = await service.get_feedback_detail(feedback_id)
    return {"data": feedback}


@router.get("/by-analyst/{analyst_id}")
async def get_analyst_feedback(
    analyst_id: str = Path(..., description="Analyst ID"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    service: FeedbackService = Depends(get_feedback_service),
):
    """
    Get feedback history for a specific analyst.
    
    Useful for performance tracking and audit purposes.
    """
    result = await service.get_by_analyst(analyst_id, page, limit)
    return {"data": result}
