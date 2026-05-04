"""
Focus Detection Module
Uses Haar Cascade for face detection as a proxy for focus
"""
import cv2
import numpy as np
from utils.logger import logger


class FocusDetector:
    """Detects focus based on face detection"""
    
    def __init__(self):
        """Initialize face cascade classifier"""
        # Load pre-trained Haar cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            logger.warning("Failed to load face cascade classifier")
        else:
            logger.info("Face cascade classifier loaded")
        
        self.last_face_detected = False
    
    def detect(self, frame: np.ndarray) -> dict:
        """
        Detect focus from frame
        
        Args:
            frame: Input frame (BGR)
        
        Returns:
            dict: {
                'focus_score': float (0-1),
                'face_detected': bool,
                'num_faces': int,
                'face_area_ratio': float
            }
        """
        if frame is None or frame.size == 0:
            return {
                'focus_score': 0.0,
                'face_detected': False,
                'num_faces': 0,
                'face_area_ratio': 0.0
            }
        
        try:
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            num_faces = len(faces)
            face_detected = num_faces > 0
            
            # Calculate face area ratio
            frame_area = frame.shape[0] * frame.shape[1]
            total_face_area = 0
            
            for (x, y, w, h) in faces:
                total_face_area += w * h
            
            face_area_ratio = total_face_area / frame_area if frame_area > 0 else 0
            
            # Required MVP behavior: 1.0 if face detected, else 0.0.
            focus_score = 1.0 if face_detected else 0.0
            self.last_face_detected = face_detected
            
            return {
                'focus_score': focus_score,
                'face_detected': face_detected,
                'num_faces': num_faces,
                'face_area_ratio': round(face_area_ratio, 4)
            }
        
        except Exception as e:
            logger.error(f"Focus detection error: {e}")
            return {
                'focus_score': 0.0,
                'face_detected': False,
                'num_faces': 0,
                'face_area_ratio': 0.0
            }
