# How State-Actions Work in TRT System

**Date:** 2025-10-15
**Current Implementation:** Hybrid (Rules + LLM + RAG)

---

## 🎯 TL;DR - How It Works Now

We use a **3-layer hybrid approach**:

1. **Layer 1: Strict Rules** (Highest Priority) - Hardcoded logic for critical flows
2. **Layer 2: LLM Reasoning** (Ollama with Llama 3.1) - Intelligent navigation decisions
3. **Layer 3: RAG System** (1000 embeddings) - Dr. Q's exact therapeutic responses

**The CSV (`STAGE1_COMPLETE.csv`) is NOT used** - It's just a reference document.

---

## 📊 Complete Flow Diagram

```
Client Input
     ↓
[1] Input Preprocessing
     ↓
[2] Session State Update
     ↓
[3] Strict Rule Overrides? ──YES──→ Use Rule Decision
     ↓ NO
[4] LLM Navigation Decision (Ollama)
     ↓
[5] RAG Query (Get Dr. Q's Response)
     ↓
[6] Generate Final Response
     ↓
[7] Update Session State
     ↓
Therapist Response
```

---

## 🔧 Layer 1: Strict Rule-Based Overrides

**File:** `src/agents/ollama_llm_master_planning_agent.py`
**Method:** `_check_strict_rule_overrides()`

### Rules Implemented:

#### Rule 1: Force Goal Clarification
```python
# If in 1.1 and NO goal stated yet → MUST ask for goal
if substate == "1.1_goal_and_vision" and not completion["goal_stated"]:
    return {
        "navigation_decision": "clarify_goal",
        "situation_type": "goal_needs_clarification",
        "rag_query": "dr_q_goal_clarification"
    }
```

**Why:** Can't proceed without establishing what client wants to achieve.

#### Rule 2: Force Vision Building
```python
# If goal just stated → MUST build vision (not explore problem yet)
if completion["goal_stated"] and not completion["vision_accepted"]:
    return {
        "navigation_decision": "build_vision",
        "rag_query": "dr_q_future_self_vision_building"
    }
```

**Why:** TRT methodology requires vision before exploring problem.

#### Rule 3: Redirect Problem to Goal
```python
# If asking about problem but goal/vision not complete → redirect to goal
if "problem" in client_input and not completion["goal_stated"]:
    return {
        "navigation_decision": "clarify_goal",
        "rag_query": "dr_q_redirect_outcome"
    }
```

**Why:** Client talking about problem before establishing goal - redirect.

### When Rules Apply:
- ✅ **Always checked first** - Before LLM reasoning
- ✅ **Takes precedence** - Overrides LLM decision
- ✅ **Critical flows only** - Only for must-follow sequences

---

## 🧠 Layer 2: LLM Navigation Decision (Ollama)

**File:** `src/agents/ollama_llm_master_planning_agent.py`
**Method:** `_get_llm_navigation_decision()`

### How It Works:

#### Step 1: Construct Prompt
```python
prompt = f"""You are Dr. Q, an expert TRT therapist. Make a navigation decision.

CURRENT CONTEXT:
- Stage: {session_state.current_stage}
- Substate: {substate}
- Client: "{client_input}"
- Emotional State: {processed_input['emotional_state']}

COMPLETION STATUS:
- Goal Stated: {"✅" if completion['goal_stated'] else "❌"}
- Vision Accepted: {"✅" if completion['vision_accepted'] else "❌"}
- Problem Identified: {"✅" if completion['problem_identified'] else "❌"}
- Body Awareness: {"✅" if completion['body_awareness_present'] else "❌"}

RECENT CONVERSATION:
{recent_history}

TRT RULES:
1. Stage 1.1: Establish goal, build future vision
2. Stage 1.2: Explore problem, develop body awareness
3. Stage 1.3: Assess pattern understanding, readiness for Stage 2
4. Always prioritize present-moment body awareness
5. Use "How do you know?" for pattern exploration

NAVIGATION OPTIONS:
- clarify_goal, build_vision, explore_problem, body_awareness_inquiry,
  pattern_inquiry, assess_readiness, general_inquiry

SITUATION TYPES:
- goal_needs_clarification, goal_stated_needs_vision, problem_needs_exploration,
  body_symptoms_exploration, explore_trigger_pattern, readiness_for_stage_2

RAG QUERIES:
- dr_q_goal_clarification, dr_q_future_self_vision_building,
  dr_q_problem_construction, dr_q_body_symptom_present_moment_inquiry,
  dr_q_how_do_you_know_technique, dr_q_transition_to_intervention

Respond in JSON format:
{{
    "reasoning": "detailed therapeutic reasoning",
    "navigation_decision": "one navigation option",
    "situation_type": "one situation type",
    "rag_query": "one rag query",
    "ready_for_next": true/false,
    "advancement_blocked_by": ["blocking factors"],
    "confidence": 0.0-1.0
}}
"""
```

#### Step 2: Call Ollama
```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Lower = more consistent
            "num_predict": 512   # Max tokens
        }
    }
)
```

