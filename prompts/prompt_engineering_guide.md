# Prompt Engineering Guide

Advanced guide for customizing and optimizing prompts in the TRT AI Therapist system.

---

## Overview

This guide covers:
1. Prompt engineering principles
2. How to modify existing prompts effectively
3. Creating new prompts for custom situations
4. Testing and validating prompt changes
5. Advanced techniques

---

## Prompt Engineering Principles

### 1. Few-Shot Learning

**What it is:** Providing examples in the prompt

**Why it works:** AI learns patterns from examples

**In our system:**
```
You are Dr. Q.

Dr. Q's examples:
1. "Where in your chest? Upper chest or center?"
2. "And where is that tightness?"

CLIENT: "I feel stressed"

Generate response like Dr. Q.
```

**Best practice:** 2-4 examples per prompt (we use 3)

---

### 2. Role Specification

**What it is:** Clearly defining who the AI is

**Why it works:** Sets behavior and tone

**Good:**
```
You are Dr. Q, an expert TRT therapist.
```

**Bad:**
```
You are a helpful assistant.
```

**In our system:** Every prompt starts with "You are Dr. Q."

---

### 3. Explicit Instructions

**What it is:** Clear, specific directions

**Why it works:** Reduces ambiguity

**Good:**
```
Use the EXACT emotion word the client mentioned.
Ask BOTH emotion AND location in one question.
```

**Bad:**
```
Be empathetic and helpful.
```

**In our system:** Every prompt has CRITICAL/IMPORTANT instructions

---

### 4. Constraints and Rules

**What it is:** Explicit do's and don'ts

**Why it works:** Prevents unwanted behaviors

**Example:**
```
CRITICAL:
- Use client's exact words (NOT generic emotions)
- Ask 1-2 sentences ONLY
- Provide multiple options (elaborative style)

NEVER:
- Repeat questions already asked
- Use yes/no questions
- Add explanations or psycho-education
```

---

### 5. Output Format Specification

**What it is:** Define exact output structure

**Why it works:** Ensures consistency

**Example:**
```
YOUR RESPONSE (just the therapist's words, 1-2 sentences):
```

**In our system:** All prompts specify exact output format

---

## Modifying Dialogue Agent Prompts

### Step-by-Step Process

**File:** `src/agents/improved_ollama_dialogue_agent.py`

#### 1. Locate the Prompt Function

Example: Modify emotion inquiry prompt

```python
# Line 1231-1256
def _construct_emotion_inquiry_prompt(self, client_input, rag_examples):
    return f"""
    You are Dr. Q. Client mentioned a problem/stress.

    CLIENT: "{client_input}"

    Dr. Q's examples:
    {rag_examples_text}

    YOUR RESPONSE (1-2 sentences):
    """
```

#### 2. Understand Current Behavior

**What it does now:**
- Asks about emotion AND body location together
- Uses elaborative style with multiple options
- Includes RAG examples

**Example output:**
```
"When you feel stress like that, what do you notice in your body?
Where do you feel it - chest, head, shoulders?"
```

#### 3. Decide What to Change

**Options:**
- Change question style (more/less elaborative)
- Modify tone (formal vs casual)
- Add/remove instructions
- Change output length

#### 4. Make the Change

**Example: Make less elaborative**

```python
def _construct_emotion_inquiry_prompt(self, client_input, rag_examples):
    return f"""
    You are Dr. Q. Client mentioned a problem/stress.

    CLIENT: "{client_input}"

    Dr. Q's style (SIMPLE - direct questions):
    - "What are you feeling?"
    - "Where do you feel it?"

    Ask about emotion. Be direct and simple.

    YOUR RESPONSE (1 short sentence):
    """
```

**Example output after change:**
```
"What are you feeling about that?"
```

#### 5. Test the Change

```bash
# Rebuild Docker
docker compose build --no-cache

# Start services
docker compose up -d

# Test conversation
curl -X POST http://localhost:8090/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_prompt_change",
    "message": "I am stressed about work"
  }'

# Check response matches your modification
```

#### 6. Validate Quality

**Check:**
- ✅ Matches Dr. Q style
- ✅ Appropriate length (1-2 sentences)
- ✅ Follows therapeutic protocol
- ✅ Natural and warm tone
- ✅ No repetition of previous questions

---

## Modifying Master Planning Prompts

### Therapeutic Reasoning Prompt

**File:** `src/agents/ollama_llm_master_planning_agent.py`

**Location:** Lines 353-415

**Current structure:**

