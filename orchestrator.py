"""
Main Orchestrator
Coordinates camera stream, AI inference, and API communication
"""
import json
import os
import time
import threading
from datetime import datetime
from pathlib import Path

from camera import StreamReader
from ai import FocusDetector, EmotionDetector, FatigueEstimator
from services import APIClient
from utils.logger import logger


class EdgeAIOrchestrator:
    """Main system orchestrator"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize orchestrator
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.stream_reader = StreamReader(
            stream_url=self.config['stream_url'],
            timeout=self.config.get('camera_read_timeout', 10)
        )
        
        self.focus_detector = FocusDetector()
        self.emotion_detector = EmotionDetector()
        self.fatigue_estimator = FatigueEstimator()
        
        self.api_client = APIClient(
            backend_url=self.config['backend_url'],
            session_id=self.config['session_id'],
            user_id=self.config['user_id'],
            device_name=self.config.get('device_name', 'Edge Device'),
            retry_attempts=self.config.get('api_retry_attempts', 3),
            retry_delay=self.config.get('api_retry_delay', 2)
        )
        
        # State
        self.is_running = False
        self.signal_count = 0
        self.start_time = None
        self.lock = threading.Lock()
        self.latest_signal = None
        self.latest_focus = None
        self.latest_fatigue = None
        self.processing_thread = None
        self.api_thread = None
        
        logger.info("=" * 60)
        logger.info("Study Partner Edge AI Orchestrator Initialized")
        logger.info("=" * 60)
        logger.info(f"Stream URL: {self.config['stream_url']}")
        logger.info(f"Backend URL: {self.config['backend_url']}")
        logger.info(f"Session ID: {self.config['session_id']}")
        logger.info(f"Send interval: {self.config['send_interval']}s")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            env_overrides = {
                'BACKEND_URL': 'backend_url',
                'STREAM_URL': 'stream_url',
                'SESSION_ID': 'session_id',
                'USER_ID': 'user_id',
                'DEVICE_NAME': 'device_name'
            }
            for env_name, config_key in env_overrides.items():
                if os.getenv(env_name):
                    config[config_key] = os.getenv(env_name)
            logger.info(f"Configuration loaded: {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {config_path}")
            raise
    
    def start(self):
        """Start the orchestrator"""
        if self.is_running:
            logger.warning("Orchestrator already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Start stream reader
        self.stream_reader.start()
        
        # Wait for stream connection
        logger.info("Waiting for stream connection...")
        connection_timeout = 30
        start_wait = time.time()
        while not self.stream_reader.is_connected():
            if time.time() - start_wait > connection_timeout:
                logger.warning(
                    f"No camera frames after {connection_timeout}s; continuing and retrying stream"
                )
                break
            time.sleep(1)
        
        if self.stream_reader.is_connected():
            logger.info("Stream connected successfully!")
        
        # Test backend connection
        logger.info("Testing backend connection...")
        if not self.api_client.test_connection():
            logger.warning("Backend connection test failed (will retry)")
        else:
            logger.info("Backend connection successful!")
        
        # Start processing and API sender threads.
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()

        self.api_thread = threading.Thread(
            target=self._api_sending_loop,
            daemon=True
        )
        self.api_thread.start()
        
        logger.info("Orchestrator started - processing signals...")
    
    def stop(self):
        """Stop the orchestrator"""
        logger.info("Stopping orchestrator...")
        self.is_running = False
        self.stream_reader.stop()
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        if self.api_thread:
            self.api_thread.join(timeout=5)
        logger.info(f"Total signals sent: {self.signal_count}")
    
    def _processing_loop(self):
        """Continuously update the latest cognitive signal from camera frames."""
        frame_resize = tuple(self.config['frame_resize'])
        
        while self.is_running:
            try:
                # Get latest frame
                frame = self.stream_reader.get_frame_resized(frame_resize)
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Run AI inference
                focus_result = self.focus_detector.detect(frame)
                emotion_result = self.emotion_detector.detect(
                    frame,
                    focus_score=focus_result['focus_score']
                )
                fatigue_result = self.fatigue_estimator.update(
                    face_detected=focus_result['face_detected']
                )

                signal_data = {
                    'focus_score': focus_result['focus_score'],
                    'emotion': emotion_result['emotion'],
                    'fatigue': fatigue_result['fatigue'],
                    'timestamp': datetime.now().isoformat()
                }

                with self.lock:
                    self.latest_signal = signal_data
                    self.latest_focus = focus_result
                    self.latest_fatigue = fatigue_result
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.05)
            
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                time.sleep(1)

    def _api_sending_loop(self):
        """Send the latest signal every configured interval without blocking inference."""
        send_interval = self.config['send_interval']

        while self.is_running:
            time.sleep(send_interval)

            with self.lock:
                signal_data = dict(self.latest_signal) if self.latest_signal else None
                focus_result = dict(self.latest_focus) if self.latest_focus else None
                fatigue_result = dict(self.latest_fatigue) if self.latest_fatigue else None

            if signal_data is None:
                logger.warning("No signal available yet; skipping send")
                continue

            success = self.api_client.send_signal(signal_data)
            if success:
                with self.lock:
                    self.signal_count += 1
                self._log_signal(signal_data, focus_result or {}, fatigue_result or {})
    
    def _log_signal(self, signal: dict, focus: dict, fatigue: dict):
        """Log signal details"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.info(
            f"[{self.signal_count:4d}] {elapsed:6.1f}s | "
            f"Focus: {signal['focus_score']:.2f} | "
            f"Emotion: {signal['emotion']:10s} | "
            f"Fatigue: {signal['fatigue']:.2f} | "
            f"Face: {focus.get('num_faces', 0)} | "
            f"NoFace: {fatigue.get('consecutive_no_face', 0)}"
        )
    
    def run(self, duration: int = None):
        """
        Run orchestrator
        
        Args:
            duration: Duration to run in seconds (None = infinite)
        """
        self.start()
        
        try:
            if duration:
                logger.info(f"Running for {duration} seconds...")
                time.sleep(duration)
                self.stop()
            else:
                logger.info("Running indefinitely (press Ctrl+C to stop)...")
                while self.is_running:
                    time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\nInterrupt received, shutting down...")
            self.stop()
        except Exception as e:
            logger.error(f"Runtime error: {e}")
            self.stop()
    
    def get_stats(self) -> dict:
        """Get current statistics"""
        if self.start_time is None:
            return {}
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        with self.lock:
            signal_rate = self.signal_count / elapsed if elapsed > 0 else 0
        
        return {
            'elapsed_seconds': elapsed,
            'total_signals': self.signal_count,
            'signal_rate': signal_rate,
            'frames_captured': self.stream_reader.frame_count,
            'is_running': self.is_running
        }
