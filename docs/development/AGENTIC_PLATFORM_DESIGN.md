# AI Therapist Enhanced - Agentic Platform Design

## Overview

This document maps our new FastAPI-based TRT AI Therapist system to the Eizen Agentic Platform structure, combining:
- Existing agentic platform advantages (processes, integrations, metadata management)
- New state-action based Master Agent + Dialogue Agent system (FastAPI at localhost:8090)

---

## Design Objects Mapping

### 1. Application (app.json)

**Application Name:** AI Therapist Enhanced
**Application Prefix:** AITE
**Description:** Advanced Trauma Resiliency Training (TRT) AI Therapist with state-action based Master and Dialogue agents, integrated via FastAPI

---

### 2. Connected Systems (cs.json)

We'll create a new Connected System pointing to our FastAPI service:

```json
{
  "csNm": "AITE_FastAPI_Core",
  "baseUrl": "http://localhost:8090",
  "auth": { "authCd": "NO_AUTH" }
}
```

We'll also keep relevant Connected Systems from the original:
- AIT_Mongo_Service_Cs (for data persistence)
- AIT_kafka_cs (for event streaming)
- AIT_Open_AI_Cs (optional - for fallback)

---

### 3. Custom Data Types (cdt.json)

Map our Pydantic models to CDTs:

#### AITE_SessionCreateRequest
- client_id (STR, optional)
- metadata (ANY, optional)

#### AITE_SessionCreateResponse
- session_id (STR)
- created_at (DATE_TIME)
- status (STR)
- message (STR)

#### AITE_ClientInputRequest
- user_input (STR, mandatory)

#### AITE_EmotionalState
- categories (ANY)
- intensity (INT)
- primary_emotion (STR)

#### AITE_SafetyChecks
- self_harm_detected (ANY)
- thinking_mode_detected (ANY)
- past_tense_detected (ANY)
- i_dont_know_detected (ANY)

#### AITE_PreprocessingResult
- original_input (STR)
- cleaned_input (STR)
- corrected_input (STR)
- emotional_state (AITE_EmotionalState)
- input_category (STR)
- spelling_corrections (ANY)
- safety_checks (AITE_SafetyChecks)

#### AITE_NavigationDecision
- decision (STR)
- next_state (STR, optional)
- rag_query (STR, optional)
- reasoning (STR, optional)

#### AITE_SessionProgress
- current_substate (STR)
- body_question_count (INT)
- completion_criteria (ANY)

#### AITE_TherapistResponse
- therapist_response (STR)
- preprocessing (AITE_PreprocessingResult)
- navigation (AITE_NavigationDecision)
- session_progress (AITE_SessionProgress)
- timestamp (DATE_TIME)

#### AITE_SessionStatusResponse
- session_id (STR)
- status (STR)
- current_substate (STR)
- body_question_count (INT)
- completion_criteria (ANY)
- turn_count (INT)
- created_at (DATE_TIME)
- last_interaction (DATE_TIME)

---

### 4. Integrations (intg.json)

Create integrations for FastAPI endpoints:

#### AITE_CreateSession_Integration
- Connected System: AITE_FastAPI_Core
- Method: POST
- Path: /api/v1/session/create
- Request Body: AITE_SessionCreateRequest
- Response: AITE_SessionCreateResponse

#### AITE_ProcessInput_Integration
- Connected System: AITE_FastAPI_Core
- Method: POST
- Path: /api/v1/session/{sessionId}/input
- Request Body: AITE_ClientInputRequest
- Response: AITE_TherapistResponse

#### AITE_GetSessionStatus_Integration
- Connected System: AITE_FastAPI_Core
- Method: GET
- Path: /api/v1/session/{sessionId}/status
- Response: AITE_SessionStatusResponse

#### AITE_DeleteSession_Integration
- Connected System: AITE_FastAPI_Core
- Method: DELETE
- Path: /api/v1/session/{sessionId}

