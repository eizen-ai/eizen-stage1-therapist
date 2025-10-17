# TRT AI Therapist - API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`
**Documentation:** `http://localhost:8000/docs` (Swagger UI)
**ReDoc:** `http://localhost:8000/redoc`

---

## Overview

The TRT AI Therapist API provides REST endpoints for integrating Dr. Q's Trauma Resiliency Training (TRT) methodology into agentic workflows. The API is fully containerized and designed for stateful session management with complete therapeutic interaction tracking.

---

## Quick Start

### Simplest Usage (Just Start Talking!)

```bash
# No need to create session first - just send input with your unique session ID!
curl -X POST http://localhost:8090/api/v1/session/user_1234/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I want to feel calm"}'

# Session auto-creates if it doesn't exist
# Continue conversation with same session_id
curl -X POST http://localhost:8090/api/v1/session/user_1234/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Yes that makes sense"}'
```

### Using Docker Compose (Recommended)

```bash
# Start all services (Ollama + TRT App)
docker-compose up -d

# Pull LLaMA model (first time only)
docker exec -it trt-ollama ollama pull llama3.1

# Check health
curl http://localhost:8090/health

# View logs
docker-compose logs -f trt-app
```

### Using Python Directly

```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama separately
ollama serve

# Start FastAPI
cd src
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Authentication

**Current Version:** No authentication required (local deployment)

**Production:** Implement API keys or OAuth2 for production deployments.

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Verify that all system components are operational.

**Response:** `200 OK`

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

**cURL Example:**

```bash
curl http://localhost:8000/health
```

---

### 2. Create Session (OPTIONAL)

**Endpoint:** `POST /api/v1/session/create`

**Description:** Create a new therapy session and initialize the TRT state machine.

**⚠️ NOTE:** Session creation is now **OPTIONAL**! Sessions auto-create when you first send input. You only need this endpoint if you want to set specific metadata upfront.

**Request Body:**

```json
{
  "session_id": "my_custom_session_001",  // OPTIONAL: Provide your own ID or omit for auto-generation
  "client_id": "client_123",
  "metadata": {
    "platform": "web",
    "version": "1.0"
  }
}
```

**Fields:**
- `session_id` (string, optional): Custom session ID. If omitted, a unique ID will be auto-generated.
- `client_id` (string, optional): Client identifier for tracking
- `metadata` (object, optional): Additional metadata

**Response:** `200 OK`

```json
{
  "session_id": "my_custom_session_001",  // Your custom ID or auto-generated
  "created_at": "2025-10-14T12:34:56",
  "status": "active",
  "message": "Session created successfully. Ready to begin therapy."
}
```

#### Auto-Generated Session ID (Default)

**cURL Example:**

```bash
# Omit session_id field for auto-generation
curl -X POST http://localhost:8000/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_123",
    "metadata": {"platform": "web"}
  }'
```

**Python Example:**

```python
import requests

# Auto-generated session ID
response = requests.post(
    "http://localhost:8000/api/v1/session/create",
    json={
        "client_id": "client_123",
        "metadata": {"platform": "web"}
    }
)

session_data = response.json()
session_id = session_data["session_id"]
print(f"Created session: {session_id}")
# Output: Created session: session_20251015_083406_0432b008
```

#### Custom Session ID (NEW!)

**cURL Example:**

```bash
# Provide your own session_id
curl -X POST http://localhost:8000/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "crm_user_12345",
    "client_id": "client_123",
    "metadata": {"platform": "web"}
  }'
```

**Python Example:**

```python
import requests

# Use your own session ID
response = requests.post(
    "http://localhost:8000/api/v1/session/create",
    json={
        "session_id": "crm_user_12345",
        "client_id": "client_123",
        "metadata": {"platform": "web", "crm_id": "12345"}
    }
)

session_data = response.json()
session_id = session_data["session_id"]
print(f"Created session: {session_id}")
# Output: Created session: crm_user_12345

