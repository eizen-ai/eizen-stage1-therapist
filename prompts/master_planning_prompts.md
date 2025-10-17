# Master Planning Agent Prompts

This file contains all prompts and rules used by the Master Planning Agent for navigation and decision-making. These can be modified to change how the AI decides "what to say" in therapy.

**Location in code:** `src/agents/ollama_llm_master_planning_agent.py`

---

## Overview

The Master Planning Agent has **two decision modes**:

1. **Strict Rule-Based Overrides** (Lines 62-248) - HIGHEST PRIORITY
2. **LLM Reasoning** (Lines 353-415) - Used when no rule override applies

**Key principle:** Rules always take precedence over AI reasoning to ensure therapeutic safety and protocol adherence.

---

## Strict Rule-Based Overrides

These rules **ALWAYS** override the LLM. They ensure critical therapeutic boundaries are maintained.

### RULE 1: Early Session Goal Inquiry

**When triggered:** In state 1.1, goal not stated, first 2 turns

**Code location:** Lines 69-88

**Logic:**
```python
if substate == "1.1_goal_and_vision" and not completion["goal_stated"]:
    if len(session_state.conversation_history) <= 2:
        return "clarify_goal"
```

**Decision output:**
```json
{
  "navigation_decision": "clarify_goal",
  "situation_type": "goal_needs_clarification",
  "rag_query": "dr_q_goal_clarification",
  "reasoning": "STRICT RULE: Must establish goal first",
  "rule_override": true
}
```

**Why important:** Ensures therapy always starts with goal clarification.

**How to modify:** Change the turn limit (currently `<= 2`) or disable by commenting out lines 69-88.

---

### RULE 2: Vision Building After Goal

**When triggered:** Goal stated but vision NOT accepted

**Code location:** Lines 90-108

**Logic:**
```python
if substate == "1.1_goal_and_vision" and completion["goal_stated"] and not completion["vision_accepted"]:
    return "build_vision"
```

**Decision output:**
```json
{
  "navigation_decision": "build_vision",
  "situation_type": "goal_stated_needs_vision",
  "rag_query": "dr_q_future_self_vision_building",
  "reasoning": "STRICT RULE: Build vision after goal stated (ALWAYS)",
  "rule_override": true
}
```

**Why important:** Prevents skipping vision building and jumping to psycho-education.

**How to modify:** Comment out lines 90-108 to make vision building optional.

---

### RULE 3: Redirect Problem to Goal

**When triggered:** Client mentions problem but goal/vision incomplete

**Code location:** Lines 110-131

**Logic:**
```python
if substate == "1.1_goal_and_vision":
    if not completion["goal_stated"] or not completion["vision_accepted"]:
        if any(word in client_lower for word in ["problem", "issue", "difficult", "hard"]):
            return "clarify_goal"
```

**Problem words tracked:**
- problem
- issue
- difficult
- hard

**Decision output:**
```json
{
  "navigation_decision": "clarify_goal",
  "situation_type": "goal_needs_clarification",
  "rag_query": "dr_q_redirect_outcome",
  "reasoning": "STRICT RULE: Redirect from problem to goal",
  "rule_override": true
}
```

**Why important:** Maintains TRT sequence - goal BEFORE problem exploration.

**How to modify:**
- Add more problem words to detection list (line 113)
- Comment out to allow problem-first conversations

---

### RULE 4: Explore Problem First in State 1.2

**When triggered:** In state 1.2, problem not identified, haven't asked yet, client not providing body info

**Code location:** Lines 133-181

**Logic:**
```python
if substate == "1.2_problem_and_body" and not completion["problem_identified"]:
    client_providing_body_info = (
        session_state.emotion_provided or
        session_state.body_location_provided or
        session_state.body_sensation_described
    )

    if not client_providing_body_info:
        # Check if we've already asked (scan last 3 exchanges)
        if not problem_question_asked:
            return "explore_problem"
```

**Problem inquiry phrases detected:**
- "what's been making it hard"
- "what's been making it difficult"
- "what's been getting in the way"
- "been making it hard"

**Decision output:**
```json
{
  "navigation_decision": "explore_problem",
  "situation_type": "problem_needs_exploration",
  "rag_query": "dr_q_problem_construction",
  "reasoning": "STRICT RULE: Explore problem FIRST before body exploration",
  "rule_override": true
}
```

**Why important:** Ensures problem question asked ONCE before body exploration.

