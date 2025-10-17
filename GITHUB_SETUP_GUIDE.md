# GitHub Setup Guide

> Complete guide for cloning and running the TRT AI Therapist from GitHub

---

## Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/trt-ai-therapist.git
cd trt-ai-therapist

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Start the system
./startup.sh
```

That's it! The API will be available at http://localhost:8090

---

## Detailed Setup Instructions

### Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed
- **Docker & Docker Compose** (recommended) OR
- **Ollama** installed locally (if not using Docker)
- **Git** for cloning
- **8GB+ RAM** (16GB recommended)
- **10GB+ free disk space**

---

## Option 1: Docker Setup (Recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/trt-ai-therapist.git
cd trt-ai-therapist
```

### Step 2: Install Docker

If you don't have Docker:

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

**macOS:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit if needed (default values work for most setups)
nano .env
```

### Step 4: Start the System

```bash
# Make startup script executable
chmod +x startup.sh

# Start all services (Ollama + API + Redis)
./startup.sh
```

This will:
- Pull Ollama Docker image
- Pull Redis image
- Build TRT API container
- Download llama3.1 model (first time only, ~5GB)
- Start all services

### Step 5: Verify Installation

```bash
# Check containers are running
docker compose ps

# Test health endpoint
curl http://localhost:8090/health

# Open API documentation
open http://localhost:8090/docs
```

---

## Option 2: Manual Setup (Without Docker)

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/trt-ai-therapist.git
cd trt-ai-therapist
```

### Step 2: Install Ollama

**Linux & macOS:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
- Download from https://ollama.ai/download

**Pull the model:**
```bash
ollama pull llama3.1
```

### Step 3: Install Redis

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
- Download from https://redis.io/download

### Step 4: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Download Embeddings

The RAG system requires pre-built embeddings. Download them:

```bash
# Option 1: Download from releases (if available)
# Check: https://github.com/YOUR_USERNAME/trt-ai-therapist/releases

# Option 2: Build embeddings yourself
python scripts/rebuild_embeddings_from_clean_data.py
```

### Step 6: Start Services

**Terminal 1 - Ollama:**
```bash
ollama serve
```

**Terminal 2 - Redis:**
```bash
redis-server
```

**Terminal 3 - TRT API:**
```bash
source venv/bin/activate
cd src
uvicorn api.main:app --host 0.0.0.0 --port 8090
```

### Step 7: Verify Installation

```bash
curl http://localhost:8090/health
```

---

## Testing Your Installation

### Test 1: Health Check

```bash
curl http://localhost:8090/health
```

Expected output:
```json
{
  "status": "healthy",
  "services": {
    "ollama": "connected",
    "rag": "ready",
    "redis": "healthy"
  }
}
```

### Test 2: Start a Session

```bash
curl -X POST http://localhost:8090/api/session/start \
  -H "Content-Type: application/json"
```

### Test 3: Send a Message

```bash
curl -X POST http://localhost:8090/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID_FROM_STEP_2",
    "message": "I want to feel less stressed"
  }'
```

---

## Configuration

### Environment Variables (.env)

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Redis Configuration
REDIS_URL=redis://:changeme@localhost:6379
REDIS_PASSWORD=changeme

# API Configuration
API_PORT=8090
LOG_LEVEL=INFO
```

### Customization

- **Change LLM Model:** Edit `OLLAMA_MODEL` in `.env`
- **Change Port:** Edit `API_PORT` in `.env` and `docker-compose.yml`
- **Adjust Redis Password:** Change `REDIS_PASSWORD` in `.env` and `docker-compose.yml`

---

## Troubleshooting

### Issue: "Ollama not connected"

**Docker:**
```bash
# Check if Ollama is running on host
ollama list

# If not, install Ollama on host machine
curl https://ollama.ai/install.sh | sh
ollama serve &
ollama pull llama3.1
```

**Manual:**
```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3.1
```

### Issue: "Redis connection failed"

**Docker:**
```bash
# Check Redis container
docker compose ps redis
docker compose logs redis

# Restart Redis
docker compose restart redis
```

**Manual:**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it
redis-server &
```

### Issue: "RAG not ready"

This means embeddings are missing or corrupted.

**Solution:**
```bash
# Option 1: Download pre-built embeddings from releases
# Check: https://github.com/YOUR_USERNAME/trt-ai-therapist/releases

# Option 2: Rebuild embeddings
python scripts/rebuild_embeddings_from_clean_data.py
```

### Issue: "Port 8090 already in use"

**Solution:**
```bash
# Option 1: Stop the process using the port
lsof -i :8090
kill -9 <PID>

# Option 2: Change the port in .env and docker-compose.yml
```

### Issue: Docker build fails

**Solution:**
```bash
# Clear Docker cache and rebuild
docker compose down
docker system prune -a
docker compose build --no-cache
docker compose up -d
```

---

## Development Setup

If you want to contribute or develop:

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt  # If exists
```

### 2. Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_improved_system.py
```

### 3. Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **mypy** for type checking

```bash
# Format code
black src/

# Lint
flake8 src/

# Type check
mypy src/
```

### 4. Documentation

- Add docstrings to all functions
- Update relevant .md files in `docs/`
- Follow existing code style

---

## Project Structure

```
trt-ai-therapist/
├── README.md                    # Main project README
├── GITHUB_SETUP_GUIDE.md       # This file
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker orchestration
├── startup.sh                   # Quick start script
├── .env.example                 # Environment template
│
├── src/                         # Source code
│   ├── api/                     # FastAPI endpoints
│   ├── core/                    # Core system
│   ├── agents/                  # AI agents
│   └── utils/                   # Utilities
│
├── data/                        # Data files
│   ├── embeddings/              # RAG embeddings
│   ├── transcripts/             # Therapy transcripts
│   └── processed/               # Processed data
│
├── config/                      # Configuration
│   └── STAGE1_COMPLETE.csv      # TRT state machine
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # System architecture
│   ├── PRESENTATION_GUIDE.md    # For presentations
│   └── ...
│
├── tests/                       # Test suite
├── examples/                    # Usage examples
└── scripts/                     # Utility scripts
```

---

## Next Steps

After successful setup:

1. **Read the Documentation**
   - [Architecture Overview](docs/ARCHITECTURE.md)
   - [API Documentation](docs/development/API_DOCUMENTATION.md)

2. **Try Examples**
   ```bash
   python examples/test_api_client.py
   ```

3. **Explore API**
   - Open http://localhost:8090/docs
   - Try the interactive API documentation

4. **Join Development**
   - Read [CONTRIBUTING.md](CONTRIBUTING.md)
   - Check [Issues](https://github.com/YOUR_USERNAME/trt-ai-therapist/issues)

---

## Support

- **Documentation:** See `docs/` directory
- **Issues:** https://github.com/YOUR_USERNAME/trt-ai-therapist/issues
- **Discussions:** https://github.com/YOUR_USERNAME/trt-ai-therapist/discussions

---

## License

MIT License - See [LICENSE](LICENSE) file

---

**Last Updated:** 2025-10-17
**Version:** 1.0
