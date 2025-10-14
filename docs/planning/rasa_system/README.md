# AI THERAPIST STAGE 1 - RASA SYSTEM

## 🎯 SYSTEM OVERVIEW

**Complete conversation management for AI Therapist Stage 1** with:
- State-action pairs with RAG retrieval
- Detection-based routing
- Framework triggers (alpha_sequence, metaphors, no_harm, card_game)
- Multiple response paths
- Priority redirects

**Built from 3 actual Dr. Q session transcripts**

---

## 📁 FILES

```
/rasa_system/
├── README.md                           ← This file
├── STAGE1_COMPLETE.csv                 ⭐ Main state-action pairs
├── intents/client_intents.yml          Client response types
├── stories/stage1_complete_stories.yml Conversation paths
└── actions/therapist_actions.json      Action definitions
```

---

## 🔑 KEY CONCEPT: FRAMEWORK TRIGGERS

**You already have these frameworks working:**
- `alpha_sequence` - Alpha induction with body checks
- `metaphors` - Dr. Q metaphors (bird's eye, bad programming, etc.)
- `no_harm` - Permission/validation protocols
- `card_game` - For clients who aren't speaking much

**System just needs to TRIGGER them at the right time.**

### **How Triggering Works:**

```python
# From CSV "Framework_Trigger" column

if state == "3.3" and client_ready:
    # TRIGGER alpha_sequence framework
    # Framework appears on screen
    # Framework handles all steps + body checks
    # Returns when complete
    alpha_sequence.trigger()

if state == "3.2" and introducing_alpha:
    # TRIGGER no_harm for permission
    no_harm.trigger('permission_check')

if state == "4.1" and transitioning_stage2:
    # TRIGGER metaphors for brain explanation
    metaphors.trigger(['bad_programming', 'short_circuit'])

if state == "SILENT" and client_not_speaking:
    # TRIGGER card_game
    card_game.trigger()
```

**Frameworks come on screen when triggered. System doesn't need to know internal details.**

---

## 📊 CSV STRUCTURE

### **Main Columns:**

| Column | Purpose | Example |
|--------|---------|---------|
| `State_ID` | Where you are | `2.4` or `THINK` |
| `State_Name` | Simple name | "Present Check" |
| `Client_Says_Example` | What client might say | "I feel it now" |
| `Client_Intent` | Intent category | `present_aware` |
| `Detection_Checks` | What to detect | `body_aware, present_tense` |
| `Therapist_Action` | What to do | `affirm_and_check` |
| `RAG_Query` | RAG retrieval tag | `dr_q_present_check` |
| `Fallback_Response` | If RAG fails | "That's right..." |
| `Framework_Trigger` | **Trigger framework** | `TRIGGER: alpha_sequence` |
| `Next_State_If` | Route if condition | `present→2.5` |
| `Next_State_Else` | Route otherwise | `not_present→guide` |

### **Example Rows:**

```csv
State_ID: 3.3
State_Name: Execute Alpha
Framework_Trigger: TRIGGER: alpha_sequence
Notes: Framework handles all 6 steps + body checks automatically

State_ID: 3.2
State_Name: Introduce Alpha
Framework_Trigger: TRIGGER: no_harm
Notes: Get permission before alpha

State_ID: 4.1
State_Name: Ready Stage 2
Framework_Trigger: TRIGGER: metaphors
Notes: Explain brain with metaphors

State_ID: SILENT
State_Name: Not Speaking
Framework_Trigger: TRIGGER: card_game (if continues)
Notes: If gentle prompt doesn't work, offer card game
```

---

## 🔄 CONVERSATION FLOW

```
1.1 Goal Inquiry → What do you want?
  ↓
1.2 Build Vision → Peaceful, present, grounded?
  ↓
1.3 Get Permission → Would it be okay? [TRIGGER: no_harm]
  ↓
2.1 Problem Inquiry → What's been difficult?
  ↓
2.2-2.4 Body Awareness → Where? What sensation? Feel it now?
  ↓
2.5 Pattern Inquiry → How do you know when it happens?
  ↓
3.1 Assess Readiness → Anything else?
  ↓
3.2 Introduce Alpha → Explain + permission [TRIGGER: no_harm]
  ↓
3.3 Execute Alpha → [TRIGGER: alpha_sequence]
  ↓
3.4-3.6 Post-Alpha → What noticed? Link to vision. Better now?
  ↓
4.1 Ready Stage 2 → Transition [TRIGGER: metaphors]

PRIORITY STATES (can happen anytime):
THINK → Redirect thinking to feeling
PAST → Redirect past to present
AFFIRM → Just say "That's right" (60%+ of time)
EMOTION → Validate strong emotion [TRIGGER: no_harm]
CRY → Normalize crying [TRIGGER: no_harm]
SILENT → Gentle prompt or [TRIGGER: card_game]
```

---

## 🎯 DETECTION-BASED ROUTING

### **LLM Master Agent Role - Semantic Intent Classification:**

**CRITICAL:** System does NOT match hard-coded keywords. LLM Master Agent performs **semantic understanding**.

```python
# WRONG approach - hard keyword matching:
if "peaceful" in message:
    intent = "state_goal_emotional"  # Fails for "ecstatic", "serene", etc.

# RIGHT approach - LLM semantic classification:
master_agent_prompt = f"""
Client said: "{client_message}"

Classify the client's intent. Use semantic understanding, not keyword matching.

Examples of intents:
- "I want to feel peaceful" → state_goal_emotional
- "I want to feel ecstatic" → state_goal_emotional (same intent, different word!)
- "I want serenity" → state_goal_emotional (same intent, synonym)
- "I'm feeling gloomy" → describes_problem (emotion word but describing problem, not goal)
- "I think it's because..." → thinking_mode_detected (PRIORITY redirect!)
- "Back when I was..." → past_tense_detected (PRIORITY redirect!)
- "My chest feels tight" → mentions_body (body awareness, present tense)

What is the intent of: "{client_message}"?
"""

# LLM understands meaning, generalizes beyond examples
intent = llama_master_agent.classify(master_agent_prompt)
```

### **Detection Checks (also semantic, not keyword-based):**

```python
detections = {
    'body_words': llm_detects_body_reference(message),  # "chest", "ache", "tight", "knot", etc.
    'thinking_mode': llm_detects_cognitive_language(message),  # "i think", "because", "probably", "maybe"
    'tense': llm_detects_tense(message),  # 'present' or 'past' from context
    'intensity': llm_detects_emotional_intensity(message),  # caps, exclamations, word choice
    'present_aware': body_aware AND present_tense,
    'self_harm': llm_detects_self_harm_language(message)  # Triggers SELFHARM state
}
```

**CSV provides EXAMPLES, LLM generalizes to ANY vocabulary client uses.**

### **Route based on detections:**

```python
# Priority 1: SAFETY - Self-harm detection
if detections['self_harm']:
    state = 'SELFHARM'  # TRIGGER: no_harm framework

# Priority 2: Redirect thinking/past
elif detections['thinking_mode']:
    state = 'THINK'  # Redirect to feeling
elif detections['tense'] == 'past':
    state = 'PAST'  # Redirect to present

# Priority 3: Just affirm if already present + body aware
elif detections['present_aware']:
    state = 'AFFIRM'  # Just say "that's right"

# Otherwise: Normal state flow
else:
    state = next_state_from_csv
```

---

## 🔌 FRAMEWORK INTEGRATION

### **Your Existing Frameworks:**

**IMPORTANT:** Frameworks are triggered strategically based on client needs and TRT methodology, not automatically at fixed states.

#### **1. alpha_sequence**
```python
# When state == 3.3:
alpha_sequence.trigger()

# Framework displays on screen
# Handles all 6 steps:
# - Jaw lower
# - Tongue relax
# - Breathing
# - Peripheral awareness
# - Bird's eye view
# - Reassociate

# Includes body checks after each step
# Returns when complete
```

#### **2. metaphors**
```python
# STRATEGIC TRIGGERS based on TRT PDF - NOT automatic
# Used in Stage 2 based on client's situation:

# Step 2 - Change logical levels:
metaphors.trigger('zebra_lion')  # Brain causing response

# Step 3 - Explain Trauma:
metaphors.trigger(['timing', 'meaning', 'similar_equals_same'])

# Step 3a - When rape/sexual trauma (when needed):
metaphors.trigger('my_body_not_me')

# Step 3b - When grief (when needed):
metaphors.trigger('grief_explanation')

# Step 9a - When guilt/shame (when needed):
metaphors.trigger('guilt_shame_explanation')

# Framework displays explanations on screen
# Triggered based on what client needs, not automatically
```

#### **3. no_harm**
```python
# SAFETY PROTOCOL - only triggered for self-harm mentions
# When client mentions self-harm/suicidal ideation (state SELFHARM):
no_harm.trigger('safety_protocol')

# Framework provides:
# - Immediate safety assessment
# - Crisis intervention protocols
# - Resource connections (hotlines, emergency contacts)
# - Risk assessment tools

# NOT used for general permission, validation, or normalization
```

#### **4. card_game**
```python
# When client not speaking (state SILENT):
if gentle_prompt_didnt_work:
    card_game.trigger()

# Framework appears on screen
# Interactive cards for non-verbal clients
```

---

## 💻 IMPLEMENTATION EXAMPLE

```python
import pandas as pd

# Load CSV
states = pd.read_csv('STAGE1_COMPLETE.csv')

# Current state
current_state = '2.4'  # Present Check

# Client message
client_message = "Yes I can feel it right now"

# Run detections
detections = {
    'body_aware': detect_body_words(client_message),  # True
    'thinking_mode': detect_thinking_mode(client_message),  # False
    'tense': detect_tense(client_message),  # 'present'
    'intensity': detect_intensity(client_message)  # low
}

# Check priority redirects first
if detections['thinking_mode']:
    current_state = 'THINK'
elif detections['tense'] == 'past':
    current_state = 'PAST'
elif detections['body_aware'] and detections['tense'] == 'present':
    # Client already present + body aware
    # Just affirm instead of asking
    current_state = 'AFFIRM'
else:
    # Normal flow - get state info
    state_row = states[states['State_ID'] == current_state].iloc[0]

    # Query RAG
    rag_tag = state_row['RAG_Query']
    rag_result = rag_system.query(rag_tag)

    # Use RAG or fallback
    if rag_result:
        response = rag_result
    else:
        response = state_row['Fallback_Response']

    # Check if framework trigger needed
    if pd.notna(state_row['Framework_Trigger']):
        framework = parse_trigger(state_row['Framework_Trigger'])
        # e.g., "TRIGGER: alpha_sequence"
        if framework == 'alpha_sequence':
            alpha_sequence.trigger()
        elif framework == 'no_harm':
            no_harm.trigger('permission')
        elif framework == 'metaphors':
            metaphors.trigger()
        elif framework == 'card_game':
            card_game.trigger()

    # Get next state based on detection
    if detections['present_aware']:
        next_state = parse_next_state(state_row['Next_State_If'])
    else:
        next_state = parse_next_state(state_row['Next_State_Else'])
```

---

## 📚 CLIENT INTENTS

From `intents/client_intents.yml`:

- `session_start` - "I'm stressed, overwhelmed"
- `states_goal` - "I want to feel peaceful"
- `accepts_vision` - "Yes that's what I want"
- `mentions_body` - "My chest feels tight"
- `present_aware` - "I feel it right now"
- `pattern_identified` - "When calendar, then thoughts, then tightness"
- `thinking_mode` - "I think it's because..." ⚠️ REDIRECT
- `past_tense` - "Back then when I was..." ⚠️ REDIRECT
- `strong_emotion` - "SO STRESSED!!!" ⚠️ VALIDATE
- `crying` - [client crying] ⚠️ NORMALIZE
- `silence` - [not speaking] → gentle prompt or card_game

---

## ✅ COMPLETION CRITERIA

Before Stage 2, all must be TRUE:

```python
{
  'goal_stated': True,
  'vision_accepted': True,
  'problem_identified': True,
  'body_awareness_present': True,
  'alpha_complete': True,
  'sentiment_improved': True
}
```

---

## 🎯 KEY POINTS

1. **Frameworks Already Exist** - System just triggers them
2. **Simple State IDs** - Easy to track (1.1, 2.4, THINK, etc.)
3. **RAG + Fallback** - Not hardcoded questions
4. **Detection Routing** - Different paths based on what client says
5. **Priority Redirects** - THINK, PAST, AFFIRM can happen anytime
6. **Framework Triggers** - Show on screen when needed
7. **Natural Flow** - Affirm 60%+ instead of always asking

---

## 📖 FILES TO USE

1. **STAGE1_COMPLETE.csv** - Main state-action pairs (use this!)
2. **intents/client_intents.yml** - Client response types
3. **stories/stage1_complete_stories.yml** - Conversation paths
4. **actions/therapist_actions.json** - Action details

---

**Status:** ✅ Complete - Ready to integrate

**Approach:** Trigger existing frameworks, don't rebuild them

**Integration:** Works with your LLaMA Master + Dialogue agents

---

*AI Therapist Stage 1 - Framework Trigger System*
