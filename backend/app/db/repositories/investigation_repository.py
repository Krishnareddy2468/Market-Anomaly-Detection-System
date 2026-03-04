"""
Investigation Repository
========================
Data access layer for investigation audit trail operations.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import InvestigationModel
from app.models.enums import InvestigationAction


class InvestigationRepository:
    """Repository for investigation timeline operations."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def create_entry(
        self,
        alert_id: str,
        action: InvestigationAction,
        old_status: Optional[str] = None,
        new_status: Optional[str] = None,
        decision: Optional[str] = None,
        notes: Optional[str] = None,
        analyst_id: Optional[str] = None,
        analyst_name: Optional[str] = None,
    ) -> Optional[InvestigationModel]:
        """Create a single append-only investigation entry."""
        if not self.session:
            return None

        row = InvestigationModel(
            alert_id=alert_id,
            action=action,
            old_status=old_status,
            new_status=new_status,
            decision=decision,
            notes=notes,
            analyst_id=analyst_id,
            analyst_name=analyst_name,
            created_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_history(self, alert_id: str) -> List[InvestigationModel]:
        """Get investigation timeline entries for an alert."""
        if not self.session:
            return []

        query = (
            select(InvestigationModel)
            .where(InvestigationModel.alert_id == alert_id)
            .order_by(InvestigationModel.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
