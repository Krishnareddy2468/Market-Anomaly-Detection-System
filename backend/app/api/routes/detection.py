"""
Detection API Routes
====================
Endpoints for real-time transaction scoring and alert generation.
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_detection_service
from app.models.schemas import DetectionRequest, DetectionResponse
from app.services.detection_service import DetectionService

router = APIRouter()


@router.post("/evaluate", response_model=DetectionResponse)
async def evaluate_transaction(
    payload: DetectionRequest,
    service: DetectionService = Depends(get_detection_service),
):
    """Evaluate one transaction and persist detection artifacts."""
    result = await service.evaluate(payload)
    return DetectionResponse(data=result)
