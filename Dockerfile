# ==============================================================================
# CivicLens AI Backend - Production Dockerfile
# Multi-stage build for optimized image size and build caching
# ==============================================================================

# ------------------------------------------------------------------------------
# STAGE 1: Builder - Install dependencies into a virtual environment
# ------------------------------------------------------------------------------
FROM python:3.13-slim AS builder

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# System build dependencies required to compile Python packages
# (OpenCV, psycopg2, YOLOv8/torch wheels, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for isolated, copyable dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# STAGE 2: Runtime - Minimal final image
# ------------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app

WORKDIR /app

# Runtime-only system dependencies (shared libs needed by OpenCV/YOLO, no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy pre-built virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Create required directories with correct ownership
RUN mkdir -p /app/uploads /app/logs /app/models && \
    chown -R appuser:appgroup /app

# Copy application source code (after deps for optimal layer caching)
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose FastAPI/Uvicorn port
EXPOSE 8000

# Docker healthcheck - assumes a /health endpoint exists in the FastAPI app
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application with Uvicorn in production mode
# (For multi-core scaling, consider running behind Gunicorn+UvicornWorker
# or scaling replicas via Docker Compose / cloud platform instead)
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--proxy-headers", \
     "--forwarded-allow-ips=*"]