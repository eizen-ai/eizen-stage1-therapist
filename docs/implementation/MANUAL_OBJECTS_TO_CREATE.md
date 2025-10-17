# Manual Object Creation Guide for Agentic Platform

**Purpose:** Add state-action tracking capabilities to existing AI Therapist application

**Application:** AI Therapist (existing)
**App Prefix:** AIT

---

## Record Types to Create (5 New)

Create these Record Types manually in the Agentic Platform UI under the existing "AI Therapist" application.

---

### 1. AIT_SessionState

**Purpose:** Track TRT therapy session progression and completion status

**Table Name:** `eza_ait_session_state`

**Fields:**

| Field Name | Field Type | Mandatory | Description |
|------------|------------|-----------|-------------|
| id | INT | No | Auto-increment primary key |
| session_id | STR | Yes | Unique session identifier |
| current_stage | STR | Yes | Current TRT stage (e.g., "stage_1_safety_building") |
| current_substate | STR | Yes | Current substate (e.g., "1.1_goal_and_vision", "1.2_problem_and_body") |
| goal_stated | STR | No | Boolean as string: "Y" or "N" |
| goal_content | STR | No | What the client's goal is |
| vision_accepted | STR | No | Boolean: "Y" or "N" |
| psycho_education_provided | STR | No | Boolean: "Y" or "N" |
| problem_identified | STR | No | Boolean: "Y" or "N" |
| problem_content | STR | No | Description of the problem |
| body_awareness_present | STR | No | Boolean: "Y" or "N" |
| present_moment_focus | STR | No | Boolean: "Y" or "N" |
| pattern_understood | STR | No | Boolean: "Y" or "N" |
| ready_for_stage_2 | STR | No | Boolean: "Y" or "N" |
| body_questions_asked | INT | No | Counter for body-related questions |
| body_location_provided | STR | No | Boolean: "Y" or "N" |
| body_sensation_described | STR | No | Boolean: "Y" or "N" |
| created_at | STR | No | Timestamp of session creation |
| updated_at | STR | No | Last update timestamp |
| is_active | STR | No | "Y" or "N" |

---

### 2. AIT_ConversationExchange

**Purpose:** Store turn-by-turn dialogue history

**Table Name:** `eza_ait_conversation_exchange`

**Fields:**

| Field Name | Field Type | Mandatory | Description |
|------------|------------|-----------|-------------|
| id | INT | No | Auto-increment primary key |
| session_id | STR | Yes | Links to AIT_SessionState |
| turn_number | INT | Yes | Conversation turn number (1, 2, 3...) |
| client_input | STR | Yes | What the client said |
| therapist_response | STR | Yes | What the therapist responded |
| substate | STR | No | Substate during this turn |
| navigation_decision | STR | No | Master agent's navigation decision |
| technique_used | STR | No | Therapeutic technique applied |
| timestamp | STR | No | When this exchange occurred |
| created_at | STR | No | Record creation timestamp |

---

### 3. AIT_StateActionPairs

**Purpose:** Capture state transitions for learning and optimization

**Table Name:** `eza_ait_state_action_pairs`

**Fields:**

| Field Name | Field Type | Mandatory | Description |
|------------|------------|-----------|-------------|
| id | INT | No | Auto-increment primary key |
| current_state | STR | Yes | Starting state (e.g., "1.1_goal_and_vision") |
| action_taken | STR | Yes | Action/decision made (e.g., "ask_clarifying_question") |
| next_state | STR | Yes | Resulting state after action |
| transition_rule | STR | No | Rule that triggered this transition |
| client_response_type | STR | No | Type of client response (e.g., "affirmation", "confusion") |
| success_count | INT | No | How many times this transition succeeded |
| total_count | INT | No | Total times this transition occurred |
| success_rate | STR | No | Calculated success rate (optional) |
| created_at | STR | No | First occurrence timestamp |
| updated_at | STR | No | Last occurrence timestamp |

