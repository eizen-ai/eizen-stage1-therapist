# Session ID in Request Body - Final Implementation

**Date:** 2025-10-15
**Status:** ✅ Implemented, Tested, and Deployed
**Version:** 3.0 (Final)

---

## 🎯 What This Is

**Single endpoint with session_id in request body:** The `/api/v1/input` endpoint accepts both `session_id` and `user_input` in the request body. First call creates the session AND processes input. Subsequent calls use the existing session.

---

## ✨ The Solution You Requested

### Your Request:
> "I don't want auto creation of ID when we give it without it in input endpoint. A session id should be there. It should not be given parameter. It should be part of request body besides input."

### What We Built:

**NEW Endpoint:** `POST /api/v1/input`

**Request Body:**
```json
{
  "session_id": "user_1234",
  "user_input": "I want to feel calm"
}
```

---

## 🚀 Complete Usage Example

### First Call (Creates Session + Processes Input)

```bash
curl -X POST http://localhost:8090/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_1234",
    "user_input": "I want to feel calm"
  }'
```

**What Happens:**
1. ✅ Session "user_1234" is created (first time)
2. ✅ Input "I want to feel calm" is processed
3. ✅ Therapist response returned
4. ✅ Session ready for next input

**Response:**
```json
{
  "therapist_response": "Got it. So you want to feel calm. I'm seeing you who's calm, at ease, lighter. Does that make sense to you?",
  "preprocessing": { ... },
  "navigation": { ... },
  "session_progress": {
    "current_substate": "1.1_goal_and_vision",
    "body_question_count": 0,
    "completion_criteria": { ... }
  },
  "timestamp": "2025-10-15T09:55:40.999178"
}
```

---

### Second Call (Uses Existing Session)

```bash
curl -X POST http://localhost:8090/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_1234",
    "user_input": "Yes that makes sense"
  }'
```

**What Happens:**
1. ✅ Uses existing session "user_1234"
2. ✅ Input "Yes that makes sense" is processed
3. ✅ Therapist response continues conversation
4. ✅ Turn count increments

---

## 📝 Request Schema

```json
{
  "session_id": "string (required)",
  "user_input": "string (required)"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | **Yes** | Your unique session identifier |
| `user_input` | string | **Yes** | Client's message/input |

---

## 💡 Integration Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8090"

# Your external system provides unique session_id
session_id = "user_1234"

# First message (creates session + processes)
response = requests.post(
    f"{BASE_URL}/api/v1/input",
    json={
        "session_id": session_id,
        "user_input": "I want to feel calm"
    }
)
result = response.json()
print(f"Therapist: {result['therapist_response']}")

# Continue conversation (uses existing session)
response = requests.post(
    f"{BASE_URL}/api/v1/input",
    json={
        "session_id": session_id,
        "user_input": "Yes that makes sense"
    }
)
result = response.json()
print(f"Therapist: {result['therapist_response']}")
```

---

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:8090";
const sessionId = "user_1234";

// First message (creates session + processes)
let response = await fetch(`${BASE_URL}/api/v1/input`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: sessionId,
    user_input: "I want to feel calm"
  })
});
let result = await response.json();
console.log(`Therapist: ${result.therapist_response}`);

// Continue conversation (uses existing session)
response = await fetch(`${BASE_URL}/api/v1/input`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: sessionId,
    user_input: "Yes that makes sense"
  })
});
result = await response.json();
console.log(`Therapist: ${result.therapist_response}`);
```

---

### cURL

```bash
# First message
curl -X POST http://localhost:8090/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user_1234", "user_input": "I want to feel calm"}'

# Second message
curl -X POST http://localhost:8090/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user_1234", "user_input": "Yes that makes sense"}'
```

---

## 🧪 Testing Results

All tests passed successfully:

### Test 1: First Input (Creates + Processes) ✅
```bash
curl -X POST http://localhost:8090/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{"session_id": "new_user_123", "user_input": "I want to feel calm"}'
```

**Result:**
- ✅ Session "new_user_123" created
- ✅ Input processed
- ✅ Therapist response: "Got it. So you want to feel calm..."
- ✅ Turn count: 1

### Test 2: Second Input (Uses Existing) ✅
```bash
curl -X POST http://localhost:8090/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{"session_id": "new_user_123", "user_input": "Yes that makes sense"}'
```

**Result:**
- ✅ Used existing session
- ✅ Input processed
- ✅ Therapist response: "Here's what's happening in the brain..."
- ✅ Turn count: 2

### Test 3: Session Verification ✅
```bash
curl http://localhost:8090/api/v1/sessions
```

**Result:**
```json
{
  "total_sessions": 1,
  "sessions": [
    {
      "session_id": "new_user_123",
      "status": "active",
      "turn_count": 2
    }
  ]
}
```

---

## 🔧 Implementation Details

### Modified Files

#### 1. `src/api/models.py`
Added `session_id` to `ClientInputRequest`:

```python
class ClientInputRequest(BaseModel):
    """Request to process client input in a session"""
    session_id: str = Field(..., description="Unique session identifier", min_length=1)
    user_input: str = Field(..., description="Client's text input", min_length=1)

    class Config:
        schema_extra = {
            "example": {
                "session_id": "user_1234",
                "user_input": "I'm feeling really stressed and overwhelmed"
            }
        }
