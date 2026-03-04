"""
Train ML Model
==============
Train and persist the ML anomaly detector artifact used by MLDetector.

Usage:
    python -m app.detection.train_model
"""

from datetime import datetime
from pathlib import Path
import random

import numpy as np
from joblib import dump
from sklearn.ensemble import IsolationForest

from app.config import settings

FEATURE_NAMES = [
    "amount_normalized",
    "time_risk",
    "velocity",
    "geo_risk",
    "device_risk",
    "destination_risk",
    "frequency_deviation",
    "account_age_risk",
]


def generate_training_data(n_normal: int = 5000, n_anomaly: int = 300) -> np.ndarray:
    """Generate synthetic feature vectors for unsupervised anomaly training."""
    normal = []
    for _ in range(n_normal):
        normal.append(
            [
                random.uniform(-0.6, 0.8),   # amount_normalized
                random.uniform(0.0, 0.2),    # time_risk
                random.uniform(0.0, 0.5),    # velocity
                random.uniform(0.05, 0.55),  # geo_risk
                random.uniform(0.0, 0.2),    # device_risk
                random.uniform(0.0, 0.3),    # destination_risk
                random.uniform(0.0, 0.6),    # frequency_deviation
                random.uniform(0.0, 0.2),    # account_age_risk
            ]
        )

    anomaly = []
    for _ in range(n_anomaly):
        anomaly.append(
            [
                random.uniform(0.9, 2.5),    # amount_normalized
                random.uniform(0.6, 1.0),    # time_risk
                random.uniform(0.7, 1.5),    # velocity
                random.uniform(0.7, 1.0),    # geo_risk
                random.uniform(0.7, 1.0),    # device_risk
                random.uniform(0.7, 1.0),    # destination_risk
                random.uniform(0.8, 2.0),    # frequency_deviation
                random.uniform(0.6, 1.0),    # account_age_risk
            ]
        )

    x = np.array(normal + anomaly, dtype=float)
    np.random.shuffle(x)
    return x


def main() -> None:
    x = generate_training_data()

    model = IsolationForest(
        n_estimators=250,
        contamination=0.06,
        random_state=42,
    )
    model.fit(x)

    scores = model.decision_function(x)
    threshold = float(np.quantile(scores, 0.08))

    artifact = {
        "model": model,
        "feature_names": FEATURE_NAMES,
        "threshold": threshold,
        "version": settings.ML_MODEL_VERSION,
        "trained_at": datetime.utcnow().isoformat(),
        "sample_count": int(x.shape[0]),
    }

    output_path = Path(settings.ML_MODEL_PATH)
    if not output_path.is_absolute():
        backend_root = Path(__file__).resolve().parents[2]
        output_path = backend_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump(artifact, output_path)

    print(f"Model trained and saved to: {output_path}")
    print(f"Samples: {x.shape[0]}")
    print(f"Feature count: {x.shape[1]}")
    print(f"Version: {settings.ML_MODEL_VERSION}")


if __name__ == "__main__":
    main()
