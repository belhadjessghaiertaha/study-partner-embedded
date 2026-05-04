"""
MJPEG Stream Reader
Handles real-time MJPEG stream parsing and frame extraction
"""
import cv2
import numpy as np
import requests
from threading import Thread, Lock, Event
from utils.logger import logger


class StreamReader:
    """
    Reads MJPEG stream from remote camera
    Extracts frames in real-time using threading
    """
    
    def __init__(self, stream_url: str, timeout: int = 10):
        """
        Initialize stream reader
        
        Args:
            stream_url: URL to MJPEG stream
            timeout: Read timeout in seconds
        """
        self.stream_url = stream_url
        self.timeout = timeout
        self.current_frame = None
        self.frame_lock = Lock()
        self.is_running = False
        self.stop_event = Event()
        self.reader_thread = None
        self.frame_count = 0
        
    def start(self):
        """Start reading stream in background thread"""
        if self.is_running:
            logger.warning("Stream reader already running")
            return
        
        self.is_running = True
        self.stop_event.clear()
        self.reader_thread = Thread(target=self._read_stream, daemon=True)
        self.reader_thread.start()
        logger.info(f"Stream reader started: {self.stream_url}")
    
    def stop(self):
        """Stop reading stream"""
        self.is_running = False
        self.stop_event.set()
        if self.reader_thread:
            self.reader_thread.join(timeout=5)
        logger.info("Stream reader stopped")
    
    def _read_stream(self):
        """Background thread: continuously read and parse MJPEG stream."""
        while not self.stop_event.is_set():
            try:
                response = requests.get(
                    self.stream_url,
                    stream=True,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                logger.info("Connected to MJPEG stream")
                bytes_buffer = b''
                
                for chunk in response.iter_content(chunk_size=1024):
                    if self.stop_event.is_set():
                        break
                    
                    if chunk:
                        bytes_buffer += chunk
                        
                        # Find JPEG frame boundaries
                        a = bytes_buffer.find(b'\xff\xd8')  # JPEG start
                        b = bytes_buffer.find(b'\xff\xd9')  # JPEG end
                        
                        if a != -1 and b != -1:
                            jpg_frame = bytes_buffer[a:b+2]
                            bytes_buffer = bytes_buffer[b+2:]
                            
                            frame = cv2.imdecode(
                                np.frombuffer(jpg_frame, dtype=np.uint8),
                                cv2.IMREAD_COLOR
                            )
                            
                            if frame is not None:
                                with self.frame_lock:
                                    self.current_frame = frame
                                    self.frame_count += 1
                                
                                if self.frame_count % 30 == 0:
                                    logger.debug(f"Frames captured: {self.frame_count}")
            
            except requests.exceptions.Timeout:
                logger.warning("Stream read timeout; retrying")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error: {e}; retrying")
            except Exception as e:
                logger.warning(f"Stream reader error: {e}; retrying")

            if not self.stop_event.is_set():
                self.stop_event.wait(5)

        self.is_running = False
        logger.info("Stream reader thread ended")
    
    def get_frame(self):
        """
        Get latest frame
        
        Returns:
            np.ndarray or None: Current frame
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def get_frame_resized(self, size: tuple):
        """
        Get latest frame resized
        
        Args:
            size: Target size (width, height)
        
        Returns:
            np.ndarray or None: Resized frame
        """
        frame = self.get_frame()
        if frame is not None:
            return cv2.resize(frame, size)
        return None
    
    def is_connected(self):
        """Check if stream is connected and receiving frames"""
        return self.is_running and self.frame_count > 0
