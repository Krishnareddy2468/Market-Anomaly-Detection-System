"""
Demo Seeder — adds 1 000 extra transactions + alerts for a polished demo.
Run from the `backend/` directory with the venv activated:
    python demo_seed.py
"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import List

from app.db.session import init_db, async_session_factory
from app.db.models import (
    TransactionModel, FeatureSnapshotModel, AlertModel,
    ModelScoreRecordModel, InvestigationModel, FeedbackModel,
)
from app.models.enums import (
    AlertSeverity, AlertStatus, EntityType, FeedbackDecision,
    FeatureCategory, InvestigationAction,
)
from app.core.logging import setup_logging, get_logger

logger = get_logger(__name__)

CHANNELS  = ["WEB", "API", "POS", "ATM", "MOBILE"]
CURRENCIES = ["INR"]
COUNTRIES  = ["US", "GB", "DE", "IN", "JP", "BR", "SG", "XX"]
CITIES     = ["New York", "London", "Mumbai", "Tokyo", "Berlin", "Singapore", "Frankfurt", None]
ANALYSTS   = [
    ("analyst-001", "Sarah Chen"),
    ("analyst-002", "James Rodriguez"),
    ("analyst-003", "Priya Patel"),
]

def _uid() -> str:
    return str(uuid.uuid4())

def _past(hours: int = 720) -> datetime:
    return datetime.utcnow() - timedelta(
        hours=random.randint(0, hours),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )

def _severity(score: float) -> AlertSeverity:
    if score >= 90: return AlertSeverity.CRITICAL
    if score >= 70: return AlertSeverity.HIGH
    if score >= 50: return AlertSeverity.MEDIUM
    return AlertSeverity.LOW


async def run_demo_seed(n_transactions: int = 1_000) -> None:
    setup_logging()
    await init_db()

    async with async_session_factory() as session:
        # ── 1. Transactions ──────────────────────────────────────────────────
        txns: List[TransactionModel] = []
        offset = random.randint(20_000, 80_000)
        for i in range(n_transactions):
            ts = _past(hours=2160)   # last 90 days for a richer timeline
            txns.append(TransactionModel(
                id=_uid(),
                transaction_id=f"TXN-{offset + i}",
                amount=round(random.uniform(5, 95_000), 2),
                currency=random.choice(CURRENCIES),
                timestamp=ts,
                channel=random.choice(CHANNELS),
                entity_id=f"ENT-{random.randint(1000, 1500)}",
                entity_type=random.choice(list(EntityType)),
                source_account=f"ACC-{random.randint(8000, 8500)}",
                destination_account=f"ACC-{random.randint(9000, 9500)}",
                ip_address=f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(1,254)}",
                device_fingerprint=_uid()[:16] if random.random() > 0.2 else None,
                geo_country=random.choice(COUNTRIES),
                geo_city=random.choice(CITIES),
                created_at=ts,
            ))
        session.add_all(txns)
        await session.flush()
        logger.info(f"Added {len(txns)} transactions")

        # ── 2. Feature snapshots ─────────────────────────────────────────────
        feat_defs = [
            ("amount_zscore",       FeatureCategory.STATISTICAL, (-2, 5)),
            ("amount_pct_from_avg", FeatureCategory.STATISTICAL, (-50, 400)),
            ("hour_of_day",         FeatureCategory.TEMPORAL,    (0, 23)),
            ("is_weekend",          FeatureCategory.TEMPORAL,    (0, 1)),
            ("is_unusual_hour",     FeatureCategory.TEMPORAL,    (0, 1)),
            ("frequency_zscore",    FeatureCategory.BEHAVIORAL,  (-1, 4)),
            ("is_new_destination",  FeatureCategory.BEHAVIORAL,  (0, 1)),
            ("geo_risk_score",      FeatureCategory.GEOGRAPHIC,  (10, 95)),
            ("device_risk_score",   FeatureCategory.DEVICE,      (0, 80)),
            ("velocity_score",      FeatureCategory.CONTEXTUAL,  (0, 100)),
        ]
        snaps: List[FeatureSnapshotModel] = []
        for txn in txns:
            run_id = _uid()
            for name, cat, (lo, hi) in feat_defs:
                snaps.append(FeatureSnapshotModel(
                    id=_uid(),
                    transaction_id=txn.id,
                    detection_run_id=run_id,
                    feature_name=name,
                    feature_value=round(random.uniform(lo, hi), 4),
                    feature_category=cat,
                    model_version="1.0.0",
                    computed_at=txn.timestamp,
                ))
        session.add_all(snaps)
        await session.flush()
        logger.info(f"Added {len(snaps)} feature snapshots")

        # ── 3. Alerts (30 % flagged) ─────────────────────────────────────────
        flagged = random.sample(txns, k=int(len(txns) * 0.30))
        alert_offset = random.randint(5_000, 9_000)
        alerts: List[AlertModel] = []
        for i, txn in enumerate(flagged):
            score  = round(random.uniform(30, 100), 2)
            status = random.choices(
                [AlertStatus.ACTIVE, AlertStatus.INVESTIGATING,
                 AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE],
                weights=[35, 20, 35, 10],
            )[0]
            alerts.append(AlertModel(
                id=_uid(),
                alert_id=f"ALT-{alert_offset + i:05d}",
                entity=f"User #{random.randint(40_000, 60_000)}",
                entity_type=txn.entity_type,
                risk_score=score,
                severity=_severity(score),
                status=status,
                description=f"Anomalous pattern detected on {txn.transaction_id}",
                transaction_id=txn.id,
                detection_run_id=_uid(),
                detection_time=txn.timestamp + timedelta(seconds=random.randint(1, 15)),
                created_at=txn.timestamp + timedelta(seconds=random.randint(1, 15)),
            ))
        session.add_all(alerts)
        await session.flush()
        logger.info(f"Added {len(alerts)} alerts")

        # ── 4. Model scores ───────────────────────────────────────────────────
        model_defs = [
            ("statistical",  "1.0.0", 0.25),
            ("behavioral",   "1.0.0", 0.35),
            ("ml_ensemble",  "3.0.0", 0.40),
        ]
        scores: List[ModelScoreRecordModel] = []
        for alert in alerts:
            for m_name, m_ver, weight in model_defs:
                raw = round(random.uniform(10, 100), 2)
                scores.append(ModelScoreRecordModel(
                    id=_uid(),
                    alert_id=alert.id,
                    detection_run_id=alert.detection_run_id,
                    model_name=m_name,
                    model_version=m_ver,
                    raw_score=raw,
                    normalized_score=round(max(0, min(100, raw + random.uniform(-5, 5))), 2),
                    confidence=round(random.uniform(0.6, 1.0), 2),
                    weight=weight,
                    explanations=None,
                    scored_at=alert.detection_time,
                ))
        session.add_all(scores)
        await session.flush()
        logger.info(f"Added {len(scores)} model score records")

        # ── 5. Investigations ─────────────────────────────────────────────────
        inv_entries: List[InvestigationModel] = []
        for alert in alerts:
            if alert.status == AlertStatus.ACTIVE:
                continue
            analyst = random.choice(ANALYSTS)
            inv_entries.append(InvestigationModel(
                id=_uid(),
                alert_id=alert.id,
                action=InvestigationAction.STATUS_CHANGED,
                old_status=AlertStatus.ACTIVE.value,
                new_status=alert.status.value,
                analyst_id=analyst[0],
                analyst_name=analyst[1],
                created_at=alert.detection_time + timedelta(minutes=random.randint(5, 120)),
            ))
            if random.random() > 0.4:
                inv_entries.append(InvestigationModel(
                    id=_uid(),
                    alert_id=alert.id,
                    action=InvestigationAction.NOTE_ADDED,
                    notes=random.choice([
                        "Reviewed transaction history — pattern consistent with fraud.",
                        "Amount within 1σ of entity baseline — likely false positive.",
                        "Geo-IP mismatch confirmed; referred for deeper review.",
                        "Velocity spike due to batch processing — not anomalous.",
                        "Cross-border pattern flagged; compliance notified.",
                        "Device fingerprint mismatch — escalated to Tier 2.",
                    ]),
                    analyst_id=analyst[0],
                    analyst_name=analyst[1],
                    created_at=alert.detection_time + timedelta(minutes=random.randint(60, 240)),
                ))
        session.add_all(inv_entries)
        await session.flush()
        logger.info(f"Added {len(inv_entries)} investigation entries")

        # ── 6. Feedback ───────────────────────────────────────────────────────
        resolved = [a for a in alerts if a.status in (AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE)]
        feedback_offset = random.randint(5_000, 9_000)
        fb_entries: List[FeedbackModel] = []
        for i, alert in enumerate(resolved):
            is_fp = alert.status == AlertStatus.FALSE_POSITIVE
            analyst = random.choice(ANALYSTS)
            fb_entries.append(FeedbackModel(
                id=_uid(),
                feedback_id=f"FBK-{feedback_offset + i:05d}",
                alert_id=alert.id,
                decision=FeedbackDecision.FALSE_POSITIVE if is_fp else FeedbackDecision.FRAUD,
                confidence=round(random.uniform(0.65, 1.0), 2),
                notes="Analyst-verified outcome.",
                analyst_id=analyst[0],
                analyst_name=analyst[1],
                used_for_training=random.random() > 0.4,
                resolved_at=alert.detection_time + timedelta(hours=random.randint(1, 48)),
            ))
        session.add_all(fb_entries)
        await session.flush()
        logger.info(f"Added {len(fb_entries)} feedback records")

        await session.commit()

    logger.info("Demo seed complete ✓  —  restart the backend to reflect new counts")


if __name__ == "__main__":
    asyncio.run(run_demo_seed(1_000))
