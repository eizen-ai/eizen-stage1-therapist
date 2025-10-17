# Redis Integration Plan for TRT System

**Date:** 2025-10-15
**Status:** Planning / Design Phase
**Goal:** Scale to multiple concurrent users

---

## 🎯 Problem We're Solving

### Current System (In-Memory)
```python
# In main.py
active_sessions: Dict[str, Dict] = {}

# Problem:
❌ Lost on restart
❌ Limited to single server
❌ No persistence
❌ Memory limited
❌ Can't scale horizontally
```

### With Redis
```python
# Sessions stored in Redis
✅ Survives restarts
✅ Multiple servers share state
✅ Persistent storage
✅ Scales to millions of sessions
✅ Horizontal scaling ready
```

---

## 📊 What to Store in Redis

### 1. Session State (Most Critical)
**Key Pattern:** `trt:session:{session_id}:state`

**Data Structure:** Hash
```python
{
    "session_id": "user_1234",
    "current_stage": "stage_1",
    "current_substate": "1.2_problem_and_body",
    "body_questions_asked": 2,
    "stage_1_completion": {
        "goal_stated": true,
        "vision_accepted": true,
        "problem_identified": true,
        "body_awareness_present": false
    },
    "created_at": "2025-10-15T09:00:00",
    "last_interaction": "2025-10-15T09:15:23",
    "turn_count": 8,
    "status": "active"
}
```

**TTL:** 24 hours (auto-expire inactive sessions)

---

### 2. Conversation History
**Key Pattern:** `trt:session:{session_id}:history`

**Data Structure:** List (LPUSH for newest)
```python
[
    {
        "turn": 8,
        "timestamp": "2025-10-15T09:15:23",
        "client_input": "I feel it in my chest",
        "therapist_response": "Where in your chest?",
        "navigation_decision": "body_location",
        "rag_query": "dr_q_location"
    },
    {
        "turn": 7,
        "timestamp": "2025-10-15T09:14:10",
        ...
    }
]
```

**Commands:**
```python
# Add new exchange
redis.lpush("trt:session:user_1234:history", json.dumps(exchange))

# Get last 5 exchanges
redis.lrange("trt:session:user_1234:history", 0, 4)

# Limit to 50 exchanges (trim old ones)
redis.ltrim("trt:session:user_1234:history", 0, 49)
```

---

### 3. Active Sessions Index
**Key Pattern:** `trt:active_sessions`

**Data Structure:** Sorted Set (by last_interaction timestamp)
```python
ZADD trt:active_sessions {timestamp} "user_1234"
ZADD trt:active_sessions {timestamp} "user_5678"
```

**Use Cases:**
```python
# Get all active sessions
redis.zrange("trt:active_sessions", 0, -1)

# Get sessions active in last hour
cutoff = time.time() - 3600
redis.zrangebyscore("trt:active_sessions", cutoff, "+inf")

# Remove inactive sessions (cleanup)
redis.zremrangebyscore("trt:active_sessions", "-inf", cutoff)
```

---

### 4. Session Metadata
**Key Pattern:** `trt:session:{session_id}:meta`

**Data Structure:** Hash
```python
{
    "client_id": "external_client_123",
    "platform": "mobile_app",
    "app_version": "2.1.0",
    "created_via": "input_endpoint",
    "external_system_id": "crm_456789"
}
```

---

### 5. Rate Limiting (Optional)
**Key Pattern:** `trt:ratelimit:{session_id}:{minute}`

**Data Structure:** String (counter)
```python
# Increment counter for this minute
redis.incr(f"trt:ratelimit:user_1234:{current_minute}")
redis.expire(f"trt:ratelimit:user_1234:{current_minute}", 60)

# Check if over limit
count = redis.get(f"trt:ratelimit:user_1234:{current_minute}")
if count > 10:  # Max 10 requests per minute
    raise RateLimitExceeded()
```

---

## 🔧 Implementation Plan

### Phase 1: Basic Session Storage