```

#### 2. `src/api/main.py`
Created new endpoint `/api/v1/input`:

```python
@app.post("/api/v1/input", response_model=TherapistResponse, tags=["Session"])
async def process_input_with_session(request: ClientInputRequest):
    """
    Process client input and generate therapist response

    **Session ID in request body** - First call creates session + processes input
    """
    try:
        session_id = request.session_id

        # Create session if it doesn't exist (first call)
        if session_id not in active_sessions:
            # Initialize therapy system
            therapy_system = ImprovedOllamaTherapySystem()
            session_state = therapy_system.create_session(session_id)

            # Store session data
            active_sessions[session_id] = {
                "session_id": session_id,
                "therapy_system": therapy_system,
                "session_state": session_state,
                "created_at": datetime.now(),
                "turn_count": 0,
                "status": "active"
            }

        # Process input
        session = active_sessions[session_id]
        result = therapy_system.process_client_input(request.user_input, session_state)

        # Update turn count
        session["turn_count"] += 1

        return response
```

---

## ✅ Key Features

### 1. Session ID in Body
- ✅ `session_id` is in request body (not URL path)
- ✅ Required field (must be provided)
- ✅ You control the unique identifier

### 2. First Call Creates Session
- ✅ Automatically creates session if doesn't exist
- ✅ Processes input in same call
- ✅ Returns therapist response immediately

### 3. Subsequent Calls Use Existing
- ✅ Finds existing session by session_id
- ✅ Continues conversation
- ✅ Maintains state and progress

### 4. Simple Integration
- ✅ Single endpoint: `/api/v1/input`
- ✅ Same request format every time
- ✅ No need to call separate /create endpoint

---

## 🔒 Your Responsibilities

As the external system, you are responsible for:

1. **Uniqueness:** Ensure each `session_id` is unique per conversation
2. **Format:** Use any string format that works for you
3. **Tracking:** Remember which session_id belongs to which user
4. **Cleanup:** Delete sessions when done (optional)

---

## 📊 Comparison: Old vs New

| Feature | Old (Path-based) | New (Body-based) |
|---------|------------------|------------------|
| **Endpoint** | `/api/v1/session/{id}/input` | `/api/v1/input` |
| **session_id** | URL path parameter | Request body field |
| **user_input** | Request body | Request body |
| **Request** | Path + Body | Body only |
| **Simplicity** | Medium | High |

### Old Way (Still Available)
```bash
curl -X POST http://localhost:8090/api/v1/session/user_1234/input \
  -d '{"user_input": "Hello"}'
```

### New Way (Recommended)
```bash
curl -X POST http://localhost:8090/api/v1/input \
  -d '{"session_id": "user_1234", "user_input": "Hello"}'
```

---

## 🚀 Deployment Status

- ✅ Deployed to Docker (port 8090)
- ✅ System healthy (Ollama connected, RAG ready)
- ✅ All tests passed
- ✅ Production ready

---

## 📚 Available Endpoints

### NEW: `/api/v1/input` (Recommended)
- **Method:** POST
- **Body:** `{"session_id": "...", "user_input": "..."}`
- **Creates:** Session on first call
- **Uses:** Existing session on subsequent calls

### OLD: `/api/v1/session/{session_id}/input` (Still Available)
- **Method:** POST
- **Path:** session_id in URL
- **Body:** `{"user_input": "..."}`
- **Works:** Same way (backward compatible)

### Optional: `/api/v1/session/create`
- **Method:** POST
- **Body:** `{"session_id": "..."}`
- **Note:** Not needed with new `/input` endpoint

---

## 🎯 Summary

| Feature | Status | Notes |
|---------|--------|-------|
| session_id in body | ✅ Implemented | Required field in request |
| First call creates | ✅ Working | Session + input processing |
| Subsequent calls continue | ✅ Working | Uses existing session |
| No separate /create | ✅ Not needed | /input does everything |
| Documentation | ✅ Complete | This document |
| Testing | ✅ Passed | All scenarios verified |
| Deployment | ✅ Live | Port 8090 |

---

## 🎉 Final Result

**Exactly what you asked for:**
1. ✅ `session_id` is in the request body (not URL parameter)
2. ✅ `session_id` is required (not optional)
3. ✅ First call creates session AND processes input
4. ✅ Subsequent calls use existing session
5. ✅ Single endpoint for everything: `/api/v1/input`

---

**Last Updated:** 2025-10-15 09:56:00
**Status:** ✅ Production Ready
**Version:** 3.0 (Final)
