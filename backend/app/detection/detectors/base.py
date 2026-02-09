"""
Base Detector
=============
Abstract base class for all fraud detectors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class DetectionResult:
    """Result from a detector."""
    score: float  # 0-100 risk score
    confidence: float = 1.0  # 0-1 confidence in the score
    explanations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDetector(ABC):
    """
    Abstract base class for fraud detectors.
    
    Each detector operates independently and produces a risk score.
    Detectors should be stateless for horizontal scaling.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique detector name."""
        pass
    
    @property
    def version(self) -> str:
        """Detector version."""
        return "1.0.0"
    
    @abstractmethod
    async def detect(self, features: Dict[str, Any]) -> DetectionResult:
        """
        Analyze features and produce a risk score.
        
        Args:
            features: Dictionary of computed features
        
        Returns:
            DetectionResult with score, confidence, and explanations
        """
        pass
    
    def normalize_score(self, raw_score: float, min_val: float = 0, max_val: float = 100) -> float:
        """Normalize a raw score to 0-100 range."""
        if max_val == min_val:
            return 50.0
        
        normalized = ((raw_score - min_val) / (max_val - min_val)) * 100
        return max(0.0, min(100.0, normalized))
    
    def clamp_score(self, score: float) -> float:
        """Clamp score to valid range."""
        return max(0.0, min(100.0, score))
