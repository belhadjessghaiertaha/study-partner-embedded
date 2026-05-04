# Multi-stage build for Study Partner Edge AI
# Target: Raspberry Pi 5 and general Linux systems

# Stage 1: Base image with dependencies
FROM python:3.11-slim-bullseye

LABEL maintainer="Study Partner" \
      description="Edge AI client for Study Partner - Real-time cognitive state sensing" \
      version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libatlas-base-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 edgeai && chown -R edgeai:edgeai /app
USER edgeai

# Basic container health check. The edge client does not expose an HTTP server.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from pathlib import Path; raise SystemExit(0 if Path('/app/main.py').exists() else 1)"

# Run application
CMD ["python", "main.py"]
