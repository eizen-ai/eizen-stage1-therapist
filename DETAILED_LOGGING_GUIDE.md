# Detailed Logging Guide for TRT AI Therapist

## Overview

The TRT AI Therapist now includes comprehensive detailed logging that shows:
- **API endpoint inputs and outputs**
- **Complete processing flow** (preprocessing → navigation → dialogue → session update)
- **Decision points** and reasoning at every step
- **LLM calls** with prompts and responses
- **State transitions** and rule applications
- **Processing times** and performance metrics

## Viewing Logs

### Real-time Logs (Recommended)

```bash
docker logs -f trt-app
```

This shows logs in real-time as requests are processed.

### Last N Lines

```bash
docker logs --tail 100 trt-app
```

Shows the last 100 log lines.

### Since Timestamp

```bash
docker logs --since 10m trt-app
```

Shows logs from the last 10 minutes.

### Save to File

```bash
docker logs trt-app > logs.txt 2>&1
```

Saves all logs to a file for analysis.

---

## Log Structure

Each request generates logs in this order:

### 1. **ENDPOINT INPUT** 📥
```
====================================================================================================
📥 ENDPOINT INPUT: /api/v1/input
====================================================================================================
Session ID: test_session_123
User Input: 'I want to feel more calm'
----------------------------------------------------------------------------------------------------
```

**What you see:**
- Which endpoint received the request
- Session ID
- Raw user input
- Any additional request metadata

---

### 2. **STEP 1: INPUT PREPROCESSING** 🔄

```
🔄 STEP 1: INPUT PREPROCESSING
   Original Input: 'I want to feel more calm'
   ✓ Cleaned Input: 'I want to feel more calm'
   ✓ Corrected Input: 'I want to feel more calm'
   ✓ Emotional State: {'detected_emotions': ['calm'], 'valence': 'positive'}
   ✓ Input Category: goal_statement
```

**What you see:**
- Original vs cleaned vs spell-corrected input
- Detected emotional state
- Input categorization (goal_statement, body_awareness, problem_mention, etc.)
- **Safety checks** (self-harm, thinking mode, past tense)

**Decision Point:** If self-harm is detected, it's shown here with ⚠️ warning

---

### 3. **STEP 2: NAVIGATION DECISION** 🧭

```
🧭 STEP 2: NAVIGATION DECISION (Master Planning Agent)
   Current Stage: stage_1_safety_building
   Current Substate: 1.1_goal_and_vision
   Completion Status:
      ✗ goal_stated: False
      ✗ vision_accepted: False
      ✗ problem_identified: False
      ✗ body_awareness_present: False
      ✗ present_moment_focus: False

   📏 RULE APPLIED: RULE 1: Goal Clarification Required
      Condition: In substate 1.1_goal_and_vision AND goal not stated AND early session
      Action: Navigate to clarify_goal

   📍 Navigation Decision: clarify_goal
   📊 Situation Type: goal_needs_clarification
   🎯 RAG Query: dr_q_goal_clarification
   💡 Reasoning: STRICT RULE: Must establish goal first
```

**What you see:**
- Current therapy stage and substate
- Completion criteria status (✓ completed, ✗ not completed)
- **Rule applications** (when strict rules override LLM)
- **LLM reasoning** (when LLM makes the decision)
- Navigation decision (what therapeutic technique to use)
- RAG query (what examples to retrieve)
- Detailed reasoning

**Decision Points:**
- Rule-based overrides (marked with 📏)
- LLM confidence scores (when LLM is used)

---

### 4. **STEP 3: DIALOGUE GENERATION** 💬

```
💬 STEP 3: DIALOGUE GENERATION (Dialogue Agent)
   Decision to Implement: clarify_goal
   📚 RAG Examples Retrieved: 3

   🤖 LLM Call: Dialogue Generation
      Model: llama3.1
      Prompt Preview: You are Dr. Q, a master TRT therapist. Generate ONE short therapeutic response...

   ✓ LLM Response Preview: So what do you want our time to focus on today? What do we want to get better for you?
   ✓ Confidence: 0.95

   ✓ Generated Response: 'So what do you want our time to focus on today? What do we want to get better for you?'
   ✓ LLM Confidence: 0.95
```

**What you see:**
- Which therapeutic technique is being applied
- How many RAG examples were retrieved
- **LLM calls** with prompt previews
- **LLM responses** with previews
- Confidence scores
- Final generated therapist response
- Technique used

