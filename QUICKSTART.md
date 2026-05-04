# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)
```bash
cd study-partner-embedded
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Step 2: Configure (1 min)
Edit `config/config.json`:
- Set `backend_url` to your Study Partner API server
- Set `stream_url` to your camera stream
- Update `session_id` and `user_id` as needed

### Step 3: Test (1 min)
```bash
python test_system.py
```

### Step 4: Run (1 min)
```bash
python main.py --test      # Quick 60-second test
# or
python main.py             # Run indefinitely
```

---

## What's Happening?

```
📷 Camera Stream
    ↓
🔄 MJPEG Parser (continuous in background thread)
    ↓
🧠 AI Inference (every frame)
    ├─ 👁️ Face detection → Focus score
    ├─ 😊 Emotion detection
    └─ 😴 Fatigue estimation
    ↓
📤 API Sending (every 5 seconds)
    ↓
🎯 Study Partner Backend
```

---

## Expected Output

```
[2024-05-03 10:30:48] [INFO] Study Partner Edge AI Orchestrator Initialized
[2024-05-03 10:30:48] [INFO] Waiting for stream connection...
[2024-05-03 10:30:50] [INFO] Stream connected successfully!
[2024-05-03 10:30:50] [INFO] Backend connection successful!
[2024-05-03 10:30:50] [INFO] Orchestrator started - processing signals...
[2024-05-03 10:30:55] [INFO] [   1]    5.1s | Focus: 0.82 | Emotion: neutral | Fatigue: 0.25
[2024-05-03 10:31:00] [INFO] [   2]   10.1s | Focus: 0.78 | Emotion: focused | Fatigue: 0.22
```

---

## Signals Being Sent

Every 5 seconds, your Raspberry Pi sends:
```json
POST /api/v1/session
{
  "session_id": "test-session-001",
  "user_id": "user-001",
  "signals": {
    "focus_score": 0.82,
    "emotion": "neutral",
    "fatigue": 0.25
  }
}
```

---

## File Structure

```
study-partner-embedded/
├── main.py                 # Start here
├── README.md              # Full documentation
├── DEPLOYMENT.md          # Production deployment
├── requirements.txt       # Python packages
├── test_system.py        # Validation script
│
├── camera/               # MJPEG stream parsing
├── ai/                   # Focus, emotion, fatigue detection
├── services/             # Backend API communication
├── config/               # Configuration
└── utils/                # Logging and utilities
```

---

## Configuration Reference

| Setting | Default | Purpose |
|---------|---------|---------|
| `backend_url` | 192.168.1.100:8000 | Study Partner API server |
| `stream_url` | 192.168.1.9:8090/video | MJPEG camera stream |
| `send_interval` | 5 | Signal sending frequency (seconds) |
| `frame_resize` | [224, 224] | Frame size for inference |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to stream | Verify stream URL: `curl http://192.168.1.9:8090/video` |
| Can't connect to backend | Verify backend URL: `curl http://192.168.1.100:8000` |
| High CPU usage | Reduce `send_interval` or `frame_resize` in config |
| Import errors | Run: `pip install -r requirements.txt` |

---

## Next Steps

1. ✅ Setup complete - your Pi is now sensing study state!
2. 📊 Check backend logs to verify signals are received
3. 🎯 Customize AI thresholds in config
4. 🚀 Deploy as system service (see DEPLOYMENT.md)
5. 📈 Integrate insights into Study Partner dashboard

---

## System Requirements

- Python 3.8+
- 150-200 MB RAM
- 10-20% CPU (Raspberry Pi 5)
- Network access to camera and backend

---

**Questions? Check README.md for complete documentation.**
