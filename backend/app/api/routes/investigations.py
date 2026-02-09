"""
Investigations API Routes
=========================
Endpoints for managing fraud investigations and submitting decisions.
"""

from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Optional

from app.models.schemas import (
    InvestigationDetailResponse,
    InvestigationDecisionRequest,
    InvestigationDecisionResponse,
    InvestigationNoteRequest,
)
from app.services.investigation_service import InvestigationService
from app.api.dependencies import get_investigation_service
from app.core.errors import NotFoundError, BusinessRuleViolation

router = APIRouter()


@router.get("/{alert_id}", response_model=InvestigationDetailResponse)
async def get_investigation(
    alert_id: str = Path(..., description="Alert ID to investigate"),
    service: InvestigationService = Depends(get_investigation_service),
):
    """
    Get investigation details for an alert.
    
    Returns comprehensive investigation context including:
    - Alert summary with risk score
    - Transaction details
    - Feature deviations
    - Historical behavior patterns
    """
    try:
        investigation = await service.get_investigation(alert_id)
        return InvestigationDetailResponse(data=investigation)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{alert_id}/decision", response_model=InvestigationDecisionResponse)
async def submit_decision(
    alert_id: str = Path(..., description="Alert ID"),
    decision: InvestigationDecisionRequest = ...,
    service: InvestigationService = Depends(get_investigation_service),
):
    """
    Submit an investigation decision.
    
    Decision options:
    - FRAUD: Confirmed fraudulent activity
    - LEGITIMATE: False positive, transaction is legitimate
    - REVIEW: Requires additional review
    
    This will:
    1. Update the alert status
    2. Record the decision for feedback loop
    3. Update model training data (if applicable)
    """
    try:
        result = await service.submit_decision(
            alert_id=alert_id,
            decision=decision.decision,
            notes=decision.notes,
            analyst_id=decision.analyst_id,
        )
        return InvestigationDecisionResponse(
            success=True,
            alert_id=alert_id,
            updated_status=result.new_status,
            message=f"Decision recorded: {decision.decision}",
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessRuleViolation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{alert_id}/notes")
async def add_investigation_note(
    alert_id: str = Path(..., description="Alert ID"),
    note: InvestigationNoteRequest = ...,
    service: InvestigationService = Depends(get_investigation_service),
):
    """
    Add a note to an ongoing investigation.
    
    Notes are appended to the investigation timeline for audit purposes.
    """
    try:
        await service.add_note(
            alert_id=alert_id,
            note=note.content,
            analyst_id=note.analyst_id,
        )
        return {"success": True, "message": "Note added successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{alert_id}/history")
async def get_investigation_history(
    alert_id: str = Path(..., description="Alert ID"),
    service: InvestigationService = Depends(get_investigation_service),
):
    """
    Get the complete investigation history for an alert.
    
    Returns timeline of:
    - Status changes
    - Notes added
    - Decisions made
    """
    try:
        history = await service.get_history(alert_id)
        return {"alert_id": alert_id, "history": history}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
