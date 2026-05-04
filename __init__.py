"""
Study Partner Edge AI Package
Real-time cognitive state sensing for Raspberry Pi
"""

__version__ = "1.0.0"
__author__ = "Study Partner Team"
__description__ = "Edge AI client for Study Partner platform"

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import EdgeAIOrchestrator
from camera import StreamReader
from ai import FocusDetector, EmotionDetector, FatigueEstimator
from services import APIClient
from utils import logger

__all__ = [
    'EdgeAIOrchestrator',
    'StreamReader',
    'FocusDetector',
    'EmotionDetector',
    'FatigueEstimator',
    'APIClient',
    'logger'
]
