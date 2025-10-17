# Redis Quick Reference Guide

## Starting the System

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

## API Endpoints

### Create/Continue Session
```bash
curl -X POST http://localhost:8090/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_unique_id",
    "user_input": "Hello, I need help"
  }'
```

### List Active Sessions
```bash
curl http://localhost:8090/api/v1/sessions
```

### Health Check
```bash
curl http://localhost:8090/health
```

## Redis Admin Commands

### View Session State
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning HGETALL "trt:session:SESSION_ID:state"
```

### View Conversation History
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning LRANGE "trt:session:SESSION_ID:history" 0 -1
```

### List All Active Sessions
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning ZRANGE "trt:active_sessions" 0 -1
```

### Check Session TTL
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning TTL "trt:session:SESSION_ID:state"
```

### Delete Specific Session
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning DEL "trt:session:SESSION_ID:state" \
                        "trt:session:SESSION_ID:history" \
                        "trt:session:SESSION_ID:meta"
```

### View Redis Memory Usage
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning INFO memory
```

### View All Keys (for debugging)
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning KEYS "trt:*"
```

## Maintenance

### Backup Redis Data
```bash
docker run --rm \
  -v therapist2_redis-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup-$(date +%Y%m%d-%H%M%S).tar.gz /data
```

### Restore Redis Data
```bash
# Stop services
docker compose down

# Restore data
docker run --rm \
  -v therapist2_redis-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/redis-backup-TIMESTAMP.tar.gz -C /

# Start services
docker compose up -d
```

### Clear All Sessions (CAUTION!)
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning FLUSHDB
```

## Monitoring

### Watch Redis in Real-Time
```bash
docker exec -it trt-redis redis-cli -a trt_secure_redis_pass_2025 --no-auth-warning
> MONITOR
```

### Check Redis Statistics
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning INFO stats
```

### View Connected Clients
```bash
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning CLIENT LIST
```

## Troubleshooting

### Redis Not Starting
```bash
# Check logs
docker compose logs redis

# Common issues:
# 1. Port 6379 already in use
# 2. Permission issues with volume
# 3. Memory overcommit warning (harmless)
```

### App Can't Connect to Redis
```bash
# Verify Redis is healthy
docker compose ps

# Check Redis password in .env matches docker-compose.yml
cat .env | grep REDIS_PASSWORD

# Test connection manually
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 PING
# Should return: PONG
```

### Session Not Persisting
```bash
# Check if AOF is enabled
docker exec trt-redis redis-cli -a trt_secure_redis_pass_2025 \
  --no-auth-warning CONFIG GET appendonly
# Should return: 1 (yes)

# Check AOF file exists
docker exec trt-redis ls -l /data/appendonly.aof*
```

## Configuration

### Change Redis Password
1. Edit `.env`:
   ```bash
   REDIS_PASSWORD=your_new_password
   ```

2. Restart services:
   ```bash
   docker compose down
   docker compose up -d
   ```

### Change Session TTL (24h default)
Edit `src/utils/redis_session_manager.py`:
```python
self.session_ttl = 86400  # Change to desired seconds
```

Then rebuild:
```bash
docker compose up -d --build
```

## Port Configuration

- **Redis:** 6379 (exposed for admin access)
- **TRT API:** 8090 (application port)
- **Ollama:** 11434 (LLM service)

## Data Locations

- **Redis Data Volume:** `therapist2_redis-data` (Docker volume)
- **App Logs:** `./logs` (host directory)
- **Embeddings:** `./data/embeddings` (host directory)

## Security Notes

- Redis password in `.env` (never commit!)
- Redis only accessible from localhost
- Internal Docker network for app-to-redis communication
- 24-hour auto-expiration of session data
- No third-party services involved

## Performance Tips

1. **Monitor memory usage:**
   ```bash
   docker stats trt-redis
   ```

2. **Adjust maxmemory if needed:**
   ```bash
   docker exec trt-redis redis-cli -a password CONFIG SET maxmemory 2gb
   docker exec trt-redis redis-cli -a password CONFIG SET maxmemory-policy allkeys-lru
   ```

3. **Enable RDB snapshots for faster restarts:**
   Edit `docker-compose.yml` and add to Redis command:
   ```
   --save 900 1 --save 300 10
   ```

## Integration Status

✅ Redis session manager implemented
✅ Docker Compose configured
✅ API endpoints updated
✅ Health checks working
✅ Session persistence verified
✅ Conversation history working
✅ TTL management active
✅ Fallback to in-memory if Redis down

**Last Updated:** October 15, 2025
**Status:** Production Ready