#### AITE_ListSessions_Integration
- Connected System: AITE_FastAPI_Core
- Method: GET
- Path: /api/v1/sessions

#### AITE_HealthCheck_Integration
- Connected System: AITE_FastAPI_Core
- Method: GET
- Path: /health

---

### 5. Processes (processDetails.json)

#### Main Process: AITE_TherapyMainWorkflow

**Purpose:** Orchestrates the complete therapy session workflow

**Process Variables:**
- sessionId (STR, param)
- customerId (STR, param)
- userInput (STR, param)
- therapistResponse (AITE_TherapistResponse)
- sessionStatus (AITE_SessionStatusResponse)
- createSessionResponse (AITE_SessionCreateResponse)

**Process Flow:**
1. **Start Node** → Check if sessionId exists
2. **XOR Gateway** → Session exists?
   - No → Call AITE_CreateSession_Integration
   - Yes → Proceed
3. **Integration Node** → Call AITE_ProcessInput_Integration (with userInput)
4. **Script Node** → Extract and format response
5. **Integration Node** → Call AITE_GetSessionStatus_Integration
6. **Script Node** → Update MongoDB (via AIT_Mongo_Service_Cs)
7. **XOR Gateway** → Session complete?
   - No → End (return response)
   - Yes → Call cleanup process
8. **End Node** → Return therapist response

#### Supporting Process: AITE_SessionManagement

**Purpose:** Create, monitor, and cleanup sessions

**Process Variables:**
- action (STR, param) - "create", "status", "delete", "list"
- sessionId (STR, optional param)
- response (ANY)

**Process Flow:**
1. **Start Node**
2. **XOR Gateway** → Route based on action
   - create → Call AITE_CreateSession_Integration
   - status → Call AITE_GetSessionStatus_Integration
   - delete → Call AITE_DeleteSession_Integration
   - list → Call AITE_ListSessions_Integration
3. **End Node** → Return response

#### Supporting Process: AITE_OnboardingWorkflow

**Purpose:** Enhanced onboarding with face registration

**Process Variables:**
- name (STR, param)
- age (INT, param)
- language (STR, param)
- country (STR, param)
- currentLocation (STR, param)
- processInput (B64, param) - face image
- sessionId (STR)

**Process Flow:**
1. **Start Node**
2. **Script Node** → Validate onboarding data
3. **Integration Node** → Face registration (if provided)
4. **Integration Node** → Create session via AITE_CreateSession_Integration
5. **Integration Node** → Store user data in MongoDB
6. **Script Node** → Format welcome message
7. **End Node** → Return sessionId and welcome message

---

### 6. Web APIs (webApiDetails.json)

#### AITE_TherapyWebAPI
- **Method:** POST
- **Path:** /AITherapistEnhanced
- **Description:** Main therapy endpoint using new FastAPI system
- **Request Body:**
  - question (STR)
  - sessionId (STR)
  - custId (STR)
- **Groovy Code:**
```groovy
def result = process.start(
    processModels = "<AITE_TherapyMainWorkflow_UUID>",
    processParameters = [
        userInput: request.body.question,
        sessionId: request.body.sessionId,
        customerId: request.body.custId
    ]
)

return [
    patientText: request.body.question,
    agentText: result.pvs.therapistResponse.therapist_response,
    preprocessing: result.pvs.therapistResponse.preprocessing,
    navigation: result.pvs.therapistResponse.navigation,
    sessionProgress: result.pvs.therapistResponse.session_progress
]
```

#### AITE_OnboardingWebAPI
- **Method:** POST
- **Path:** /OnboardingEnhanced
- **Request Body:**
  - name (STR)
  - age (INT)
  - language (STR)
  - country (STR)
  - currentLocation (STR)
  - faceImage (B64, optional)
- **Groovy Code:**
```groovy
def result = process.start(
    processModels = "<AITE_OnboardingWorkflow_UUID>",
    processParameters = [
        name: request.body.name,
        age: request.body.age,
        language: request.body.language,
        country: request.body.country,
        currentLocation: request.body.currentLocation,
        processInput: request.body.faceImage
    ]
)

return result.pvs
```

