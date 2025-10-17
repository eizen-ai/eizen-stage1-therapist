# BMAD Testing Protocol for TRT System

## What is BMAD?

**B**ehavior
**M**easurement
**A**nalysis
**D**ocumentation

A structured approach to test, document, and fix issues systematically.

---

## Testing Workflow

### Phase 1: Manual Testing
1. Run the system manually
2. Document observations using BMAD format
3. Identify issues
4. Report findings

### Phase 2: Fix Implementation
1. Review BMAD reports
2. Implement fixes
3. Document changes

### Phase 3: Verification
1. Re-test with same scenarios
2. Confirm fixes work
3. Mark as resolved

---

## BMAD Report Format

Use this exact format for every issue you find:

```markdown
## Issue #[NUMBER]: [SHORT TITLE]

### BEHAVIOR (What Happened)
**State:** [Current substate]
**Turn:** [Turn number]
**Input:** "[Client's input]"
**Output:** "[Therapist's response]"
**Expected:** "[What should have happened]"
**Actual:** "[What actually happened]"

### MEASUREMENT (Quantitative Data)
- Body questions asked: X/3
- Current completion criteria:
  - goal_stated: [true/false]
  - vision_accepted: [true/false]
  - problem_identified: [true/false]
  - body_awareness_present: [true/false]
  - etc.
- Session turn: X
- Processing time: X.Xs

### ANALYSIS (Why It Happened)
**Root Cause:** [Technical explanation]
**Related Code:** [File:line_number]
**Pattern:** [Is this recurring? Similar to other issues?]

### DOCUMENTATION (Fix Required)
**Priority:** [HIGH/MEDIUM/LOW]
**Fix Type:** [Bug Fix / Enhancement / Logic Change]
**Proposed Solution:** [How to fix it]
**Files to Modify:** [List files]
```

---

## Testing Scenarios

### Scenario 1: Full Happy Path
**Goal:** Complete Stage 1 from start to finish

**Test Steps:**
1. Start: "I want to feel less anxious"
2. Vision acceptance: "Yes, that makes sense"
3. Psycho-education: Continue with emotional response
4. Problem: "Work deadlines stress me out"
5. Body location: "My chest"
6. Sensation: "Tight, heavy"
7. Present moment: "Yes, right now"
8. Pattern: "When I see my calendar, I think 'I can't handle this', then my chest tightens"
9. Readiness: "No, that's all"
10. **Alpha sequence:** "Calmer" → "Calmer" → "Much calmer"

**Expected:** Smooth progression through all states including alpha

---

### Scenario 2: No Body Awareness (Escape Route)
**Goal:** Test 3-question limit and alpha trigger

**Test Steps:**
1. Start: "I want peace"
2. Vision: "Yes"
3. Problem: "Everything is overwhelming"
4. Body Q1: "I don't know" or vague answer
5. Body Q2: "I'm not sure" or thinking answer
6. Body Q3: "Maybe my head?" or unclear
7. **Expected:** Force advance to 3.1_assess_readiness
8. **Expected:** Then advance to 3.2_alpha_sequence
9. Test alpha: "Calmer" responses

---

### Scenario 3: Alpha Sequence Resistance
**Goal:** Test alpha normalization

**Test Steps:**
1. Complete states 1.1 → 1.1.5 → 1.2 → 3.1
2. Alpha starts: Lower jaw
3. **Respond:** "It feels weird, more tense"
4. **Expected:** Normalization response
5. **Expected:** Retry checkpoint
6. **Respond:** "Okay, calmer now"
7. Continue sequence

---

### Scenario 4: State Transition Validation
**Goal:** Verify all state transitions

**Check:**
- 1.1_goal_and_vision → 1.1.5_psycho_education ✅
- 1.1.5_psycho_education → 1.2_problem_and_body ✅
- 1.2_problem_and_body → 3.1_assess_readiness ✅
- 3.1_assess_readiness → 3.2_alpha_sequence ✅ (NEW FIX)
- 3.2_alpha_sequence → stage_1_complete ✅ (NEW FIX)

---

## How to Run Test

### Step 1: Start Test Session
```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2
python3 -m src.core.improved_ollama_system
```

### Step 2: Track Progress
Use `status` command during testing to see:
- Current state
- Body questions count
- Completion criteria

### Step 3: Document Issues
Create BMAD report for EVERY issue found

### Step 4: Report Findings
Save all BMAD reports in one file:
```
TEST_FINDINGS_[DATE].md
```

---

## Example BMAD Report

