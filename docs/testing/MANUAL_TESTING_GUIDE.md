# Manual Testing Guide - Interactive Feedback Workflow

**Purpose:** Test the TRT Stage 1 system manually and collaborate on improvements

---

## Quick Start

### 1. Run Test Session

```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2
source venv/bin/activate
cd src/core
python improved_ollama_system.py
```

### 2. Play the Role of Client

Type responses as if you were a real client seeking therapy. The AI will respond as the therapist.

### 3. Take Notes

As you test, note any issues:
- Wrong state transitions
- Inappropriate responses
- Logic errors
- Loops or stuck behavior
- Spelling/grammar issues
- Anything that feels "off"

### 4. Share Results

After the session, you'll find a log file in `logs/improved_manual_YYYYMMDD_HHMMSS.json`

---

## How to Share Feedback With Me

### Option 1: Share the Log File (Easiest)

Just paste the contents of your session log file. I can analyze:
- Exact conversation flow
- State transitions
- Where it went wrong
- What fixes are needed

**Example:**
```
"Here's my test session that got stuck in a loop:
[paste logs/improved_manual_20251014_073045.json contents]

Issues I noticed:
1. Got stuck asking about body location 5 times
2. Didn't recognize I mentioned 'chest' on turn 3
3. Never advanced past state 2.2"
```

### Option 2: Quick Summary Format

```
TEST SESSION SUMMARY
Date: [date]
Duration: [X turns / Y minutes]
Final State: [state ID]

ISSUE #1:
Turn: [X]
Client Said: "[your input]"
Therapist Said: "[AI response]"
Expected: [what should have happened]
Actual: [what actually happened]
State: [current_substate]

ISSUE #2:
...
```

### Option 3: Live Testing (Real-Time)

You can also test while I'm active and share issues immediately:
- Copy-paste the turn-by-turn dialogue
- Tell me where it feels wrong
- I'll diagnose and suggest fixes on the spot

---

## What I Can Fix

Based on your feedback, I can modify:

### ✅ **State Machine Logic (CSV)**
- Adjust when states transition
- Modify detection logic
- Change routing rules
- Add/remove states

### ✅ **Session State Manager**
- Completion criteria logic
- Problem identification thresholds
- Body awareness detection
- Pattern recognition

### ✅ **Master Planning Agent**
- Navigation decisions
- Intent classification
- Priority state handling
- Escape routes

### ✅ **Dialogue Agent**
- Response generation
- RAG queries
- Fallback responses
- Affirmation vs. questioning ratio

### ✅ **Input Preprocessing**
- Spelling correction rules
- Emotion detection
- Safety triggers
- Context awareness

---

## Test Scenarios to Try

### Scenario 1: Happy Path (Should Work Smoothly)

**Your Responses:**
1. "I've been feeling really stressed lately"
2. "I want to feel calm and at peace"
3. "Yes, that sounds good"
4. "Yes, I'm willing to try"
5. [After psycho-ed:] "That makes sense"
6. "Work has been overwhelming, constant deadlines"
7. "I feel it in my chest"
8. "It's tight, like a knot"
9. "Yes, I feel it right now"
10. "When I see my calendar fill up, I think 'I can't handle this', then I feel the tightness"

**Expected Result:**
- Should advance through states 1.1 → 1.2 → 1.3 → 1.1.5 → 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 3.1
- Should NOT loop on any state
- Should reach alpha readiness (3.1) within 10-12 turns

---

### Scenario 2: Vague Responses (Tests Problem Identification)

**Your Responses:**
1. "I don't know, just not feeling great"
2. "I guess... less stressed?"
3. "Sure"
4. "Okay"
5. [After psycho-ed:] "I guess"
6. "Just... everything"
7. "I don't know"
8. "Nowhere really"

**Expected Result:**
- Should gently guide you to be more specific
- Should NOT loop infinitely
- Should eventually advance even with vague responses
- After 3 body attempts, should escape to alpha (3.1)

