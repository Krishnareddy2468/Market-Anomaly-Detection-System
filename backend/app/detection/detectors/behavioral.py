"""
Behavioral Detector
===================
Behavioral pattern analysis detector.
Compares current transaction against historical entity behavior.
"""

from typing import Dict, Any, List

from app.detection.detectors.base import BaseDetector, DetectionResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class BehavioralDetector(BaseDetector):
    """
    Behavioral anomaly detector.
    
    Analyzes:
    - Deviation from normal spending patterns
    - New transaction destinations
    - Channel changes
    - Time pattern changes
    - Frequency deviations
    """
    
    @property
    def name(self) -> str:
        return "behavioral"
    
    async def detect(self, features: Dict[str, Any]) -> DetectionResult:
        """Analyze behavioral patterns."""
        score = 0.0
        explanations: List[str] = []
        
        # 1. Spending Pattern Deviation
        amount_pct_deviation = features.get("amount_pct_from_avg", 0)
        if amount_pct_deviation > 200:  # More than 200% above average
            contribution = min(25, (amount_pct_deviation - 200) / 20)
            score += contribution
            explanations.append(f"Spending {amount_pct_deviation:.0f}% above typical")
        
        # 2. New Destination Analysis
        is_new_destination = features.get("is_new_destination", False)
        if is_new_destination:
            score += 15
            explanations.append("First-time transaction destination")
        
        # 3. Channel Behavior
        is_new_channel = features.get("is_new_channel", False)
        if is_new_channel:
            score += 10
            explanations.append("New transaction channel used")
        
        # 4. Time Pattern Deviation
        time_pattern_score = features.get("time_pattern_deviation", 0)
        if time_pattern_score > 50:
            contribution = time_pattern_score * 0.2
            score += contribution
            explanations.append("Unusual time pattern for this entity")
        
        # 5. Frequency Deviation
        frequency_zscore = features.get("frequency_zscore", 0)
        if abs(frequency_zscore) > 2:
            contribution = min(20, abs(frequency_zscore) * 5)
            score += contribution
            if frequency_zscore > 0:
                explanations.append(f"Transaction frequency {abs(frequency_zscore):.1f}x higher than usual")
            else:
                # Unusually low frequency might indicate dormant account takeover
                explanations.append("Activity after dormant period")
        
        # 6. Geographic Pattern
        is_new_location = features.get("is_new_geo_location", False)
        location_distance = features.get("location_distance_km", 0)
        
        if is_new_location and location_distance > 500:
            contribution = min(25, location_distance / 100)
            score += contribution
            explanations.append(f"Transaction from new location ({location_distance:.0f}km away)")
        
        # 7. Account Age Factor
        account_age_days = features.get("account_age_days", 365)
        if account_age_days < 30:
            # New accounts are higher risk
            score += 10
            explanations.append("New account (less than 30 days old)")
        
        # Normalize
        final_score = self.clamp_score(score)
        
        # Confidence based on historical data availability
        has_history = features.get("has_historical_data", False)
        confidence = 0.9 if has_history else 0.5
        
        logger.debug(
            "Behavioral detection complete",
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
                "has_history": has_history,
            },
        )