---

### 4. AIT_CompletionEvents

**Purpose:** Track milestone events and completion criteria

**Table Name:** `eza_ait_completion_events`

**Fields:**

| Field Name | Field Type | Mandatory | Description |
|------------|------------|-----------|-------------|
| id | INT | No | Auto-increment primary key |
| session_id | STR | Yes | Links to AIT_SessionState |
| event_type | STR | Yes | Type of event (e.g., "goal_stated", "vision_accepted", "body_awareness_present", "problem_identified") |
| turn_number | INT | Yes | Turn when event occurred |
| client_input | STR | No | Client input that triggered the event |
| substate | STR | No | Substate when event occurred |
| timestamp | STR | No | When the event was recorded |

**Common Event Types:**
- `goal_stated` - Client stated their goal
- `vision_accepted` - Client accepted the vision
- `psycho_education_provided` - Psycho-education was given
- `problem_identified` - Problem was identified
- `body_awareness_present` - Body awareness established
- `present_moment_focus` - Present moment focus achieved
- `pattern_understood` - Pattern was understood
- `ready_for_stage_2` - Ready to advance to Stage 2
- `substate_advanced` - Advanced to next substate
- `stage_complete` - Stage completed

---

### 5. AIT_NavigationContext

**Purpose:** Log master agent navigation decisions and reasoning

**Table Name:** `eza_ait_navigation_context`

**Fields:**

| Field Name | Field Type | Mandatory | Description |
|------------|------------|-----------|-------------|
| id | INT | No | Auto-increment primary key |
| session_id | STR | Yes | Links to AIT_SessionState |
| turn_number | INT | Yes | Turn number |
| navigation_decision | STR | Yes | Decision made (e.g., "continue_exploration", "advance_to_1.2", "provide_psycho_education") |
| ready_to_advance | STR | No | Boolean: "Y" or "N" |
| next_substate | STR | No | Recommended next substate |
| reasoning | STR | No | Why this decision was made |
| completion_status | STR | No | JSON string with completion criteria status |
| timestamp | STR | No | When decision was made |

**Common Navigation Decisions:**
- `continue_exploration` - Stay in current state, explore more
- `provide_psycho_education` - Give psycho-education
- `advance_to_1.2` - Move to problem and body exploration
- `advance_to_3.1` - Move to alpha readiness
- `assess_readiness` - Check if ready to advance
- `start_alpha_sequence` - Begin alpha sequence
- `stage_complete` - Stage is complete

---

## Custom Data Types to Create (Optional Enhancements)

If you want to add structured data types for better API integration:

### AIT_SessionStateInput

**Purpose:** Input structure for creating/updating sessions

**Attributes:**

| Attribute Name | Type | Mandatory | Multiple |
|----------------|------|-----------|----------|
| session_id | STR | Yes | No |
| current_stage | STR | Yes | No |
| current_substate | STR | Yes | No |
| completion_status | ANY | No | No |

### AIT_SessionStateOutput

**Purpose:** Output structure for session queries

**Attributes:**

| Attribute Name | Type | Mandatory | Multiple |
|----------------|------|-----------|----------|
| session_id | STR | Yes | No |
| current_stage | STR | Yes | No |
| current_substate | STR | Yes | No |
| completion_status | ANY | No | No |
| ready_to_advance | STR | No | No |
| next_substate | STR | No | No |

### AIT_ConversationTurn

**Purpose:** Structure for a single conversation turn

**Attributes:**

| Attribute Name | Type | Mandatory | Multiple |
|----------------|------|-----------|----------|
| turn_number | INT | Yes | No |
| client_input | STR | Yes | No |
| therapist_response | STR | Yes | No |
| substate | STR | No | No |
| timestamp | STR | No | No |

---

## Web APIs to Create (Optional)

If you want to expose these new features via API:

### 1. Session State API