---

### Scenario 3: No Body Awareness (Tests Escape Route)

**Your Responses:**
1. "I'm stressed about work"
2. "I want to feel better"
3. "Yes"
4. "Okay"
5. [After psycho-ed:] "Yes, makes sense"
6. "My boss is demanding, deadlines are tight, too much to do"
7. "I don't feel anything in my body"
8. "No, I don't notice anything physical"
9. "Still nothing"

**Expected Result:**
- Should ask about body 3 times MAX
- After 3 attempts, should say something like "⚠️ MAX body questions (3) reached"
- Should advance to state 3.1 (alpha sequence will develop body awareness)
- Should NOT keep asking "where do you feel it?"

---

### Scenario 4: Spelling Test

**Your Responses:**
- "I feel it right now" → should stay "right now"
- "It feels tight" → should stay "tight"
- "My chest feels right" → might correct to "tight" (context-dependent)
- "I'm light headed" → should stay "light headed"

**Expected Result:**
- Context-appropriate corrections only
- No "right now" → "tight now" errors

---

### Scenario 5: Past Tense (Tests Redirect)

**Your Responses:**
1. "I've been stressed"
2. "I want to feel calm"
3. "Yes"
4. "Okay"
5. [After psycho-ed:] "When I was younger, my parents were very demanding..."
6. [Continue with past story]

**Expected Result:**
- Should redirect: "That was then. Right now, what are you FEELING?"
- After 3 attempts, should direct to alpha (3.2) for present-moment grounding
- Should NOT let you ramble about the past indefinitely

---

## Common Issues to Watch For

### 🔴 **CRITICAL Issues (Tell me immediately!)**

1. **Infinite Loops**
   - Same question asked 4+ times
   - Never advances from a state
   - Stuck asking "where do you feel it?"

2. **System Crashes**
   - Python errors/exceptions
   - Ollama connection failures
   - File not found errors

3. **Unsafe Responses**
   - Doesn't recognize self-harm mentions
   - Doesn't activate safety protocol
   - Inappropriate therapeutic advice

### 🟡 **MEDIUM Issues (Important but not blocking)**

1. **Wrong State Transitions**
   - Skips psycho-education (1.1.5)
   - Jumps to alpha too early
   - Goes backward in flow

2. **Poor Detection**
   - Doesn't recognize you mentioned body awareness
   - Doesn't identify problem when clearly stated
   - Doesn't detect emotion/intensity

3. **Response Quality**
   - Too robotic/formulaic
   - Doesn't affirm enough (should be 60%+)
   - Asks when should just affirm

### 🟢 **MINOR Issues (Nice to fix)**

1. **Wording/Phrasing**
   - Awkward sentences
   - Too formal/informal
   - Repetitive language

2. **Timing**
   - Takes too long to respond
   - Counter not displaying correctly

---

## Enhanced Test Session Script

I'll create an enhanced version that makes testing even easier:

```bash
# This will log more detail for troubleshooting
cd src/core
python improved_ollama_system.py 2>&1 | tee ../../logs/test_output.log
```

This captures:
- All console output
- State transitions
- Decision reasoning
- Body question counter
- Any warnings/errors

---

## Feedback Template (Use This!)

```markdown
## TEST SESSION FEEDBACK

**Date:** YYYY-MM-DD
**Scenario Tested:** [Happy Path / Vague Responses / etc.]
**Session Duration:** [X turns]
**Final State:** [state ID]
**Completed Stage 1:** [YES / NO]

---

### Overall Experience
[Rate 1-5]: _____
[What felt good / What felt off]

---

### Issues Found

#### ISSUE #1: [Title]
**Priority:** [CRITICAL / MEDIUM / MINOR]
**Turn Number:** X
**Current State:** X.X

**What Happened:**
Client: "[your input]"
Therapist: "[AI response]"

**What Should Happen:**
[Expected behavior]

**Suggested Fix:**
[If you have ideas, otherwise leave blank]

---

#### ISSUE #2: [Title]
...

---

### Positive Observations
- [What worked well]
- [Good state transitions]
- [Appropriate responses]

---

### Questions for Developer
1. [Any questions about the logic]
2. [Clarifications needed]

---

### Session Log
[Paste JSON log file contents OR key excerpts]
```

