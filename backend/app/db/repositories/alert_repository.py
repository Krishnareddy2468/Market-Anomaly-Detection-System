"""
Alert Repository
================
Data access layer for alert operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AlertModel
from app.models.enums import AlertSeverity, AlertStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class AlertRepository:
    """Repository for alert database operations."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
    
    async def get_by_id(self, alert_id: str) -> Optional[AlertModel]:
        """Get alert by alert_id."""
        if not self.session:
            return None
            
        query = select(AlertModel).where(AlertModel.alert_id == alert_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        severity: Optional[AlertSeverity] = None,
        status: Optional[AlertStatus] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[List[AlertModel], int]:
        """Get paginated list of alerts with filters."""
        if not self.session:
            return [], 0
        
        # Build base query
        query = select(AlertModel)
        count_query = select(func.count(AlertModel.id))
        
        # Apply filters
        conditions = []
        
        if severity:
            conditions.append(AlertModel.severity == severity)
        
        if status:
            conditions.append(AlertModel.status == status)
        
        if search:
            conditions.append(
                AlertModel.alert_id.ilike(f"%{search}%") |
                AlertModel.entity.ilike(f"%{search}%")
            )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        
        # Apply pagination and ordering (by detection_time for analyst relevance)
        query = query.order_by(AlertModel.detection_time.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        alerts = result.scalars().all()
        
        return list(alerts), total
    
    async def update_status(
        self,
        alert_id: str,
        new_status: AlertStatus,
    ) -> bool:
        """Update alert status."""
        if not self.session:
            return False
        
        query = (
            update(AlertModel)
            .where(AlertModel.alert_id == alert_id)
            .values(status=new_status, updated_at=datetime.utcnow())
        )
        
        result = await self.session.execute(query)
        return result.rowcount > 0
    
    async def get_count_by_severity(self) -> dict:
        """Get alert counts grouped by severity."""
        if not self.session:
            return {}
        
        query = (
            select(AlertModel.severity, func.count(AlertModel.id))
            .group_by(AlertModel.severity)
        )
        
        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}
    
    async def get_active_count(self) -> int:
        """Get count of active alerts."""
        if not self.session:
            return 0
        
        query = select(func.count(AlertModel.id)).where(
            AlertModel.status.in_([AlertStatus.ACTIVE, AlertStatus.INVESTIGATING])
        )
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def get_trend_data(
        self,
        hours: int = 24,
    ) -> List[dict]:
        """Get hourly alert counts for trend chart (based on detection_time)."""
        if not self.session:
            return []
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = (
            select(
                func.date_trunc('hour', AlertModel.detection_time).label('hour'),
                func.count(AlertModel.id).label('count'),
            )
            .where(AlertModel.detection_time >= start_time)
            .group_by('hour')
            .order_by('hour')
        )
        
        result = await self.session.execute(query)
        return [{"hour": row.hour, "count": row.count} for row in result.all()]

    async def get_high_risk_alerts(
        self,
        min_score: float = 70.0,
        limit: int = 20,
    ) -> List[AlertModel]:
        """Get recent high-risk alerts for analyst priority view."""
        if not self.session:
            return []

        query = (
            select(AlertModel)
            .where(
                and_(
                    AlertModel.risk_score >= min_score,
                    AlertModel.status.in_([AlertStatus.ACTIVE, AlertStatus.INVESTIGATING]),
                )
            )
            .order_by(AlertModel.risk_score.desc(), AlertModel.detection_time.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