**API Name:** `AIT_GetSessionState`
**Method:** GET
**Relative Path:** `session-state/{session_id}`

**Purpose:** Retrieve current session state

**Body/Query Parameters:**
- `session_id` (STR, mandatory)

**Returns:** AIT_SessionStateOutput

---

### 2. Save Conversation Turn API

**API Name:** `AIT_SaveConversationTurn`
**Method:** POST
**Relative Path:** `conversation-turn`

**Purpose:** Save a conversation exchange

**Body:**
```json
{
  "session_id": "string",
  "turn_number": 1,
  "client_input": "string",
  "therapist_response": "string",
  "substate": "string"
}
```

---

### 3. Track State Transition API

**API Name:** `AIT_TrackStateTransition`
**Method:** POST
**Relative Path:** `state-transition`

**Purpose:** Log a state transition

**Body:**
```json
{
  "current_state": "string",
  "action_taken": "string",
  "next_state": "string",
  "transition_rule": "string"
}
```

---

### 4. Log Completion Event API

**API Name:** `AIT_LogCompletionEvent`
**Method:** POST
**Relative Path:** `completion-event`

**Purpose:** Record a milestone event

**Body:**
```json
{
  "session_id": "string",
  "event_type": "string",
  "turn_number": 1,
  "client_input": "string"
}
```

---

## Integration with Python Code

Your Python code in `src/core/session_state_manager.py` and `src/core/improved_ollama_system.py` can integrate with these tables via the platform's REST APIs.

### Example: Save Session State

```python
import requests

def save_session_state(session_state):
    """Save session state to platform"""

    data = {
        "session_id": session_state.session_id,
        "current_stage": session_state.current_stage,
        "current_substate": session_state.current_substate,
        "goal_stated": "Y" if session_state.stage_1_completion["goal_stated"] else "N",
        "goal_content": session_state.stage_1_completion["goal_content"],
        "vision_accepted": "Y" if session_state.stage_1_completion["vision_accepted"] else "N",
        "problem_identified": "Y" if session_state.stage_1_completion["problem_identified"] else "N",
        "body_awareness_present": "Y" if session_state.stage_1_completion["body_awareness_present"] else "N",
        "body_questions_asked": session_state.body_questions_asked,
        "updated_at": datetime.now().isoformat()
    }

    # Use platform API to save
    response = requests.post(
        "https://your-platform.eizen.ai/api/ait_session_state",
        json=data,
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )

    return response.json()
```

### Example: Save Conversation Turn

```python
def save_conversation_turn(session_id, turn_number, client_input, therapist_response, substate):
    """Save conversation exchange"""

    data = {
        "session_id": session_id,
        "turn_number": turn_number,
        "client_input": client_input,
        "therapist_response": therapist_response,
        "substate": substate,
        "timestamp": datetime.now().isoformat()
    }

    response = requests.post(
        "https://your-platform.eizen.ai/api/conversation-turn",
        json=data,
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )

    return response.json()
```

---

## Summary

**To implement state-action tracking, create these 5 Record Types manually:**

1. ✅ **AIT_SessionState** (19 fields) - Session tracking
2. ✅ **AIT_ConversationExchange** (10 fields) - Dialogue history
3. ✅ **AIT_StateActionPairs** (11 fields) - State transitions
4. ✅ **AIT_CompletionEvents** (7 fields) - Milestone tracking
5. ✅ **AIT_NavigationContext** (9 fields) - Navigation decisions

**Once created, you'll have:**
- Complete session persistence
- Turn-by-turn conversation tracking
- State transition learning capability
- Milestone event tracking
- Navigation decision logging

---

## Verification Checklist

After creating these objects, verify:

- [ ] All 5 Record Types created
- [ ] All fields added to each Record Type
- [ ] Database tables created (check in DB if you have access)
- [ ] Can insert test records via UI or API
- [ ] Python code can connect via API endpoints

---

**Questions? Need clarification on any field or structure? Let me know!**
