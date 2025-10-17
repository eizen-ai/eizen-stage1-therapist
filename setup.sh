#!/bin/bash
# TRT AI Therapist - Automated Setup Script
# This script sets up the project after cloning from GitHub

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  TRT AI Therapist - Setup Script"
echo "========================================"
echo ""

# Check if running from project root
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${BLUE}Step 1/6: Checking prerequisites...${NC}"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python 3 found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Check Docker (recommended but optional)
if command_exists docker; then
    echo -e "${GREEN}✓ Docker found${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Docker not found (optional)${NC}"
    DOCKER_AVAILABLE=false
fi

# Check Git
if command_exists git; then
    echo -e "${GREEN}✓ Git found${NC}"
else
    echo -e "${YELLOW}⚠ Git not found${NC}"
fi

echo ""
echo -e "${BLUE}Step 2/6: Setting up environment...${NC}"

# Create .env from .env.example if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
    else
        echo -e "${YELLOW}⚠ .env.example not found, creating default .env${NC}"
        cat > .env << 'EOF'
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Redis Configuration
REDIS_URL=redis://:changeme@localhost:6379
REDIS_PASSWORD=changeme

# API Configuration
API_PORT=8090
LOG_LEVEL=INFO
EOF
    fi
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo ""
echo -e "${BLUE}Step 3/6: Setting up Python environment...${NC}"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created virtual environment${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ Upgraded pip${NC}"

# Install dependencies
echo "Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Installed Python dependencies${NC}"

echo ""
echo -e "${BLUE}Step 4/6: Checking data files...${NC}"

# Check if embeddings exist
if [ -f "data/embeddings/trt_rag_index.faiss" ] && [ -f "data/embeddings/trt_rag_metadata.json" ]; then
    echo -e "${GREEN}✓ RAG embeddings found${NC}"
else
    echo -e "${YELLOW}⚠ RAG embeddings not found${NC}"
    echo ""
    echo "You need to either:"
    echo "  1. Download pre-built embeddings from GitHub releases, OR"
    echo "  2. Build embeddings yourself (requires therapy transcripts)"
    echo ""
    read -p "Do you want to build embeddings now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "scripts/rebuild_embeddings_from_clean_data.py" ]; then
            echo "Building embeddings..."
            python scripts/rebuild_embeddings_from_clean_data.py
            echo -e "${GREEN}✓ Built RAG embeddings${NC}"
        else
            echo -e "${RED}✗ Build script not found${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ You'll need to add embeddings before running the system${NC}"
    fi
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/embeddings
mkdir -p data/processed
echo -e "${GREEN}✓ Created necessary directories${NC}"

echo ""
echo -e "${BLUE}Step 5/6: Checking services...${NC}"

# Check if we should use Docker or manual setup
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo ""
    echo "Docker is available. You have two options:"
    echo "  1. Docker setup (recommended - includes Ollama + Redis)"
    echo "  2. Manual setup (you manage Ollama + Redis separately)"
    echo ""
    read -p "Use Docker setup? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        USE_DOCKER=true
    else
        USE_DOCKER=false
    fi
else
    USE_DOCKER=false
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Docker setup selected"
    echo ""
    echo "To start the system, run:"
    echo -e "${GREEN}  ./startup.sh${NC}"
    echo ""
else
    echo "Manual setup selected"
    echo ""
    echo "You need to install and start:"
    echo ""

    # Check Ollama
    if command_exists ollama; then
        echo -e "${GREEN}✓ Ollama found${NC}"
    else
        echo -e "${RED}✗ Ollama not found${NC}"
        echo "  Install: curl https://ollama.ai/install.sh | sh"
    fi

    # Check Redis
    if command_exists redis-server; then
        echo -e "${GREEN}✓ Redis found${NC}"
    else
        echo -e "${RED}✗ Redis not found${NC}"
        echo "  Install: sudo apt-get install redis-server (Ubuntu/Debian)"
        echo "           brew install redis (macOS)"
    fi

    echo ""
    echo "After installing Ollama and Redis:"
    echo ""
    echo "  1. Start Ollama: ollama serve"
    echo "  2. Pull model: ollama pull llama3.1"
    echo "  3. Start Redis: redis-server"
    echo "  4. Start API: source venv/bin/activate && cd src && uvicorn api.main:app --host 0.0.0.0 --port 8090"
fi

echo ""
echo -e "${BLUE}Step 6/6: Making scripts executable...${NC}"

# Make scripts executable
chmod +x startup.sh 2>/dev/null || true
chmod +x update_docker.sh 2>/dev/null || true
echo -e "${GREEN}✓ Scripts are executable${NC}"

echo ""
echo "========================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "========================================"
echo ""

if [ "$USE_DOCKER" = true ]; then
    echo "Next steps:"
    echo "  1. Run: ./startup.sh"
    echo "  2. Open: http://localhost:8090/docs"
else
    echo "Next steps:"
    echo "  1. Install Ollama: curl https://ollama.ai/install.sh | sh"
    echo "  2. Install Redis: (see instructions above)"
    echo "  3. Start services manually (see GITHUB_SETUP_GUIDE.md)"
fi

echo ""
echo "Documentation:"
echo "  - Setup Guide: GITHUB_SETUP_GUIDE.md"
echo "  - Architecture: docs/ARCHITECTURE.md"
echo "  - API Docs: docs/development/API_DOCUMENTATION.md"
echo ""
