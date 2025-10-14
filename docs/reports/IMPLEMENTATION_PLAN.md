# Implementation Plan for Dr. Q Style Fixes

## Summary
The current system has several issues preventing it from matching Dr. Q's actual therapeutic style. This plan outlines specific code changes needed to fix these issues.

## Key Changes Needed

### 1. Psycho-Education Module Fix
**File:** `code_implementation/psycho_education.py`

**Current Problem:** `should_provide_education()` never returns True

**Root Cause Analysis:** Need to check the actual logic

**Proposed Fix:**
```python
def should_provide_education(self, session_state):
    # Provide psycho-education AFTER vision accepted, BEFORE problem inquiry
    completion = session_state.stage_1_completion

    # Trigger conditions:
    # 1. Vision has been accepted
    # 2. Psycho-education not yet provided
    # 3. Currently in 1.1_goal_and_vision or just transitioned

    if (completion.get("vision_accepted", False) and
        not completion.get("psycho_education_provided", False) and
        not self.education_provided):
        return True

    return False
```

### 2. Stage Progression Fix
**File:** `code_implementation/session_state_manager.py`

**Current Problem:** Stuck in 1.1.5_psycho_education, never advances to 1.2

**Proposed Fix:** Update `check_substate_completion()`:
```python
elif self.current_substate == "1.1.5_psycho_education":
    # After psycho-education provided AND client understands, advance
    if (self.stage_1_completion.get("psycho_education_provided", False)):
        # Don't wait for "education_understood" - advance immediately after providing
        return True, "1.2_problem_and_body"
    return False, None
```

### 3. Repetitive Question Tracking
**File:** `code_implementation/improved_ollama_dialogue_agent.py`

**Current Problem:** Asks "How do you know when that feeling starts?" multiple times

**Proposed Fix:** In `_generate_affirmation_response()` around line 209:
```python
elif not session_state.pattern_inquiry_asked:
    # Check if we already asked this recently
    candidate_q = "How do you know when that feeling starts? What's happening in that moment?"
    if not session_state.was_question_asked_recently("How do you know"):
        next_question = candidate_q
        session_state.pattern_inquiry_asked = True  # Mark as asked
    else:
        # Already asked, move on
        session_state.pattern_inquiry_asked = True
        next_question = "Tell me more about that."
```

### 4. Dr. Q Body Connection Style
**File:** `code_implementation/improved_ollama_dialogue_agent.py`

**Current Problem:** Using "What's happening in that moment?" instead of "How are you feeling NOW?"

**Dr. Q's Actual Approach:**
- He asks "How are you feeling that NOW?" to connect client to present moment body sensations
- NOT asking about past patterns or triggers yet

**Proposed Fix:** Replace pattern inquiry with present moment inquiry:
```python
# OLD (line 210):
next_question = "How do you know when that feeling starts? What's happening in that moment?"

# NEW:
next_question = "How are you feeling that NOW?"
```

Also update the present moment confirmation check:
```python
# After client mentions body sensation
elif not session_state.present_moment_confirmed:
    next_question = "How are you feeling that NOW?"
    session_state.present_moment_confirmed = True
```

### 5. LLM Artifact Removal
**File:** `code_implementation/improved_ollama_dialogue_agent.py` in `_parse_dialogue_response()`

**Current Problem:** "Here's a short therapeutic response:" appearing in output

**Proposed Fix:** Add to artifact_patterns list:
```python
artifact_patterns = [
    "Here's a short therapeutic response:",
    "Here is a short therapeutic response:",
    "Here's a therapeutic response:",
    "Since the client",
    "Since they",
    "Given that",
    "Because the",
    "I'll respond with:",
    "I will say:",
    "My response is:",
    "I'll ask:",
    "I'm going to"
]

# Also add better cleaning:
for pattern in artifact_patterns:
    if pattern in response:
        # Remove everything before the actual response
        response = response.split(pattern, 1)[-1].strip()
        response = response.strip(':"\'').strip()
```

### 6. Better RAG Integration
**File:** `code_implementation/improved_ollama_dialogue_agent.py` in `_construct_improved_dialogue_prompt()`

**Current Problem:** LLM not adapting Dr. Q's style from RAG examples

**Proposed Fix:** Strengthen the RAG instruction:
```python
DR. Q EXAMPLES - STUDY THESE CAREFULLY AND MATCH HIS EXACT STYLE:
{rag_examples_text}

CRITICAL INSTRUCTION:
- The examples above show Dr. Q's ACTUAL responses from real sessions
- ADAPT his exact phrasing, warmth, and simplicity
- Use similar sentence structures and word choices
- Match his natural, conversational tone
- DO NOT add clinical language or formal phrasing
```

## Implementation Order

1. **First:** Fix psycho-education timing (most critical for stage flow)
2. **Second:** Fix stage progression (unblocks the stuck state)
3. **Third:** Fix repetitive questions (improves conversation quality)
4. **Fourth:** Update body connection style (matches Dr. Q's actual approach)
5. **Fifth:** Better artifact removal (cleaner responses)
6. **Sixth:** Better RAG integration (overall style improvement)

## Testing After Each Fix

After implementing each fix, test with this conversation flow:
```
YOU: i am feeling annoyed
EXPECTED: "Yeah, you've been feeling annoyed. What do we want our time to focus on today?"

YOU: i want to feel peaceful
EXPECTED: "Got it. So you want to feel peaceful. I'm seeing you who's peaceful, at ease, lighter. Does that make sense to you?"

YOU: yes
EXPECTED: [PSYCHO-EDUCATION - zebra-lion explanation]

YOU: yes that makes sense
EXPECTED: "Good. So what's been making it hard for you?" [Problem inquiry - should now be in 1.2_problem_and_body]

YOU: i feel stressed
EXPECTED: "How are you feeling that NOW?" [Present moment body connection]
```

## Questions for Review

Before I implement, please confirm:

1. **Psycho-education timing:** Should it happen immediately after vision accepted, or only when client says "yes" to "Does that make sense to you?"

2. **Stage progression:** Should we advance to 1.2_problem_and_body immediately after providing psycho-education, or wait for client to acknowledge understanding?

3. **Body connection:** Is "How are you feeling that NOW?" the right Dr. Q phrasing, or should it be something else from his actual sessions?

4. **Pattern inquiry:** Should we eliminate "How do you know when that starts?" entirely from Stage 1, or just use it less frequently?

Please review and let me know if this approach matches Dr. Q's actual methodology!
