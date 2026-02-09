"""
Feature Engineer
================
Extracts and computes features from raw transactions for detection.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import random
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
            "currency": "USD",
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
        amount = getattr(transaction, 'amount', 0)
        
        # Mock historical statistics (would come from database)
        historical_mean = 1500.0
        historical_std = 800.0
        
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
        # Mock behavioral analysis (would come from behavior service)
        historical_transactions = getattr(transaction, 'historical_transactions', None)
        has_history = historical_transactions is not None and len(historical_transactions or []) > 0
        
        # For MVP, generate mock behavioral signals
        return {
            "has_historical_data": has_history,
            "is_new_destination": random.random() > 0.8,
            "is_new_channel": random.random() > 0.9,
            "frequency_zscore": random.uniform(-1, 3),
            "time_pattern_deviation": random.uniform(0, 80),
            "is_new_geo_location": random.random() > 0.85,
            "location_distance_km": random.uniform(0, 2000) if random.random() > 0.7 else 0,
            "account_age_days": random.randint(1, 1000),
            "hourly_transaction_count": random.randint(0, 8),
        }
    
    def _extract_device_features(self, transaction: Any) -> Dict[str, Any]:
        """Extract device and location features."""
        ip_address = getattr(transaction, 'ip_address', None)
        device_fingerprint = getattr(transaction, 'device_fingerprint', None)
        geo_location = getattr(transaction, 'geo_location', None)
        
        # Calculate device hash (for new device detection)
        device_hash = None
        if device_fingerprint:
            device_hash = hashlib.sha256(device_fingerprint.encode()).hexdigest()[:16]
        
        # Mock geo risk scoring
        geo_risk_score = 30.0  # Default low risk
        if geo_location:
            country_code = geo_location[:2] if len(geo_location) >= 2 else ""
            if country_code in self.HIGH_RISK_COUNTRIES:
                geo_risk_score = 85.0
        
        return {
            "has_ip_address": ip_address is not None,
            "has_device_fingerprint": device_fingerprint is not None,
            "device_hash": device_hash,
            "is_new_device": random.random() > 0.85,  # Mock
            "geo_risk_score": geo_risk_score,
            "is_vpn": random.random() > 0.95,  # Mock VPN detection
            "is_tor": random.random() > 0.99,  # Mock Tor detection
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