#### AITE_SessionManagementWebAPI
- **Method:** POST
- **Path:** /SessionManagement
- **Request Body:**
  - action (STR) - "create", "status", "delete", "list"
  - sessionId (STR, optional)
- **Groovy Code:**
```groovy
def result = process.start(
    processModels = "<AITE_SessionManagement_UUID>",
    processParameters = [
        action: request.body.action,
        sessionId: request.body.sessionId
    ]
)

return result.pvs.response
```

#### AITE_HealthCheckWebAPI
- **Method:** GET
- **Path:** /HealthCheck
- **Groovy Code:**
```groovy
def integrationOutput = integration.call(
    integrations = "<AITE_HealthCheck_Integration_UUID>",
    integrationParameters = [:]
)

return integrationOutput
```

---

### 7. Rules (ruleDetails.json)

#### AITE_SessionValidation_Rule
- Validates session data before processing
- Checks: sessionId format, userInput not empty, customerId exists

#### AITE_SafetyCheck_Rule
- Evaluates safety flags from preprocessing
- Triggers escalation if self-harm detected

#### AITE_StageCompletion_Rule
- Evaluates stage 1 completion criteria
- Returns boolean: ready_for_stage_2

---

### 8. Record Types (rtDetails.json)

#### AITE_SessionRecord
- Stores session metadata in database
- Fields:
  - sessionId (PRIMARY KEY)
  - customerId
  - status
  - createdAt
  - lastInteraction
  - turnCount
  - completionCriteria

#### AITE_InteractionRecord
- Stores each therapy interaction
- Fields:
  - interactionId (PRIMARY KEY)
  - sessionId (FOREIGN KEY)
  - turnNumber
  - patientText
  - agentText
  - preprocessing
  - navigation
  - timestamp

---

## Key Advantages of This Design

### From Original AI Therapist:
1. ✅ **Metadata Management** - Kafka events, MongoDB persistence
2. ✅ **Process Orchestration** - Complex workflows with XOR gateways
3. ✅ **Integration Hub** - Metaphors, NoHarm, Face Auth services
4. ✅ **Business Rules** - Validation, safety checks, completion logic
5. ✅ **Record Keeping** - Structured data storage

### From New FastAPI System:
1. ✅ **Master Planning Agent** - State-action based therapeutic navigation
2. ✅ **Dialogue Agent** - Dr. Q methodology with RAG
3. ✅ **Session State Manager** - 31-state CSV machine
4. ✅ **Input Preprocessing** - Emotion detection, safety checks
5. ✅ **REST API** - Standard HTTP interface for external integrations
6. ✅ **Containerization** - Docker deployment with all dependencies

---

## Deployment Strategy

### 1. FastAPI Service (Existing - Port 8090)
```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2
docker-compose up -d
```

### 2. Agentic Platform (New Export)
1. Import `Enhanced_AI_Therapist_export/` folder
2. Update Connected System `AITE_FastAPI_Core` baseUrl if needed
3. Publish all processes
4. Test Web APIs via platform interface

### 3. Integration Testing
- Test onboarding flow
- Test therapy session flow
- Verify MongoDB persistence
- Check Kafka event streaming

---

## Migration Path

For users transitioning from old AI Therapist:

1. **Keep existing APIs** - No breaking changes
2. **Add new endpoints** - `/AITherapistEnhanced`, `/OnboardingEnhanced`
3. **Gradual migration** - Test new system in parallel
4. **Data compatibility** - Both systems can share MongoDB

---

## Next Steps

1. ✅ Generate all 8 JSON files
2. ✅ Create UUIDs for all objects
3. ✅ Package into `Enhanced_AI_Therapist_export/` folder
4. ✅ Validate JSON structure
5. ✅ Test import on agentic platform
