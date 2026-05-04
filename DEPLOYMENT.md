# Study Partner Edge AI - Deployment Guide

## 🚀 Raspberry Pi 5 Setup

### System Prerequisites
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libatlas-base-dev \
    libjasper-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libopenjp2-7

# Optional: Install git for version control
sudo apt-get install -y git
```

### Network Setup
```bash
# Configure static IP (optional but recommended)
sudo nano /etc/dhcpcd.conf

# Example for static IP:
# interface eth0
# static ip_address=192.168.1.20/24
# static routers=192.168.1.1
# static domain_name_servers=8.8.8.8
```

---

## 📦 Application Setup

### 1. Create Application Directory
```bash
sudo mkdir -p /opt/study-partner-edge
sudo chown pi:pi /opt/study-partner-edge
cd /opt/study-partner-edge
```

### 2. Clone/Copy Application
```bash
# Via git (if available)
git clone <repository> .

# Or copy files manually
cp -r study-partner-embedded/* .
```

### 3. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### 4. Configure Application
```bash
# Edit configuration for your environment
nano config/config.json

# Update:
# - backend_url: Your backend server IP/domain
# - stream_url: Your camera stream IP/port
# - session_id: Your session identifier
# - user_id: Your user identifier
```

### 5. Test Installation
```bash
python test_system.py
```

---

## 🔄 Running as Service

### Create Systemd Service
```bash
sudo nano /etc/systemd/system/study-partner-edge.service
```

### Service File Content
```ini
[Unit]
Description=Study Partner Edge AI System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/study-partner-edge
ExecStart=/opt/study-partner-edge/venv/bin/python /opt/study-partner-edge/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits (optional)
CPUQuota=75%
MemoryLimit=256M

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable study-partner-edge

# Start service
sudo systemctl start study-partner-edge

# Check status
sudo systemctl status study-partner-edge

# View logs
sudo journalctl -u study-partner-edge -f

# Stop service
sudo systemctl stop study-partner-edge
```

---

## 🐳 Docker Deployment (Alternative)

### Dockerfile
```dockerfile
FROM arm64v8/python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff5 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "main.py"]
```

### Build and Run
```bash
# Build image
docker build -t study-partner-edge:latest .

# Run container
docker run -d \
  --name study-partner-edge \
  --restart unless-stopped \
  --network host \
  study-partner-edge:latest
```

---

## 📊 Monitoring

### Check Service Status
```bash
sudo systemctl status study-partner-edge
```

### View Live Logs
```bash
sudo journalctl -u study-partner-edge -f
```

### Check Resource Usage
```bash
# CPU and Memory
top -u pi

# Network
sudo iftop

# Disk
df -h /opt/study-partner-edge
```

### Performance Metrics
```bash
# CPU temperature (useful for Pi)
vcgencmd measure_temp

# System uptime
uptime
```

---

## 🔧 Troubleshooting

### Service Won't Start
```bash
# Check error logs
sudo journalctl -u study-partner-edge -n 50

# Test configuration
cd /opt/study-partner-edge
source venv/bin/activate
python test_system.py
```

### High CPU Usage
1. Check if face detection is throttling:
   - Increase `send_interval` in config
   - Reduce `frame_resize` dimensions

2. Monitor process:
   ```bash
   ps aux | grep main.py
   ```

### Network Issues
```bash
# Test backend connectivity
curl -v http://192.168.1.100:8000/health

# Test camera stream
curl -v http://192.168.1.9:8090/video

# Check network interface
ifconfig eth0
```

### Memory Issues
```bash
# Monitor memory usage
free -h

# Check if process is leaking memory
watch -n 1 'ps aux | grep main.py'
```

---

## 🔐 Security Hardening

### 1. Update System Regularly
```bash
sudo apt-get update && sudo apt-get upgrade
```

### 2. Configure Firewall
```bash
sudo apt-get install -y ufw

# Allow SSH (if using)
sudo ufw allow 22/tcp

# Default deny
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

### 3. Restrict Application Access
```bash
# Run as non-root user (already pi)
# Service already configured to run as pi user
```

### 4. Use HTTPS for Backend
```json
{
  "backend_url": "https://your-backend-domain.com",
  ...
}
```

### 5. Secure Configuration
```bash
# Restrict config file permissions
sudo chmod 600 /opt/study-partner-edge/config/config.json
sudo chown pi:pi /opt/study-partner-edge/config/config.json
```

---

## 📈 Performance Optimization

### 1. GPU Acceleration (if available)
Currently using CPU-based inference. For Pi 5:
- Consider ONNX Runtime for ARM optimization
- Explore hardware accelerators if available

### 2. Threading Tuning
Modify `orchestrator.py` if needed:
```python
# Increase processing loop frequency
time.sleep(0.01)  # Instead of 0.05
```

### 3. Frame Processing
Optimize in `config/config.json`:
```json
{
  "frame_resize": [160, 160],  # Smaller for faster processing
  "send_interval": 10          # Less frequent updates
}
```

---

## 🚀 Scaling

### Multiple Cameras
1. Run multiple instances with different configs
2. Use docker-compose for orchestration
3. Modify main.py to accept camera ID parameter

### Data Aggregation
1. Collect signals from multiple Pi devices
2. Send to central collector
3. Aggregate for insights

---

## 📝 Logging & Debugging

### Enable Debug Logging
Edit `utils/logger.py`:
```python
self.logger.setLevel(logging.DEBUG)  # More verbose
```

### Log Rotation
Add to service file or use logrotate:
```bash
sudo nano /etc/logrotate.d/study-partner-edge
```

```
/var/log/study-partner-edge.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 🔄 Updates & Maintenance

### Backup Configuration
```bash
cp config/config.json config/config.json.backup
```

### Update Application
```bash
cd /opt/study-partner-edge
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart study-partner-edge
```

### Health Checks
```bash
# Script to verify system health
#!/bin/bash
curl -f http://localhost:8000/health || \
  systemctl restart study-partner-edge
```

---

## 📞 Support

For issues, check:
1. System logs: `sudo journalctl -u study-partner-edge`
2. Test script: `python test_system.py`
3. Configuration: Verify `config/config.json`
4. Network: Test connectivity to stream and backend

---

**Happy deploying! 🚀**
