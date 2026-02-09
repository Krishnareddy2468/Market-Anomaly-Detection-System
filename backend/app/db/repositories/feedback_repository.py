"""
Feedback Repository
===================
Data access layer for feedback/resolution operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FeedbackModel
from app.models.enums import FeedbackDecision
from app.core.logging import get_logger

logger = get_logger(__name__)


class FeedbackRepository:
    """Repository for feedback database operations."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
    
    async def get_by_id(self, feedback_id: str) -> Optional[FeedbackModel]:
        """Get feedback by feedback_id."""
        if not self.session:
            return None
        
        query = select(FeedbackModel).where(FeedbackModel.feedback_id == feedback_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_alert(self, alert_id: str) -> Optional[FeedbackModel]:
        """Get feedback for an alert."""
        if not self.session:
            return None
        
        query = select(FeedbackModel).where(FeedbackModel.alert_id == alert_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        decision: Optional[FeedbackDecision] = None,
        analyst: Optional[str] = None,
        days: Optional[int] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[FeedbackModel], int]:
        """Get paginated feedback history."""
        if not self.session:
            return [], 0
        
        # Build query
        query = select(FeedbackModel)
        count_query = select(func.count(FeedbackModel.id))
        
        conditions = []
        
        if decision:
            conditions.append(FeedbackModel.decision == decision)
        
        if analyst:
            conditions.append(FeedbackModel.analyst_id.ilike(f"%{analyst}%"))
        
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            conditions.append(FeedbackModel.created_at >= start_date)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        
        # Get data
        query = query.order_by(FeedbackModel.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        feedback = list(result.scalars().all())
        
        return feedback, total
    
    async def get_summary_stats(self, days: int = 7) -> dict:
        """Get summary statistics for feedback."""
        if not self.session:
            return {}
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(
                func.count(FeedbackModel.id).label('total'),
                func.sum(
                    func.case(
                        (FeedbackModel.decision == FeedbackDecision.FRAUD, 1),
                        else_=0
                    )
                ).label('frauds'),
                func.sum(
                    func.case(
                        (FeedbackModel.decision == FeedbackDecision.FALSE_POSITIVE, 1),
                        else_=0
                    )
                ).label('false_positives'),
            )
            .where(FeedbackModel.created_at >= start_date)
        )
        
        result = await self.session.execute(query)
        row = result.one()
        
        return {
            "total": row.total or 0,
            "frauds": row.frauds or 0,
            "false_positives": row.false_positives or 0,
        }
    
    async def get_by_analyst(
        self,
        analyst_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> List[FeedbackModel]:
        """Get feedback by analyst."""
        if not self.session:
            return []
        
        query = (
            select(FeedbackModel)
            .where(FeedbackModel.analyst_id == analyst_id)
            .order_by(FeedbackModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