**Decision Points:**
- 🔀 Decision Point markers (e.g., "PRIORITY 1: Self-Harm Detection")
- 🎭 Therapeutic techniques (e.g., "affirmation_and_proceed", "thinking_mode_redirect")

---

### 5. **STEP 4: SESSION STATE UPDATE** 💾

```
💾 STEP 4: SESSION STATE UPDATE
   Updated Substate: 1.1_goal_and_vision
   Body Questions Asked: 0
   Conversation Turns: 1
```

**What you see:**
- Updated substate after processing
- Body question count (tracks therapy progression)
- Number of conversation turns

---

### 6. **STATE TRANSITIONS** 🔄

```
🔄 State Transition: 1.2_problem_and_body → 3.1_assess_readiness
   Trigger: Body question limit reached (3/3)
```

**What you see:**
- When the system moves between therapy substates
- What triggered the transition

---

### 7. **PROCESSING SUMMARY** ⏱️

```
⏱️  PROCESSING SUMMARY
   Session ID: test_session_123
   Total Processing Time: 1.234s
```

**What you see:**
- Session identifier
- Total time taken to process the request

---

### 8. **ENDPOINT OUTPUT** 📤

```
----------------------------------------------------------------------------------------------------
📤 ENDPOINT OUTPUT: /api/v1/input
Session ID: test_session_123
Therapist Response: 'So what do you want our time to focus on today?'
Metadata: {
  "current_substate": "1.1_goal_and_vision",
  "navigation_decision": "clarify_goal",
  "processing_time": 1.234
}
====================================================================================================
```

**What you see:**
- Final therapist response sent to client
- Current therapy substate
- Navigation decision made
- Processing time

---

## Log Symbols Guide

| Symbol | Meaning |
|--------|---------|
| 📥 | Endpoint input received |
| 📤 | Endpoint output sent |
| 🔄 | Processing step or state transition |
| 🧭 | Navigation decision |
| 💬 | Dialogue generation |
| 💾 | Session state update |
| ⏱️ | Processing time/summary |
| 📏 | Rule-based decision |
| 🤖 | LLM call/reasoning |
| 📚 | RAG retrieval |
| 🎯 | RAG query |
| 📍 | Navigation decision |
| 📊 | Situation type |
| 💡 | Reasoning |
| ✓ | Success/Completed |
| ✗ | Not completed |
| ⚠️ | Warning (safety checks) |
| 🔀 | Decision point |
| 🎭 | Therapeutic technique |
| ❌ | Error |

---

## Example Log Flow

Here's a complete example of a single request:

```
====================================================================================================
📥 ENDPOINT INPUT: /api/v1/input
====================================================================================================
Session ID: session_20251021_130045
User Input: 'I feel stressed about school'
----------------------------------------------------------------------------------------------------

🔄 STEP 1: INPUT PREPROCESSING
   Original Input: 'I feel stressed about school'
   ✓ Cleaned Input: 'I feel stressed about school'
   ✓ Corrected Input: 'I feel stressed about school'
   ✓ Emotional State: {'detected_emotions': ['stress'], 'valence': 'negative', 'intensity': 'moderate'}
   ✓ Input Category: problem_mention

🧭 STEP 2: NAVIGATION DECISION (Master Planning Agent)
   Current Stage: stage_1_safety_building
   Current Substate: 1.2_problem_and_body
   Completion Status:
      ✓ goal_stated: True
      ✓ vision_accepted: True
      ✗ problem_identified: False
      ✗ body_awareness_present: False

   📍 Navigation Decision: explore_problem
   📊 Situation Type: problem_needs_exploration
   🎯 RAG Query: dr_q_problem_construction
   💡 Reasoning: Client mentioned problem/stress, need to explore

💬 STEP 3: DIALOGUE GENERATION (Dialogue Agent)
   Decision to Implement: explore_problem
   📚 RAG Examples Retrieved: 3

   🔀 Decision Point: Using RAG+LLM for explore_problem
      Reasoning: Exploratory scenario with RAG examples available

   🤖 LLM Call: Dialogue Generation
      Model: llama3.1
      Prompt Preview: You are Dr. Q. Client mentioned problem/stress. CLIENT: "I feel stressed about school"...

   ✓ LLM Response Preview: Where do you feel that stress in your body?

   ✓ Generated Response: 'Where do you feel that stress in your body?'
   ✓ LLM Confidence: 0.85

💾 STEP 4: SESSION STATE UPDATE
   Updated Substate: 1.2_problem_and_body
   Body Questions Asked: 1
   Conversation Turns: 3

⏱️  PROCESSING SUMMARY
   Session ID: session_20251021_130045
   Total Processing Time: 1.456s

----------------------------------------------------------------------------------------------------
📤 ENDPOINT OUTPUT: /api/v1/input
Session ID: session_20251021_130045
Therapist Response: 'Where do you feel that stress in your body?'
Metadata: {
  "current_substate": "1.2_problem_and_body",
  "navigation_decision": "explore_problem",
  "processing_time": 1.456
}
====================================================================================================
```

