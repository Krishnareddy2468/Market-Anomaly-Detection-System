"""
Backend API Smoke Test
======================
Exercises every route group against a running backend + seeded database.

Usage:
    # 1. Point at a database and start the API
    export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/fraud_detection"
    python -m app.db.seed                      # optional: populate demo data
    uvicorn app.main:app --port 8000

    # 2. Run the smoke test (from backend/)
    python scripts/smoke_test.py               # defaults to http://127.0.0.1:8000
    BASE_URL=http://127.0.0.1:8000 python scripts/smoke_test.py

Exit code is non-zero if any check fails, so it is CI-friendly.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

import httpx

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")

_passed = 0
_failed = 0


def check(name: str, method: str, path: str, *, json=None, params=None, expect: int = 200):
    global _passed, _failed
    try:
        resp = httpx.request(method, BASE_URL + path, json=json, params=params, timeout=20)
    except Exception as exc:  # noqa: BLE001
        print(f"❌ {name} -> connection error: {exc}")
        _failed += 1
        return None

    if resp.status_code == expect:
        print(f"✅ {name} -> {resp.status_code}")
        _passed += 1
    else:
        print(f"❌ {name} -> {resp.status_code} (expected {expect})\n   {resp.text[:300]}")
        _failed += 1
    return resp


def main() -> int:
    print(f"================ BACKEND SMOKE TESTS ({BASE_URL}) ================")

    # --- Health ---
    check("GET /health", "GET", "/health")

    # --- Dashboard ---
    check("GET dashboard/metrics", "GET", "/api/dashboard/metrics")
    check("GET dashboard/alerts-trend", "GET", "/api/dashboard/alerts-trend", params={"range": "24h"})
    check("GET dashboard/severity-distribution", "GET", "/api/dashboard/severity-distribution")

    # --- Alerts ---
    resp = check("GET alerts (paged)", "GET", "/api/alerts", params={"page": 1, "limit": 5})
    alert_id = None
    if resp is not None and resp.status_code == 200:
        rows = resp.json().get("data") or []
        if rows:
            alert_id = rows[0].get("alert_id") or rows[0].get("id")

    # --- Analytics ---
    check("GET analytics/metrics", "GET", "/api/analytics/metrics")
    check("GET analytics/model-performance", "GET", "/api/analytics/model-performance")
    check("GET analytics/alert-volume", "GET", "/api/analytics/alert-volume")
    check("GET analytics/confusion-matrix", "GET", "/api/analytics/confusion-matrix")
    check("GET analytics/detection-rate", "GET", "/api/analytics/detection-rate")

    # --- Feedback ---
    check("GET feedback (list)", "GET", "/api/feedback", params={"page": 1, "limit": 5})
    check("GET feedback/summary", "GET", "/api/feedback/summary")

    # --- Alert detail + investigation context (uses a real seeded alert) ---
    if alert_id:
        check(f"GET alerts/{alert_id}", "GET", f"/api/alerts/{alert_id}")
        check(f"GET investigations/{alert_id}", "GET", f"/api/investigations/{alert_id}")
        check(f"GET investigations/{alert_id}/history", "GET", f"/api/investigations/{alert_id}/history")
    else:
        print("⚠️  no seeded alert found; skipped alert-detail/investigation reads")

    # --- Detection pipeline: suspicious transaction ---
    suspicious_ts = datetime.now(timezone.utc).replace(hour=2, minute=14).isoformat()
    suspicious = {
        "transaction_id": f"SMOKE-{int(datetime.now().timestamp())}",
        "amount": 7_670_000,
        "timestamp": suspicious_ts,
        "source_account": "ACC-SRC-1",
        "destination_account": "ACC-DST-9",
        "entity_id": "user-smoke-1",
        "entity_type": "USER",
        "currency": "INR",
        "channel": "API",
    }
    resp = check("POST detection/evaluate (suspicious)", "POST", "/api/detection/evaluate", json=suspicious)
    if resp is not None and resp.status_code == 200:
        d = resp.json().get("data", resp.json())
        print(f"   risk={d.get('risk_score')} severity={d.get('severity')} "
              f"alert={d.get('should_alert')} ms={d.get('processing_time_ms')}")

    # --- Detection pipeline: benign transaction ---
    benign = dict(
        suspicious,
        transaction_id=f"SMOKE-LOW-{int(datetime.now().timestamp())}",
        amount=2_850,
        timestamp=datetime.now(timezone.utc).replace(hour=10, minute=30).isoformat(),
        channel="POS",
    )
    resp = check("POST detection/evaluate (benign)", "POST", "/api/detection/evaluate", json=benign)
    if resp is not None and resp.status_code == 200:
        d = resp.json().get("data", resp.json())
        print(f"   risk={d.get('risk_score')} severity={d.get('severity')} alert={d.get('should_alert')}")

    print("=================================================================")
    print(f"PASS={_passed} FAIL={_failed}")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
