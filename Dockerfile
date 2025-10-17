# Dockerfile for AI Therapist - TRT System
# Multi-stage build for optimized image size

FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/

# Create directories for logs and embeddings
RUN mkdir -p logs data/embeddings

# Set Python path
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8090/health || exit 1

# Run FastAPI server on port 8090
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8090"]
