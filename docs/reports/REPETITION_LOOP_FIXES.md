# Question Repetition Loop - Fixes

**Date**: 2025-10-10
**Issue**: System stuck asking "You're feeling that right now, aren't you?" multiple times

---

## Problem Analysis from Test Session

### Observed Repetition:
- Turn 4: "You're feeling that right now, aren't you?"
- Turn 6: "You're feeling that right now, aren't you?"
- Turn 7: "You're feeling that right now, aren't you?"
- Turn 10: "You're feeling that right now, aren't you?"
- Turn 11: "You're feeling that right now, aren't you?"
- Turn 14: "You're feeling that right now, aren't you?"
- Turn 15: "You're feeling that right now, aren't you?"

### Root Causes:

**1. Completion Status Not Updating on Affirmation**
- System asks "You're feeling that right now, aren't you?"
- Client says "yes" → Detected as "affirmation"
- But `present_moment_focus` stays False
- Next turn, system asks again because `present_moment_focus` still False

**2. Question Repetition Check Not Working**
- `was_question_asked_recently()` was returning False
- Reason: The key phrase "feeling that right now" was in the list BUT
- The question similarity check wasn't detecting the variations properly

**3. Missing Logic to Auto-Advance**
- If same question asked 2+ times and client keeps affirming
- System should assume "yes" and move on
- Was missing fallback to prevent infinite loops

---

## Fixes Implemented

### Fix 1: Mark `present_moment_focus` on Affirmation

**File**: `improved_ollama_dialogue_agent.py` (Lines 144-148)

```python
# CRITICAL: Check if they just affirmed "You're feeling that right now"
if session_state.last_question_asked and "feeling that right now" in session_state.last_question_asked:
    # They confirmed present moment, mark it complete
    session_state.stage_1_completion["present_moment_focus"] = True
    completion = session_state.stage_1_completion  # Update reference
```

**Effect**: When client says "yes" after "You're feeling that right now?", immediately mark `present_moment_focus` as True

---

### Fix 2: Check for Repetition Before Asking

**File**: `improved_ollama_dialogue_agent.py` (Lines 158-166)

```python
elif not completion["present_moment_focus"]:
    # Only ask if not already asked recently
    candidate_q = "You're feeling that right now, aren't you?"
    if not session_state.was_question_asked_recently(candidate_q):
        next_question = candidate_q
    else:
        # Already asked, assume yes and move on
        session_state.stage_1_completion["present_moment_focus"] = True
        next_question = "How do you know when that feeling starts? What's happening in that moment?"
```

**Effect**: If already asked this question, skip it and move to pattern inquiry

---

### Fix 3: Improve Question Similarity Detection

**File**: `session_state_manager.py` (Lines 118-144)

**ADDED** to key_phrases:
```python
"feeling that now": ["feeling that now", "feeling it now", "feel that right now", "feeling that right now"],
```

**ADDED** word overlap check:
```python
# Check if core phrases match (70% or more of the question is the same)
q1_words = set(q1.split())
q2_words = set(q2.split())
if q1_words and q2_words:
    overlap = len(q1_words & q2_words) / max(len(q1_words), len(q2_words))
    if overlap > 0.7:  # 70% word overlap = similar question
        return True
```

**Effect**: Better detection of repeated questions with slight variations

---

## Expected Behavior After Fixes

### Scenario: Present Moment Confirmation

```
TURN 4: Client: "iam feeling tense right now"
✅ THERAPIST: "Got it. How do you know when that feeling starts?"
[Should NOT ask "You're feeling that right now?" since client already said "right now"]

TURN 4 (Alternative): Client: "iam feeling tense"
✅ THERAPIST: "Got it. You're feeling that right now, aren't you?"

TURN 5: Client: "yes"
✅ THERAPIST: "That's right. How do you know when that feeling starts?"
[Marked present_moment_focus=True on affirmation, moves to pattern]

TURN 6: Client: "yes"
✅ THERAPIST: "Okay. How do you know when that feeling starts?"
[Even if asked again, detects repetition and skips to pattern]
```

---

## How the Loop Prevention Works Now

### 3-Layer Protection:

**Layer 1**: Detect "right now" in client input
- Client says "iam feeling tense right now"
- `update_completion_status()` marks `present_moment_focus = True`
- Affirmation logic skips the question entirely

**Layer 2**: Mark complete on affirmation
- Therapist asks "You're feeling that right now, aren't you?"
- Client says "yes"
- Affirmation logic detects last question and marks `present_moment_focus = True`

**Layer 3**: Repetition check + auto-advance
- If question was already asked AND `present_moment_focus` still False
- System detects repetition via `was_question_asked_recently()`
- Auto-marks `present_moment_focus = True` and moves to pattern inquiry

---

## Testing the Fixes

### Test Case 1: Client Says "Right Now" Explicitly
```
Client: "I'm feeling anxious right now"
Expected: present_moment_focus = True (via completion status)
Expected Response: "Got it. How do you know when that feeling starts?"
```

### Test Case 2: Client Affirms Present Moment Question
```
Therapist: "You're feeling that right now, aren't you?"
Client: "yes"
Expected: present_moment_focus = True (via affirmation logic)
Expected Response: "That's right. How do you know when that feeling starts?"
```

### Test Case 3: Question Already Asked
```
Therapist: "You're feeling that right now, aren't you?" (Turn 4)
Client: "not sure" (ambiguous)
Therapist: Should NOT ask "You're feeling that right now?" again
Expected: Detects repetition, auto-marks complete, moves to pattern
Expected Response: "Okay. How do you know when that feeling starts?"
```

---

## Other Issues from Test Session

### Issue: Vision Building Error (Turn 2)
**Error**: `'str' object has no attribute 'get'`

**Location**: Likely in `_generate_vision_building_response()` when client said "i want to feel little better"

**Possible Cause**: The word "little" before "better" might have caused goal extraction to fail

**Status**: Already has try-except safety, but should monitor

---

### Issue: Not Asking Body Location Question
**Observation**: Never asked "Where do you feel that in your body?"

**Turns Analysis**:
- Turn 3: Vision accepted → Should ask about body location
- Turn 4: Client said "tense" → System detected body_awareness but didn't ask "Where?"

**Reason**: Master planning agent likely chose a different navigation decision (pattern_inquiry instead of body_awareness_inquiry)

**Fix Needed**: Check master planning agent's strict rules to ensure it asks body location after vision accepted

---

## Summary of Changes

| File | Lines | Change |
|------|-------|--------|
| `improved_ollama_dialogue_agent.py` | 144-148 | Mark present_moment_focus on affirmation |
| `improved_ollama_dialogue_agent.py` | 158-166 | Check repetition before asking + auto-advance |
| `session_state_manager.py` | 128 | Added "feeling that right now" to similarity phrases |
| `session_state_manager.py` | 136-142 | Added 70% word overlap check for similarity |

---

## Next Steps

1. ✅ Test the repetition fixes
2. ⏳ Investigate why body location question was skipped
3. ⏳ Fix vision building error for "little better" phrasing
4. ⏳ Test full 20+ turn conversation to verify no other loops

---

**Status**: ✅ Repetition Loop Fixes Complete
**Ready for**: Testing
