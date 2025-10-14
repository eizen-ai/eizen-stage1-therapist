# Quick Start - Manual Testing

## 🚀 Start Testing in 3 Steps

### 1. Start a Test Session
```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2
python test_helper.py start
```

### 2. Play the Client Role
Type responses as a therapy client would. Example flow:
- "I've been feeling stressed"
- "I want to feel calm"
- "Yes, that makes sense"
- "Work has been overwhelming"
- "I feel it in my chest"
- etc.

### 3. Analyze & Share Results
```bash
# Analyze the session you just completed
python test_helper.py analyze

# Extract potential issues automatically
python test_helper.py issues

# Generate feedback template to share with me
python test_helper.py feedback
```

---

## 📋 Helper Commands

```bash
# Start test session
python test_helper.py start

# Analyze most recent session
python test_helper.py analyze

# Find issues automatically
python test_helper.py issues

# Generate feedback template
python test_helper.py feedback

# Compare last 2 sessions
python test_helper.py compare
```

---

## 💬 How to Share Feedback With Me

### Option 1: Use Helper Script (Easiest!)
```bash
python test_helper.py feedback > my_feedback.txt
```
Then just paste the contents of `my_feedback.txt` to me.

### Option 2: Share Log File
```bash
# Find your latest log
ls -lt logs/improved_manual_*.json | head -1

# Copy its contents and paste to me
cat logs/improved_manual_[timestamp].json
```

### Option 3: Quick Description
Just tell me:
- What you tried
- What went wrong
- Which turn it happened on

I can work with any format!

---

## ⚡ Quick Scenarios to Test

### Happy Path (Should Work)
```
"I'm stressed" → "I want calm" → "Yes" → "Work is overwhelming"
→ "I feel it in my chest" → "It's tight" → "Yes, right now"
```

### No Body Awareness (Tests Escape)
```
"I'm stressed" → "I want calm" → "Yes" → "Work problems"
→ "I don't feel anything" → "Still nothing" → "No, nothing"
```

### Vague Responses (Tests Patience)
```
"I don't know" → "I guess..." → "Maybe" → "Just... stuff"
→ "Everywhere" → "I don't know"
```

---

## 🔍 What to Watch For

### 🔴 Critical (Tell me ASAP!)
- Same question asked 4+ times in a row
- System never advances from a state
- Crashes or errors

### 🟡 Medium (Important)
- Skips psycho-education (state 1.1.5)
- Doesn't recognize body location when you mention it
- Counter stays at 0

### 🟢 Minor (Nice to fix)
- Awkward wording
- Too robotic
- Repetitive phrases

---

## 🤝 Collaboration Flow

**You test** → **Share results** → **I analyze** → **I propose fix** → **I implement** → **You re-test** → **Repeat until perfect!**

---

## 📞 Example Exchange

**You:**
> "Tested happy path. Got stuck asking about body 5 times. Log: improved_manual_20251014_080000.json"

**Me:**
> "Looking at your log... I see the issue! The detection isn't recognizing 'chest'. I'll add it to the body_words list in session_state_manager.py. Can you test again after this fix?"

**You:**
> "Tested again - works now! Moving to next scenario."

---

## Ready?

```bash
# Let's go!
python test_helper.py start
```

When done, run:
```bash
python test_helper.py feedback
```

And share the output with me. Easy! 🎉
