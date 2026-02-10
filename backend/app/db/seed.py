"""
Database Seeder
===============
Populates the database with synthetic data for development & testing.

Usage:
    python -m app.db.seed
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import List

from app.db.session import init_db, get_db_session, async_session_factory
from app.db.models import (
    TransactionModel,
    FeatureSnapshotModel,
    AlertModel,
    ModelScoreRecordModel,
    InvestigationModel,
    FeedbackModel,
    MetricsSnapshotModel,
)
from app.models.enums import (
    AlertSeverity,
    AlertStatus,
    EntityType,
    FeedbackDecision,
    FeatureCategory,
    InvestigationAction,
    MetricScope,
    MetricPeriod,
)
from app.core.logging import setup_logging, get_logger

logger = get_logger(__name__)

# -----------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------

CHANNELS = ["WEB", "API", "POS", "ATM", "MOBILE"]
CURRENCIES = ["USD", "EUR", "GBP"]
COUNTRIES = ["US", "GB", "DE", "IN", "JP", "BR", "XX"]
ANALYSTS = [
    ("analyst-001", "Sarah Chen"),
    ("analyst-002", "James Rodriguez"),
    ("analyst-003", "Priya Patel"),
]


def _uid() -> str:
    return str(uuid.uuid4())


def _past(hours: int = 720) -> datetime:
    """Random datetime within the last `hours` hours."""
    return datetime.utcnow() - timedelta(
        hours=random.randint(0, hours),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )


def _severity_from_score(score: float) -> AlertSeverity:
    if score >= 90:
        return AlertSeverity.CRITICAL
    if score >= 70:
        return AlertSeverity.HIGH
    if score >= 50:
        return AlertSeverity.MEDIUM
    return AlertSeverity.LOW


# -----------------------------------------------------------------
# Entity generators
# -----------------------------------------------------------------

def generate_transactions(n: int = 200) -> List[TransactionModel]:
    txns = []
    for i in range(n):
        ts = _past()
        txns.append(TransactionModel(
            id=_uid(),
            transaction_id=f"TXN-{10000 + i}",
            amount=round(random.uniform(5, 50_000), 2),
            currency=random.choice(CURRENCIES),
            timestamp=ts,
            channel=random.choice(CHANNELS),
            entity_id=f"ENT-{random.randint(1000, 1200)}",
            entity_type=random.choice(list(EntityType)),
            source_account=f"ACC-{random.randint(8000, 8100)}",
            destination_account=f"ACC-{random.randint(9000, 9200)}",
            ip_address=f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
            device_fingerprint=_uid()[:16] if random.random() > 0.3 else None,
            geo_country=random.choice(COUNTRIES),
            geo_city=random.choice(["New York", "London", "Mumbai", "Tokyo", "Berlin", None]),
            created_at=ts,
        ))
    return txns


def generate_features_for_txn(
    txn: TransactionModel, run_id: str
) -> List[FeatureSnapshotModel]:
    """Generate a set of feature snapshots for one transaction."""
    features = []
    feature_defs = [
        ("amount_zscore", FeatureCategory.STATISTICAL, random.uniform(-2, 5)),
        ("amount_pct_from_avg", FeatureCategory.STATISTICAL, random.uniform(-50, 400)),
        ("hour_of_day", FeatureCategory.TEMPORAL, float(txn.timestamp.hour)),
        ("is_weekend", FeatureCategory.TEMPORAL, float(txn.timestamp.weekday() >= 5)),
        ("is_unusual_hour", FeatureCategory.TEMPORAL, float(txn.timestamp.hour < 5)),
        ("frequency_zscore", FeatureCategory.BEHAVIORAL, random.uniform(-1, 4)),
        ("is_new_destination", FeatureCategory.BEHAVIORAL, float(random.random() > 0.7)),
        ("geo_risk_score", FeatureCategory.GEOGRAPHIC, random.uniform(10, 95)),
        ("device_risk_score", FeatureCategory.DEVICE, random.uniform(0, 80)),
        ("velocity_score", FeatureCategory.CONTEXTUAL, random.uniform(0, 100)),
    ]
    for name, cat, val in feature_defs:
        features.append(FeatureSnapshotModel(
            id=_uid(),
            transaction_id=txn.id,
            detection_run_id=run_id,
            feature_name=name,
            feature_value=round(val, 4),
            feature_category=cat,
            model_version="1.0.0",
            computed_at=txn.timestamp,
        ))
    return features


def generate_alerts(
    transactions: List[TransactionModel], fraction: float = 0.25
) -> List[AlertModel]:
    """Flag a fraction of transactions as anomalous."""
    alerts = []
    flagged = random.sample(transactions, k=int(len(transactions) * fraction))
    for i, txn in enumerate(flagged):
        score = round(random.uniform(30, 100), 2)
        sev = _severity_from_score(score)
        status = random.choices(
            [AlertStatus.ACTIVE, AlertStatus.INVESTIGATING, AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE],
            weights=[40, 25, 25, 10],
        )[0]
        alerts.append(AlertModel(
            id=_uid(),
            alert_id=f"ALT-{1000 + i:04d}",
            entity=f"User #{random.randint(40000, 50000)}",
            entity_type=txn.entity_type,
            risk_score=score,
            severity=sev,
            status=status,
            description=f"Anomalous pattern detected on {txn.transaction_id}",
            transaction_id=txn.id,
            detection_run_id=_uid(),
            detection_time=txn.timestamp + timedelta(seconds=random.randint(1, 15)),
            created_at=txn.timestamp + timedelta(seconds=random.randint(1, 15)),
        ))
    return alerts


def generate_model_scores(
    alerts: List[AlertModel],
) -> List[ModelScoreRecordModel]:
    """Generate per-model scores for every alert."""
    records = []
    model_defs = [
        ("statistical", "1.0.0", 0.25),
        ("behavioral", "1.0.0", 0.35),
        ("ml_ensemble", "3.0.0", 0.40),
    ]
    for alert in alerts:
        for model_name, version, weight in model_defs:
            raw = round(random.uniform(10, 100), 2)
            normalised = round(max(0, min(100, raw + random.uniform(-5, 5))), 2)
            records.append(ModelScoreRecordModel(
                id=_uid(),
                alert_id=alert.id,
                detection_run_id=alert.detection_run_id,
                model_name=model_name,
                model_version=version,
                raw_score=raw,
                normalized_score=normalised,
                confidence=round(random.uniform(0.5, 1.0), 2),
                weight=weight,
                explanations=None,
                scored_at=alert.detection_time,
            ))
    return records


def generate_investigations(
    alerts: List[AlertModel],
) -> List[InvestigationModel]:
    """Generate investigation audit entries for non-ACTIVE alerts."""
    entries = []
    for alert in alerts:
        if alert.status == AlertStatus.ACTIVE:
            continue
        analyst = random.choice(ANALYSTS)
        # Status change entry
        entries.append(InvestigationModel(
            id=_uid(),
            alert_id=alert.id,
            action=InvestigationAction.STATUS_CHANGED,
            old_status=AlertStatus.ACTIVE.value,
            new_status=alert.status.value,
            analyst_id=analyst[0],
            analyst_name=analyst[1],
            created_at=alert.detection_time + timedelta(minutes=random.randint(5, 120)),
        ))
        # Optional note
        if random.random() > 0.4:
            entries.append(InvestigationModel(
                id=_uid(),
                alert_id=alert.id,
                action=InvestigationAction.NOTE_ADDED,
                notes=random.choice([
                    "Reviewed transaction history — pattern consistent with fraud.",
                    "Amount within 1σ of entity baseline — likely false positive.",
                    "Geo-IP mismatch confirmed; referred for deeper review.",
                    "Velocity spike due to batch processing — not anomalous.",
                ]),
                analyst_id=analyst[0],
                analyst_name=analyst[1],
                created_at=alert.detection_time + timedelta(minutes=random.randint(60, 240)),
            ))
    return entries


def generate_feedback(
    alerts: List[AlertModel],
) -> List[FeedbackModel]:
    """Create feedback for resolved / false-positive alerts."""
    feedback = []
    resolved = [a for a in alerts if a.status in (AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE)]
    for i, alert in enumerate(resolved):
        is_fp = alert.status == AlertStatus.FALSE_POSITIVE
        analyst = random.choice(ANALYSTS)
        feedback.append(FeedbackModel(
            id=_uid(),
            feedback_id=f"FBK-{2000 + i:04d}",
            alert_id=alert.id,
            decision=FeedbackDecision.FALSE_POSITIVE if is_fp else FeedbackDecision.FRAUD,
            confidence=round(random.uniform(0.6, 1.0), 2),
            notes="Analyst-verified outcome.",
            analyst_id=analyst[0],
            analyst_name=analyst[1],
            used_for_training=random.random() > 0.5,
            resolved_at=alert.detection_time + timedelta(hours=random.randint(1, 48)),
        ))
    return feedback


def generate_metrics_snapshots(hours: int = 48) -> List[MetricsSnapshotModel]:
    """Generate hourly metrics snapshots for the last N hours."""
    snapshots = []
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    for h in range(hours):
        start = now - timedelta(hours=hours - h)
        end = start + timedelta(hours=1)
        total_txn = random.randint(800, 2000)
        total_alert = random.randint(5, 40)
        crit = random.randint(0, 3)
        high = random.randint(1, 8)
        med = random.randint(2, 15)
        low = total_alert - crit - high - med
        resolved = random.randint(0, total_alert // 2)
        frauds = random.randint(0, resolved)
        fps = resolved - frauds
        snapshots.append(MetricsSnapshotModel(
            id=_uid(),
            window_start=start,
            window_end=end,
            period=MetricPeriod.HOURLY,
            scope=MetricScope.GLOBAL,
            scope_value=None,
            total_transactions=total_txn,
            total_alerts=total_alert,
            critical_alerts=crit,
            high_alerts=high,
            medium_alerts=med,
            low_alerts=max(0, low),
            resolved_alerts=resolved,
            confirmed_frauds=frauds,
            false_positives=fps,
            avg_risk_score=round(random.uniform(35, 75), 2),
            precision=round(random.uniform(0.6, 0.95), 4),
            recall=round(random.uniform(0.5, 0.90), 4),
            f1_score=round(random.uniform(0.55, 0.92), 4),
            avg_resolution_time_sec=round(random.uniform(600, 7200), 1),
            computed_at=end,
        ))
    return snapshots


# -----------------------------------------------------------------
# Main seed routine
# -----------------------------------------------------------------

async def seed() -> None:
    """Populate the database with synthetic data."""
    setup_logging()
    logger.info("Starting database seed …")

    await init_db()

    async with async_session_factory() as session:
        # 1. Transactions
        txns = generate_transactions(200)
        session.add_all(txns)
        await session.flush()
        logger.info(f"Seeded {len(txns)} transactions")

        # 2. Feature Snapshots
        all_features: List[FeatureSnapshotModel] = []
        for txn in txns:
            run_id = _uid()
            all_features.extend(generate_features_for_txn(txn, run_id))
        session.add_all(all_features)
        await session.flush()
        logger.info(f"Seeded {len(all_features)} feature snapshots")

        # 3. Alerts
        alerts = generate_alerts(txns, fraction=0.25)
        session.add_all(alerts)
        await session.flush()
        logger.info(f"Seeded {len(alerts)} alerts")

        # 4. Model Score Records
        scores = generate_model_scores(alerts)
        session.add_all(scores)
        await session.flush()
        logger.info(f"Seeded {len(scores)} model score records")

        # 5. Investigations
        investigations = generate_investigations(alerts)
        session.add_all(investigations)
        await session.flush()
        logger.info(f"Seeded {len(investigations)} investigation entries")

        # 6. Feedback
        fb = generate_feedback(alerts)
        session.add_all(fb)
        await session.flush()
        logger.info(f"Seeded {len(fb)} feedback records")

        # 7. Metrics Snapshots
        metrics = generate_metrics_snapshots(48)
        session.add_all(metrics)
        await session.flush()
        logger.info(f"Seeded {len(metrics)} metrics snapshots")

        await session.commit()

    logger.info("Database seed complete ✓")


if __name__ == "__main__":
    asyncio.run(seed())