---

## Testing the Logging

### Quick Test

```bash
# Terminal 1: Start watching logs
docker logs -f trt-app

# Terminal 2: Run test script
python test_detailed_logging.py
```

### Manual Test

```bash
# Terminal 1: Watch logs
docker logs -f trt-app

# Terminal 2: Send test request
curl -X POST http://localhost:8000/api/v1/input \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_123",
    "user_input": "I want to feel peaceful"
  }'
```

---

## What Each Component Logs

### API Endpoint (`main.py`)
- Request received (endpoint, session_id, user_input)
- Session existence check
- Processing completion
- Response sent (therapist_response, metadata)
- Errors

### Therapy System Wrapper (`therapy_system_wrapper.py`)
- Preprocessing start and results
- Navigation start and results
- Dialogue generation start and results
- Session updates
- State transitions
- Processing summary

### Master Planning Agent (`ollama_llm_master_planning_agent.py`)
- Rule-based decision applications
- LLM calls for navigation decisions
- Navigation reasoning
- Completion status checks

### Dialogue Agent (`improved_ollama_dialogue_agent.py`)
- Priority checks (self-harm, thinking mode, past tense)
- Therapeutic technique decisions
- RAG retrievals
- LLM calls for dialogue generation
- Response generation

---

## Filtering Logs

### Show only endpoint I/O

```bash
docker logs trt-app 2>&1 | grep -E "ENDPOINT (INPUT|OUTPUT)"
```

### Show only navigation decisions

```bash
docker logs trt-app 2>&1 | grep "Navigation Decision"
```

### Show only LLM calls

```bash
docker logs trt-app 2>&1 | grep "LLM Call"
```

### Show only errors

```bash
docker logs trt-app 2>&1 | grep "ERROR"
```

### Show rule applications

```bash
docker logs trt-app 2>&1 | grep "RULE APPLIED"
```

---

## Troubleshooting with Logs

### Problem: Response seems wrong

**Check:**
1. Preprocessing output (was input misunderstood?)
2. Navigation decision (was the right technique chosen?)
3. Completion status (are flags set correctly?)
4. LLM prompt and response (did LLM generate appropriate response?)

### Problem: System stuck in loop

**Check:**
1. State transitions (is substate advancing?)
2. Completion criteria (what's blocking progression?)
3. Body question count (reached limit?)
4. Navigation reasoning (why same decision repeatedly?)

### Problem: Unexpected behavior

**Check:**
1. Rule applications (which rules fired?)
2. Decision points (which priorities triggered?)
3. Session state updates (flags/counters correct?)

---

## Performance Monitoring

Check processing times in logs:

```bash
docker logs trt-app 2>&1 | grep "Processing Time"
```

Typical times:
- **Fast:** < 1s (rule-based responses, simple cases)
- **Normal:** 1-2s (LLM calls with RAG)
- **Slow:** > 3s (complex LLM prompts or multiple LLM calls)

---

## Tips

1. **Always run `docker logs -f trt-app` when testing** - You'll see exactly what's happening
2. **Use grep to filter** - Focus on specific components when debugging
3. **Check timestamps** - See how long each step takes
4. **Look for ERROR logs** - Catch failures immediately
5. **Watch state transitions** - Understand therapy progression
6. **Monitor LLM calls** - See what prompts are being used

---

## Summary

The detailed logging system provides complete visibility into:
✓ What input the system receives
✓ How it processes that input
✓ What decisions are made at each step
✓ Why those decisions were made
✓ What output is generated
✓ How long everything takes

This makes debugging, monitoring, and understanding the system behavior much easier!