```python
def _construct_therapeutic_prompt(self, client_input, session_state, events, processed_input):
    return f"""
    You are Dr. Q, an expert TRT therapist.

    CURRENT CONTEXT:
    - Stage: {session_state.current_stage}
    - Client: "{client_input}"

    COMPLETION STATUS:
    - Goal Stated: ✅/❌

    TRT RULES:
    1. Stage 1.1: Establish goal
    2. Stage 1.2: Explore problem

    NAVIGATION OPTIONS:
    - clarify_goal, build_vision, explore_problem

    Respond in JSON format:
    {{
        "reasoning": "...",
        "navigation_decision": "...",
        "situation_type": "...",
        "rag_query": "..."
    }}
    """
```

### Customization Examples

#### Add New TRT Rule

```python
TRT RULES:
1. Stage 1.1: Establish goal, build future vision
2. Stage 1.2: Explore problem, develop body awareness
3. Stage 1.3: Assess pattern understanding
7. NEW RULE: Always validate before advancing  # ADD THIS
```

#### Add New Navigation Option

```python
NAVIGATION OPTIONS:
- clarify_goal, build_vision, explore_problem
- your_new_option  # ADD THIS

# Then add corresponding RAG query
RAG QUERIES:
- dr_q_goal_clarification
- your_new_rag_query  # ADD THIS
```

#### Change Decision Criteria

```python
# Make vision building optional
TRT RULES:
1. Stage 1.1: Establish goal (vision optional)  # MODIFIED
```

---

## Creating New Prompts

### When to Create a New Prompt

Create a new focused prompt when:
1. Specific situation needs unique handling
2. Existing prompts don't cover the case
3. Want to enforce specific style for situation

### Template for New Prompt

```python
def _construct_your_new_prompt(self, client_input, session_state, rag_examples):
    """
    YOUR PROMPT DESCRIPTION

    When used: [Specific triggering condition]
    Expected output: [What response should look like]
    """

    # Extract context
    emotion = session_state.most_recent_emotion_or_problem
    goal = session_state.tracked_goal

    # Format RAG examples
    rag_examples_text = "\n".join([
        f'{i+1}. "{ex["doctor_example"]}"'
        for i, ex in enumerate(rag_examples[:3])
    ])

    # Build prompt
    return f"""
You are Dr. Q, an expert TRT therapist.

CONTEXT:
- Client just provided: [what they provided]
- Therapeutic goal: [what you want to achieve]

CLIENT: "{client_input}"

Dr. Q's examples:
{rag_examples_text}

Dr. Q's style:
- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]

CRITICAL INSTRUCTIONS:
1. [Must do #1]
2. [Must do #2]

NEVER:
- [Must not do #1]
- [Must not do #2]

YOUR RESPONSE (just the therapist's words, 1-2 sentences):
"""
```

### Example: New "Clarification" Prompt

```python
def _construct_clarification_prompt(self, client_input, session_state, rag_examples):
    """
    Ask for clarification when client response is unclear

    When used: Client gives vague or ambiguous answer
    Expected output: Gentle clarification question
    """

    last_question = session_state.conversation_history[-1]['therapist_response']

    rag_examples_text = "\n".join([
        f'{i+1}. "{ex["doctor_example"]}"'
        for i, ex in enumerate(rag_examples[:3])
    ])

    return f"""
You are Dr. Q. You just asked: "{last_question}"

CLIENT: "{client_input}"

The client's response is unclear. Ask a gentle clarification question.

Dr. Q's clarification style:
- "Can you say more about that?"
- "What do you mean by [their words]?"
- "I'm not sure I understand. Could you explain?"

Be warm, non-judgmental, use their exact words.

YOUR RESPONSE (1 sentence):
"""
```

### Integrate New Prompt

**Step 1:** Add function to dialogue agent class

```python
# In improved_ollama_dialogue_agent.py
class ImprovedOllamaDialogueAgent:

    def _construct_clarification_prompt(self, client_input, session_state, rag_examples):
        # [prompt code here]
```

**Step 2:** Add triggering logic

```python
# In _construct_general_prompt or create new function
def generate_response(self, navigation_output, client_input, session_state):

    # Check if clarification needed
    if self._needs_clarification(client_input):
        prompt = self._construct_clarification_prompt(
            client_input, session_state, rag_examples
        )
        return self._call_ollama(prompt)

    # Otherwise use existing prompts
    ...
```

**Step 3:** Add detection function

```python
def _needs_clarification(self, client_input):
    """Detect if response is too vague"""
    vague_responses = ["i don't know", "maybe", "sort of", "kind of", "idk"]
    return any(phrase in client_input.lower() for phrase in vague_responses)
```

---

## Advanced Techniques

### 1. Dynamic Example Selection

**Current:** Always use top 3 RAG examples

**Advanced:** Select examples based on similarity threshold

```python
def get_high_quality_examples(self, rag_examples):
    """Only use examples with high similarity"""
    return [
        ex for ex in rag_examples
        if ex['similarity_score'] > 0.85  # High quality only
    ]
```

