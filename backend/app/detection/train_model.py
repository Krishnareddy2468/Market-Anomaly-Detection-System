"""
Train ML Model
==============
Train and persist the ML anomaly detector artifact used by MLDetector.

Usage:
    python -m app.detection.train_model
    python -m app.detection.train_model --dataset /path/to/fraud_transactions.csv
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

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


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for training."""
    parser = argparse.ArgumentParser(description="Train anomaly model from dataset")
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Path to CSV dataset (must include timestamp + label + base transaction fields)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output path for model artifact. Defaults to ML_MODEL_PATH.",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.2,
        help="Validation split ratio using time-based split (default: 0.2).",
    )
    return parser.parse_args()


def resolve_dataset_path(dataset_arg: Optional[str]) -> Path:
    """Resolve the dataset path from CLI, env, or default data folder."""
    if dataset_arg:
        return Path(dataset_arg).expanduser().resolve()

    env_dataset = settings.model_dump().get("TRAINING_DATASET_PATH")
    if env_dataset:
        return Path(str(env_dataset)).expanduser().resolve()

    backend_root = Path(__file__).resolve().parents[2]
    return (backend_root / "data" / "fraud_transactions.csv").resolve()


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create deterministic features aligned to runtime detector inputs."""
    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True, errors="coerce")
    work = work.dropna(subset=["timestamp", "amount", "label", "entity_id"])
    work = work.sort_values("timestamp").reset_index(drop=True)

    work["amount"] = pd.to_numeric(work["amount"], errors="coerce").fillna(0.0)
    amount_mean = float(work["amount"].mean())
    amount_std = float(work["amount"].std(ddof=0)) or 1.0
    work["amount_normalized"] = (work["amount"] - amount_mean) / amount_std

    work["hour"] = work["timestamp"].dt.hour
    work["time_risk"] = work["hour"].isin([0, 1, 2, 3, 4]).astype(float)

    work["tx_date"] = work["timestamp"].dt.date
    day_count = (
        work.groupby(["entity_id", "tx_date"], observed=True)["transaction_id"]
        .transform("count")
        .astype(float)
    )
    work["velocity"] = np.clip(day_count / 10.0, 0.0, 1.5)

    country_fraud_rate = work.groupby("geo_country", observed=True)["label"].mean().to_dict()
    device_fraud_rate = work.groupby("device_fingerprint", observed=True)["label"].mean().to_dict()
    destination_fraud_rate = (
        work.groupby("destination_account", observed=True)["label"].mean().to_dict()
    )
    work["geo_risk"] = work["geo_country"].map(country_fraud_rate).fillna(0.0).astype(float)
    work["device_risk"] = (
        work["device_fingerprint"].map(device_fraud_rate).fillna(0.0).astype(float)
    )
    work["destination_risk"] = (
        work["destination_account"].map(destination_fraud_rate).fillna(0.0).astype(float)
    )

    entity_daily_mean = work.groupby("entity_id", observed=True)["amount"].transform("mean")
    entity_daily_std = work.groupby("entity_id", observed=True)["amount"].transform("std")
    entity_daily_std = entity_daily_std.replace(0, np.nan).fillna(1.0)
    work["frequency_deviation"] = np.clip(
        np.abs((work["amount"] - entity_daily_mean) / entity_daily_std), 0.0, 3.0
    )

    first_seen = work.groupby("entity_id", observed=True)["timestamp"].transform("min")
    account_age_days = (work["timestamp"] - first_seen).dt.total_seconds() / 86400.0
    work["account_age_risk"] = np.clip(1.0 - (account_age_days / 365.0), 0.0, 1.0)

    return work


def train_eval_split(work: pd.DataFrame, val_ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split dataset by timestamp so validation simulates future traffic."""
    ratio = min(max(val_ratio, 0.05), 0.4)
    split_idx = int(len(work) * (1.0 - ratio))
    train_df = work.iloc[:split_idx].copy()
    val_df = work.iloc[split_idx:].copy()
    if len(train_df) < 1000 or len(val_df) < 200:
        raise ValueError("Dataset too small after split; provide more rows or adjust --val-ratio")
    return train_df, val_df


def evaluate(
    y_true: np.ndarray,
    anomaly_scores: np.ndarray,
    threshold: float,
) -> Dict[str, float]:
    """Compute supervised validation metrics using anomaly score threshold."""
    y_pred = (anomaly_scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "roc_auc": float(roc_auc_score(y_true, anomaly_scores)),
        "pr_auc": float(average_precision_score(y_true, anomaly_scores)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }


def main() -> None:
    args = parse_args()
    dataset_path = resolve_dataset_path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    required_cols = {
        "transaction_id",
        "timestamp",
        "amount",
        "destination_account",
        "entity_id",
        "device_fingerprint",
        "geo_country",
        "label",
    }
    raw_df = pd.read_csv(dataset_path)
    missing = required_cols - set(raw_df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")

    work = engineer_features(raw_df)
    train_df, val_df = train_eval_split(work, args.val_ratio)

    x_train = train_df[FEATURE_NAMES].to_numpy(dtype=float)
    y_train = train_df["label"].to_numpy(dtype=int)
    x_train_normals = x_train[y_train == 0]
    if len(x_train_normals) < 500:
        raise ValueError("Too few normal samples to train IsolationForest robustly")

    model = IsolationForest(n_estimators=250, contamination=0.06, random_state=42, n_jobs=-1)
    model.fit(x_train_normals)

    train_anomaly_scores = -model.decision_function(x_train)
    val_anomaly_scores = -model.decision_function(val_df[FEATURE_NAMES].to_numpy(dtype=float))
    y_val = val_df["label"].to_numpy(dtype=int)

    fraud_rate_train = float(np.clip(y_train.mean(), 0.005, 0.20))
    threshold = float(np.quantile(train_anomaly_scores, 1.0 - fraud_rate_train))
    metrics = evaluate(y_val, val_anomaly_scores, threshold)

    artifact = {
        "model": model,
        "feature_names": FEATURE_NAMES,
        "threshold": threshold,
        "version": settings.ML_MODEL_VERSION,
        "trained_at": datetime.utcnow().isoformat(),
        "sample_count": int(len(work)),
        "train_count": int(len(train_df)),
        "val_count": int(len(val_df)),
        "dataset_path": str(dataset_path),
        "fraud_rate_train": float(y_train.mean()),
        "fraud_rate_val": float(y_val.mean()),
        "metrics": metrics,
    }

    output_path = Path(args.output) if args.output else Path(settings.ML_MODEL_PATH)
    if not output_path.is_absolute():
        backend_root = Path(__file__).resolve().parents[2]
        output_path = backend_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump(artifact, output_path)

    print(f"Model trained and saved to: {output_path}")
    print(f"Dataset: {dataset_path}")
    print(f"Samples: {len(work)} (train={len(train_df)}, val={len(val_df)})")
    print(f"Feature count: {len(FEATURE_NAMES)}")
    print(f"Fraud rate: train={y_train.mean():.4f} val={y_val.mean():.4f}")
    print(f"Threshold (anomaly score): {threshold:.6f}")
    print(
        "Validation metrics: "
        f"ROC-AUC={metrics['roc_auc']:.4f}, "
        f"PR-AUC={metrics['pr_auc']:.4f}, "
        f"Precision={metrics['precision']:.4f}, "
        f"Recall={metrics['recall']:.4f}, "
        f"F1={metrics['f1']:.4f}"
    )
    print(f"Version: {settings.ML_MODEL_VERSION}")


if __name__ == "__main__":
    main()
