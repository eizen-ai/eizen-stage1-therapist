# TRT AI Therapist - Deployment Guide

**Version:** 1.0.0
**Date:** 2025-10-14

---

## Quick Start (Docker)

### 1. One-Command Startup

```bash
# Make startup script executable (first time only)
chmod +x startup.sh

# Start entire system
./startup.sh
```

This will:
- Start Ollama service
- Start TRT FastAPI application
- Pull LLaMA 3.1 model (if not already available)
- Run health checks
- Display access URLs

**Access Points:**
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## Manual Docker Deployment

### Step 1: Start Services

```bash
docker-compose up -d
```

### Step 2: Pull LLaMA Model

```bash
docker exec -it trt-ollama ollama pull llama3.1
```

### Step 3: Verify Health

```bash
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T12:34:56",
  "services": {
    "ollama": "connected",
    "rag": "ready",
    "state_machine": "loaded"
  }
}
```

---

## Testing the API

### Create a Session

```bash
curl -X POST http://localhost:8000/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{"client_id": "test_client"}'
```

**Response:**
```json
{
  "session_id": "session_20251014_123456_a1b2c3d4",
  "created_at": "2025-10-14T12:34:56",
  "status": "active",
  "message": "Session created successfully. Ready to begin therapy."
}
```

### Send Client Input

```bash
SESSION_ID="session_20251014_123456_a1b2c3d4"

curl -X POST "http://localhost:8000/api/v1/session/${SESSION_ID}/input" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I am feeling really stressed"}'
```

### Check Session Status

```bash
curl "http://localhost:8000/api/v1/session/${SESSION_ID}/status"
```

---

## Python Client Example

### Complete Therapy Session

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Create session
response = requests.post(f"{BASE_URL}/api/v1/session/create")
session_id = response.json()["session_id"]
print(f"Session ID: {session_id}")

# Conversation loop
conversation = [
    "I'm feeling really stressed",
    "I want to feel calm",
    "Yes, that makes sense",
    "I feel it in my chest",
    "It's tight",
    "Right now",
    "Nothing more",
    "Yes, I'm ready"
]

for user_input in conversation:
    response = requests.post(
        f"{BASE_URL}/api/v1/session/{session_id}/input",
        json={"user_input": user_input}
    )
    result = response.json()
    print(f"\nClient: {user_input}")
    print(f"Therapist: {result['therapist_response']}")
    print(f"State: {result['session_progress']['current_substate']}")

# Get final status
response = requests.get(f"{BASE_URL}/api/v1/session/{session_id}/status")
status = response.json()
completed = sum(status['completion_criteria'].values())
print(f"\nCompleted: {completed}/11 criteria")
```

---

## Docker Management

### View Logs

```bash
# All services
docker-compose logs -f

# TRT app only
docker-compose logs -f trt-app

# Ollama only
docker-compose logs -f ollama
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart TRT app only
docker-compose restart trt-app
```

### Stop Services

```bash
# Stop (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Rebuild After Code Changes

```bash
# Rebuild TRT app image
docker-compose build trt-app

# Restart with new image
docker-compose up -d trt-app
```

---

## Environment Configuration

### Custom Ollama URL

```bash
# docker-compose.override.yml
version: '3.8'

services:
  trt-app:
    environment:
      - OLLAMA_BASE_URL=http://custom-ollama:11434
```

### Using External Ollama

```yaml
# docker-compose.yml (modify trt-app service)
services:
  trt-app:
    environment:
      - OLLAMA_BASE_URL=http://192.168.1.100:11434
    # Remove depends_on for ollama service
```

---

## Production Deployment

### 1. Enable GPU Support (if available)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 2. Add Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/trt-api
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 3. Add SSL/TLS (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.your-domain.com
```

### 4. Add Authentication

```python
# src/api/auth.py (example)
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

---

## Monitoring

### Health Check Monitoring

```bash
# Add to crontab for monitoring
*/5 * * * * curl -f http://localhost:8000/health || echo "TRT API is down" | mail -s "Alert" admin@example.com
```

### Prometheus Integration (Future)

```python
# requirements.txt
prometheus-fastapi-instrumentator==6.1.0

# src/api/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

**Metrics endpoint:** `GET /metrics`

---

## Troubleshooting

### Issue: Ollama not connecting

**Solution:**
```bash
# Check Ollama container is running
docker ps | grep ollama

# Check Ollama logs
docker logs trt-ollama

# Restart Ollama
docker-compose restart ollama
```

### Issue: Model not found

**Solution:**
```bash
# List available models
docker exec trt-ollama ollama list

# Pull LLaMA 3.1
docker exec trt-ollama ollama pull llama3.1
```

### Issue: RAG embeddings missing

**Solution:**
```bash
# Generate embeddings (from host)
cd src/utils
python generate_rag_embeddings.py

# Copy to container (if needed)
docker cp data/embeddings trt-app:/app/data/
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use port 8080 instead
```

### Issue: Out of memory

**Solution:**
```yaml
# docker-compose.yml - Add resource limits
services:
  trt-app:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

---

## Backup and Restore

### Backup Session Data (if using persistent storage)

```bash
# Backup Docker volumes
docker run --rm -v therapist2_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama_backup.tar.gz /data

# Backup logs
tar czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

### Restore

```bash
# Restore Ollama data
docker run --rm -v therapist2_ollama_data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama_backup.tar.gz -C /
```

---

## Performance Tuning

### Multi-Worker Setup

```bash
# Use Gunicorn instead of Uvicorn
pip install gunicorn

# Start with multiple workers
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Caching (Redis)

```yaml
# docker-compose.yml - Add Redis
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

```python
# requirements.txt
redis==5.0.1

# Cache session data in Redis instead of in-memory
```

---

## Security Checklist

### Production Deployment

- [ ] Add API key authentication
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Enable request logging
- [ ] Set up monitoring alerts
- [ ] Regular security updates
- [ ] Implement session timeouts
- [ ] Add data encryption
- [ ] Configure firewall rules

---

## Next Steps

1. **Test the deployment:**
   ```bash
   ./startup.sh
   curl http://localhost:8000/health
   ```

2. **Run a test session:**
   ```bash
   python examples/test_api_client.py  # (create this)
   ```

3. **Review API documentation:**
   - Open http://localhost:8000/docs
   - Test endpoints in Swagger UI

4. **Monitor logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Plan production deployment:**
   - Add authentication
   - Configure SSL/TLS
   - Set up monitoring
   - Plan backup strategy

---

## Support

**Documentation:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
**Issues:** Check Docker logs first
**Health Check:** http://localhost:8000/health

---

**Status:** ✅ Ready for Deployment
**Last Updated:** 2025-10-14