```markdown
## Issue #1: Alpha Sequence Not Triggered After 3.1

### BEHAVIOR
**State:** 3.1_assess_readiness
**Turn:** 8
**Input:** "No, that's all"
**Output:** Session ended at stage_1_complete
**Expected:** Should advance to 3.2_alpha_sequence and run alpha
**Actual:** Went directly to stage_1_complete without alpha

### MEASUREMENT
- Body questions asked: 3/3
- Completion criteria:
  - pattern_understood: true
  - rapport_established: true
- Current substate: stage_1_complete (WRONG - should be 3.2_alpha_sequence)
- Session turn: 8

### ANALYSIS
**Root Cause:** session_state_manager.py line 349-353 returns "stage_1_complete" instead of "3.2_alpha_sequence"
**Related Code:** src/core/session_state_manager.py:353
**Pattern:** This affects ALL sessions - alpha never executes

### DOCUMENTATION
**Priority:** HIGH (Alpha is critical for Stage 1 completion)
**Fix Type:** Logic Change
**Proposed Solution:** Change line 353 to return "3.2_alpha_sequence"
**Files to Modify:**
- src/core/session_state_manager.py
- src/core/improved_ollama_system.py (add alpha handler)
```

---

## Quick Reference: What to Test

### ✅ Core Flow
- [ ] Goal inquiry works
- [ ] Vision building works
- [ ] Psycho-education triggers
- [ ] Problem exploration works
- [ ] Body questions (max 3)
- [ ] Escape route triggers at 3 questions
- [ ] **Alpha sequence executes** (NEW)
- [ ] Alpha checkpoints work
- [ ] Stage 1 completes gracefully

### ✅ Edge Cases
- [ ] Client gives vague answers
- [ ] Client doesn't understand questions
- [ ] Client resists alpha
- [ ] Client provides body info immediately
- [ ] Client rambles or goes off-topic

### ✅ State Transitions
- [ ] All states advance correctly
- [ ] No skipped states
- [ ] No infinite loops
- [ ] Completion criteria tracked correctly

---

## Using Claude for Testing

### For Reporting Issues:
**Just tell me directly in chat:**
- Copy the therapist's response
- Tell me what was wrong
- Mention the turn number
- I'll understand and fix immediately

**No need for formal BMAD format** - I can extract that myself!

### For Testing Fixes:
**After I make changes, just say:**
- "Test the alpha sequence fix"
- "Run scenario 1 again"
- "Check if issue #X is resolved"

**I'll run the test and show you results immediately**

### Fast Workflow:
```
YOU: "Tested scenario 1, alpha didn't trigger at turn 9"
ME: [Makes fix]
ME: [Tests fix]
ME: "Fixed! Alpha now triggers. Please verify?"
YOU: [Re-tests manually]
YOU: "Works!" or "Still has issue X"
```

---

## After Testing

### Collect All BMAD Reports
Create single file with all issues:

```markdown
# Test Session Report - [DATE]

**Tester:** [Your name]
**Duration:** X minutes
**Scenarios Tested:** [List]
**Total Issues Found:** X

---

[Issue #1 BMAD Report]

---

[Issue #2 BMAD Report]

---

## Summary
- Critical issues: X
- Medium priority: X
- Low priority: X
```

---

## Fast Iteration Process with Claude

1. **YOU Test (5-10 min):** Run manual test session
2. **YOU Report (1 min):** "Alpha didn't trigger" or "Got stuck at turn X"
3. **CLAUDE Fixes (5-10 min):** I implement and test fix
4. **YOU Verify (3-5 min):** Quick re-test same scenario
5. **Repeat:** Until all scenarios pass

**Goal:** Multiple short cycles instead of one long test

### What to Tell Claude:

✅ **Good reports:**
- "Alpha didn't start after turn 9 in state 3.1"
- "Therapist repeated same question 3 times"
- "Got stuck in 1.2, kept asking about body"
- "Session ended without running alpha"

❌ **Don't need:**
- Formal BMAD format (Claude will handle)
- Technical analysis (Claude will figure out)
- File names/line numbers (Claude will find)

**Just describe what happened - Claude will fix it!**

---

## Commands During Testing

```bash
# During session
status          # Show current state
quit            # End session

# Check logs
cat logs/improved_manual_YYYYMMDD_HHMMSS.json

# Check Redis (if needed)
curl http://localhost:8090/api/v1/sessions
```

---

## Success Criteria

Session is successful when:
- ✅ All states transition correctly
- ✅ Alpha sequence executes after 3.1
- ✅ Alpha completes with 3 checkpoints
- ✅ Stage 1 reaches completion gracefully
- ✅ No infinite loops
- ✅ No repeated questions
- ✅ Natural conversation flow

---

**Ready to test? Start with Scenario 1 (Happy Path) and document findings!**
