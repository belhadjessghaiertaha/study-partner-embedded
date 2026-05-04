"""
API Client for Study Partner Backend
Posts edge AI session signals to the Study Partner AI orchestrator.
"""
import requests
import os
from datetime import datetime
from typing import Optional, Dict
from utils.logger import logger


class APIClient:
    """Client for the Study Partner backend session endpoint."""
    
    def __init__(
        self,
        backend_url: str,
        session_id: str,
        user_id: str,
        device_name: str = "Edge Device",
        retry_attempts: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize API client
        
        Args:
            backend_url: Base URL of Study Partner backend
            session_id: Study session ID
            user_id: User/Device ID
            device_name: Human-readable device name
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.backend_url = backend_url.rstrip('/')
        self.session_id = session_id
        self.user_id = user_id
        self.device_name = device_name
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.device_token = os.getenv('EDGE_DEVICE_TOKEN')
        
        # Existing AI orchestrator endpoint.
        self.session_endpoint = f"{self.backend_url}/api/v1/session"
        self.health_endpoint = f"{self.backend_url}/api/v1/health"
        
        self.is_connected = False
        self.last_response = None
        self.signal_count = 0
        
        logger.info(f"API Client initialized for: {self.backend_url}")
        logger.info(f"Session endpoint: {self.session_endpoint}")
        logger.info(f"Session ID: {self.session_id} | User ID: {self.user_id}")
    
    def test_connection(self) -> bool:
        """
        Test connection to backend.
        
        Returns:
            bool: True if connection successful
        """
        try:
            try:
                response = requests.get(self.health_endpoint, timeout=5)
            except requests.RequestException:
                response = requests.get(f"{self.backend_url}/health", timeout=5)

            self.is_connected = response.status_code in [200, 404]
            if self.is_connected:
                logger.info("Connected to backend")
            else:
                logger.warning(f"Backend returned: {response.status_code}")
            return self.is_connected
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            self.is_connected = False
            return False
    
    def send_signal(self, signal_data: Dict) -> bool:
        """
        Send AI signal to backend AI orchestrator via POST /api/v1/session.
        
        Args:
            signal_data: Signal data dict with focus_score, emotion, fatigue, timestamp
        
        Returns:
            bool: True if successful
        """
        payload = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "signals": {
                "focus_score": float(signal_data.get('focus_score', 0.0)),
                "emotion": str(signal_data.get('emotion', 'neutral')),
                "fatigue": float(signal_data.get('fatigue', 0.0)),
                "timestamp": signal_data.get('timestamp', datetime.now().isoformat())
            }
        }
        
        success = self._post_with_retry(self.session_endpoint, payload)
        if success:
            self.signal_count += 1
        return success
    
    def _post_with_retry(self, url: str, data: Dict) -> bool:
        """
        POST request with retry logic and backoff
        
        Args:
            url: Endpoint URL
            data: JSON payload
        
        Returns:
            bool: True if successful
        """
        import time
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = requests.post(
                    url,
                    json=data,
                    timeout=10,
                    headers={
                        'Content-Type': 'application/json',
                        'X-Device-ID': self.user_id,
                        'X-Session-ID': self.session_id,
                        **({'X-Device-Token': self.device_token} if self.device_token else {})
                    }
                )
                
                self.last_response = response
                
                if response.status_code in [200, 201, 202, 204]:
                    logger.debug(f"Signal sent successfully (status: {response.status_code})")
                    return True
                else:
                    logger.warning(
                        f"API response {response.status_code} | Attempt {attempt}/{self.retry_attempts}"
                    )
                    
                    if attempt < self.retry_attempts:
                        time.sleep(self.retry_delay * attempt)  # Exponential backoff
            
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt}/{self.retry_attempts}")
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay * attempt)
            
            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    f"Connection error on attempt {attempt}/{self.retry_attempts}: {str(e)[:80]}"
                )
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay * attempt)
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return False
        
        logger.error(f"Failed after {self.retry_attempts} attempts to {url}")
        return False
    
    def get_last_response(self) -> Optional[requests.Response]:
        """Get last API response"""
        return self.last_response
