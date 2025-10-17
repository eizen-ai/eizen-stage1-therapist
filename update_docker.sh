#!/bin/bash
# Update Docker deployment with latest code changes
# This script rebuilds the Docker image to include all recent fixes

set -e

echo "=================================="
echo "TRT AI Therapist - Docker Update"
echo "=================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"

# Detect docker-compose or docker compose
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo -e "${RED}Error: Neither 'docker-compose' nor 'docker compose' found${NC}"
    echo "Please install Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose found: $DOCKER_COMPOSE_CMD${NC}"
echo ""

# Stop running containers
echo "Step 1/5: Stopping existing containers..."
$DOCKER_COMPOSE_CMD down || true
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# Remove old image to force rebuild
echo "Step 2/5: Removing old image..."
docker rmi therapist2-trt-app:latest 2>/dev/null || echo "No old image to remove"
echo -e "${GREEN}✓ Old image removed${NC}"
echo ""

# Build new image with latest code
echo "Step 3/5: Building new Docker image with latest fixes..."
echo -e "${YELLOW}This includes:${NC}"
echo "  • Emotion tracking fix (uses exact emotion/problem mentioned)"
echo "  • Question repetition prevention (scans last 6 turns)"
echo "  • Elaborative questions (Dr. Q style with multiple options)"
echo "  • Post-alpha state fix (goes directly to session conclusion)"
echo ""
$DOCKER_COMPOSE_CMD build --no-cache
echo -e "${GREEN}✓ New image built${NC}"
echo ""

# Start containers
echo "Step 4/5: Starting updated containers..."
$DOCKER_COMPOSE_CMD up -d
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Wait for health check
echo "Step 5/5: Waiting for services to be healthy..."
sleep 5

# Check if services are running
if docker ps | grep -q "trt-app"; then
    echo -e "${GREEN}✓ TRT App is running${NC}"
else
    echo -e "${YELLOW}⚠ TRT App may not be running properly${NC}"
fi

if docker ps | grep -q "trt-redis"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠ Redis may not be running properly${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ Docker Update Complete!${NC}"
echo "=================================="
echo ""
echo "Services available at:"
echo "  • API: http://localhost:8090"
echo "  • API Docs: http://localhost:8090/docs"
echo "  • Health Check: http://localhost:8090/health"
echo ""
echo "View logs:"
echo "  $DOCKER_COMPOSE_CMD logs -f trt-app"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8090/health"
echo ""
echo "Recent fixes included in this update:"
echo "  1. Emotion tracking - uses exact emotion/problem from client"
echo "  2. Question repetition - prevents repetitive questions (6-turn scan)"
echo "  3. Elaborative questions - Dr. Q style with multiple options"
echo "  4. Post-alpha fix - proper transition to session conclusion"
echo ""
