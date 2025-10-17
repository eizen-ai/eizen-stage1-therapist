# Port Configuration

## Current Setup

**API Port:** `8090` (Host) → `8000` (Container)

### Why Port 8090?

- Port `8000` - Common default, may conflict with other dev servers
- Port `8080` - Already in use by another service on your system
- Port `8090` - ✅ **Available and configured**

---

## Access URLs

Once the system is started with `./startup.sh`:

- **Swagger UI (Interactive API Docs):** http://localhost:8090/docs
- **ReDoc (Alternative Docs):** http://localhost:8090/redoc
- **Health Check:** http://localhost:8090/health

---

## Changing the Port (If Needed)

If port 8090 is not suitable, you can change it easily:

### 1. Edit docker-compose.yml

```yaml
services:
  trt-app:
    ports:
      - "YOUR_PORT:8000"  # Change YOUR_PORT to desired port (e.g., 9000, 3000, etc.)
```

### 2. Restart the system

```bash
docker-compose down
docker-compose up -d
```

### 3. Access the new port

```bash
curl http://localhost:YOUR_PORT/health
```

---

## Common Port Conflicts

### If port is already in use:

```bash
# Find what's using the port
lsof -i :8090

# Or
netstat -tlnp | grep 8090
ss -tlnp | grep 8090

# Kill the process (if safe to do so)
kill -9 <PID>
```

---

## Port Mapping Explained

```
Your Computer (Host)          Docker Container
┌─────────────────┐          ┌──────────────┐
│  localhost:8090 │◄────────►│ container    │
│                 │          │ port 8000    │
│  (External)     │          │ (Internal)   │
└─────────────────┘          └──────────────┘
```

- **Host Port (8090):** What you access from your browser/code
- **Container Port (8000):** What FastAPI runs on inside Docker
- Docker handles the mapping automatically

---

## Testing the Port

```bash
# Quick health check
curl http://localhost:8090/health

# Expected response (if running):
# {"status":"healthy","services":{...}}

# If not running yet:
./startup.sh
```

---

## All Service Ports

| Service | Host Port | Container Port | Purpose |
|---------|-----------|----------------|---------|
| Ollama | 11434 | 11434 | LLM inference API |
| TRT API | **8090** | 8000 | FastAPI REST endpoints |

---

**Current Configuration:** Port `8090` ✅
**Status:** Available and ready to use
**Last Updated:** 2025-10-14