#### Step 1: Install Redis Client
```bash
pip install redis
```

Add to `requirements.txt`:
```
redis==5.0.1
```

#### Step 2: Create Redis Manager
**File:** `src/utils/redis_manager.py`

```python
import redis
import json
from typing import Dict, Optional
from datetime import datetime
import os

class RedisSessionManager:
    """Manages TRT sessions in Redis"""

    def __init__(self, redis_url=None):
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.session_ttl = 86400  # 24 hours

    def save_session_state(self, session_id: str, session_state) -> bool:
        """Save session state to Redis"""
        key = f"trt:session:{session_id}:state"

        data = {
            "session_id": session_id,
            "current_stage": session_state.current_stage,
            "current_substate": session_state.current_substate,
            "body_questions_asked": session_state.body_questions_asked,
            "stage_1_completion": json.dumps(session_state.stage_1_completion),
            "last_interaction": datetime.now().isoformat()
        }

        # Save as hash
        self.redis.hset(key, mapping=data)

        # Set TTL
        self.redis.expire(key, self.session_ttl)

        # Add to active sessions index
        self.redis.zadd("trt:active_sessions", {session_id: datetime.now().timestamp()})

        return True

    def load_session_state(self, session_id: str) -> Optional[Dict]:
        """Load session state from Redis"""
        key = f"trt:session:{session_id}:state"

        data = self.redis.hgetall(key)

        if not data:
            return None

        # Parse JSON fields
        if "stage_1_completion" in data:
            data["stage_1_completion"] = json.loads(data["stage_1_completion"])

        # Convert numeric fields
        if "body_questions_asked" in data:
            data["body_questions_asked"] = int(data["body_questions_asked"])

        return data

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return self.redis.exists(f"trt:session:{session_id}:state") > 0

    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        # Delete all keys for this session
        keys = [
            f"trt:session:{session_id}:state",
            f"trt:session:{session_id}:history",
            f"trt:session:{session_id}:meta"
        ]

        self.redis.delete(*keys)

        # Remove from active sessions
        self.redis.zrem("trt:active_sessions", session_id)

        return True

    def add_conversation_exchange(self, session_id: str, exchange: Dict) -> bool:
        """Add conversation exchange to history"""
        key = f"trt:session:{session_id}:history"

        # Add to list
        self.redis.lpush(key, json.dumps(exchange))

        # Keep only last 50 exchanges
        self.redis.ltrim(key, 0, 49)

        # Set TTL
        self.redis.expire(key, self.session_ttl)

        return True

    def get_conversation_history(self, session_id: str, limit: int = 10) -> list:
        """Get conversation history"""
        key = f"trt:session:{session_id}:history"

        # Get last N exchanges
        history = self.redis.lrange(key, 0, limit - 1)

        # Parse JSON
        return [json.loads(exchange) for exchange in history]

    def list_active_sessions(self, limit: int = 100) -> list:
        """List active sessions"""
        # Get from sorted set (most recent first)
        return self.redis.zrevrange("trt:active_sessions", 0, limit - 1)

    def cleanup_inactive_sessions(self, hours: int = 24):
        """Remove sessions inactive for X hours"""
        import time
        cutoff = time.time() - (hours * 3600)

        # Get inactive sessions
        inactive = self.redis.zrangebyscore("trt:active_sessions", "-inf", cutoff)

        # Delete each
        for session_id in inactive:
            self.delete_session(session_id)

        return len(inactive)
```

#### Step 3: Update FastAPI to Use Redis
**File:** `src/api/main.py`

