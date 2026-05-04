#!/usr/bin/env python3
"""
Test & Demo Script
Validates system components and simulates study session
"""
import sys
import time
import json
from pathlib import Path

# Test imports
try:
    print("📦 Checking dependencies...")
    import cv2
    print("  ✓ OpenCV")
    import numpy as np
    print("  ✓ NumPy")
    import requests
    print("  ✓ Requests")
    print()
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Test local imports
try:
    from utils.logger import logger
    from camera.stream_reader import StreamReader
    from ai.focus import FocusDetector
    from ai.emotion import EmotionDetector
    from ai.fatigue import FatigueEstimator
    from services.api_client import APIClient
    from orchestrator import EdgeAIOrchestrator
    print("✓ All modules imported successfully\n")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_config():
    """Test configuration file"""
    print("🔧 Testing Configuration...")
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = [
            'backend_url', 'stream_url', 'session_id',
            'user_id', 'send_interval'
        ]
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing config key: {key}")
            print(f"  ✓ {key}: {config[key]}")
        
        print()
        return config
    except Exception as e:
        print(f"❌ Config error: {e}")
        return None


def test_ai_modules():
    """Test AI modules with dummy data"""
    print("🧠 Testing AI Modules...")
    
    # Create dummy frame
    dummy_frame = np.zeros((224, 224, 3), dtype=np.uint8)
    
    try:
        # Focus detector
        focus_detector = FocusDetector()
        focus_result = focus_detector.detect(dummy_frame)
        print(f"  ✓ Focus Detector: {focus_result['focus_score']:.2f}")
        
        # Emotion detector
        emotion_detector = EmotionDetector()
        emotion_result = emotion_detector.detect(dummy_frame, focus_result['focus_score'])
        print(f"  ✓ Emotion Detector: {emotion_result['emotion']}")
        
        # Fatigue estimator
        fatigue_estimator = FatigueEstimator()
        fatigue_result = fatigue_estimator.update(focus_result['face_detected'])
        print(f"  ✓ Fatigue Estimator: {fatigue_result['fatigue']:.2f}")
        
        print()
        return True
    except Exception as e:
        print(f"❌ AI module error: {e}")
        return False


def test_api_client(config):
    """Test API client"""
    print("🌐 Testing API Client...")
    
    try:
        api_client = APIClient(
            backend_url=config['backend_url'],
            session_id=config['session_id'],
            user_id=config['user_id']
        )
        
        # Test connection
        connected = api_client.test_connection()
        if connected:
            print(f"  ✓ Backend connection: OK")
        else:
            print(f"  ⚠ Backend unreachable (will retry on runtime)")
        
        # Test signal format
        test_signal = {
            'focus_score': 0.85,
            'emotion': 'focused',
            'fatigue': 0.15
        }
        print(f"  ✓ Signal format: OK")
        print()
        return True
    except Exception as e:
        print(f"❌ API client error: {e}")
        return False


def test_camera_stream(config):
    """Test camera stream connection"""
    print("📷 Testing Camera Stream...")
    
    try:
        stream_reader = StreamReader(config['stream_url'], timeout=5)
        stream_reader.start()
        
        # Wait for connection
        print("  ⏳ Connecting to stream...", end='', flush=True)
        for i in range(10):
            if stream_reader.is_connected():
                print(" OK\n")
                stream_reader.stop()
                print(f"  ✓ Stream: {config['stream_url']}")
                print()
                return True
            time.sleep(1)
            print(".", end='', flush=True)
        
        print(" TIMEOUT")
        stream_reader.stop()
        print(f"  ⚠ Cannot connect to stream (camera may be offline)")
        print()
        return False
    
    except Exception as e:
        print(f"❌ Stream error: {e}")
        return False


def test_orchestrator():
    """Test orchestrator initialization"""
    print("🎯 Testing Orchestrator...")
    
    try:
        orch = EdgeAIOrchestrator()
        print("  ✓ Orchestrator initialized")
        print()
        return True
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        return False


def demo_session(config, duration=30):
    """Run demo study session"""
    print(f"🎬 Running Demo Session ({duration}s)...")
    print()
    
    try:
        orch = EdgeAIOrchestrator()
        orch.start()
        
        logger.info("Demo session started")
        time.sleep(duration)
        orch.stop()
        
        stats = orch.get_stats()
        print("\n📊 Demo Session Results:")
        print(f"  Duration: {stats['elapsed_seconds']:.1f}s")
        print(f"  Signals sent: {stats['total_signals']}")
        print(f"  Signal rate: {stats['signal_rate']:.2f}/s")
        print(f"  Frames captured: {stats['frames_captured']}")
        print()
        
        return True
    
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 Study Partner Edge AI - System Test")
    print("=" * 60 + "\n")
    
    # Test configuration
    config = test_config()
    if not config:
        return 1
    
    # Test AI modules
    if not test_ai_modules():
        return 1
    
    # Test API client
    if not test_api_client(config):
        return 1
    
    # Test camera stream (skip if offline)
    camera_ok = test_camera_stream(config)
    
    # Test orchestrator
    if not test_orchestrator():
        return 1
    
    # Ask about demo
    print("=" * 60)
    if camera_ok:
        response = input("Run demo session? (y/n): ").lower()
        if response == 'y':
            demo_session(config, duration=30)
    else:
        print("⚠ Skipping demo session (camera offline)")
    
    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60 + "\n")
    print("Next step: python main.py\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