**How to modify:**
- Change detection phrases (line 158-159)
- Adjust history scan depth (currently last 3 exchanges, line 155)
- Comment out to skip problem inquiry

---

### RULE 5: Advance to Readiness After Body Exploration

**When triggered:** Client says "nothing else" OR reached max body cycles (2)

**Code location:** Lines 183-225

**Logic:**
```python
if substate == "1.2_problem_and_body":
    client_said_nothing_else = any(phrase in client_lower for phrase in [
        "nothing", "no", "that's it", "that's all", "nothing more",
        "nothing else", "nope", "nah", "i'm good", "all good"
    ])

    reached_max_cycles = session_state.body_enquiry_cycles >= 2

    # Check if therapist just asked "what else?"
    just_asked_what_else = any(phrase in last_therapist_response for phrase in [
        "what else", "anything else", "is there anything else"
    ])

    if (client_said_nothing_else and just_asked_what_else) or reached_max_cycles:
        session_state.current_substate = "3.1_assess_readiness"
        return "assess_readiness"
```

**"Nothing else" phrases:**
- nothing
- no
- that's it
- that's all
- nothing more
- nothing else
- nope
- nah
- i'm good
- all good
- im good
- that is it

**"What else" phrases:**
- what else
- anything else
- is there anything else
- anything i'm missing

**Max body cycles:** 2 (configurable)

**Decision output:**
```json
{
  "current_substate": "3.1_assess_readiness",
  "navigation_decision": "assess_readiness",
  "situation_type": "readiness_for_alpha",
  "rag_query": "dr_q_ready",
  "reasoning": "Client said 'nothing else' OR reached max cycles (2/2)",
  "rule_override": true
}
```

**Why important:** Prevents endless body exploration loop.

**How to modify:**
- Change max cycles (line 194): `>= 2` → `>= 3` (allow more cycles)
- Add/remove "nothing else" phrases (lines 188-191)
- Add/remove "what else" phrases (lines 201)

---

### RULE 6: Readiness Assessment Only in State 3.1

**When triggered:** In state 3.1_assess_readiness

**Code location:** Lines 227-245

**Logic:**
```python
if substate == "3.1_assess_readiness":
    return "assess_readiness"
```

**Decision output:**
```json
{
  "navigation_decision": "assess_readiness",
  "situation_type": "readiness_for_alpha",
  "rag_query": "dr_q_ready",
  "reasoning": "In state 3.1, assess readiness for alpha (NO more body questions)",
  "rule_override": true
}
```

**Why important:** Prevents looping back to body exploration after already completing it.

**How to modify:** Comment out lines 227-245 to allow body questions in state 3.1.

---

## LLM Reasoning Prompt

When NO rule override applies, the system uses LLM reasoning.

**Function:** `_construct_therapeutic_prompt()`

**Code location:** Lines 353-415

**Current prompt:**

```
You are Dr. Q, an expert TRT (Trauma Resolution Therapy) therapist. Make a navigation decision for this therapeutic moment.

CURRENT CONTEXT:
- Stage: {session_state.current_stage}
- Substate: {substate}
- Client: "{client_input}"
- Emotional State: {processed_input['emotional_state']}

COMPLETION STATUS:
- Goal Stated: ✅/❌
- Vision Accepted: ✅/❌
- Problem Identified: ✅/❌
- Body Awareness: ✅/❌
- Present Focus: ✅/❌

RECENT CONVERSATION:
{last 3 exchanges}

TRT RULES:
1. Stage 1.1: Establish goal, build future vision
2. Stage 1.2: Explore problem, develop body awareness
3. Stage 1.3: Assess pattern understanding, readiness for Stage 2
4. Always prioritize present-moment body awareness
5. Use "How do you know?" for pattern exploration
6. Don't advance until criteria met

NAVIGATION OPTIONS:
- clarify_goal, build_vision, explore_problem, body_awareness_inquiry, pattern_inquiry, assess_readiness, general_inquiry

SITUATION TYPES:
- goal_needs_clarification, goal_stated_needs_vision, problem_needs_exploration, body_symptoms_exploration, explore_trigger_pattern, readiness_for_stage_2, general_therapeutic_inquiry

RAG QUERIES:
- dr_q_goal_clarification, dr_q_future_self_vision_building, dr_q_problem_construction, dr_q_body_symptom_present_moment_inquiry, dr_q_how_do_you_know_technique, dr_q_transition_to_intervention, general_dr_q_approach

Respond in JSON format:
{
    "reasoning": "detailed therapeutic reasoning",
    "navigation_decision": "one navigation option",
    "situation_type": "one situation type",
    "rag_query": "one rag query",
    "ready_for_next": true/false,
    "advancement_blocked_by": ["blocking factors"],
    "confidence": 0.0-1.0,
    "therapeutic_focus": "what to focus on"
}
```

