"""
API Dependencies
================
FastAPI dependency injection for services and common resources.
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.alert_service import AlertService
from app.services.analytics_service import AnalyticsService
from app.services.dashboard_service import DashboardService
from app.services.feedback_service import FeedbackService
from app.services.investigation_service import InvestigationService
from app.services.detection_service import DetectionService
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feature_snapshot_repository import FeatureSnapshotRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.investigation_repository import InvestigationRepository
from app.db.repositories.model_score_repository import ModelScoreRepository
from app.db.repositories.transaction_repository import TransactionRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with get_db_session() as session:
        yield session


async def get_alert_service(
    session: AsyncSession = Depends(get_db),
) -> AlertService:
    """Get AlertService dependency."""
    return AlertService(
        alert_repo=AlertRepository(session),
        transaction_repo=TransactionRepository(session),
        feature_repo=FeatureSnapshotRepository(session),
        model_score_repo=ModelScoreRepository(session),
    )


async def get_dashboard_service(
    session: AsyncSession = Depends(get_db),
) -> DashboardService:
    """Get DashboardService dependency."""
    return DashboardService(
        alert_repo=AlertRepository(session),
        transaction_repo=TransactionRepository(session),
        feedback_repo=FeedbackRepository(session),
    )


async def get_investigation_service(
    session: AsyncSession = Depends(get_db),
) -> InvestigationService:
    """Get InvestigationService dependency."""
    return InvestigationService(
        alert_repo=AlertRepository(session),
        transaction_repo=TransactionRepository(session),
        feedback_repo=FeedbackRepository(session),
        feature_repo=FeatureSnapshotRepository(session),
        model_score_repo=ModelScoreRepository(session),
        investigation_repo=InvestigationRepository(session),
    )


async def get_analytics_service(
    session: AsyncSession = Depends(get_db),
) -> AnalyticsService:
    """Get AnalyticsService dependency."""
    return AnalyticsService(
        alert_repo=AlertRepository(session),
        feedback_repo=FeedbackRepository(session),
        model_score_repo=ModelScoreRepository(session),
        transaction_repo=TransactionRepository(session),
    )


async def get_feedback_service(
    session: AsyncSession = Depends(get_db),
) -> FeedbackService:
    """Get FeedbackService dependency."""
    return FeedbackService(
        feedback_repo=FeedbackRepository(session),
        alert_repo=AlertRepository(session),
    )


async def get_detection_service(
    session: AsyncSession = Depends(get_db),
) -> DetectionService:
    """Get DetectionService dependency."""
    return DetectionService(
        transaction_repo=TransactionRepository(session),
        feature_repo=FeatureSnapshotRepository(session),
        alert_repo=AlertRepository(session),
        model_score_repo=ModelScoreRepository(session),
    )