# Later, use your CRM ID directly!
response = requests.post(
    "http://localhost:8000/api/v1/session/crm_user_12345/input",
    json={"user_input": "I want to feel calm"}
)
```

**Duplicate Check:**
If the session ID already exists, returns `409 Conflict`:

```json
{
  "error": "HTTPException",
  "message": "Session ID 'crm_user_12345' already exists. Please use a different ID or omit it for auto-generation.",
  "timestamp": "2025-10-15T08:34:15.120207"
}
```

**Use Cases:**
- ✅ CRM system integration (use CRM user IDs)
- ✅ Mobile app integration (use device/user combination)
- ✅ Webhook integration (use external system IDs)
- ✅ Multi-platform tracking (platform_userid format)

**See:** [Custom Session ID Guide](./CUSTOM_SESSION_ID_GUIDE.md) for complete examples and best practices.

---

### 3. Process Client Input

**Endpoint:** `POST /api/v1/session/{session_id}/input`

**Description:** Process client input and generate therapist response with complete preprocessing, navigation, and state tracking.

**✨ AUTO-CREATES SESSION:** If the `session_id` doesn't exist, it will be automatically created. Just start talking!

**Path Parameters:**
- `session_id` (string, required): Your unique session identifier (auto-creates if doesn't exist)

**Request Body:**

```json
{
  "user_input": "I'm feeling really stressed and overwhelmed"
}
```

**Response:** `200 OK`

```json
{
  "therapist_response": "I hear you're feeling stressed and overwhelmed. What would we like to get out of our session today?",
  "preprocessing": {
    "original_input": "I'm feeling really stressed and overwhelmed",
    "cleaned_input": "i am feeling really stressed and overwhelmed",
    "corrected_input": "i am feeling really stressed and overwhelmed",
    "emotional_state": {
      "categories": {
        "negative_moderate": ["stressed", "overwhelmed"]
      },
      "intensity": 2,
      "primary_emotion": "moderate_distress"
    },
    "input_category": "feeling_statement",
    "spelling_corrections": [],
    "safety_checks": {
      "self_harm_detected": {
        "detected": false,
        "phrases_found": [],
        "severity": "none"
      },
      "thinking_mode_detected": {
        "detected": false,
        "phrases_found": []
      },
      "past_tense_detected": {
        "detected": false,
        "phrases_found": []
      },
      "i_dont_know_detected": {
        "detected": false,
        "phrases_found": []
      }
    }
  },
  "navigation": {
    "decision": "continue",
    "next_state": "1.1_goal_and_vision",
    "rag_query": "client feeling stressed and overwhelmed, ask about session goal",
    "reasoning": "Client expressed emotional distress, advancing to goal clarification"
  },
  "session_progress": {
    "current_substate": "1.1_goal_and_vision",
    "body_question_count": 0,
    "completion_criteria": {
      "goal_established": false,
      "vision_created": false,
      "problem_identified": false,
      "body_awareness_present": false,
      "body_location_identified": false,
      "body_sensation_identified": false,
      "present_moment_focus": false,
      "pattern_understood": false,
      "rapport_established": false,
      "alpha_state_achieved": false,
      "ready_for_stage_2": false
    }
  },
  "timestamp": "2025-10-14T12:35:00"
}
```

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/v1/session/session_20251014_123456_a1b2c3d4/input \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "I am feeling really stressed"
  }'
```

**Python Example:**

```python
import requests

session_id = "session_20251014_123456_a1b2c3d4"

response = requests.post(
    f"http://localhost:8000/api/v1/session/{session_id}/input",
    json={"user_input": "I'm feeling really stressed"}
)

result = response.json()
print(f"Therapist: {result['therapist_response']}")
print(f"State: {result['session_progress']['current_substate']}")
print(f"Emotion: {result['preprocessing']['emotional_state']['primary_emotion']}")
```

---

### 4. Get Session Status

**Endpoint:** `GET /api/v1/session/{session_id}/status`

**Description:** Retrieve current session status, progress, and completion criteria.

**Path Parameters:**
- `session_id` (string, required): Session identifier

**Response:** `200 OK`

```json
{
  "session_id": "session_20251014_123456_a1b2c3d4",
  "status": "active",
  "current_substate": "1.2_problem_and_body",
  "body_question_count": 1,
  "completion_criteria": {
    "goal_established": true,
    "vision_created": true,
    "problem_identified": true,
    "body_awareness_present": false,
    "body_location_identified": false,
    "body_sensation_identified": false,
    "present_moment_focus": false,
    "pattern_understood": false,
    "rapport_established": false,
    "alpha_state_achieved": false,
    "ready_for_stage_2": false
  },
  "turn_count": 5,
  "created_at": "2025-10-14T12:34:56",
  "last_interaction": "2025-10-14T12:38:23"
}
```

