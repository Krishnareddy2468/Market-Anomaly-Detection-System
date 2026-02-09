"""
API Dependencies
================
FastAPI dependency injection for services and common resources.
"""

from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.alert_service import AlertService
from app.services.analytics_service import AnalyticsService
from app.services.dashboard_service import DashboardService
from app.services.feedback_service import FeedbackService
from app.services.investigation_service import InvestigationService
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.transaction_repository import TransactionRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with get_db_session() as session:
        yield session


def get_alert_service() -> AlertService:
    """Get AlertService dependency."""
    return AlertService(
        alert_repo=AlertRepository(),
        transaction_repo=TransactionRepository(),
    )


def get_dashboard_service() -> DashboardService:
    """Get DashboardService dependency."""
    return DashboardService(
        alert_repo=AlertRepository(),
    )


def get_investigation_service() -> InvestigationService:
    """Get InvestigationService dependency."""
    return InvestigationService(
        alert_repo=AlertRepository(),
        transaction_repo=TransactionRepository(),
        feedback_repo=FeedbackRepository(),
    )


def get_analytics_service() -> AnalyticsService:
    """Get AnalyticsService dependency."""
    return AnalyticsService(
        alert_repo=AlertRepository(),
        feedback_repo=FeedbackRepository(),
    )


def get_feedback_service() -> FeedbackService:
    """Get FeedbackService dependency."""
    return FeedbackService(
        feedback_repo=FeedbackRepository(),
        alert_repo=AlertRepository(),
    )