```python
from src.utils.redis_manager import RedisSessionManager

# Initialize Redis
redis_manager = RedisSessionManager()

@app.post("/api/v1/input", response_model=TherapistResponse)
async def process_input_with_session(request: ClientInputRequest):
    """Process input with Redis session storage"""

    session_id = request.session_id

    # Check if session exists in Redis
    if not redis_manager.session_exists(session_id):
        # Create new session
        therapy_system = ImprovedOllamaTherapySystem()
        session_state = therapy_system.create_session(session_id)

        # Save to Redis
        redis_manager.save_session_state(session_id, session_state)

        # Save metadata
        redis_manager.redis.hset(
            f"trt:session:{session_id}:meta",
            mapping={
                "created_at": datetime.now().isoformat(),
                "created_via": "input_endpoint"
            }
        )
    else:
        # Load existing session from Redis
        session_data = redis_manager.load_session_state(session_id)

        # Reconstruct session state
        therapy_system = ImprovedOllamaTherapySystem()
        session_state = therapy_system.create_session(session_id)

        # Restore state
        session_state.current_stage = session_data["current_stage"]
        session_state.current_substate = session_data["current_substate"]
        session_state.body_questions_asked = session_data["body_questions_asked"]
        session_state.stage_1_completion = session_data["stage_1_completion"]

    # Process input
    result = therapy_system.process_client_input(request.user_input, session_state)

    # Save updated state to Redis
    redis_manager.save_session_state(session_id, session_state)

    # Save conversation exchange
    redis_manager.add_conversation_exchange(session_id, {
        "timestamp": datetime.now().isoformat(),
        "client_input": request.user_input,
        "therapist_response": result["therapist_response"],
        "navigation_decision": result["navigation"].get("navigation_decision")
    })

    # Build response
    response = TherapistResponse(...)

    return response


@app.get("/api/v1/sessions")
async def list_sessions():
    """List all active sessions from Redis"""
    session_ids = redis_manager.list_active_sessions(limit=100)

    sessions_list = []
    for session_id in session_ids:
        session_data = redis_manager.load_session_state(session_id)
        if session_data:
            sessions_list.append({
                "session_id": session_id,
                "current_substate": session_data["current_substate"],
                "last_interaction": session_data["last_interaction"]
            })

    return {
        "total_sessions": len(sessions_list),
        "sessions": sessions_list
    }


@app.delete("/api/v1/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session from Redis"""
    redis_manager.delete_session(session_id)
    return {"message": f"Session {session_id} deleted"}
```

---

### Phase 2: Advanced Features

#### Caching RAG Results
**Key Pattern:** `trt:rag_cache:{rag_query}:{hash}`

```python
import hashlib

def query_rag_with_cache(rag_query: str, client_input: str):
    """Query RAG with Redis caching"""

    # Create cache key
    cache_key = hashlib.md5(f"{rag_query}:{client_input}".encode()).hexdigest()
    redis_key = f"trt:rag_cache:{rag_query}:{cache_key}"

    # Check cache
    cached = redis.get(redis_key)
    if cached:
        return json.loads(cached)

    # Query RAG
    results = rag_system.query(rag_query, client_input)

    # Cache for 1 hour
    redis.setex(redis_key, 3600, json.dumps(results))

    return results
```

#### Session Analytics
**Key Pattern:** `trt:analytics:daily:{date}`

```python
def track_session_metrics(session_id: str, event: str):
    """Track session events for analytics"""
    today = datetime.now().strftime("%Y-%m-%d")

    # Increment counters
    redis.hincrby(f"trt:analytics:daily:{today}", "total_inputs", 1)
    redis.hincrby(f"trt:analytics:daily:{today}", f"event:{event}", 1)

    # Set TTL (keep 30 days)
    redis.expire(f"trt:analytics:daily:{today}", 30 * 86400)
```

#### Distributed Locking
```python
from redis.lock import Lock

def process_with_lock(session_id: str):
    """Prevent concurrent processing of same session"""

    lock_key = f"trt:lock:{session_id}"
    lock = redis.lock(lock_key, timeout=10)

    if lock.acquire(blocking=True, blocking_timeout=5):
        try:
            # Process session
            result = process_session(session_id)
            return result
        finally:
            lock.release()
    else:
        raise Exception("Session is being processed by another request")
```

---

## 🐳 Docker Integration