**cURL Example:**

```bash
curl http://localhost:8000/api/v1/session/session_20251014_123456_a1b2c3d4/status
```

**Python Example:**

```python
import requests

session_id = "session_20251014_123456_a1b2c3d4"

response = requests.get(
    f"http://localhost:8000/api/v1/session/{session_id}/status"
)

status = response.json()
print(f"State: {status['current_substate']}")
print(f"Turns: {status['turn_count']}")
print(f"Completed: {sum(status['completion_criteria'].values())} / 11")
```

---

### 5. List All Sessions

**Endpoint:** `GET /api/v1/sessions`

**Description:** List all active sessions with metadata.

**Response:** `200 OK`

```json
{
  "total_sessions": 2,
  "sessions": [
    {
      "session_id": "session_20251014_123456_a1b2c3d4",
      "client_id": "client_123",
      "status": "active",
      "created_at": "2025-10-14T12:34:56",
      "last_interaction": "2025-10-14T12:38:23",
      "turn_count": 5
    },
    {
      "session_id": "session_20251014_130000_e5f6g7h8",
      "client_id": "client_456",
      "status": "completed",
      "created_at": "2025-10-14T13:00:00",
      "last_interaction": "2025-10-14T13:15:42",
      "turn_count": 18
    }
  ],
  "timestamp": "2025-10-14T13:20:00"
}
```

**cURL Example:**

```bash
curl http://localhost:8000/api/v1/sessions
```

---

### 6. Delete Session

**Endpoint:** `DELETE /api/v1/session/{session_id}`

**Description:** Delete a session and free resources.

**Path Parameters:**
- `session_id` (string, required): Session identifier

**Response:** `200 OK`

```json
{
  "message": "Session 'session_20251014_123456_a1b2c3d4' deleted successfully",
  "timestamp": "2025-10-14T13:30:00"
}
```

**cURL Example:**

```bash
curl -X DELETE http://localhost:8000/api/v1/session/session_20251014_123456_a1b2c3d4
```

---

## Complete Workflow Example

### Simplified Workflow (Recommended - No Session Creation Needed!)

```python
import requests

BASE_URL = "http://localhost:8090"

# Your external system provides unique session_id
session_id = "user_1234"  # Could be: CRM ID, user ID, device ID, etc.

# Just start talking! Session auto-creates on first input
conversation = [
    "I'm feeling really stressed and overwhelmed",
    "I want to feel calm and peaceful",
    "Yes, that makes sense",
    "I feel it in my chest",
    "It's tight and heavy",
    "Right now",
    "Nothing more",
    "Yes, I'm ready"
]

for i, user_input in enumerate(conversation, 1):
    print(f"Turn {i} - Client: {user_input}")

    response = requests.post(
        f"{BASE_URL}/api/v1/session/{session_id}/input",
        json={"user_input": user_input}
    )

    result = response.json()
    print(f"Turn {i} - Therapist: {result['therapist_response']}")
    print(f"         State: {result['session_progress']['current_substate']}\n")

# Check final status
status_response = requests.get(f"{BASE_URL}/api/v1/session/{session_id}/status")
status = status_response.json()
completed = sum(status['completion_criteria'].values())
print(f"✅ Session completed {completed}/11 criteria")
```

### Traditional Workflow (With Explicit Session Creation)

