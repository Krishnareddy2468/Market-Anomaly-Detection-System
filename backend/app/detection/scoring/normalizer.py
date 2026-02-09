"""
Score Normalizer
================
Utilities for normalizing and calibrating risk scores.
"""

from typing import List, Optional
import math


class ScoreNormalizer:
    """
    Score normalization utilities.
    
    Provides methods to:
    - Normalize raw model outputs to 0-100 scale
    - Calibrate scores for consistent interpretation
    - Apply transformations (sigmoid, linear, etc.)
    """
    
    @staticmethod
    def linear_normalize(
        value: float,
        min_val: float,
        max_val: float,
        target_min: float = 0,
        target_max: float = 100,
    ) -> float:
        """
        Linear normalization to target range.
        
        Maps [min_val, max_val] → [target_min, target_max]
        """
        if max_val == min_val:
            return (target_min + target_max) / 2
        
        normalized = (value - min_val) / (max_val - min_val)
        scaled = normalized * (target_max - target_min) + target_min
        
        return max(target_min, min(target_max, scaled))
    
    @staticmethod
    def sigmoid_normalize(
        value: float,
        center: float = 0.5,
        steepness: float = 10,
    ) -> float:
        """
        Sigmoid normalization.
        
        Creates an S-curve transformation.
        Useful for making extreme values more distinguishable.
        """
        # Scale input to be centered at 0
        x = (value - center) * steepness
        
        # Apply sigmoid
        sigmoid = 1 / (1 + math.exp(-x))
        
        # Scale to 0-100
        return sigmoid * 100
    
    @staticmethod
    def zscore_normalize(
        value: float,
        mean: float,
        std: float,
        max_zscore: float = 3.0,
    ) -> float:
        """
        Z-score based normalization.
        
        Normalizes based on standard deviations from mean.
        """
        if std == 0:
            return 50.0
        
        zscore = (value - mean) / std
        
        # Clamp to max z-score range
        zscore = max(-max_zscore, min(max_zscore, zscore))
        
        # Convert to 0-100 scale
        normalized = ((zscore / max_zscore) + 1) / 2 * 100
        
        return normalized
    
    @staticmethod
    def percentile_normalize(
        value: float,
        reference_values: List[float],
    ) -> float:
        """
        Percentile-based normalization.
        
        Returns the percentile rank of the value.
        """
        if not reference_values:
            return 50.0
        
        count_below = sum(1 for v in reference_values if v < value)
        percentile = (count_below / len(reference_values)) * 100
        
        return percentile
    
    @staticmethod
    def clamp(value: float, min_val: float = 0, max_val: float = 100) -> float:
        """Clamp value to range."""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def decay_old_score(
        old_score: float,
        new_score: float,
        decay_factor: float = 0.8,
    ) -> float:
        """
        Apply exponential decay when combining old and new scores.
        
        Useful for rolling risk assessments.
        """
        return (old_score * decay_factor) + (new_score * (1 - decay_factor))
    
    @staticmethod
    def combine_scores(
        scores: List[float],
        method: str = "mean",
        weights: Optional[List[float]] = None,
    ) -> float:
        """
        Combine multiple scores using various methods.
        
        Methods:
        - mean: Simple average
        - weighted: Weighted average
        - max: Maximum value
        - rms: Root mean square
        """
        if not scores:
            return 0.0
        
        if method == "mean":
            return sum(scores) / len(scores)
        
        elif method == "weighted":
            if weights is None:
                weights = [1.0] * len(scores)
            total_weight = sum(weights)
            if total_weight == 0:
                return 0.0
            return sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        elif method == "max":
            return max(scores)
        
        elif method == "rms":
            mean_square = sum(s ** 2 for s in scores) / len(scores)
            return math.sqrt(mean_square)
        
        else:
            raise ValueError(f"Unknown combination method: {method}")
