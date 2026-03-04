"""
Feature Engineer
================
Extracts and computes features from raw transactions for detection.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import hashlib

from app.core.logging import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    """
    Feature engineering pipeline.
    
    Transforms raw transaction data into features for fraud detection:
    - Statistical features (amount z-scores, etc.)
    - Temporal features (time of day, day of week, etc.)
    - Behavioral features (deviation from patterns)
    - Entity features (account age, history, etc.)
    - Device/location features
    """
    
    # High-risk countries (example list)
    HIGH_RISK_COUNTRIES = {"XX", "YY", "ZZ"}
    
    # Unusual hours (midnight to 5 AM)
    UNUSUAL_HOURS = set(range(0, 5))
    
    def __init__(self):
        self.feature_version = "1.0.0"

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Convert datetimes to naive UTC for consistent arithmetic."""
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    @staticmethod
    def _to_datetime(value: Any) -> Optional[datetime]:
        """Best-effort conversion to datetime."""
        if isinstance(value, datetime):
            return FeatureEngineer._normalize_datetime(value)
        if isinstance(value, str):
            text = value.strip()
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            try:
                parsed = datetime.fromisoformat(text)
                return FeatureEngineer._normalize_datetime(parsed)
            except ValueError:
                return None
        return None

    def _history_rows(self, transaction: Any) -> List[Dict[str, Any]]:
        """Normalize historical transactions to dictionaries."""
        history = getattr(transaction, "historical_transactions", None) or []
        normalized: List[Dict[str, Any]] = []
        for item in history:
            if isinstance(item, dict):
                normalized.append(item)
                continue

            normalized.append(
                {
                    "transaction_id": getattr(item, "transaction_id", None),
                    "amount": getattr(item, "amount", None),
                    "timestamp": getattr(item, "timestamp", None),
                    "destination_account": getattr(item, "destination_account", None),
                    "channel": getattr(item, "channel", None),
                    "device_fingerprint": getattr(item, "device_fingerprint", None),
                    "geo_country": getattr(item, "geo_country", None),
                }
            )
        return normalized
    
    async def extract_features(self, transaction: Any) -> Dict[str, Any]:
        """
        Extract all features from a transaction.
        
        Returns a dictionary of computed features ready for detectors.
        """
        logger.debug(
            "Extracting features",
            transaction_id=getattr(transaction, 'transaction_id', 'unknown'),
        )
        
        features: Dict[str, Any] = {}
        
        # Basic transaction features
        features.update(self._extract_basic_features(transaction))
        
        # Temporal features
        features.update(self._extract_temporal_features(transaction))
        
        # Statistical features
        features.update(await self._extract_statistical_features(transaction))
        
        # Behavioral features
        features.update(await self._extract_behavioral_features(transaction))
        
        # Device/location features
        features.update(self._extract_device_features(transaction))
        
        # Add metadata
        features["feature_version"] = self.feature_version
        features["extracted_at"] = datetime.utcnow().isoformat()
        
        return features
    
    def _extract_basic_features(self, transaction: Any) -> Dict[str, Any]:
        """Extract basic transaction features."""
        return {
            "transaction_id": getattr(transaction, 'transaction_id', ''),
            "amount": getattr(transaction, 'amount', 0),
            "currency": getattr(transaction, 'currency', 'INR'),
            "source_account": getattr(transaction, 'source_account', ''),
            "destination_account": getattr(transaction, 'destination_account', ''),
            "channel": getattr(transaction, 'channel', 'unknown'),
        }
    
    def _extract_temporal_features(self, transaction: Any) -> Dict[str, Any]:
        """Extract time-based features."""
        timestamp = getattr(transaction, 'timestamp', datetime.utcnow())
        
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        return {
            "hour_of_day": hour,
            "day_of_week": day_of_week,
            "is_weekend": day_of_week >= 5,
            "is_unusual_hour": hour in self.UNUSUAL_HOURS,
            "is_end_of_month": timestamp.day > 25,
            "quarter": (timestamp.month - 1) // 3 + 1,
        }
    
    async def _extract_statistical_features(self, transaction: Any) -> Dict[str, Any]:
        """
        Extract statistical features.
        
        In production, these would be computed from historical data.
        """
        amount = float(getattr(transaction, 'amount', 0))
        history = self._history_rows(transaction)
        historical_amounts: List[float] = []
        for row in history:
            value = row.get("amount")
            if isinstance(value, (int, float)):
                historical_amounts.append(float(value))
        
        if len(historical_amounts) >= 5:
            historical_mean = sum(historical_amounts) / len(historical_amounts)
            variance = sum((x - historical_mean) ** 2 for x in historical_amounts) / len(historical_amounts)
            historical_std = max(1.0, variance ** 0.5)
        else:
            historical_mean = amount if amount > 0 else 1500.0
            historical_std = max(1.0, historical_mean * 0.5)
        
        # Z-score calculation
        if historical_std > 0:
            amount_zscore = (amount - historical_mean) / historical_std
        else:
            amount_zscore = 0
        
        # Percentage deviation from average
        if historical_mean > 0:
            amount_pct_from_avg = ((amount - historical_mean) / historical_mean) * 100
        else:
            amount_pct_from_avg = 0
        
        return {
            "amount_zscore": round(amount_zscore, 2),
            "amount_pct_from_avg": round(amount_pct_from_avg, 2),
            "historical_mean": historical_mean,
            "historical_std": historical_std,
            "is_above_average": amount > historical_mean,
            "is_high_value": amount > 10000,
        }
    
    async def _extract_behavioral_features(self, transaction: Any) -> Dict[str, Any]:
        """
        Extract behavioral pattern features.
        
        Compares current transaction to entity's historical behavior.
        """
        history = self._history_rows(transaction)
        now = getattr(transaction, "timestamp", datetime.utcnow())
        now_dt = self._normalize_datetime(now) if isinstance(now, datetime) else datetime.utcnow()

        parsed_history: List[Dict[str, Any]] = []
        for row in history:
            ts = self._to_datetime(row.get("timestamp"))
            if ts is None:
                continue
            parsed_history.append({**row, "parsed_timestamp": ts})

        has_history = len(parsed_history) > 0
        current_destination = getattr(transaction, "destination_account", None)
        current_channel = getattr(transaction, "channel", None)
        current_geo = getattr(transaction, "geo_location", None)

        historical_destinations = {
            row.get("destination_account")
            for row in parsed_history
            if row.get("destination_account")
        }
        historical_channels = {
            row.get("channel")
            for row in parsed_history
            if row.get("channel")
        }
        historical_geos = {
            row.get("geo_country")
            for row in parsed_history
            if row.get("geo_country")
        }

        is_new_destination = bool(current_destination) and current_destination not in historical_destinations
        is_new_channel = bool(current_channel) and current_channel not in historical_channels
        is_new_geo_location = bool(current_geo) and current_geo not in historical_geos

        hourly_transaction_count = sum(
            1
            for row in parsed_history
            if 0 <= (now_dt - row["parsed_timestamp"]).total_seconds() <= 3600
        )

        daily_counts: Dict[str, int] = {}
        for row in parsed_history:
            day_key = row["parsed_timestamp"].date().isoformat()
            daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
        current_day_key = now_dt.date().isoformat()
        current_day_count = daily_counts.get(current_day_key, 0) + 1
        day_values = list(daily_counts.values()) if daily_counts else [0]
        day_mean = sum(day_values) / len(day_values)
        day_std = (sum((x - day_mean) ** 2 for x in day_values) / len(day_values)) ** 0.5
        if day_std < 1e-6:
            frequency_zscore = 0.0
        else:
            frequency_zscore = (current_day_count - day_mean) / day_std

        historical_hours = [row["parsed_timestamp"].hour for row in parsed_history]
        if historical_hours:
            avg_hour = sum(historical_hours) / len(historical_hours)
            time_pattern_deviation = min(100.0, abs(now_dt.hour - avg_hour) * 8.0)
        else:
            time_pattern_deviation = 0.0

        if parsed_history:
            earliest = min(row["parsed_timestamp"] for row in parsed_history)
            account_age_days = max(1, int((now_dt - earliest).total_seconds() / 86400))
        else:
            account_age_days = 1

        return {
            "has_historical_data": has_history,
            "is_new_destination": is_new_destination,
            "is_new_channel": is_new_channel,
            "frequency_zscore": round(float(frequency_zscore), 2),
            "time_pattern_deviation": round(float(time_pattern_deviation), 2),
            "is_new_geo_location": is_new_geo_location,
            "location_distance_km": 0.0,
            "account_age_days": account_age_days,
            "hourly_transaction_count": hourly_transaction_count,
        }
    
    def _extract_device_features(self, transaction: Any) -> Dict[str, Any]:
        """Extract device and location features."""
        ip_address = getattr(transaction, 'ip_address', None)
        device_fingerprint = getattr(transaction, 'device_fingerprint', None)
        geo_location = getattr(transaction, 'geo_location', None)
        history = self._history_rows(transaction)
        
        # Calculate device hash (for new device detection)
        device_hash = None
        if device_fingerprint:
            device_hash = hashlib.sha256(device_fingerprint.encode()).hexdigest()[:16]
        
        # Deterministic geo risk scoring
        geo_risk_score = 30.0  # Default low risk
        if geo_location:
            country_code = geo_location[:2] if len(geo_location) >= 2 else ""
            if country_code in self.HIGH_RISK_COUNTRIES:
                geo_risk_score = 85.0

        known_devices = {
            row.get("device_fingerprint")
            for row in history
            if row.get("device_fingerprint")
        }
        is_new_device = bool(device_fingerprint) and device_fingerprint not in known_devices

        ip_prefix = (ip_address or "").strip().lower()
        is_tor = ip_prefix.startswith("tor:")
        is_vpn = ip_prefix.startswith("vpn:")
        
        return {
            "has_ip_address": ip_address is not None,
            "has_device_fingerprint": device_fingerprint is not None,
            "device_hash": device_hash,
            "is_new_device": is_new_device,
            "geo_risk_score": geo_risk_score,
            "is_vpn": is_vpn,
            "is_tor": is_tor,
        }
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names produced by this engineer."""
        return [
            # Basic
            "transaction_id", "amount", "currency", "source_account",
            "destination_account", "channel",
            # Temporal
            "hour_of_day", "day_of_week", "is_weekend", "is_unusual_hour",
            "is_end_of_month", "quarter",
            # Statistical
            "amount_zscore", "amount_pct_from_avg", "historical_mean",
            "historical_std", "is_above_average", "is_high_value",
            # Behavioral
            "has_historical_data", "is_new_destination", "is_new_channel",
            "frequency_zscore", "time_pattern_deviation", "is_new_geo_location",
            "location_distance_km", "account_age_days", "hourly_transaction_count",
            # Device
            "has_ip_address", "has_device_fingerprint", "device_hash",
            "is_new_device", "geo_risk_score", "is_vpn", "is_tor",
            # Metadata
            "feature_version", "extracted_at",
        ]