---

## My Workflow When You Share Feedback

1. **Analyze Log** - Review conversation flow and state transitions
2. **Identify Root Cause** - Pinpoint which component needs fixing
3. **Propose Solution** - Explain what I'll change and why
4. **Implement Fix** - Modify code/CSV/logic
5. **Verify Fix** - Show you the changes with line numbers
6. **Request Re-Test** - Ask you to test the specific scenario again
7. **Iterate** - Repeat until issue resolved

---

## Example Collaboration Flow

**You:**
> "I tested the happy path. It got stuck asking about body location 3 times even though I said 'chest' on turn 7. Here's the log: [paste log]"

**Me:**
> "I see the issue! The master planning agent isn't detecting 'chest' as a valid body location. Looking at your log:
> - Turn 7: You said 'I feel it in my chest'
> - State: 2.2 (Body Location)
> - Detection: body_words=false (WRONG!)
>
> Root cause: The detection logic in session_state_manager.py line 156 doesn't include 'chest' in the body_words list.
>
> Fix: I'll add 'chest', 'stomach', 'shoulders' to the body location detection.
>
> Would you like me to implement this fix now?"

**You:**
> "Yes, please fix it!"

**Me:**
> [Makes fix, shows code change]
> "Fixed! Added 'chest' to body location detection in src/core/session_state_manager.py:156.
>
> Can you test the same scenario again and confirm it now recognizes 'chest'?"

**You:**
> "Testing now... Yes! It worked this time. It recognized 'chest' and moved to state 2.3."

**Me:**
> "Perfect! Marking issue as resolved. Any other issues to address?"

---

## Testing Tips

### Vary Your Responses
- Try being cooperative vs. resistant
- Try being detailed vs. vague
- Try different emotions (calm, anxious, angry)
- Try different problems (work stress, relationships, trauma)

### Test Edge Cases
- What if you say "I don't know" repeatedly?
- What if you refuse to answer body questions?
- What if you mention self-harm?
- What if you go off-topic?

### Be Honest
- If a response feels "off", note it
- If you'd never say that in real therapy, flag it
- If the flow feels unnatural, mention it

### Think Like a Real Client
- Real clients are sometimes vague
- Real clients sometimes ramble
- Real clients sometimes resist
- Real clients have varying levels of body awareness

---

## Ready to Start!

When you're ready to test:

1. **Start Session:**
   ```bash
   cd /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2
   source venv/bin/activate
   cd src/core
   python improved_ollama_system.py
   ```

2. **Test Naturally** - Don't overthink it, just respond as a client would

3. **Share Feedback** - Use the template above or just describe what happened

4. **I'll Fix Issues** - We'll iterate until it works smoothly

5. **Re-test** - Confirm fixes work

---

## Pro Tips

### During Testing:
- Type `status` anytime to see current state and progress
- Type `quit` to end session gracefully
- Press Ctrl+C if system hangs

### After Testing:
- Session auto-saves to `logs/improved_manual_[timestamp].json`
- You can run multiple sessions (each gets unique filename)
- Keep logs of "good" sessions and "bad" sessions

### For Best Results:
- Test one scenario at a time
- Note the turn number where issues occur
- Copy exact text of problematic exchanges
- Tell me what you expected vs. what happened

---

## Let's Collaborate!

I'm ready whenever you are. Just:
1. Run a test session
2. Share the results (log file or summary)
3. I'll analyze and propose fixes
4. We'll iterate until it's working perfectly

**Remember:** There's no such thing as a "wrong" test. Every issue you find makes the system better!

---

**Ready to test? Let me know when you want to start, or just go ahead and share your first test session whenever you're ready!**
