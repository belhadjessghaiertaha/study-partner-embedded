"""
Fatigue Estimation Module
Estimates fatigue based on face detection and temporal patterns
"""
import numpy as np
from utils.logger import logger


class FatigueEstimator:
    """Estimates fatigue level from continuous observations"""
    
    def __init__(self, window_size: int = 10):
        """
        Initialize fatigue estimator
        
        Args:
            window_size: Number of frames to consider for fatigue calculation
        """
        self.window_size = window_size
        self.face_detection_history = []
        self.fatigue_level = 0.0
        self.consecutive_no_face = 0
        logger.info(f"Fatigue estimator initialized (window={window_size})")
    
    def update(self, face_detected: bool) -> dict:
        """
        Update fatigue estimation
        
        Args:
            face_detected: Whether face was detected in current frame
        
        Returns:
            dict: {
                'fatigue': float (0-1),
                'confidence': float,
                'consecutive_no_face': int
            }
        """
        try:
            # Add to history
            self.face_detection_history.append(face_detected)
            
            # Keep window size
            if len(self.face_detection_history) > self.window_size:
                self.face_detection_history.pop(0)
            
            # Update consecutive no-face counter
            if not face_detected:
                self.consecutive_no_face += 1
            else:
                self.consecutive_no_face = 0
            
            # Calculate fatigue based on face detection patterns
            if len(self.face_detection_history) > 0:
                # Proportion of frames without face
                no_face_count = len(self.face_detection_history) - sum(self.face_detection_history)
                no_face_ratio = no_face_count / len(self.face_detection_history)
                
                # Consecutive no-face penalty
                consecutive_penalty = min(self.consecutive_no_face / 30.0, 0.5)  # Max 0.5 from consecutive
                
                # Combine metrics
                self.fatigue_level = (no_face_ratio * 0.6) + (consecutive_penalty * 0.4)
                
                # Clamp to [0, 1]
                self.fatigue_level = max(0.0, min(1.0, self.fatigue_level))
            
            # Confidence increases with more observations
            confidence = min(len(self.face_detection_history) / self.window_size, 1.0)
            
            return {
                'fatigue': round(self.fatigue_level, 4),
                'confidence': round(confidence, 4),
                'consecutive_no_face': self.consecutive_no_face
            }
        
        except Exception as e:
            logger.error(f"Fatigue estimation error: {e}")
            return {
                'fatigue': 0.5,
                'confidence': 0.0,
                'consecutive_no_face': 0
            }
    
    def get_fatigue_level(self) -> float:
        """Get current fatigue level (0-1)"""
        return self.fatigue_level
    
    def reset(self):
        """Reset fatigue estimator"""
        self.face_detection_history.clear()
        self.fatigue_level = 0.0
        self.consecutive_no_face = 0
