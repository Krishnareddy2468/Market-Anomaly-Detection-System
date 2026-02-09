"""
Risk Scorer
===========
Combines detector outputs into a unified risk score.
"""

from typing import Dict, List
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScoringResult:
    """Result of risk scoring."""
    composite_score: float
    component_scores: Dict[str, float]
    score_breakdown: Dict[str, float]
    confidence: float


class RiskScorer:
    """
    Unified risk scoring engine.
    
    Combines multiple detector outputs into a single,
    interpretable risk score.
    """
    
    # Default weights for score components
    DEFAULT_WEIGHTS = {
        "statistical": 0.25,
        "behavioral": 0.35,
        "ml": 0.40,
    }
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        self._validate_weights()
    
    def _validate_weights(self) -> None:
        """Ensure weights sum to 1.0 (or close)."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(
                "Weights do not sum to 1.0, normalizing",
                total=total,
            )
            # Normalize weights
            self.weights = {k: v / total for k, v in self.weights.items()}
    
    def calculate_composite_score(
        self,
        detector_scores: Dict[str, float],
        confidences: Dict[str, float] = None,
    ) -> ScoringResult:
        """
        Calculate composite risk score from detector outputs.
        
        Uses confidence-weighted averaging:
        - Higher confidence scores contribute more
        - Missing detectors don't affect the score adversely
        """
        confidences = confidences or {k: 1.0 for k in detector_scores}
        
        weighted_sum = 0.0
        total_weight = 0.0
        score_breakdown = {}
        
        for detector, score in detector_scores.items():
            weight = self.weights.get(detector, 0.0)
            confidence = confidences.get(detector, 1.0)
            
            # Effective weight considers both assigned weight and confidence
            effective_weight = weight * confidence
            
            contribution = score * effective_weight
            weighted_sum += contribution
            total_weight += effective_weight
            
            score_breakdown[detector] = {
                "raw_score": score,
                "weight": weight,
                "confidence": confidence,
                "contribution": contribution,
            }
        
        # Calculate composite score
        if total_weight > 0:
            composite_score = weighted_sum / total_weight
        else:
            composite_score = 50.0  # Neutral if no data
        
        # Overall confidence is the weighted average of confidences
        overall_confidence = (
            sum(c * self.weights.get(d, 0) for d, c in confidences.items())
            / sum(self.weights.get(d, 0) for d in confidences)
            if confidences else 1.0
        )
        
        logger.debug(
            "Composite score calculated",
            composite_score=composite_score,
            confidence=overall_confidence,
        )
        
        return ScoringResult(
            composite_score=round(composite_score, 2),
            component_scores=detector_scores,
            score_breakdown=score_breakdown,
            confidence=round(overall_confidence, 2),
        )
    
    def apply_business_rules(
        self,
        base_score: float,
        rules_context: Dict,
    ) -> float:
        """
        Apply business rules to adjust the score.
        
        Examples:
        - VIP customers: reduce score by 10%
        - High-value merchants: validation required regardless
        - Known fraud patterns: minimum score of 80
        """
        adjusted_score = base_score
        
        # Example business rules
        if rules_context.get("is_vip_customer"):
            adjusted_score *= 0.9
        
        if rules_context.get("matches_known_pattern"):
            adjusted_score = max(adjusted_score, 80.0)
        
        if rules_context.get("verified_merchant"):
            adjusted_score *= 0.85
        
        if rules_context.get("high_risk_country"):
            adjusted_score = min(100, adjusted_score + 15)
        
        return max(0.0, min(100.0, adjusted_score))
    
    def get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level."""
        if score >= 90:
            return "CRITICAL"
        elif score >= 70:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        elif score >= 30:
            return "LOW"
        else:
            return "MINIMAL"
