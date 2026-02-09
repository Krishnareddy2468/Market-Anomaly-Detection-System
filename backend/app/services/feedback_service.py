"""
Feedback Service
================
Business logic for feedback history and analyst decision tracking.
"""

from datetime import datetime, timedelta
from typing import Optional, List
import random
import uuid

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
        
        # Generate mock data
        all_feedback = self._generate_mock_feedback()
        
        # Apply filters
        filtered = all_feedback
        
        if filters.decision:
            filtered = [f for f in filtered if f.decision == filters.decision]
        
        if filters.analyst:
            filtered = [f for f in filtered if filters.analyst.lower() in f.analyst.lower()]
        
        # Sort by resolved_at descending
        filtered.sort(key=lambda x: x.resolved_at, reverse=True)
        
        # Paginate
        total = len(filtered)
        start = (filters.page - 1) * filters.limit
        end = start + filters.limit
        page_feedback = filtered[start:end]
        
        total_pages = (total + filters.limit - 1) // filters.limit
        
        # Calculate summary
        fraud_count = sum(1 for f in all_feedback if f.decision == FeedbackDecision.FRAUD)
        fp_count = sum(1 for f in all_feedback if f.decision == FeedbackDecision.FALSE_POSITIVE)
        
        return FeedbackResult(
            feedback=page_feedback,
            pagination=PaginationInfo(
                page=filters.page,
                total_pages=total_pages,
                total_records=total,
                has_next=filters.page < total_pages,
                has_previous=filters.page > 1,
            ),
            summary=FeedbackSummary(
                total_resolutions=len(all_feedback),
                confirmed_frauds=fraud_count,
                false_positives=fp_count,
                resolution_rate=95.2,
            ),
        )
    
    async def get_summary(self, range: str = "7d") -> FeedbackSummary:
        """Get summary statistics for feedback."""
        logger.info("Fetching feedback summary", range=range)
        
        return FeedbackSummary(
            total_resolutions=238,
            confirmed_frauds=215,
            false_positives=23,
            resolution_rate=95.2,
        )
    
    async def get_feedback_detail(self, feedback_id: str) -> Feedback:
        """Get detailed feedback record."""
        logger.info("Fetching feedback detail", feedback_id=feedback_id)
        
        return Feedback(
            feedback_id=feedback_id,
            alert_id=f"ALT-{random.randint(1, 100):03d}",
            entity=f"User #{random.randint(10000, 99999)}",
            decision=random.choice([FeedbackDecision.FRAUD, FeedbackDecision.FALSE_POSITIVE]),
            notes="Investigation completed. Confirmed with customer.",
            resolved_at=datetime.now() - timedelta(hours=random.randint(1, 48)),
            analyst="John Smith",
        )
    
    async def get_by_analyst(
        self,
        analyst_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> List[Feedback]:
        """Get feedback history for a specific analyst."""
        logger.info("Fetching analyst feedback", analyst_id=analyst_id, page=page)
        
        # Mock data
        return [
            Feedback(
                feedback_id=str(uuid.uuid4()),
                alert_id=f"ALT-{random.randint(1, 100):03d}",
                entity=f"User #{random.randint(10000, 99999)}",
                decision=random.choice([FeedbackDecision.FRAUD, FeedbackDecision.FALSE_POSITIVE]),
                notes="Investigation completed.",
                resolved_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
                analyst=analyst_id,
            )
            for _ in range(min(limit, 10))
        ]
    
    def _generate_mock_feedback(self) -> List[Feedback]:
        """Generate mock feedback data."""
        analysts = ["John Smith", "Sarah Johnson", "Michael Chen", "Emma Davis", "Robert Wilson"]
        
        feedback_list = []
        for i in range(25):
            is_fraud = random.random() > 0.3  # 70% fraud rate
            
            notes_fraud = [
                "Unusual location, confirmed with customer",
                "Multiple red flags, device fingerprint mismatch",
                "Matched against known fraud patterns",
                "Account takeover attempt confirmed",
            ]
            notes_fp = [
                "Customer travel, known pattern",
                "Legitimate high-value transaction for business",
                "API integration test, whitelisted",
                "Bulk purchase by authorized distributor",
            ]
            
            feedback_list.append(Feedback(
                feedback_id=f"FBK-{str(i + 1).zfill(3)}",
                alert_id=f"ALT-{str(random.randint(1, 100)).zfill(3)}",
                entity=f"User #{random.randint(10000, 99999)}",
                decision=FeedbackDecision.FRAUD if is_fraud else FeedbackDecision.FALSE_POSITIVE,
                notes=random.choice(notes_fraud if is_fraud else notes_fp),
                resolved_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
                analyst=random.choice(analysts),
            ))
        
        return feedback_list