#### Step 3: Parse LLM Response
```python
{
    "reasoning": "Client stated goal 'I want to feel calm'. Need to build vision.",
    "navigation_decision": "build_vision",
    "situation_type": "goal_stated_needs_vision",
    "rag_query": "dr_q_future_self_vision_building",
    "ready_for_next": false,
    "confidence": 0.9
}
```

### What LLM Decides:
- ✅ **Navigation decision** - What therapeutic action to take
- ✅ **Situation type** - Classification of current moment
- ✅ **RAG query** - Which Dr. Q response to retrieve
- ✅ **Readiness** - Whether client is ready to advance
- ✅ **Reasoning** - Therapeutic rationale

### Configuration Files Used:

#### `config/system/core_system/simplified_navigation.json`
```json
{
  "stage_1_navigation": {
    "1.1_goal_and_vision": {
      "objective": "Get therapeutic goal AND future self vision",
      "completion_criteria": ["goal_stated", "vision_accepted"],
      "triggers": {
        "goal_stated": "build_vision",
        "vision_accepted": "provide_psycho_education"
      },
      "rag_queries": {
        "clarify_goal": "dr_q_goal_clarification",
        "build_vision": "dr_q_future_self_vision_building"
      }
    }
  }
}
```

**Purpose:** Provides structure for LLM prompt - defines objectives, triggers, and RAG query mappings.

#### `config/system/core_system/input_classification_patterns.json`
```json
{
  "situation_classifications": {
    "goal_related": ["want to feel", "need to", "hope to"],
    "body_symptoms": ["pain", "ache", "tension", "tight"],
    "emotional_patterns": ["feel like", "always feel"],
    "crisis_indicators": ["can't handle", "want to hurt"]
  }
}
```

**Purpose:** Pattern matching for input classification (used in preprocessing).

---

## 📚 Layer 3: RAG System (Dr. Q's Responses)

**File:** `src/agents/improved_ollama_dialogue_agent.py`
**Data:** `data/embeddings/trt_rag_index.faiss` (1000 state-action pairs)

### How It Works:

#### Step 1: Get RAG Query from Navigation
```python
navigation_output = {
    "rag_query": "dr_q_future_self_vision_building"
}
```

#### Step 2: Retrieve Similar Examples
```python
# Query RAG system
rag_results = self.rag_system.query(
    query_text="dr_q_future_self_vision_building",
    top_k=5  # Get 5 most similar examples
)

# Results:
[
    {
        "client_input": "I want to feel calm",
        "dr_q_response": "So you want to feel calm. I'm seeing you who's calm, at ease, lighter. Does that make sense to you?",
        "substate": "1.1_goal_and_vision",
        "similarity": 0.95
    },
    {
        "client_input": "I need peace",
        "dr_q_response": "You need peace. I'm seeing you peaceful, centered, free. That's where we're headed.",
        "substate": "1.1_goal_and_vision",
        "similarity": 0.92
    },
    ...
]
```

#### Step 3: Construct Context
```python
# Build context from RAG results
rag_context = ""
for result in rag_results:
    rag_context += f"Client: {result['client_input']}\n"
    rag_context += f"Dr. Q: {result['dr_q_response']}\n\n"
```

#### Step 4: Generate Response with LLM
```python
prompt = f"""You are Dr. Q. Generate a therapeutic response.

CLIENT INPUT: "{client_input}"
NAVIGATION: {navigation_decision}
SUBSTATE: {current_substate}

DR. Q'S STYLE (from similar situations):
{rag_context}

Generate response matching Dr. Q's therapeutic style and approach.
"""

# Call Ollama to generate
response = ollama.generate(prompt)
```

### RAG Data Source:
**File:** `data/state_actions/all_dr_q_exchanges.json`

```json
[
    {
        "client_input": "I want to feel calm",
        "therapist_response": "Got it. So you want to feel calm. I'm seeing you who's calm, at ease, lighter. Does that make sense to you?",
        "substate": "1.1_goal_and_vision",
        "action": "build_vision",
        "rag_key": "dr_q_future_self_vision_building"
    },
    {
        "client_input": "Yes that makes sense",
        "therapist_response": "Here's what's happening in the brain. When facing a threat, the brain activates a survival response...",
        "substate": "1.1.5_psycho_education",
        "action": "provide_education",
        "rag_key": "dr_q_psycho_education"
    }
]
```

**Total Embeddings:** 1000 state-action pairs

---

## 🔄 Complete Example Flow

### User Input: "I want to feel calm"

#### Step 1: Input Preprocessing
```python
{
    "original_input": "I want to feel calm",
    "corrected_input": "i want to feel calm",
    "emotional_state": {
        "categories": {"positive": ["calm"]},
        "intensity": 0,
        "primary_emotion": "positive_state"
    },
    "input_category": "goal_statement"
}
```

#### Step 2: Session State Update
```python
session_state.update_completion_status(input, preprocessing)
# Detects: goal_stated = True
```

#### Step 3: Strict Rule Check
```python
# Rule: If goal just stated → build vision
if completion["goal_stated"] and not completion["vision_accepted"]:
    return {
        "navigation_decision": "build_vision",
        "rag_query": "dr_q_future_self_vision_building"
    }
# ✅ RULE MATCHES - Skip LLM, use this
```

