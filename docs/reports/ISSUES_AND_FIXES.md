# Critical Issues and Fixes Needed

## Issues Identified from Manual Testing

### 1. Repetitive Questions ❌
**Problem:** System asks "How do you know when that feeling starts?" multiple times (Turns 8, 12, 14)
**Root Cause:** `_generate_affirmation_response()` lines 209-210 don't check if question was recently asked
**Fix Needed:** Add tracking for all questions asked, not just specific ones

### 2. Wrong Body Connection Style ❌
**Problem:** Asking "What's happening in that moment?" instead of Dr. Q's actual approach
**Dr. Q's Actual Style:** "How are you feeling NOW?" - focuses on present moment body connection, NOT past patterns
**Fix Needed:** Change pattern inquiry approach to match Dr. Q's real sessions

### 3. Psycho-Education Not Provided ❌
**Problem:** Never provided zebra-lion brain explanation
**Expected Flow:**
1. Goal stated → Build vision → Vision accepted
2. → **PROVIDE PSYCHO-EDUCATION (zebra-lion)**
3. → THEN ask about problem/body
**Current Flow:** Skips psycho-education, goes straight to body inquiry
**Fix Needed:** Update `psycho_education.py` `should_provide_education()` logic

### 4. Stage Progression Stuck ❌
**Problem:** Session stuck in `1.1.5_psycho_education` for 15+ turns
**Expected:** After psycho-education provided → advance to `1.2_problem_and_body`
**Fix Needed:** Update stage progression logic in `session_state_manager.py`

### 5. Not Using RAG Examples ⚠️
**Problem:** Responses don't match Dr. Q's actual style from transcripts
**Evidence:** Turn 15 response has "Here's a short therapeutic response:" artifact - shows LLM generation not properly using RAG
**Fix Needed:** Improve how RAG examples are incorporated into LLM prompts

### 6. LLM Artifacts in Responses ❌
**Problem:** Turn 15 showed "Here's a short therapeutic response:" in output
**Fix Needed:** Better artifact removal in `_parse_dialogue_response()`

## Proposed Fixes (Priority Order)

### Priority 1: Fix Psycho-Education Timing and Stage Progression
**File:** `psycho_education.py`
**Change:** Update `should_provide_education()` to trigger after vision accepted, before problem inquiry

**File:** `session_state_manager.py`
**Change:** Fix `check_substate_completion()` for 1.1.5_psycho_education to properly advance

### Priority 2: Fix Repetitive Questions
**File:** `improved_ollama_dialogue_agent.py`
**Change:** In `_generate_affirmation_response()`, add comprehensive question tracking:
```python
# Check if we already asked "How do you know..."
if session_state.was_question_asked_recently("How do you know"):
    # Move to next topic instead of repeating
    next_question = "Tell me more about that."
```

### Priority 3: Change Body Connection Style
**File:** `improved_ollama_dialogue_agent.py`
**Change:** Replace "What's happening in that moment?" with Dr. Q's actual style:
- After body location/sensation described → "How are you feeling that NOW?"
- For present moment connection → "What's that like right now?"

### Priority 4: Better RAG Integration
**File:** `improved_ollama_dialogue_agent.py`
**Change:** Update `_construct_improved_dialogue_prompt()` to emphasize RAG examples more:
```
CRITICAL: Study the Dr. Q examples above and ADAPT his exact phrasing style.
Match his warmth, simplicity, and natural conversation flow.
```

### Priority 5: Better LLM Artifact Removal
**File:** `improved_ollama_dialogue_agent.py`
**Change:** Add more artifact patterns to `_parse_dialogue_response()`:
```python
artifact_patterns = [
    "Here's a short therapeutic response:",
    "Here is a short therapeutic response:",
    ...
]
```

## Dr. Q's Actual Stage 1 Flow (from TRT Manual)

```
1. Opening question: "What brings you in?"
2. Client states problem/feeling
3. Acknowledge + Goal clarification: "Yeah, you've been feeling X. What do we want our time to focus on today?"
4. Client states goal (may need menu if "I don't know")
5. Build vision: "Got it. So you want to feel peaceful. I'm seeing you who's calm, at ease, lighter. Does that make sense to you?"
6. Client accepts vision: "Yes"
7. ** PSYCHO-EDUCATION **: "Let me tell you how the brain works... zebra-lion explanation"
8. ** AFTER PSYCHO-EDUCATION **: "So what's been making it hard for you?" (problem inquiry)
9. Client describes problem
10. Body inquiry: "How are you feeling that NOW?" (present moment connection)
11. Continue with body awareness, present moment focus
12. Move to Stage 1.3 (Readiness check)
```

## Test Cases for Verification

After fixes, test these scenarios:

1. **Repetition Test:** Give body location → sensation → affirm. Should NOT ask "How do you know" more than once.
2. **Psycho-Education Test:** State goal → Accept vision → Should get zebra-lion explanation NEXT
3. **Stage Progression Test:** After psycho-education → Should advance to 1.2_problem_and_body
4. **Dr. Q Style Test:** Check if responses match real Dr. Q phrasing from RAG examples