### Update `docker-compose.yml`

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: trt-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    container_name: trt-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  trt-app:
    build: .
    container_name: trt-app
    ports:
      - "8090:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.1
      - REDIS_URL=redis://redis:6379
    depends_on:
      - ollama
      - redis
    restart: unless-stopped

volumes:
  ollama-data:
  redis-data:
```

---

## 📊 Benefits of Redis Integration

### 1. Persistence
- ✅ Sessions survive server restart
- ✅ Can restore conversation context
- ✅ No data loss

### 2. Scalability
- ✅ Multiple API servers share sessions
- ✅ Load balancer can route to any server
- ✅ Horizontal scaling ready

### 3. Performance
- ✅ Fast in-memory access
- ✅ Can cache RAG results
- ✅ Efficient session lookup

### 4. Features
- ✅ Automatic session expiration (TTL)
- ✅ Session analytics
- ✅ Rate limiting
- ✅ Distributed locking

---

## 🔄 Migration Strategy

### Step 1: Add Redis (Non-Breaking)
```python
# Keep in-memory as fallback
active_sessions: Dict[str, Dict] = {}

# Add Redis
redis_manager = RedisSessionManager()

# Write to both
def save_session(session_id, session_state):
    active_sessions[session_id] = session_state  # Old way
    redis_manager.save_session_state(session_id, session_state)  # New way
```

### Step 2: Read from Redis First
```python
def get_session(session_id):
    # Try Redis first
    session = redis_manager.load_session_state(session_id)
    if session:
        return session

    # Fallback to in-memory
    return active_sessions.get(session_id)
```

### Step 3: Remove In-Memory (Full Redis)
```python
# Remove: active_sessions: Dict[str, Dict] = {}
# Use only: redis_manager
```

---

## 💰 Cost & Performance

### Redis Memory Usage

**Per Session:**
- State: ~2 KB
- History (50 exchanges): ~50 KB
- Metadata: ~1 KB
- **Total:** ~53 KB per session

**Capacity:**
- 1 GB Redis = ~18,000 concurrent sessions
- 4 GB Redis = ~72,000 concurrent sessions
- 16 GB Redis = ~290,000 concurrent sessions

### Performance
- Read latency: < 1ms
- Write latency: < 1ms
- Throughput: 100,000+ ops/sec

---

## 🔒 Security Considerations

### 1. Redis Authentication
```yaml
# docker-compose.yml
redis:
  command: redis-server --requirepass YOUR_STRONG_PASSWORD

# In code
redis_url = "redis://:YOUR_STRONG_PASSWORD@redis:6379"
```

### 2. Encrypted Connections (TLS)
```python
redis = redis.from_url(
    "rediss://redis:6379",  # Note: rediss (TLS)
    ssl_cert_reqs=None
)
```

### 3. Network Isolation
```yaml
# docker-compose.yml
networks:
  internal:
    driver: bridge

services:
  redis:
    networks:
      - internal
    # Don't expose port to host in production
```

---

## 📝 Next Steps

### Immediate (Phase 1)
1. ✅ Add `redis` to requirements.txt
2. ✅ Create `RedisSessionManager` class
3. ✅ Update `main.py` to use Redis
4. ✅ Add Redis to `docker-compose.yml`
5. ✅ Test session persistence

### Future (Phase 2)
1. ⏳ Add RAG caching
2. ⏳ Implement rate limiting
3. ⏳ Add session analytics
4. ⏳ Multi-server deployment
5. ⏳ Redis Cluster for high availability

---

## 🎯 Summary

### Current (In-Memory)
```
Single Server → In-Memory Dict → Lost on Restart
```

### With Redis
```
Multiple Servers → Shared Redis → Persistent Storage
     ↓                 ↓                ↓
Load Balanced    Session State    Survives Restarts
Horizontally     Conversation     Analytics Ready
Scalable         History          Rate Limited
```

---

**Ready to implement?** I can help you build this step by step! 🚀

**Want me to start with Phase 1 (Basic Session Storage)?**
