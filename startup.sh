#!/bin/bash
# Startup script for TRT AI Therapist System

set -e

echo "🚀 Starting TRT AI Therapist System..."
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed (v2 plugin or v1 standalone)
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Start services
echo "📦 Starting Docker containers..."
$COMPOSE_CMD up -d

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service to be ready..."
sleep 10

# Check if LLaMA model is available
echo "🔍 Checking for LLaMA 3.1 model..."
if ! docker exec trt-ollama ollama list | grep -q "llama3.1"; then
    echo "📥 Pulling LLaMA 3.1 model (this may take a while)..."
    docker exec trt-ollama ollama pull llama3.1
else
    echo "✅ LLaMA 3.1 model already available"
fi

# Wait for TRT app to be ready
echo "⏳ Waiting for TRT app to be ready..."
sleep 5

# Health check
echo "🏥 Running health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:8090/health)
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ System is healthy and ready!"
    echo ""
    echo "🎉 TRT AI Therapist API is running!"
    echo "========================================"
    echo "📝 API Documentation: http://localhost:8090/docs"
    echo "📋 ReDoc: http://localhost:8090/redoc"
    echo "🏥 Health Check: http://localhost:8090/health"
    echo ""
    echo "🔧 Management Commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop system:  docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo ""
else
    echo "⚠️ System health check returned: $HEALTH_STATUS"
    echo "Please check logs: docker-compose logs"
fi
