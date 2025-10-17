# Custom Session ID Guide

**Feature:** Allow external systems to assign their own session IDs
**Status:** ✅ Implemented and tested
**Version:** 1.0
**Date:** 2025-10-15

---

## 🎯 Overview

The TRT Therapy API now supports **both auto-generated and custom session IDs**, making it easy to integrate with external systems that need to maintain their own session tracking.

### Why This Matters

**Before:** Systems had to store the mapping between their IDs and auto-generated session IDs
```
External System ID → API Session ID mapping needed
user_12345 → session_20251015_083406_0432b008 (stored in database)
```

**After:** Systems can use their own IDs directly
```
External System ID = API Session ID (no mapping needed!)
user_12345 → user_12345 (direct usage)
```

---

## 🚀 Usage

### Option 1: Auto-Generated Session ID (Default)

**Request:**
```bash
curl -X POST http://localhost:8090/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "session_id": "session_20251015_083406_0432b008",
  "created_at": "2025-10-15T08:34:11.753923",
  "status": "active",
  "message": "Session created successfully. Ready to begin therapy."
}
```

**Format:** `session_YYYYMMDD_HHMMSS_UUID`
- Timestamp-based
- Guaranteed unique
- Sortable chronologically

---

### Option 2: Custom Session ID (New!)

**Request:**
```bash
curl -X POST http://localhost:8090/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_custom_session_001",
    "client_id": "external_client_123",
    "metadata": {
      "platform": "mobile_app",
      "external_id": "crm_123456"
    }
  }'
```

**Response:**
```json
{
  "session_id": "my_custom_session_001",
  "created_at": "2025-10-15T08:34:15.093155",
  "status": "active",
  "message": "Session created successfully. Ready to begin therapy."
}
```

**Your session ID is used as-is!**

---

## 📋 Request Schema

```json
{
  "session_id": "string (optional)",
  "client_id": "string (optional)",
  "metadata": {
    "key": "value"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | No | Custom session ID. If omitted, auto-generated |
| `client_id` | string | No | Client identifier for tracking |
| `metadata` | object | No | Additional custom metadata |

---

## ✅ Validation Rules

### Custom Session ID Rules

1. **Must be unique** - Cannot reuse existing session ID
2. **Any format allowed** - Use your own naming convention
3. **Case-sensitive** - `Session_001` ≠ `session_001`
4. **No length limit** - Use what makes sense for your system

### Duplicate Detection

**Attempting to create duplicate:**
```bash
curl -X POST http://localhost:8090/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my_custom_session_001"}'
```

**Error Response (409 Conflict):**
```json
{
  "error": "HTTPException",
  "message": "Session ID 'my_custom_session_001' already exists. Please use a different ID or omit it for auto-generation.",
  "timestamp": "2025-10-15T08:34:15.120207"
}
```

---

## 💡 Integration Examples

### Example 1: CRM Integration

Use CRM user IDs directly:

```python
import requests

def create_therapy_session(crm_user_id, user_name):
    """Create therapy session using CRM user ID"""
    response = requests.post(
        "http://localhost:8090/api/v1/session/create",
        json={
            "session_id": f"crm_user_{crm_user_id}",
            "client_id": crm_user_id,
            "metadata": {
                "user_name": user_name,
                "platform": "crm",
                "created_from": "customer_portal"
            }
        }
    )
    return response.json()

# Usage
session = create_therapy_session("12345", "John Doe")
print(f"Session created: {session['session_id']}")

# Later, send input using your CRM ID
requests.post(
    f"http://localhost:8090/api/v1/session/crm_user_12345/input",
    json={"user_input": "I want to feel calm"}
)
```

---

### Example 2: Mobile App Integration

Use device/user combination:

```javascript
// JavaScript/React Native
async function createSession(userId, deviceId) {
  const sessionId = `mobile_${userId}_${deviceId}`;

  const response = await fetch('http://localhost:8090/api/v1/session/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      session_id: sessionId,
      client_id: userId,
      metadata: {
        platform: 'mobile_app',
        device_id: deviceId,
        app_version: '2.1.0'
      }
    })
  });

  return await response.json();
}

// Usage
const session = await createSession('user_456', 'device_abc');
console.log('Session:', session.session_id); // mobile_user_456_device_abc
```

---

### Example 3: Multi-Platform Integration

Track sessions across platforms:

```python
import requests
from datetime import datetime

