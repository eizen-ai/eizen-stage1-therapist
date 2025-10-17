# TRT AI Therapist - Quick Start Guide

**Port:** 8090 (Changed from 8000/8080 to avoid conflicts)
**Status:** Ready for deployment

---

## 🚀 Start the System (One Command)

```bash
./startup.sh
```

**Wait ~30 seconds for:**
- Docker containers to start
- Ollama to initialize
- LLaMA 3.1 model to load
- Health checks to pass

---

## 🌐 Access Points

Once started, access these URLs:

- **📝 API Documentation (Swagger UI):** http://localhost:8090/docs
- **📋 ReDoc (Alternative Docs):** http://localhost:8090/redoc
- **🏥 Health Check:** http://localhost:8090/health

---

## ✅ Verify It's Working

### Option 1: Health Check (Browser)

Open: http://localhost:8090/health

**Expected Response:**
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

### Option 2: Health Check (Terminal)

```bash
curl http://localhost:8090/health
```

### Option 3: Run Test Client

```bash
python examples/test_api_client.py
```

**Expected Output:**
```
🏥 Checking API health...
✅ API is healthy
   Ollama: connected
   RAG: ready
   State Machine: loaded

📝 Creating session for client: example_client
✅ Session created: session_20251014_123456_a1b2c3d4

🔄 Turn 1
👤 Client: I'm feeling really stressed and overwhelmed
🩺 Therapist: I hear you're feeling stressed and overwhelmed. What would we like to get out of our session today?
   📊 Metadata:
      State: 1.1_goal_and_vision
      Emotion: moderate_distress
...
```

---

## 🧪 Test API Manually

### 1. Create Session

```bash
curl -X POST http://localhost:8090/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{"client_id": "test_user"}'
```

**Response:**
```json
{
  "session_id": "session_20251014_123456_abc123",
  "created_at": "2025-10-14T12:34:56",
  "status": "active",
  "message": "Session created successfully. Ready to begin therapy."
}
```

**Copy the `session_id` from response!**

---

### 2. Send First Input

Replace `SESSION_ID` with the ID from step 1:

```bash
curl -X POST http://localhost:8090/api/v1/session/SESSION_ID/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I am feeling really stressed and overwhelmed"}'
```

**Response:**
```json
{
  "therapist_response": "I hear you're feeling stressed and overwhelmed. What would we like to get out of our session today?",
  "preprocessing": {
    "emotional_state": {
      "primary_emotion": "moderate_distress",
      "intensity": 2
    }
  },
  "session_progress": {
    "current_substate": "1.1_goal_and_vision",
    "body_question_count": 0
  }
}
```

---

### 3. Continue Conversation

Send more inputs with the same session ID:

```bash
# Turn 2: State goal
curl -X POST http://localhost:8090/api/v1/session/SESSION_ID/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I want to feel calm and peaceful"}'

# Turn 3: Affirmation
curl -X POST http://localhost:8090/api/v1/session/SESSION_ID/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Yes, that makes sense"}'

# Turn 4: Body location
curl -X POST http://localhost:8090/api/v1/session/SESSION_ID/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I feel it in my chest"}'
```

---

### 4. Check Session Status

```bash
curl http://localhost:8090/api/v1/session/SESSION_ID/status
```

**Response:**
```json
{
  "session_id": "session_20251014_123456_abc123",
  "status": "active",
  "current_substate": "1.2_problem_and_body",
  "body_question_count": 1,
  "completion_criteria": {
    "goal_established": true,
    "vision_created": true,
    "problem_identified": true,
    "body_awareness_present": false
  },
  "turn_count": 4
}
```

---

## 🐍 Python Example

```python
import requests

BASE_URL = "http://localhost:8090"

# Create session
resp = requests.post(f"{BASE_URL}/api/v1/session/create")
session_id = resp.json()["session_id"]
print(f"Session: {session_id}")

# Send input
resp = requests.post(
    f"{BASE_URL}/api/v1/session/{session_id}/input",
    json={"user_input": "I'm feeling stressed"}
)

result = resp.json()
print(f"Therapist: {result['therapist_response']}")
print(f"State: {result['session_progress']['current_substate']}")
```

---

## 🛑 Stop the System

```bash
docker-compose down
```

**To stop and remove all data:**
```bash
docker-compose down -v
```

---

## 🔧 Troubleshooting

### Port 8080 already in use?

**Check what's using the port:**
```bash
lsof -i :8090
```

**Change to a different port:**

Edit `docker-compose.yml`:
```yaml
ports:
  - "8090:8000"  # Change 8080 to 8090
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

---

### Can't connect to http://localhost:8090/health

**Check if containers are running:**
```bash
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE                  STATUS
abc123         therapist2-trt-app     Up 2 minutes (healthy)
def456         ollama/ollama:latest   Up 2 minutes (healthy)
```

**If containers aren't running:**
```bash
docker-compose logs
```

---

### Ollama not responding

**Check Ollama logs:**
```bash
docker logs trt-ollama
```

**Verify model is loaded:**
```bash
docker exec trt-ollama ollama list
```

**If llama3.1 is missing:**
```bash
docker exec trt-ollama ollama pull llama3.1
```

---

### "RAG embeddings not found" error

**Generate embeddings:**
```bash
# Activate virtual environment
source venv/bin/activate

# Generate embeddings
cd src/utils
python generate_rag_embeddings.py
```

---

## 📚 Full Documentation

- **API Reference:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Complete README:** [README.md](README.md)

---

## 🎯 Next Steps

1. ✅ Start system: `./startup.sh`
2. ✅ Open docs: http://localhost:8090/docs
3. ✅ Test API: `python examples/test_api_client.py`
4. ✅ Integrate into your workflow!

---

**Port:** 8080
**Status:** ✅ Ready to use
**Last Updated:** 2025-10-14