#### Step 4: RAG Query
```python
# Query: "dr_q_future_self_vision_building"
rag_results = [
    {
        "client": "I want to feel calm",
        "dr_q": "So you want to feel calm. I'm seeing you who's calm, at ease, lighter.",
        "similarity": 0.95
    }
]
```

#### Step 5: Generate Response
```python
# LLM generates response using RAG examples
response = "Got it. So you want to feel calm. I'm seeing you who's calm, at ease, lighter. Does that make sense to you?"
```

#### Step 6: Return to Client
```json
{
    "therapist_response": "Got it. So you want to feel calm. I'm seeing you who's calm, at ease, lighter. Does that make sense to you?",
    "preprocessing": {...},
    "navigation": {
        "decision": "build_vision",
        "current_substate": "1.1_goal_and_vision",
        "rag_query": "dr_q_future_self_vision_building"
    },
    "session_progress": {
        "current_substate": "1.1_goal_and_vision",
        "completion_criteria": {
            "goal_stated": true,
            "vision_accepted": false
        }
    }
}
```

---

## 📋 What Each File Does

### `/config/STAGE1_COMPLETE.csv`
- **Used:** ❌ No
- **Purpose:** Reference document only
- **Contains:** Complete state machine blueprint
- **Checked:** Only for existence in health check

### `/config/system/core_system/simplified_navigation.json`
- **Used:** ✅ Yes
- **Purpose:** LLM prompt structure
- **Contains:** Stage objectives, triggers, RAG query mappings
- **Loaded:** On system initialization

### `/config/system/core_system/input_classification_patterns.json`
- **Used:** ✅ Yes
- **Purpose:** Input classification patterns
- **Contains:** Keyword patterns for situation types
- **Loaded:** On system initialization

### `/data/embeddings/trt_rag_index.faiss`
- **Used:** ✅ Yes
- **Purpose:** RAG vector database
- **Contains:** 1000 embedded state-action pairs
- **Loaded:** On system initialization

### `/data/embeddings/trt_rag_metadata.json`
- **Used:** ✅ Yes
- **Purpose:** RAG metadata
- **Contains:** Full text of all state-action pairs
- **Loaded:** With FAISS index

### `/data/state_actions/all_dr_q_exchanges.json`
- **Used:** ✅ Yes (during embedding generation)
- **Purpose:** Source data for RAG
- **Contains:** All Dr. Q exchanges
- **Loaded:** Only when rebuilding embeddings

---

## 🎯 Summary: How Rules Are Followed

### We DON'T:
- ❌ Parse the CSV file during runtime
- ❌ Use hardcoded state transition tables
- ❌ Follow rigid deterministic paths

### We DO:
- ✅ Use **strict rules** for critical sequences (goal → vision → problem)
- ✅ Use **LLM reasoning** for intelligent navigation (Ollama with context)
- ✅ Use **RAG retrieval** for Dr. Q's authentic responses (1000 examples)
- ✅ Use **session state tracking** for completion criteria
- ✅ Use **configuration files** to structure LLM prompts

### The Hybrid Advantage:
1. **Flexibility** - LLM handles edge cases
2. **Authenticity** - RAG provides Dr. Q's actual style
3. **Correctness** - Rules enforce critical methodology
4. **Intelligence** - LLM makes context-aware decisions

---

## 🔍 Where to Look for Logic

### Navigation Logic:
**File:** `src/agents/ollama_llm_master_planning_agent.py`
- Lines 62-144: Strict rule overrides
- Lines 249-311: LLM prompt construction
- Lines 367-420: Fallback rule-based decisions

### Response Generation:
**File:** `src/agents/improved_ollama_dialogue_agent.py`
- RAG query and response generation

### Session Tracking:
**File:** `src/core/session_state_manager.py`
- Completion criteria tracking
- State advancement logic

### Configuration:
**Files:**
- `config/system/core_system/simplified_navigation.json`
- `config/system/core_system/input_classification_patterns.json`

---

## 💡 Want to Change the Rules?

### Option 1: Modify Strict Rules (Recommended)
**File:** `src/agents/ollama_llm_master_planning_agent.py`
**Method:** `_check_strict_rule_overrides()`

Add new rule:
```python
# RULE 4: Force body inquiry after problem
if completion["problem_identified"] and not completion["body_awareness_present"]:
    return {
        "navigation_decision": "body_awareness_inquiry",
        "rag_query": "dr_q_body_symptom_present_moment_inquiry"
    }
```

### Option 2: Update LLM Prompt
**File:** `src/agents/ollama_llm_master_planning_agent.py`
**Method:** `_construct_therapeutic_prompt()`

Modify prompt to emphasize different rules.

### Option 3: Update Configuration
**File:** `config/system/core_system/simplified_navigation.json`

Change triggers, RAG queries, or completion criteria.

### Option 4: Implement CSV-Based State Machine
Would require:
1. CSV parser
2. State transition engine
3. Deterministic flow controller

---

**Last Updated:** 2025-10-15
**Current Approach:** Hybrid (Rules + LLM + RAG)
**Works:** ✅ Yes, tested and deployed