### How to Modify LLM Prompt

**To change conversation context depth:**
```python
# Line 363 - currently last 3 exchanges
recent_exchanges = session_state.conversation_history[-3:]

# Change to last 5 exchanges
recent_exchanges = session_state.conversation_history[-5:]
```

**To add new TRT rules:**
```python
# Lines 386-392 - Add your rule to this section
TRT RULES:
1. Stage 1.1: Establish goal, build future vision
2. Stage 1.2: Explore problem, develop body awareness
...
7. YOUR NEW RULE HERE
```

**To add navigation options:**
```python
# Line 395 - Add new decision type
NAVIGATION OPTIONS:
- clarify_goal, build_vision, your_new_option
```

**To adjust LLM temperature (creativity):**
```python
# Line 336 - currently 0.3 (focused)
"temperature": 0.3,

# Make more creative: 0.7
# Make more deterministic: 0.1
```

---

## Fallback Decision System

When LLM fails, fallback to simple rules.

**Function:** `_fallback_rule_based_decision()`

**Code location:** Lines 471-524

**Logic:**
```python
if substate == "1.1_goal_and_vision":
    if not completion["goal_stated"]:
        return "clarify_goal"
    else:
        return "build_vision"

# Default
return "general_inquiry"
```

**Why important:** Ensures system never crashes - always has a decision.

**How to modify:** Add more fallback cases for different substates.

---

## Navigation Decision Types

The system outputs one of these decisions:

| Decision | When Used | Example Question |
|----------|-----------|------------------|
| `clarify_goal` | Goal not stated | "What would you like to work on?" |
| `build_vision` | Goal stated, need vision | "How will you know you've achieved it?" |
| `explore_problem` | Need problem identification | "What's been making it hard?" |
| `body_awareness_inquiry` | Exploring body symptoms | "Where do you feel that in your body?" |
| `pattern_inquiry` | Understanding triggers | "How do you know you're stressed?" |
| `assess_readiness` | Ready for alpha sequence | "Would you like to try something?" |
| `general_inquiry` | Fallback | General therapeutic response |

---

## Situation Types

The decision includes a situation type for context:

| Situation Type | Meaning |
|----------------|---------|
| `goal_needs_clarification` | Client hasn't stated clear goal |
| `goal_stated_needs_vision` | Goal stated, build future vision |
| `problem_needs_exploration` | Need to identify specific problem |
| `body_symptoms_exploration` | Exploring body awareness |
| `emotion_to_body` | Emotion identified, ask body location |
| `body_location_to_sensation` | Location identified, ask sensation quality |
| `explore_trigger_pattern` | Understanding "how do you know" |
| `readiness_for_alpha` | Ready for intervention |
| `general_therapeutic_inquiry` | General conversation |

---

## RAG Queries

Each decision includes a RAG query to retrieve relevant Dr. Q examples:

| RAG Query | Retrieves Examples Of |
|-----------|----------------------|
| `dr_q_goal_clarification` | Goal inquiry questions |
| `dr_q_future_self_vision_building` | Vision building dialogue |
| `dr_q_problem_construction` | Problem exploration |
| `dr_q_body_symptom_present_moment_inquiry` | Body awareness questions |
| `dr_q_body_location_inquiry` | "Where in your body?" |
| `dr_q_sensation_quality_inquiry` | "What kind of sensation?" |
| `dr_q_how_do_you_know_technique` | Pattern exploration |
| `dr_q_ready` | Readiness assessment |
| `dr_q_transition_to_intervention` | Moving to alpha sequence |
| `general_dr_q_approach` | General Dr. Q style |

---

## Configuration Files

The Master Planning Agent loads rules from:

### `config/system/core_system/simplified_navigation.json`

**Loaded at:** Line 25

**Contains:** TRT stage navigation rules

**How to modify:** Edit JSON file to change stage advancement logic

### `config/system/core_system/input_classification_patterns.json`

**Loaded at:** Line 29

**Contains:** Pattern matching rules for client input

**How to modify:** Edit JSON file to add new patterns

---

## System Parameters

### Ollama Configuration

**Location:** Line 16