```python
import requests
import json

BASE_URL = "http://localhost:8090"

# Step 1: Create session
create_response = requests.post(
    f"{BASE_URL}/api/v1/session/create",
    json={"client_id": "test_client"}
)
session_id = create_response.json()["session_id"]
print(f"✅ Created session: {session_id}\n")

# Step 2: Conduct therapy conversation
conversation = [
    "I'm feeling really stressed and overwhelmed",
    "I want to feel calm and peaceful",
    "Yes, that makes sense",
    "I feel it in my chest",
    "It's tight and heavy",
    "Right now",
    "Nothing more",
    "Yes, I'm ready"
]

for i, user_input in enumerate(conversation, 1):
    print(f"Turn {i} - Client: {user_input}")

    response = requests.post(
        f"{BASE_URL}/api/v1/session/{session_id}/input",
        json={"user_input": user_input}
    )

    result = response.json()
    print(f"Turn {i} - Therapist: {result['therapist_response']}")
    print(f"         State: {result['session_progress']['current_substate']}")
    print(f"         Emotion: {result['preprocessing']['emotional_state']['primary_emotion']}\n")

# Step 3: Check final status
status_response = requests.get(
    f"{BASE_URL}/api/v1/session/{session_id}/status"
)
status = status_response.json()
completed = sum(status['completion_criteria'].values())
print(f"✅ Session completed {completed}/11 criteria")

# Step 4: Delete session
delete_response = requests.delete(
    f"{BASE_URL}/api/v1/session/{session_id}"
)
print(f"✅ {delete_response.json()['message']}")
```

---

## Error Responses

All endpoints return structured error responses:

### 404 Not Found

```json
{
  "error": "HTTPException",
  "message": "Session 'session_invalid' not found",
  "timestamp": "2025-10-14T12:34:56"
}
```

### 500 Internal Server Error

```json
{
  "error": "InternalServerError",
  "message": "Failed to process input: Ollama connection timeout",
  "timestamp": "2025-10-14T12:34:56"
}
```

---

## Data Models

### SessionProgress

```python
{
  "current_substate": str,           # Current TRT state (e.g., "1.1_goal_and_vision")
  "body_question_count": int,        # Number of body questions asked (MAX 3)
  "completion_criteria": {
    "goal_established": bool,
    "vision_created": bool,
    "problem_identified": bool,
    "body_awareness_present": bool,
    "body_location_identified": bool,
    "body_sensation_identified": bool,
    "present_moment_focus": bool,
    "pattern_understood": bool,
    "rapport_established": bool,
    "alpha_state_achieved": bool,
    "ready_for_stage_2": bool
  }
}
```

### EmotionalState

```python
{
  "categories": {
    "negative_high": ["overwhelmed", "panic"],
    "negative_moderate": ["stressed", "anxious"],
    "negative_low": ["sad", "tired"],
    "neutral": ["okay", "fine"],
    "positive": ["calm", "happy"]
  },
  "intensity": int,                  # 0-3 scale
  "primary_emotion": str             # Primary category
}
```

---

## Deployment

### Docker Compose (Production)

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
    restart: always

  trt-app:
    build: .
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WORKERS=4
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
    restart: always
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.1` | LLM model to use |
| `PYTHONUNBUFFERED` | `1` | Disable Python output buffering |

---

## Rate Limits

**Current Version:** No rate limiting

**Recommended for Production:**
- 10 requests/minute per session
- 100 sessions per client_id
- Implement using Redis + `slowapi`

---

## Monitoring

### Prometheus Metrics (Future)

```python
# Add to requirements.txt
prometheus-fastapi-instrumentator==6.1.0

# Add to main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

**Metrics endpoint:** `GET /metrics`

---

## Security Considerations

### Production Checklist

- [ ] Add API key authentication
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Enable CORS restrictions
- [ ] Add logging and monitoring
- [ ] Implement session timeouts
- [ ] Add data encryption at rest
- [ ] Regular security audits

---

## Troubleshooting

### Common Issues

**1. Ollama connection failed**

```bash
# Check Ollama is running
docker ps | grep ollama

# Check Ollama logs
docker logs trt-ollama

# Pull model if missing
docker exec -it trt-ollama ollama pull llama3.1
```

**2. RAG embeddings not found**

```bash
# Regenerate embeddings (from project root)
cd src/utils
python generate_rag_embeddings.py
```

**3. Session not found**

Sessions are stored in-memory. They will be lost on restart. For persistence, integrate Redis or PostgreSQL.

---

## API Changelog

### v1.0.0 (2025-10-14)
- Initial release
- Session management endpoints
- Complete TRT Stage 1 implementation
- Docker containerization
- Comprehensive error handling

---

## Support

**Documentation:** `/docs` (Swagger UI)
**ReDoc:** `/redoc`
**GitHub Issues:** [Repository URL]
**Email:** [Your Contact]

---

**Last Updated:** 2025-10-14
**API Version:** 1.0.0
**Status:** ✅ Production Ready
