"""
Feedback Service
================
Business logic for feedback history and analyst decision tracking.
"""

from datetime import datetime, timedelta
from typing import Optional, List

from app.models.schemas import (
    Feedback,
    FeedbackFilters,
    FeedbackResult,
    FeedbackSummary,
    PaginationInfo,
)
from app.models.enums import FeedbackDecision
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.alert_repository import AlertRepository
from app.core.errors import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class FeedbackService:
    """Service for feedback and resolution history."""
    
    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        alert_repo: AlertRepository,
    ):
        self.feedback_repo = feedback_repo
        self.alert_repo = alert_repo
    
    async def get_feedback_history(self, filters: FeedbackFilters) -> FeedbackResult:
        """
        Get paginated feedback history.
        
        Shows resolved alerts with decisions and analyst notes.
        """
        logger.info("Fetching feedback history", filters=filters.model_dump())

        days = self._range_to_days(filters.range)
        offset = (filters.page - 1) * filters.limit
        rows, total = await self.feedback_repo.get_list(
            decision=filters.decision,
            analyst=filters.analyst,
            days=days,
            offset=offset,
            limit=filters.limit,
        )

        feedback_items: List[Feedback] = []
        for row in rows:
            alert = await self.alert_repo.get_by_db_id(row.alert_id)
            feedback_items.append(
                Feedback(
                    feedback_id=row.feedback_id,
                    alert_id=alert.alert_id if alert else row.alert_id,
                    entity=alert.entity if alert else "Unknown",
                    decision=row.decision,
                    notes=row.notes,
                    resolved_at=row.resolved_at,
                    analyst=row.analyst_name or row.analyst_id or "system",
                )
            )

        total_pages = (total + filters.limit - 1) // filters.limit if total else 0

        if days:
            now = datetime.utcnow()
            summary_counts = await self.feedback_repo.get_counts_in_range(
                now - timedelta(days=days),
                now,
            )
        else:
            summary_counts = await self.feedback_repo.get_summary_stats(days=36500)

        total_resolutions = summary_counts.get("total", 0)
        confirmed_frauds = summary_counts.get("frauds", 0)
        false_positives = summary_counts.get("false_positives", 0)
        resolution_rate = (
            (confirmed_frauds / total_resolutions) * 100
            if total_resolutions
            else 0.0
        )

        return FeedbackResult(
            feedback=feedback_items,
            pagination=PaginationInfo(
                page=filters.page,
                total_pages=total_pages,
                total_records=total,
                has_next=filters.page < total_pages,
                has_previous=filters.page > 1,
            ),
            summary=FeedbackSummary(
                total_resolutions=total_resolutions,
                confirmed_frauds=confirmed_frauds,
                false_positives=false_positives,
                resolution_rate=round(resolution_rate, 2),
            ),
        )
    
    async def get_summary(self, range: str = "7d") -> FeedbackSummary:
        """Get summary statistics for feedback."""
        logger.info("Fetching feedback summary", range=range)

        days = self._range_to_days(range) or 36500
        now = datetime.utcnow()
        counts = await self.feedback_repo.get_counts_in_range(
            now - timedelta(days=days),
            now,
        )
        total = counts.get("total", 0)
        frauds = counts.get("frauds", 0)
        fps = counts.get("false_positives", 0)

        return FeedbackSummary(
            total_resolutions=total,
            confirmed_frauds=frauds,
            false_positives=fps,
            resolution_rate=round((frauds / total) * 100, 2) if total else 0.0,
        )
    
    async def get_feedback_detail(self, feedback_id: str) -> Feedback:
        """Get detailed feedback record."""
        logger.info("Fetching feedback detail", feedback_id=feedback_id)

        row = await self.feedback_repo.get_by_id(feedback_id)
        if not row:
            raise NotFoundError(f"Feedback {feedback_id} not found")
        alert = await self.alert_repo.get_by_db_id(row.alert_id)

        return Feedback(
            feedback_id=row.feedback_id,
            alert_id=alert.alert_id if alert else row.alert_id,
            entity=alert.entity if alert else "Unknown",
            decision=row.decision,
            notes=row.notes,
            resolved_at=row.resolved_at,
            analyst=row.analyst_name or row.analyst_id or "system",
        )
    
    async def get_by_analyst(
        self,
        analyst_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> List[Feedback]:
        """Get feedback history for a specific analyst."""
        logger.info("Fetching analyst feedback", analyst_id=analyst_id, page=page)

        offset = (page - 1) * limit
        rows = await self.feedback_repo.get_by_analyst(
            analyst_id=analyst_id,
            offset=offset,
            limit=limit,
        )

        items: List[Feedback] = []
        for row in rows:
            alert = await self.alert_repo.get_by_db_id(row.alert_id)
            items.append(
                Feedback(
                    feedback_id=row.feedback_id,
                    alert_id=alert.alert_id if alert else row.alert_id,
                    entity=alert.entity if alert else "Unknown",
                    decision=row.decision,
                    notes=row.notes,
                    resolved_at=row.resolved_at,
                    analyst=row.analyst_name or row.analyst_id or analyst_id,
                )
            )
        return items

    def _range_to_days(self, range_value: str) -> Optional[int]:
        """Map API range token to day count."""
        mapping = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "all": None,
        }
        return mapping.get(range_value, 30)
