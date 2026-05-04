# 📡 API Reference

## Endpoint: POST /api/v1/session

### Overview
Send real-time cognitive state signals from edge device to Study Partner backend AI orchestrator.

### URL
```
POST {backend_url}/api/v1/session
```

### Example
```
POST http://192.168.1.100:8000/api/v1/session
```

---

## Request Format

### Headers
```
Content-Type: application/json
```

### Body

```json
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

### Field Descriptions

| Field | Type | Range | Required | Example | Notes |
|-------|------|-------|----------|---------|-------|
| `session_id` | string | - | Yes | "test-session-001" | Unique study session ID |
| `user_id` | string | - | Yes | "user-001" | Student/user identifier |
| `signals.focus_score` | float | 0.0-1.0 | Yes | 0.82 | 1.0 = highly focused, 0.0 = no focus |
| `signals.emotion` | string | see below | Yes | "neutral" | Emotional state classification |
| `signals.fatigue` | float | 0.0-1.0 | Yes | 0.25 | 0.0 = alert, 1.0 = severely fatigued |

### Emotion Values
Valid emotion strings:
- `"focused"` - Student is engaged and focused
- `"neutral"` - Baseline emotional state
- `"distracted"` - Student appears distracted
- `"tired"` - Student appears tired/drowsy

---

## Sending Signals

### Python Example (Using requests)
```python
import requests
import json

url = "http://192.168.1.100:8000/api/v1/session"

payload = {
    "session_id": "test-session-001",
    "user_id": "user-001",
    "signals": {
        "focus_score": 0.82,
        "emotion": "neutral",
        "fatigue": 0.25
    }
}

response = requests.post(
    url,
    json=payload,
    timeout=10,
    headers={'Content-Type': 'application/json'}
)

if response.status_code in [200, 201, 202]:
    print("Signal sent successfully")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### cURL Example
```bash
curl -X POST http://192.168.1.100:8000/api/v1/session \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-001",
    "user_id": "user-001",
    "signals": {
      "focus_score": 0.82,
      "emotion": "neutral",
      "fatigue": 0.25
    }
  }'
```

---

## Response Format

### Success Response (200/201/202)
```json
{
  "success": true,
  "message": "Signal received and processed",
  "session_id": "test-session-001",
  "timestamp": "2024-05-03T10:30:55Z"
}
```

### Error Response (4xx/5xx)
```json
{
  "success": false,
  "error": "Invalid request format",
  "details": "Missing required field: signals",
  "code": "INVALID_PAYLOAD"
}
```

---

## Signal Interpretation

### Focus Score Meaning

| Score | State | Interpretation |
|-------|-------|-----------------|
| 0.9-1.0 | High Focus | Face clearly visible, engaged |
| 0.7-0.9 | Good Focus | Face mostly visible, attentive |
| 0.5-0.7 | Moderate | Some distraction visible |
| 0.2-0.5 | Low Focus | Face obscured or turned away |
| 0.0-0.2 | No Focus | No face detected or highly distracted |

**Current Implementation**: Binary (1.0 if face detected, 0.0 if not)

### Emotion Mapping

| Emotion | Trigger | Signal Meaning |
|---------|---------|-----------------|
| "focused" | High focus score + face | Student is engaged |
| "neutral" | Mid focus score | Balanced attention |
| "distracted" | Low focus + face present | Mind wandering |
| "tired" | Face absent/eyes closed | Fatigue or disengagement |

### Fatigue Score Meaning

| Score | State | Interpretation |
|-------|-------|-----------------|
| 0.0-0.2 | Alert | No fatigue signs |
| 0.2-0.4 | Normal | Baseline fatigue level |
| 0.4-0.7 | Rising | Fatigue increasing |
| 0.7-0.9 | High | Significant fatigue |
| 0.9-1.0 | Critical | Severe fatigue/disengagement |

**Current Implementation**: Based on no-face frame ratio in 10-frame window

---

## Signal Frequency

### Recommended
- **Interval**: 5 seconds between signals
- **Rate**: 0.2 signals/second = 12 per minute
- **Network Usage**: ~2KB per signal = ~400 bytes/sec

### Configurable
```json
{
  "send_interval": 5
}
```

Adjust based on:
- Network bandwidth constraints
- Processing power
- Real-time requirements

---

## Backend Processing Pipeline

### Flow After Signal Reception

```
1. Signal Arrival
   ↓
2. Schema Validation
   ├─ Check required fields
   ├─ Validate types
   └─ Verify value ranges
   ↓
3. Session Lookup
   ├─ Find session_id
   └─ Find user_id
   ↓
4. Signal Routing
   ├─ Focus Agent
   ├─ Emotion Agent
   └─ Fatigue Agent
   ↓
5. Decision Making
   ├─ Compare vs. baseline
   ├─ Detect anomalies
   └─ Trigger interventions
   ↓
6. Action Generation
   ├─ Adjust study plan
   ├─ Send notifications
   └─ Log metrics
```