### 2. Context-Aware Prompting

**Current:** Same prompt structure for all situations

**Advanced:** Adjust prompt based on session progress

```python
def _construct_adaptive_prompt(self, client_input, session_state, rag_examples):

    turn_count = len(session_state.conversation_history)

    if turn_count <= 3:
        # Early session - more guidance
        style_note = "Be warm and welcoming. Build rapport."
    elif turn_count <= 10:
        # Mid session - focus on exploration
        style_note = "Focus on body awareness exploration."
    else:
        # Late session - prepare for intervention
        style_note = "Assess readiness for alpha sequence."

    return f"""
    You are Dr. Q. Session turn {turn_count}.

    {style_note}

    CLIENT: "{client_input}"
    ...
    """
```

### 3. Multi-Turn Consistency

**Problem:** AI forgets what was asked 3-4 turns ago

**Solution:** Include conversation summary in prompt

```python
def _construct_context_aware_prompt(self, client_input, session_state, rag_examples):

    # Summarize what's been asked
    asked_about = []
    for exchange in session_state.conversation_history[-5:]:
        therapist_q = exchange['therapist_response']
        if "where" in therapist_q.lower() and "body" in therapist_q.lower():
            asked_about.append("body location")
        if "what kind" in therapist_q.lower() and "sensation" in therapist_q.lower():
            asked_about.append("sensation quality")

    already_asked = ", ".join(asked_about)

    return f"""
    You are Dr. Q.

    ALREADY ASKED ABOUT: {already_asked}

    CLIENT: "{client_input}"

    Ask about something NEW (not already covered).
    ...
    """
```

### 4. Fallback Chaining

**Problem:** Sometimes RAG returns no examples

**Solution:** Chain of fallbacks

```python
def get_examples_with_fallback(self, navigation_output, client_input):

    # Try 1: Specific RAG query
    examples = self.rag_system.get_few_shot_examples(
        navigation_output, client_input, context_filter=rag_query
    )

    if len(examples) >= 2:
        return examples

    # Try 2: General RAG query
    examples = self.rag_system.get_few_shot_examples(
        navigation_output, client_input, context_filter="general_dr_q_approach"
    )

    if len(examples) >= 2:
        return examples

    # Try 3: Hardcoded fallback examples
    return self._get_hardcoded_examples(navigation_output['situation_type'])
```

### 5. Prompt Compression

**Problem:** Long prompts slow down inference

**Solution:** Compress context while keeping key info

```python
def _construct_compressed_prompt(self, client_input, rag_examples):

    # Compress examples
    compressed_examples = "\n".join([
        f'{i+1}. {ex["doctor_example"][:80]}...'  # Truncate to 80 chars
        for i, ex in enumerate(rag_examples[:2])  # Use only 2 examples
    ])

    return f"""
Dr. Q therapist.

Examples:
{compressed_examples}

Client: "{client_input}"

1-2 sentences:
"""
```

**Trade-off:** Faster, but less context for AI

---

## Testing Prompts

### Unit Testing

Create test cases for each prompt:

```python
# tests/test_prompts.py

def test_emotion_inquiry_prompt():
    agent = ImprovedOllamaDialogueAgent()

    # Test input
    client_input = "I'm stressed about work"
    rag_examples = [
        {"doctor_example": "Where do you feel that stress?"}
    ]

    # Generate prompt
    prompt = agent._construct_emotion_inquiry_prompt(
        client_input, rag_examples
    )

    # Assertions
    assert "Dr. Q" in prompt
    assert client_input in prompt
    assert "Where do you feel" in rag_examples[0]['doctor_example']
    assert "YOUR RESPONSE" in prompt
```

### Integration Testing

Test full conversation flow:

```bash
# Start test conversation
curl -X POST http://localhost:8090/api/session/start \
  -H "Content-Type: application/json" \
  -d '{"session_id": "prompt_test"}'

# Send test message
curl -X POST http://localhost:8090/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "prompt_test",
    "message": "I want to feel calm but work is stressing me out"
  }'

# Check response quality
# - Matches Dr. Q style?
# - Appropriate length?
# - Follows protocol?
```

### A/B Testing

Compare prompt variants:

```python
def ab_test_prompts():
    """Test two prompt variants"""

    test_inputs = [
        "I'm stressed",
        "My chest hurts",
        "I feel anxious"
    ]

    results_a = []
    results_b = []

    for input in test_inputs:
        # Test prompt A (current)
        response_a = generate_with_prompt_a(input)
        results_a.append(response_a)

        # Test prompt B (new variant)
        response_b = generate_with_prompt_b(input)
        results_b.append(response_b)

    # Compare quality
    print("Prompt A avg length:", np.mean([len(r) for r in results_a]))
    print("Prompt B avg length:", np.mean([len(r) for r in results_b]))

    # Manual quality review
    for i, (a, b) in enumerate(zip(results_a, results_b)):
        print(f"\nInput {i+1}: {test_inputs[i]}")
        print(f"A: {a}")
        print(f"B: {b}")
        print("Which is better? (a/b): ", end="")
```

