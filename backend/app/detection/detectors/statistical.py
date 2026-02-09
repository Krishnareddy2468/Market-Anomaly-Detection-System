"""
Statistical Detector
====================
Rule-based and statistical anomaly detection.
Uses Z-scores, thresholds, and basic statistical analysis.
"""

from typing import Dict, Any, List

from app.detection.detectors.base import BaseDetector, DetectionResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class StatisticalDetector(BaseDetector):
    """
    Statistical anomaly detector.
    
    Analyzes:
    - Amount deviations (Z-score)
    - Time pattern anomalies
    - Velocity violations
    - Threshold breaches
    """
    
    # Thresholds
    HIGH_AMOUNT_THRESHOLD = 10000  # USD
    ZSCORE_THRESHOLD = 3.0
    VELOCITY_THRESHOLD = 5  # transactions per hour
    
    @property
    def name(self) -> str:
        return "statistical"
    
    async def detect(self, features: Dict[str, Any]) -> DetectionResult:
        """Run statistical analysis on features."""
        score = 0.0
        explanations: List[str] = []
        
        # 1. Amount Analysis
        amount = features.get("amount", 0)
        amount_zscore = features.get("amount_zscore", 0)
        
        if amount > self.HIGH_AMOUNT_THRESHOLD:
            contribution = min(30, (amount / self.HIGH_AMOUNT_THRESHOLD) * 15)
            score += contribution
            explanations.append(f"High transaction amount: ${amount:,.2f}")
        
        if abs(amount_zscore) > self.ZSCORE_THRESHOLD:
            contribution = min(25, abs(amount_zscore) * 5)
            score += contribution
            explanations.append(f"Amount deviation: {amount_zscore:.1f}σ from mean")
        
        # 2. Time Pattern Analysis
        is_unusual_hour = features.get("is_unusual_hour", False)
        if is_unusual_hour:
            score += 15
            explanations.append("Transaction at unusual hour")
        
        # 3. Velocity Check
        hourly_count = features.get("hourly_transaction_count", 0)
        if hourly_count > self.VELOCITY_THRESHOLD:
            contribution = min(20, (hourly_count - self.VELOCITY_THRESHOLD) * 5)
            score += contribution
            explanations.append(f"High transaction velocity: {hourly_count}/hour")
        
        # 4. Geographic Risk
        geo_risk = features.get("geo_risk_score", 0)
        if geo_risk > 50:
            contribution = geo_risk * 0.2
            score += contribution
            if geo_risk > 80:
                explanations.append("High-risk geographic location")
        
        # 5. Device Risk
        is_new_device = features.get("is_new_device", False)
        if is_new_device:
            score += 10
            explanations.append("New device fingerprint")
        
        # Normalize and clamp
        final_score = self.clamp_score(score)
        
        # Confidence based on data availability
        data_points = sum([
            1 if features.get("amount") is not None else 0,
            1 if features.get("amount_zscore") is not None else 0,
            1 if features.get("hourly_transaction_count") is not None else 0,
            1 if features.get("geo_risk_score") is not None else 0,
        ])
        confidence = min(1.0, data_points / 3)
        
        logger.debug(
            "Statistical detection complete",
            score=final_score,
            confidence=confidence,
            explanations=explanations,
        )
        
        return DetectionResult(
            score=final_score,
            confidence=confidence,
            explanations=explanations,
            metadata={
                "detector": self.name,
                "version": self.version,
            },
        )
