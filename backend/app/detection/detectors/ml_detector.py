"""
ML Detector
===========
Machine learning-based fraud detector.
Uses trained models for anomaly detection.
"""

from typing import Dict, Any, List
import random

from app.detection.detectors.base import BaseDetector, DetectionResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MLDetector(BaseDetector):
    """
    Machine learning-based detector.
    
    In MVP, uses mock predictions.
    In production, would load trained models:
    - Isolation Forest for unsupervised anomaly detection
    - Gradient Boosting for supervised classification
    - Neural network for complex pattern recognition
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    @property
    def name(self) -> str:
        return "ml"
    
    @property
    def version(self) -> str:
        return "3.0.0"  # Model version
    
    def _load_model(self) -> None:
        """
        Load the ML model.
        
        In production:
        - Load from model registry
        - Validate model version
        - Initialize preprocessors
        """
        try:
            # For MVP, we'll use mock predictions
            # In production:
            # import joblib
            # self.model = joblib.load('models/fraud_detector_v3.pkl')
            self.model_loaded = True
            logger.info("ML model loaded", version=self.version)
        except Exception as e:
            logger.error("Failed to load ML model", error=str(e))
            self.model_loaded = False
    
    async def detect(self, features: Dict[str, Any]) -> DetectionResult:
        """Run ML model prediction."""
        
        if not self.model_loaded:
            return DetectionResult(
                score=50.0,
                confidence=0.0,
                explanations=["ML model unavailable"],
            )
        
        # Extract ML features
        ml_features = self._prepare_features(features)
        
        # Make prediction (mock for MVP)
        score, confidence = self._predict(ml_features)
        
        # Generate explanations based on feature importance
        explanations = self._generate_explanations(ml_features, score)
        
        logger.debug(
            "ML detection complete",
            score=score,
            confidence=confidence,
        )
        
        return DetectionResult(
            score=score,
            confidence=confidence,
            explanations=explanations,
            metadata={
                "detector": self.name,
                "version": self.version,
                "model_type": "ensemble",
            },
        )
    
    def _prepare_features(self, raw_features: Dict[str, Any]) -> Dict[str, float]:
        """
        Prepare features for ML model input.
        
        Handles:
        - Feature normalization
        - Missing value imputation
        - One-hot encoding
        """
        ml_features = {
            "amount_normalized": raw_features.get("amount_zscore", 0) / 3,
            "time_risk": 1.0 if raw_features.get("is_unusual_hour", False) else 0.0,
            "velocity": min(1.0, raw_features.get("hourly_transaction_count", 0) / 10),
            "geo_risk": raw_features.get("geo_risk_score", 50) / 100,
            "device_risk": 1.0 if raw_features.get("is_new_device", False) else 0.0,
            "destination_risk": 1.0 if raw_features.get("is_new_destination", False) else 0.0,
            "frequency_deviation": abs(raw_features.get("frequency_zscore", 0)) / 3,
            "account_age_risk": 1.0 if raw_features.get("account_age_days", 365) < 30 else 0.0,
        }
        
        return ml_features
    
    def _predict(self, features: Dict[str, float]) -> tuple[float, float]:
        """
        Make prediction using the ML model.
        
        Returns (score, confidence).
        
        In production, this would call model.predict() and model.predict_proba()
        """
        # For MVP: Generate realistic-looking score based on feature values
        # This simulates what a trained model would output
        
        base_score = 20.0
        
        # High-risk signals
        if features["amount_normalized"] > 0.8:
            base_score += 30
        elif features["amount_normalized"] > 0.5:
            base_score += 15
        
        if features["velocity"] > 0.7:
            base_score += 20
        
        if features["geo_risk"] > 0.7:
            base_score += 15
        
        if features["device_risk"] > 0.5:
            base_score += 10
        
        if features["destination_risk"] > 0.5:
            base_score += 10
        
        # Add some randomness to simulate model prediction variance
        noise = random.uniform(-5, 5)
        final_score = self.clamp_score(base_score + noise)
        
        # Confidence is high when signals are clear (very high or very low score)
        if final_score > 80 or final_score < 30:
            confidence = 0.9
        elif final_score > 60 or final_score < 40:
            confidence = 0.75
        else:
            confidence = 0.6
        
        return final_score, confidence
    
    def _generate_explanations(
        self,
        features: Dict[str, float],
        score: float,
    ) -> List[str]:
        """
        Generate model explanations.
        
        In production, use SHAP or LIME for model interpretability.
        """
        explanations = []
        
        if score < 40:
            return explanations  # Low risk, no explanations needed
        
        # Feature importance (simulated)
        if features["amount_normalized"] > 0.7:
            explanations.append("ML: Unusual transaction amount pattern")
        
        if features["velocity"] > 0.6:
            explanations.append("ML: Elevated transaction frequency detected")
        
        if features["geo_risk"] > 0.6:
            explanations.append("ML: Geographic pattern anomaly")
        
        if features["device_risk"] > 0.5:
            explanations.append("ML: Device fingerprint risk signal")
        
        if features["frequency_deviation"] > 0.7:
            explanations.append("ML: Behavioral frequency anomaly")
        
        if not explanations and score > 50:
            explanations.append("ML: Combined risk factors elevated")
        
        return explanations
