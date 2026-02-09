"""
Detection Engine
================
Main orchestrator for the fraud detection pipeline.
Coordinates feature engineering, multiple detectors, and risk scoring.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.detection.detectors.base import BaseDetector, DetectionResult
from app.detection.detectors.statistical import StatisticalDetector
from app.detection.detectors.behavioral import BehavioralDetector
from app.detection.detectors.ml_detector import MLDetector
from app.detection.scoring.risk_scorer import RiskScorer
from app.detection.features.feature_engineer import FeatureEngineer
from app.models.enums import AlertSeverity
from app.core.logging import get_logger
from app.core.observability import metrics

logger = get_logger(__name__)


@dataclass
class TransactionInput:
    """Input transaction for detection."""
    transaction_id: str
    amount: float
    timestamp: datetime
    source_account: str
    destination_account: str
    channel: Optional[str] = None
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    geo_location: Optional[str] = None
    
    # Historical context (if available)
    historical_transactions: Optional[List[Dict]] = None


@dataclass
class DetectionOutput:
    """Output from the detection engine."""
    transaction_id: str
    risk_score: float
    severity: AlertSeverity
    should_alert: bool
    detector_scores: Dict[str, float]
    feature_values: Dict[str, Any]
    explanations: List[str]
    processing_time_ms: float


class DetectionEngine:
    """
    Main fraud detection engine.
    
    Orchestrates:
    1. Feature engineering
    2. Multiple detector execution
    3. Score aggregation
    4. Alert decision
    """
    
    def __init__(
        self,
        risk_threshold_alert: float = 50.0,
        detector_weights: Optional[Dict[str, float]] = None,
    ):
        self.risk_threshold_alert = risk_threshold_alert
        
        # Initialize components
        self.feature_engineer = FeatureEngineer()
        self.risk_scorer = RiskScorer()
        
        # Initialize detectors
        self.detectors: List[BaseDetector] = [
            StatisticalDetector(),
            BehavioralDetector(),
            MLDetector(),
        ]
        
        # Detector weights for score aggregation
        self.detector_weights = detector_weights or {
            "statistical": 0.25,
            "behavioral": 0.35,
            "ml": 0.40,
        }
        
        logger.info(
            "Detection engine initialized",
            detectors=[d.name for d in self.detectors],
            threshold=risk_threshold_alert,
        )
    
    async def process_transaction(
        self,
        transaction: TransactionInput,
    ) -> DetectionOutput:
        """
        Process a single transaction through the detection pipeline.
        
        Flow:
        1. Feature Engineering → Extract meaningful features
        2. Detector Execution → Run all detectors in parallel
        3. Score Aggregation → Combine detector scores
        4. Alert Decision → Determine if alert should be raised
        """
        import time
        start_time = time.perf_counter()
        
        logger.info("Processing transaction", transaction_id=transaction.transaction_id)
        
        try:
            # Step 1: Feature Engineering
            features = await self.feature_engineer.extract_features(transaction)
            
            # Step 2: Run Detectors
            detector_results: Dict[str, DetectionResult] = {}
            
            for detector in self.detectors:
                try:
                    result = await detector.detect(features)
                    detector_results[detector.name] = result
                except Exception as e:
                    logger.error(
                        "Detector failed",
                        detector=detector.name,
                        error=str(e),
                    )
                    # Use neutral score on failure
                    detector_results[detector.name] = DetectionResult(
                        score=50.0,
                        confidence=0.0,
                        explanations=["Detector unavailable"],
                    )
            
            # Step 3: Aggregate Scores
            composite_score = self._aggregate_scores(detector_results)
            
            # Step 4: Determine Severity and Alert Decision
            severity = self._get_severity(composite_score)
            should_alert = composite_score >= self.risk_threshold_alert
            
            # Collect explanations
            explanations = []
            for result in detector_results.values():
                explanations.extend(result.explanations)
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Track metrics
            metrics.track_detection_score(composite_score)
            if should_alert:
                metrics.track_alert_created(severity.value)
            
            output = DetectionOutput(
                transaction_id=transaction.transaction_id,
                risk_score=round(composite_score, 2),
                severity=severity,
                should_alert=should_alert,
                detector_scores={name: r.score for name, r in detector_results.items()},
                feature_values=features,
                explanations=explanations,
                processing_time_ms=round(processing_time, 2),
            )
            
            logger.info(
                "Transaction processed",
                transaction_id=transaction.transaction_id,
                risk_score=output.risk_score,
                should_alert=should_alert,
                processing_time_ms=output.processing_time_ms,
            )
            
            return output
            
        except Exception as e:
            logger.error(
                "Detection pipeline failed",
                transaction_id=transaction.transaction_id,
                error=str(e),
            )
            raise
    
    def _aggregate_scores(
        self,
        detector_results: Dict[str, DetectionResult],
    ) -> float:
        """
        Aggregate detector scores using weighted average.
        
        Weights can be adjusted based on detector performance.
        """
        total_weight = 0.0
        weighted_sum = 0.0
        
        for detector_name, result in detector_results.items():
            weight = self.detector_weights.get(detector_name, 0.0)
            
            # Adjust weight by confidence
            effective_weight = weight * result.confidence
            
            weighted_sum += result.score * effective_weight
            total_weight += effective_weight
        
        if total_weight == 0:
            return 50.0  # Neutral score if no detectors contributed
        
        return weighted_sum / total_weight
    
    def _get_severity(self, score: float) -> AlertSeverity:
        """Determine alert severity from risk score."""
        if score >= 90:
            return AlertSeverity.CRITICAL
        elif score >= 70:
            return AlertSeverity.HIGH
        elif score >= 50:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    async def batch_process(
        self,
        transactions: List[TransactionInput],
    ) -> List[DetectionOutput]:
        """Process multiple transactions."""
        results = []
        for transaction in transactions:
            result = await self.process_transaction(transaction)
            results.append(result)
        return results