class TherapySessionManager:
    def __init__(self, api_url="http://localhost:8090"):
        self.api_url = api_url

    def create_session(self, user_id, platform, **metadata):
        """Create session with platform-specific ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{platform}_{user_id}_{timestamp}"

        response = requests.post(
            f"{self.api_url}/api/v1/session/create",
            json={
                "session_id": session_id,
                "client_id": user_id,
                "metadata": {
                    "platform": platform,
                    "timestamp": timestamp,
                    **metadata
                }
            }
        )
        return response.json()

    def send_message(self, session_id, user_input):
        """Send message to existing session"""
        response = requests.post(
            f"{self.api_url}/api/v1/session/{session_id}/input",
            json={"user_input": user_input}
        )
        return response.json()

# Usage
manager = TherapySessionManager()

# Web session
web_session = manager.create_session(
    "user_789",
    "web",
    browser="chrome",
    ip="192.168.1.1"
)

# Mobile session for same user
mobile_session = manager.create_session(
    "user_789",
    "mobile",
    device="iPhone",
    os_version="iOS 17"
)

print(web_session['session_id'])     # web_user_789_20251015_083406
print(mobile_session['session_id'])  # mobile_user_789_20251015_083410
```

---

### Example 4: Webhook Integration

Handle webhooks from external services:

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook/therapy/start', methods=['POST'])
def start_therapy_session():
    """Handle webhook to start therapy session"""
    data = request.json
    external_id = data.get('external_id')
    user_info = data.get('user_info', {})

    # Create session using external system's ID
    session_response = requests.post(
        'http://localhost:8090/api/v1/session/create',
        json={
            "session_id": f"webhook_{external_id}",
            "client_id": user_info.get('user_id'),
            "metadata": {
                "source": "webhook",
                "external_system": data.get('system_name'),
                "webhook_timestamp": data.get('timestamp'),
                **user_info
            }
        }
    )

    if session_response.status_code == 200:
        return jsonify({
            "success": True,
            "session_id": f"webhook_{external_id}",
            "message": "Therapy session created"
        })
    else:
        return jsonify({
            "success": False,
            "error": session_response.json()
        }), 400
```

---

## 🔒 Best Practices

### 1. **Use Meaningful IDs**
```python
# Good
session_id = "crm_user_12345"
session_id = "mobile_app_user_456_device_abc"
session_id = "web_session_789_20251015"

# Avoid (but technically valid)
session_id = "x"
session_id = "123"
session_id = "temp"
```

### 2. **Include Context in ID**
```python
# Include platform/source
f"{platform}_{user_id}"

# Include timestamp for uniqueness
f"{platform}_{user_id}_{timestamp}"

# Include environment
f"{env}_{platform}_{user_id}"  # prod_web_12345
```

### 3. **Handle Duplicates Gracefully**
```python
def create_session_with_retry(base_id, max_retries=3):
    """Try creating session with fallback IDs"""
    for i in range(max_retries):
        session_id = f"{base_id}_{i}" if i > 0 else base_id

        response = requests.post(
            "http://localhost:8090/api/v1/session/create",
            json={"session_id": session_id}
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code != 409:  # Not duplicate error
            raise Exception(f"Failed: {response.text}")

    # All retries failed, use auto-generated
    response = requests.post(
        "http://localhost:8090/api/v1/session/create",
        json={}  # Omit session_id for auto-generation
    )
    return response.json()
```

### 4. **Validate Before Sending**
```python
def validate_session_id(session_id):
    """Validate session ID before sending"""
    if not session_id:
        raise ValueError("Session ID cannot be empty")

    if len(session_id) > 255:
        raise ValueError("Session ID too long")

    # Check for valid characters (optional)
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise ValueError("Invalid characters in session ID")

    return True

# Usage
session_id = "my_custom_session_001"
validate_session_id(session_id)
```

---

## 📊 Comparison: Auto vs Custom

| Feature | Auto-Generated | Custom |
|---------|---------------|--------|
| **Format** | `session_YYYYMMDD_HHMMSS_UUID` | Any string |
| **Uniqueness** | Guaranteed | You ensure |
| **Sortable** | Yes (by timestamp) | Depends on your format |
| **Integration** | Need ID mapping | Direct usage |
| **Collision Risk** | None | Possible (checked) |
| **Use Case** | Standalone usage | System integration |

---

## 🧪 Testing

### Test Auto-Generated ID
```bash
curl -X POST http://localhost:8090/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test Custom ID
```bash
curl -X POST http://localhost:8090/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_custom_001"}'
```

### Test Duplicate (Should Fail)
```bash
curl -X POST http://localhost:8090/api/v1/session/create \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_custom_001"}'
```

### Use Custom Session
```bash
curl -X POST http://localhost:8090/api/v1/session/test_custom_001/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I want to feel calm"}'
```

---

## 🔄 Migration Guide

### If You're Already Using Auto-Generated IDs

**No changes needed!** The auto-generation still works exactly the same way.

```python
# Still works!
response = requests.post(
    "http://localhost:8090/api/v1/session/create",
    json={}
)
```

### If You Want to Switch to Custom IDs

```python
# Old way (with mapping)
response = requests.post(
    "http://localhost:8090/api/v1/session/create",
    json={}
)
api_session_id = response.json()['session_id']

# Store mapping in your database
db.save_mapping(my_user_id, api_session_id)

# New way (direct usage)
response = requests.post(
    "http://localhost:8090/api/v1/session/create",
    json={"session_id": f"user_{my_user_id}"}
)
# No mapping needed! Just use user_{my_user_id} directly
```

---

## 📚 Related Documentation

- **API Documentation:** `docs/development/API_DOCUMENTATION.md`
- **Quick Start:** `docs/deployment/QUICK_START.md`
- **Integration Examples:** `examples/agentic_workflow.py`

---

## ✅ Summary

**What Changed:**
- ✅ `session_id` field added to `SessionCreateRequest` (optional)
- ✅ Duplicate detection added (returns 409 Conflict)
- ✅ Auto-generation still works (when field is omitted)
- ✅ Fully backward compatible

**Benefits:**
- 🎯 Easy integration with external systems
- 🔗 No need for ID mapping tables
- 📊 Use your own naming conventions
- ✨ Simplified architecture

**Status:** Production ready and tested! ✅

---

**Last Updated:** 2025-10-15
**Version:** 1.0.0
