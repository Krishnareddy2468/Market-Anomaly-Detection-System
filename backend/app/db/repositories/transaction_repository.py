"""
Transaction Repository
======================
Data access layer for transaction operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TransactionModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class TransactionRepository:
    """Repository for transaction database operations."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
    
    async def get_by_id(self, transaction_id: str) -> Optional[TransactionModel]:
        """Get transaction by transaction_id."""
        if not self.session:
            return None
        
        query = select(TransactionModel).where(
            TransactionModel.transaction_id == transaction_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_account(
        self,
        account_id: str,
        limit: int = 100,
    ) -> List[TransactionModel]:
        """Get transactions for an account."""
        if not self.session:
            return []
        
        query = (
            select(TransactionModel)
            .where(
                (TransactionModel.source_account == account_id) |
                (TransactionModel.destination_account == account_id)
            )
            .order_by(TransactionModel.timestamp.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_historical_for_entity(
        self,
        entity_id: str,
        days: int = 30,
    ) -> List[TransactionModel]:
        """Get historical transactions for behavioral analysis."""
        if not self.session:
            return []
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(TransactionModel)
            .where(
                (TransactionModel.source_account == entity_id) &
                (TransactionModel.timestamp >= start_date)
            )
            .order_by(TransactionModel.timestamp.asc())
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_total_count(self) -> int:
        """Get total transaction count."""
        if not self.session:
            return 0
        
        query = select(func.count(TransactionModel.id))
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def get_volume_stats(
        self,
        hours: int = 24,
    ) -> dict:
        """Get transaction volume statistics."""
        if not self.session:
            return {}
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = (
            select(
                func.count(TransactionModel.id).label('count'),
                func.sum(TransactionModel.amount).label('total_amount'),
                func.avg(TransactionModel.amount).label('avg_amount'),
                func.avg(TransactionModel.risk_score).label('avg_risk_score'),
            )
            .where(TransactionModel.timestamp >= start_time)
        )
        
        result = await self.session.execute(query)
        row = result.one()
        
        return {
            "count": row.count or 0,
            "total_amount": float(row.total_amount or 0),
            "avg_amount": float(row.avg_amount or 0),
            "avg_risk_score": float(row.avg_risk_score or 0),
        }