---

## Common Modifications

### Make Questions Less Elaborative

**Before:**
```python
Dr. Q's style (ELABORATIVE - multiple options):
- "Where in your body? Chest, head, shoulders?"
- "What kind of sensation? Achy, tight, stabbing?"
```

**After:**
```python
Dr. Q's style (SIMPLE - direct):
- "Where in your body?"
- "What kind of sensation?"
```

### Add More Context to Prompts

**Before:**
```python
CLIENT: "{client_input}"
```

**After:**
```python
CONTEXT:
- Goal: {session_state.tracked_goal}
- Problem: {session_state.tracked_problem}
- Body location: {session_state.body_location}

CLIENT: "{client_input}"
```

### Adjust Response Length

**Before:**
```python
YOUR RESPONSE (1-2 sentences):
```

**After (shorter):**
```python
YOUR RESPONSE (1 short sentence, max 15 words):
```

**After (longer):**
```python
YOUR RESPONSE (2-3 sentences with validation and question):
```

### Change Tone

**Before (warm):**
```python
Be warm, empathetic, and validating.
```

**After (neutral):**
```python
Be professional and direct.
```

**After (very warm):**
```python
Be extremely warm, validating, and gentle. Use affirmations.
```

---

## Prompt Optimization Checklist

When creating or modifying prompts:

- [ ] **Role clearly defined** ("You are Dr. Q")
- [ ] **Context provided** (client input, session state)
- [ ] **Examples included** (2-4 RAG examples)
- [ ] **Style specified** (elaborative, warm, concise)
- [ ] **Critical instructions** (MUST do / NEVER do)
- [ ] **Output format** (1-2 sentences, just therapist words)
- [ ] **Variables filled** (emotion, body part, goal)
- [ ] **Fallback handling** (what if no RAG examples?)
- [ ] **Tested** (generates expected output?)
- [ ] **Validated** (matches Dr. Q style?)

---

## Troubleshooting

### Problem: AI ignores instructions

**Solution:** Make instructions more explicit

```python
# Before
"Use client's emotion word"

# After
CRITICAL: Use the EXACT emotion word the client mentioned.
For example, if client says "stressed", use "stressed" NOT "anxious" or "worried".
```

### Problem: Responses too long

**Solution:** Add strict length constraint

```python
# Before
"1-2 sentences"

# After
"1 sentence ONLY. Maximum 20 words. NO explanations."
```

### Problem: Not matching Dr. Q style

**Solution:** Add more RAG examples and style guidelines

```python
# Increase examples
max_examples=5  # Was 3

# Add explicit style rules
Dr. Q ALWAYS:
- Gives multiple options
- Uses client's exact words
- Asks open questions
- Stays present-focused
```

### Problem: Repeating questions

**Solution:** Add conversation history check

```python
LAST 3 THERAPIST QUESTIONS:
1. "{last_q_1}"
2. "{last_q_2}"
3. "{last_q_3}"

CRITICAL: Do NOT ask anything similar to the above questions.
```

---

## Best Practices

### 1. Start with Examples

Always show AI what you want through examples, not just instructions.

### 2. Be Specific

"Ask about body location" → "Ask where in their body they feel the sensation. Provide 3 specific options."

### 3. Use Constraints

Tell AI what NOT to do, not just what to do.

### 4. Test Iteratively

Make small changes, test, refine. Don't change everything at once.

### 5. Monitor in Production

Log prompts and responses to identify issues.

### 6. Version Control

Keep old prompts commented out for rollback:

```python
# OLD VERSION (pre-2025-10-17)
# def _construct_emotion_inquiry_prompt_v1(...)
#     return "..."

# CURRENT VERSION (2025-10-17)
def _construct_emotion_inquiry_prompt(...)
    return "..."
```

---

## Resources

### Learn More

- **Prompt Engineering Guide:** https://www.promptingguide.ai/
- **OpenAI Best Practices:** https://platform.openai.com/docs/guides/prompt-engineering
- **Few-Shot Learning:** https://arxiv.org/abs/2005.14165

### Our Documentation

- [Dialogue Agent Prompts](./dialogue_prompts.md) - Current prompts
- [Master Planning Prompts](./master_planning_prompts.md) - Navigation prompts
- [RAG System](./rag_system.md) - Example retrieval

---

**Last Updated:** 2025-10-17
**Version:** 1.0