```python
def __init__(self, ollama_url="http://localhost:11434", model="llama3.1"):
```

**How to change:**
- Use different model: `model="llama2"`
- Use remote Ollama: `ollama_url="http://192.168.1.100:11434"`

### LLM Parameters

**Location:** Lines 335-338

```python
"options": {
    "temperature": 0.3,      # Creativity (0.0-1.0)
    "num_predict": 512      # Max tokens
}
```

**How to modify:**
- More creative: `"temperature": 0.7`
- Longer responses: `"num_predict": 1024`
- Faster responses: `"num_predict": 256`

---

## Testing Your Changes

After modifying prompts or rules:

```bash
# 1. Rebuild Docker
docker compose build --no-cache

# 2. Restart services
docker compose up -d

# 3. Test navigation decision
curl -X POST http://localhost:8090/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "message": "I want to feel less stressed"
  }'

# 4. Check decision in response
# Should see: navigation_decision, situation_type, rag_query
```

---

## Decision Flow Example

### Client Input: "I'm stressed about work deadlines"

**Step 1: Check Rule Overrides**
- In state 1.2?
- Problem identified? NO
- Already asked problem question? NO
- Client providing body info? NO

**Rule 4 triggered:** explore_problem

**Step 2: Output Decision**
```json
{
  "navigation_decision": "explore_problem",
  "situation_type": "problem_needs_exploration",
  "rag_query": "dr_q_problem_construction",
  "reasoning": "STRICT RULE: Explore problem FIRST",
  "rule_override": true
}
```

**Step 3: Dialogue Agent Uses This**
- Retrieves Dr. Q examples for "problem_construction"
- Generates: "What's been making it hard to meet those deadlines?"

---

## Modifying Rules vs Prompts

### When to Modify Rules (Strict Overrides)

Change rules when you want to:
- Enforce mandatory therapeutic sequences
- Prevent certain actions in specific states
- Add safety guardrails
- Change state advancement criteria

**Example:** Require 3 body cycles instead of 2
```python
# Line 194
reached_max_cycles = session_state.body_enquiry_cycles >= 3  # Changed from 2
```

### When to Modify LLM Prompt

Change prompt when you want to:
- Adjust AI's reasoning style
- Add therapeutic context
- Change how decisions are made (not what decisions are enforced)
- Improve decision quality

**Example:** Add more therapeutic principles
```python
# Line 389 - Add to TRT RULES section
7. Validate client's experience before exploring further
8. Use client's exact words when reflecting
```

---

## Priority Order

Decision-making happens in this order:

1. **Strict Rule Overrides** (Lines 62-248) - HIGHEST PRIORITY
2. **LLM Reasoning** (Lines 302-324) - If no rule applies
3. **Fallback Rules** (Lines 471-524) - If LLM fails

**Example:**

```
Client: "I'm stressed"
State: 1.2, problem not identified

Priority 1: Check rules → RULE 4 applies → explore_problem
(LLM never consulted because rule took precedence)

Client: "I feel tightness in my chest"
State: 1.2, problem identified, body location provided

Priority 1: Check rules → No rule applies
Priority 2: Ask LLM → LLM decides → body_awareness_inquiry
Priority 3: (Not needed, LLM succeeded)
```

---

## Common Modifications

### Make Goal Inquiry Optional

Comment out RULE 1:

```python
# Lines 69-88
# if substate == "1.1_goal_and_vision" and not completion["goal_stated"]:
#     ...
#     return clarify_goal decision
```

### Allow More Body Exploration

Change max cycles:

```python
# Line 194
reached_max_cycles = session_state.body_enquiry_cycles >= 5  # Allow 5 cycles
```

### Add New "Nothing Else" Phrases

```python
# Lines 188-191 - Add your phrases
client_said_nothing_else = any(phrase in client_lower for phrase in [
    "nothing", "no", "that's it",
    "i don't know",  # NEW
    "not sure",      # NEW
])
```

### Make Vision Building Optional

Comment out RULE 2:

```python
# Lines 90-108
# if completion["goal_stated"] and not completion["vision_accepted"]:
#     ...
#     return build_vision decision
```

---

## See Also

- [Dialogue Agent Prompts](./dialogue_prompts.md) - Response generation prompts
- [RAG System](./rag_system.md) - How examples are retrieved
- [Session State Manager](../src/core/session_state_manager.py) - State tracking logic

---

**Last Updated:** 2025-10-17
**Version:** 1.0 (Latest fixes included)
