# TRT AI Therapist - Prompts Documentation

This directory contains documentation of all prompts used by the TRT AI Therapist system, allowing you to understand exactly how the AI generates therapeutic responses.

---

## Overview

The TRT system uses **two main AI agents**, each with specialized prompts:

1. **Master Planning Agent** - Decides "what to say" (navigation, stage detection)
2. **Dialogue Agent** - Decides "how to say it" (response generation in Dr. Q's style)

---

## Directory Structure

```
prompts/
├── README.md                          # This file - Overview and quick start
├── dialogue_prompts.md                # ✅ All dialogue agent prompts (6 prompts)
├── master_planning_prompts.md         # ✅ Navigation decision prompts (6 rules + LLM)
├── rag_system.md                      # ✅ RAG retrieval system explained
└── prompt_engineering_guide.md        # ✅ Advanced customization guide
```

**All files created! ✅** You can now view and modify all prompts externally.

---

## Quick Reference

### Master Planning Agent

**Purpose:** Analyze client input and decide current therapeutic stage/substate

**Location:** `src/agents/ollama_llm_master_planning_agent.py`

**Key Decisions:**
- Current TRT stage (1.1, 1.2, 1.3, etc.)
- Situation type (goal_inquiry, body_exploration, etc.)
- Next action (ask_emotion, ask_body_location, start_alpha, etc.)
- RAG query for retrieving Dr. Q examples

---

### Dialogue Agent

**Purpose:** Generate therapeutic responses in Dr. Q's style

**Location:** `src/agents/improved_ollama_dialogue_agent.py`

**Prompt Types:**
1. **Focused Prompts** - Specialized for specific situations
   - Initial goal inquiry
   - Emotion exploration
   - Body location questions
   - Sensation quality questions
   - Problem clarification
   - Alpha sequence guidance

2. **General Prompt** - Fallback for all other situations

---

## How It Works (Example)

### Client Input
```
"I'm stressed about work deadlines"
```

### Step 1: Master Planning
**Input to Master Agent:**
- Client message
- Conversation history
- Current session state

**Master Agent Analyzes:**
- Emotion mentioned: "stressed"
- Problem mentioned: "work deadlines"
- Current stage: Should ask about body location

**Output:**
```json
{
  "current_stage": "1.2_problem_and_body",
  "situation_type": "emotion_to_body",
  "rag_query": "dr_q_body_location_inquiry",
  "next_action": "ask_body_location"
}
```

### Step 2: RAG Retrieval
**Query:** Find similar Dr. Q examples for "body location inquiry"

**Retrieved Examples:** (Top 3)
1. "Where in your chest? Upper chest, center, or more to the side?"
2. "And where is that tightness? What part of your body?"
3. "When you notice that feeling, where is it? Chest, throat, stomach?"

### Step 3: Dialogue Generation
**Dialogue Agent receives:**
- Client message: "I'm stressed about work deadlines"
- Tracked emotion: "stress from work"
- Situation: "emotion_to_body"
- Dr. Q examples: [3 examples above]

**Dialogue Agent uses focused prompt:**
```
You are Dr. Q. Client just mentioned emotion: "stress from work"

Dr. Q examples:
1. "Where in your chest?..."
2. "And where is that tightness?..."
3. "When you notice that feeling?..."

Generate response like Dr. Q - elaborate with multiple options.
Use exact emotion: "stress from work"
```

**Generated Response:**
```
"When you feel that stress from work, where in your body do you
notice it? What location comes to mind first?"
```

---

## Prompt Customization

All prompts can be customized by modifying the agent files:

### Master Planning Prompts
**File:** `src/agents/ollama_llm_master_planning_agent.py`
**Function:** `_construct_master_prompt()`
**Lines:** ~100-200

### Dialogue Agent Prompts
**File:** `src/agents/improved_ollama_dialogue_agent.py`
**Functions:**
- `_construct_initial_goal_prompt()` - Lines ~1200
- `_construct_emotion_inquiry_prompt()` - Lines ~1240
- `_construct_emotion_to_body_prompt()` - Lines ~1270
- `_construct_sensation_quality_prompt()` - Lines ~1330
- `_construct_problem_inquiry_prompt()` - Lines ~1400
- `_construct_general_prompt()` - Lines ~1470

---

## See Also

- [Dialogue Agent Prompts](./dialogue_prompts.md) - All 6 response generation prompts
- [Master Planning Prompts](./master_planning_prompts.md) - Navigation and decision-making
- [RAG System](./rag_system.md) - How Dr. Q examples are retrieved
- [Prompt Engineering Guide](./prompt_engineering_guide.md) - Advanced customization

---

## Key Principles

Our prompts follow these principles:

1. **Few-shot Learning** - Always include Dr. Q examples
2. **Elaborative Style** - Multiple options, not yes/no questions
3. **Tracking Accuracy** - Use exact emotion/problem client mentioned
4. **Context-Aware** - Different prompts for different situations
5. **Concise Output** - 1-2 sentences, therapist style

---

For detailed prompt code, see the documentation files in this directory.
