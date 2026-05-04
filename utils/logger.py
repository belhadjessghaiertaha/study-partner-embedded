"""
Logging utility for Study Partner Edge AI
"""
import logging
import sys
from datetime import datetime


class Logger:
    """Custom logger for the Edge AI system"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = logging.getLogger('StudyPartnerEdgeAI')
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler with color
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler
        self.logger.addHandler(console_handler)
        self._initialized = True
    
    def get_logger(self):
        """Get the logger instance"""
        return self.logger


# Global logger instance
logger = Logger().get_logger()