---

## Error Handling

### Network Errors

#### Timeout (>10s)
**Action**: Retry up to 3 times with 2s backoff
```
Attempt 1: Immediate
Attempt 2: After 2s
Attempt 3: After 4s
```

#### Connection Refused
**Cause**: Backend not running  
**Action**: Continue buffering, retry at next interval

#### DNS Failure
**Cause**: Invalid backend URL  
**Action**: Log error, continue with next signal

### Validation Errors

#### Missing Fields
```json
{
  "error": "Missing required field: signals.focus_score"
}
```

#### Invalid Emotion Value
```json
{
  "error": "Invalid emotion: 'confused'. Valid: focused, neutral, distracted, tired"
}
```

#### Out of Range
```json
{
  "error": "focus_score must be between 0.0 and 1.0, got 1.5"
}
```

---

## Batch Operations (Future)

### Proposed: Batch Signals
```json
POST /api/v1/session/batch
{
  "signals": [
    { "session_id": "...", "user_id": "...", "signals": {...} },
    { "session_id": "...", "user_id": "...", "signals": {...} }
  ]
}
```

Benefits:
- Reduce request overhead
- Improve throughput
- Better for offline scenarios

---

## Rate Limits

### Current (No explicit limits)
- Default: Continuous sending allowed
- Implementation: Per client responsibility

### Recommended Limits (Future)
- Max 1000 signals/session/day
- Max 100 requests/minute per client
- Quota reset: UTC midnight

---

## Authentication (Future)

### Proposed: API Key Authentication
```
Authorization: Bearer {api_key}
```

### Proposed: Session Token
```
POST /api/v1/auth/session
{
  "device_id": "rpi5-001",
  "api_key": "..."
}

Response:
{
  "token": "jwt...",
  "expires_in": 3600
}
```

---

## Data Retention

### Default Retention
- **Signals**: 90 days
- **Sessions**: Until explicit deletion
- **Aggregates**: 1 year

### Archival
- Move to cold storage after 90 days
- Compress signals
- Generate summaries

---

## Monitoring & Debugging

### Check Connection
```bash
curl -i http://192.168.1.100:8000/health
```

### Check Signal Format
```bash
# Enable verbose logging in main.py
logger.setLevel(logging.DEBUG)
```

### Mock Backend (Testing)
```python
# Simple Flask server for testing
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/v1/session', methods=['POST'])
def session():
    data = request.json
    print(f"Received: {data}")
    return {'success': True}, 200

app.run(host='0.0.0.0', port=8000)
```

---

## Integration Checklist

- [ ] Backend endpoint confirmed at `/api/v1/session`
- [ ] Backend accepts POST requests
- [ ] Backend validates JSON format
- [ ] Verify 200/201/202 success response
- [ ] Test with sample signal
- [ ] Verify signal appears in backend logs
- [ ] Test with multiple sessions
- [ ] Test error handling (invalid emotion, etc.)
- [ ] Test retry logic (kill backend, verify reconnect)
- [ ] Monitor first 60-second run

---

## Examples

### Example 1: Alert Student
```json
{
  "session_id": "session-2024-05-03-001",
  "user_id": "student-042",
  "signals": {
    "focus_score": 0.15,
    "emotion": "distracted",
    "fatigue": 0.45
  }
}
```
**Backend Action**: Send gentle notification to refocus

### Example 2: Fatigue Warning
```json
{
  "session_id": "session-2024-05-03-001",
  "user_id": "student-042",
  "signals": {
    "focus_score": 0.05,
    "emotion": "tired",
    "fatigue": 0.87
  }
}
```
**Backend Action**: Suggest break, lower study intensity

### Example 3: Excellent Engagement
```json
{
  "session_id": "session-2024-05-03-001",
  "user_id": "student-042",
  "signals": {
    "focus_score": 0.95,
    "emotion": "focused",
    "fatigue": 0.12
  }
}
```
**Backend Action**: Maintain current pace, increase difficulty

---

## Support & Troubleshooting

### Signal not reaching backend?
1. Verify backend URL in config
2. Test with curl: `curl -X POST http://backend:8000/api/v1/session ...`
3. Check backend logs
4. Verify network connectivity

### Invalid response?
1. Check response status code
2. Read error message in response
3. Validate signal format against examples
4. Check emotion is one of: focused, neutral, distracted, tired

### Intermittent failures?
1. Increase api_retry_attempts in config
2. Check network stability
3. Monitor backend load
4. Add more spacing between sends

---

**For full documentation, see README.md and ARCHITECTURE.md**
