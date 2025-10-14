# AI THERAPIST STAGE 1 - EDGE CASE & LOOP TESTING

**Testing for stuck loops, absurd responses, and system resilience**

---

## 🚨 POTENTIAL LOOP RISKS IDENTIFIED

### **Loop Risk #1: State 2.1_seek ↔ Client Never Mentions Body**

**Scenario:** Client keeps talking about external stressors, never mentions body

```
State: 2.1_seek
CSV: Next_State_Else = "still_external→repeat"
```

**RISK:** Could loop infinitely if client never mentions body

---

#### **TEST: Client Refuses Body Awareness**

**Exchange 1:**
```
THERAPIST: "When you think about deadlines, where do you feel it in your body?"
CLIENT: "I don't feel anything in my body. It's just the work that's the problem."

MASTER AGENT:
  body_words = False
  Route to: 2.1_seek (repeat)
```

**Exchange 2:**
```
THERAPIST: "I understand work is the issue. When you think about it, is there any sensation anywhere in your body?"
CLIENT: "No, I told you - it's not about my body. It's about my boss."

MASTER AGENT:
  body_words = False
  Route to: 2.1_seek (repeat again)
```

**Exchange 3:**
```
THERAPIST: [repeat question again]
CLIENT: "Why do you keep asking about my body? I don't feel anything!"
```

### ⚠️ **LOOP DETECTED: 2.1_seek → 2.1_seek → 2.1_seek**

---

#### **SOLUTION: Add Loop Counter & Alternative Path**

**Proposed Fix:**
```python
# Track loop attempts
if state == '2.1_seek':
    loop_count += 1

    if loop_count >= 3:  # After 3 attempts
        # Alternative: Use card_game to help them identify body sensations
        card_game.trigger('body_identification')

        if still_no_body_awareness:
            # Some clients truly don't have body awareness yet
            # Continue without body location, focus on vision/alpha
            state = '3.1'  # Skip to readiness assessment
            note = "Client struggled with body awareness - will develop during alpha"
```

**Updated CSV Entry:**
```csv
2.1_seek,Seek Body,"...",no_body_awareness,no_body_words,guide_to_body,dr_q_to_body,"...",TRIGGER: card_game (if 3+ attempts),body_mentioned→2.2,3_attempts→3.1,"After 3 attempts with no body awareness, use card_game or skip to alpha (body awareness will develop during process)"
```

---

### **Loop Risk #2: State THINK ↔ Client Keeps Thinking Mode**

**Scenario:** Client can't stop analyzing/thinking

```
State: THINK
CSV: Next_State_Else = "still_thinking→repeat"
```

---

#### **TEST: Persistent Thinking Mode**

**Exchange 1:**
```
THERAPIST: "Rather than thinking, what are you FEELING right now?"
CLIENT: "Well, I think I'm feeling anxious, but I'm not sure why. Maybe it's because of my childhood patterns."

MASTER AGENT:
  thinking_mode = True (still using "I think", "because", "maybe")
  Route to: THINK (repeat)
```

**Exchange 2:**
```
THERAPIST: "What are you FEELING in this moment?"
CLIENT: "I'm analyzing it - I think it must be related to past experiences that created this pattern."

MASTER AGENT:
  thinking_mode = True
  Route to: THINK (repeat again)
```

### ⚠️ **LOOP DETECTED: THINK → THINK → THINK**

---

#### **SOLUTION: Progressive Grounding**

**Proposed Fix:**
```python
if state == 'THINK':
    think_redirect_count += 1

    if think_redirect_count == 1:
        # First attempt: gentle redirect
        response = "Rather than thinking, what are you FEELING?"

    elif think_redirect_count == 2:
        # Second attempt: body grounding
        response = "Let's pause the thinking. Take a breath. What do you notice in your body right now?"

    elif think_redirect_count >= 3:
        # Third attempt: direct to alpha sequence (will naturally ground them)
        state = '3.2'  # Introduce alpha
        note = "Client stuck in thinking mode - alpha sequence will help ground"
```

---

### **Loop Risk #3: State PAST ↔ Client Keeps Going to Past**

**Scenario:** Client keeps talking about "back then"

---

#### **TEST: Stuck in Past**

**Exchange 1:**
```
THERAPIST: "That was then. Right now, what are you FEELING?"
CLIENT: "But back then when my father left, that's when all this started."

MASTER AGENT:
  tense = 'past' ("back then")
  Route to: PAST (repeat)
```

**Exchange 2:**
```
THERAPIST: "Right now, in this moment, what are you feeling?"
CLIENT: "I'm remembering how it felt back when I was 10 years old..."

MASTER AGENT:
  tense = 'past'
  Route to: PAST (repeat again)
```

### ⚠️ **LOOP DETECTED: PAST → PAST → PAST**

---

#### **SOLUTION: Stronger Present-Moment Anchoring**

**Proposed Fix:**
```python
if state == 'PAST':
    past_redirect_count += 1

    if past_redirect_count == 1:
        response = "That was then. Right now, what are you FEELING?"

    elif past_redirect_count == 2:
        # Stronger anchoring
        response = "I hear that happened back then. Your body is here with me NOW. What's your body feeling in THIS moment?"

    elif past_redirect_count >= 3:
        # Direct body check + alpha
        response = "Let's bring you into now. Feel your feet on the floor. Take a breath."
        state = '3.2'  # Move to alpha introduction
        note = "Client stuck in past - alpha will bring to present"
```

---

## 🎭 ABSURD COMMENT TESTING

### **Test 1: Completely Off-Topic**

**CLIENT:** "Did you see the game last night? That touchdown was incredible!"

**MASTER AGENT ANALYSIS:**
```python
detections = {
    'self_harm': False,
    'body_words': False,
    'thinking_mode': False,
    'tense': 'past',
    'off_topic': True  # LLM detects: sports, unrelated to therapy
}

intent = "off_topic"
# Route to: OFF state (from CSV)
```

**CSV LOOKUP - State OFF:**
```csv
OFF,Off Topic,"Did you see the game?",off_topic,topic_check,redirect_gently,dr_q_redirect,"I appreciate that. Back to what we're working on...",none,back→continue,still_off→firmer,"Gentle redirect"
```

**THERAPIST:** "I appreciate that. Back to what we're working on - you mentioned feeling stressed. Where in your body do you feel that?"

**✅ HANDLES CORRECTLY:** Redirects back to therapy focus

---

### **Test 2: Gibberish / Incoherent**

**CLIENT:** "asdfkj banana purple elephant flying spaceship brain tornado!!!"

**MASTER AGENT ANALYSIS:**
```python
# LLM detects incoherence
intent = "incoherent"

# Could indicate:
# 1. Client in crisis/psychotic break
# 2. Testing system
# 3. Typing error
```

**PROPOSED HANDLING:**
```python
if intent == 'incoherent':
    # Check for crisis indicators first
    if high_intensity and fragmented:
        state = 'CRISIS'  # New state needed
        response = "I'm noticing you're having a hard time expressing yourself. Take a breath. Are you safe right now?"
    else:
        # Assume typo/error
        response = "I didn't quite catch that. Could you say that again?"
```

**⚠️ GAP IDENTIFIED:** Need CRISIS state for incoherent/manic responses

---

### **Test 3: Hostile / Angry at Therapist**

**CLIENT:** "This is stupid! You don't understand anything! Why do you keep asking the same questions?!"

**MASTER AGENT ANALYSIS:**
```python
detections = {
    'self_harm': False,
    'intensity': 'very_high',
    'hostile': True,
    'anger_at_therapist': True
}

intent = "high_intensity" (goes to EMOTION state)
```

**CSV LOOKUP - State EMOTION:**
```csv
EMOTION,Strong Emotion,"I'm SO STRESSED!!! Can't TAKE it!!!",high_intensity,"caps, exclamations, intensity",validate_ground,dr_q_validate,"That's right, there's a lot there. Take a breath...",none,calm→continue,escalated→support,"Validate + ground when high intensity"
```

**THERAPIST:** "That's right, there's a lot there. I hear your frustration. Take a breath with me..."

**CLIENT:** "Don't tell me to breathe! This isn't working!"

**PROPOSED HANDLING:**
```python
if hostility_continues:
    # Acknowledge rupture
    response = "I hear this isn't feeling helpful right now. What would be more useful for you?"

    # If still hostile after 2-3 exchanges
    response = "I want this to work for you. Would you be open to trying something different, or would you prefer to pause?"
```

**✅ EMOTION state handles, but needs escalation path**

---

### **Test 4: One-Word Responses**

**THERAPIST:** "What's been making it hard?"
**CLIENT:** "Work."

**THERAPIST:** "Tell me more about work?"
**CLIENT:** "Busy."

**THERAPIST:** "What about it feels difficult?"
**CLIENT:** "Everything."

**MASTER AGENT:**
```python
# Minimal engagement - similar to SILENT state
if word_count < 3 and continues:
    # Try card_game
    card_game.trigger('engagement')
```

**✅ SILENT/card_game state can handle**

---

### **Test 5: Overly Detailed / Rambling**

**CLIENT:** "Well, it started back in 1987 when I was working at this company, and my manager - his name was Bob - he had this habit of coming in at 8:45 every morning, and one day he brought donuts, which was unusual because typically he would bring bagels, but this particular Tuesday, which I remember because it was my cousin's birthday, he brought..." [continues for 5 minutes]

**MASTER AGENT:**
```python
# LLM detects: excessive detail, rambling, no body awareness
intent = "rambling"

# Need to interrupt and redirect
```

**PROPOSED HANDLING:**
```python
if excessive_length and no_body_reference:
    # Gentle interrupt
    response = "I appreciate you sharing all that context. Let me ask - when you think about all of this, where do you feel it in your body?"

    # Redirect to present moment + body
```

**⚠️ GAP IDENTIFIED:** Need rambling/excessive detail handling

---

### **Test 6: False Emergency / Manipulation**

**CLIENT:** "My heart is racing so fast I think I'm dying!" [no actual emergency]

**MASTER AGENT:**
```python
detections = {
    'intensity': 'very_high',
    'body_words': True ("heart racing"),
    'crisis_language': True ("dying")
}

# Could be:
# 1. Actual panic attack (genuine)
# 2. Somatic experiencing (therapeutic)
# 3. Manipulation/attention-seeking
```

**PROPOSED HANDLING:**
```python
# Assess safety first, then ground
response = "I hear your heart is racing. That's your body's response. Take a slow breath with me. Are you safe right now?"

if client_confirms_safe:
    # It's somatic - work with it
    response = "Good. That racing heart - that's your body in fight/flight. Let's work with that sensation..."

    # Continue therapeutic work
    state = '2.4'  # Present check - they're body aware
```

**✅ System can handle as body awareness + intensity**

---

## 🔄 UNSATISFACTORY RESPONSE TESTING

### **Test 1: Client Says "This Isn't Helping"**

**THERAPIST:** "Where in your body do you feel the stress?"
**CLIENT:** "This isn't helping. I don't see the point of this."

**CURRENT HANDLING:**
```python
# Would likely classify as "hesitant" or "off_topic"
# But needs specific handling
```

**PROPOSED HANDLING:**
```python
if "not helping" or "don't see the point":
    # Acknowledge and redirect
    response = "I hear this doesn't feel helpful yet. Trust the process for a moment - when you think about what's bothering you, what do you notice in your body?"

    if still_resistant:
        # Explain briefly
        response = "The reason I'm asking about your body is because stress lives there. By connecting to it, we can release it. Would you be willing to try?"
```

**⚠️ GAP IDENTIFIED:** Need resistance/skepticism handling

---

### **Test 2: Client Says "I Don't Know" Repeatedly**

**THERAPIST:** "Where do you feel it?"
**CLIENT:** "I don't know."

**THERAPIST:** "Just notice - any sensation anywhere?"
**CLIENT:** "I don't know."

**THERAPIST:** "Take a moment to check in with your body..."
**CLIENT:** "I don't know."

**PROPOSED HANDLING:**
```python
if "dont_know" count >= 3:
    # Switch to card_game (visual/tactile)
    card_game.trigger('body_identification')

    # Or: Switch to more general question
    response = "That's okay. Instead of feeling, what do you WANT? How do you want to feel instead?"
    state = '1.2'  # Return to vision-building
```

**✅ card_game can help, OR loop back to vision**

---

### **Test 3: Client Disagrees with Vision**

**THERAPIST:** "So we want you to be peaceful, present, grounded. Does that make sense?"
**CLIENT:** "No, that's not what I want. I want to be successful and rich."

**MASTER AGENT:**
```python
intent = "rejects_vision" (not accepts_vision)
# Next_State_Else = "clarify→explain"
```

**THERAPIST:** "I hear you want success and wealth. And how do you want to FEEL when you have that?"
**CLIENT:** "Confident and powerful."

**THERAPIST:** "Got it - confident, powerful. We can work with that."

**✅ System handles with clarify path**

---

## 📊 LOOP PREVENTION SUMMARY

### **Identified Loops & Solutions:**

| Loop Risk | Current CSV | Proposed Fix | Status |
|-----------|-------------|--------------|---------|
| **2.1_seek → 2.1_seek** | repeats indefinitely | After 3 attempts: trigger card_game OR skip to 3.1 | ⚠️ NEEDS FIX |
| **THINK → THINK** | repeats indefinitely | Progressive grounding → alpha at attempt 3 | ⚠️ NEEDS FIX |
| **PAST → PAST** | repeats indefinitely | Stronger anchoring → alpha at attempt 3 | ⚠️ NEEDS FIX |
| **1.1 → 1.1_redirect → 1.1** | client won't state goal | After 3 attempts: accept current state, work with it | ⚠️ NEEDS FIX |

---

### **Implementation: Add Loop Counters**

```python
class SessionState:
    def __init__(self):
        self.current_state = '1.1'
        self.loop_counters = {
            '2.1_seek': 0,
            'THINK': 0,
            'PAST': 0,
            '1.1': 0,
            'SILENT': 0
        }
        self.max_loops = 3  # Maximum times to repeat same state

    def check_loop(self, state):
        """Check if we're stuck in a loop"""
        if state in self.loop_counters:
            self.loop_counters[state] += 1

            if self.loop_counters[state] >= self.max_loops:
                # Trigger escape route
                return self.escape_loop(state)

        # Reset other counters (not looping)
        for key in self.loop_counters:
            if key != state:
                self.loop_counters[key] = 0

        return state

    def escape_loop(self, stuck_state):
        """Escape routes for stuck states"""
        escape_routes = {
            '2.1_seek': {
                'action': 'trigger_card_game_or_skip',
                'next_state': '3.1',  # Skip to readiness
                'message': "Let's try something different..."
            },
            'THINK': {
                'action': 'direct_to_alpha',
                'next_state': '3.2',
                'message': "Let's pause the thinking and do a grounding exercise..."
            },
            'PAST': {
                'action': 'direct_to_alpha',
                'next_state': '3.2',
                'message': "Let's bring you into the present moment..."
            },
            '1.1': {
                'action': 'accept_current_state',
                'next_state': '1.2',
                'message': "I hear what's troubling you. Let's work with that..."
            },
            'SILENT': {
                'action': 'trigger_card_game',
                'next_state': 'SILENT',
                'framework': 'card_game'
            }
        }

        return escape_routes.get(stuck_state)
```

---

## 🔧 RECOMMENDED CSV UPDATES

### **Add Loop Escape Logic:**

```csv
2.1_seek,Seek Body,"...",no_body_awareness,no_body_words,guide_to_body,dr_q_to_body,"...",TRIGGER: card_game (3+ attempts),body→2.2,3_attempts→3.1,"MAX 3 attempts then escape"

THINK,Redirect Thinking,"...",thinking_mode,"...",redirect_thinking,dr_q_think_redirect,"...",none,feeling→continue,3_attempts→3.2,"MAX 3 attempts then alpha"

PAST,Redirect Past,"...",past_tense,"...",redirect_past,dr_q_past_redirect,"...",none,present→continue,3_attempts→3.2,"MAX 3 attempts then alpha"

SILENT,Not Speaking,"...",silence,incomplete_response,prompt_or_cards,dr_q_prompt,"...",TRIGGER: card_game (2+ attempts),speaks→continue,2_attempts→card_game,"MAX 2 prompts then card_game"
```

---

## ⚠️ CRITICAL GAPS IDENTIFIED

### **1. CRISIS State Missing**

**Need:** State for client in acute crisis (incoherent, manic, severe panic)

```csv
CRISIS,Acute Crisis,"[incoherent/severe panic]",crisis_detected,"incoherent, severe_panic",safety_assess,none,"I hear you're having a really hard time. Are you safe right now?",TRIGGER: no_harm (if unsafe),safe→calm→continue,unsafe→resources,"Safety assessment + grounding"
```

### **2. RESISTANCE State Missing**

**Need:** State for "this isn't helping" / skepticism

```csv
RESISTANCE,Client Resistant,"This isn't helping",resistant,skepticism_detected,address_resistance,dr_q_resistance,"I hear this doesn't feel helpful yet. Trust the process...",none,willing→continue,still_resistant→explain,"Address therapeutic resistance"
```

### **3. RAMBLING Handling Missing**

**Need:** Interrupt pattern for excessive detail

```python
if excessive_length(message) and no_body_reference:
    response = gentle_interrupt() + redirect_to_body()
```

---

## ✅ LOOP-PROOF RECOMMENDATIONS

### **Strategy 1: Maximum Loop Counter**
- Track how many times in same state
- After 3 attempts, escape to next logical state

### **Strategy 2: Progressive Intervention**
- Attempt 1: Gentle
- Attempt 2: More directive
- Attempt 3: Framework trigger or skip

### **Strategy 3: Always Have Exit**
- Every state should have "escape route"
- When stuck → move toward alpha (grounding)

### **Strategy 4: Session Timer**
- If session exceeds expected time (60+ min) without progress
- System flags for human review

---

## 🎯 EDGE CASE TEST RESULTS

| Test Scenario | Current Handling | Loops? | Needs Fix |
|--------------|------------------|--------|-----------|
| Never mentions body | ❌ Repeats infinitely | YES | ✅ Add escape to 3.1 |
| Keeps thinking mode | ❌ Repeats infinitely | YES | ✅ Add escape to 3.2 |
| Stuck in past | ❌ Repeats infinitely | YES | ✅ Add escape to 3.2 |
| Off-topic | ✅ OFF state redirects | NO | ✅ Works |
| Incoherent gibberish | ⚠️ No specific handling | NO | ⚠️ Add CRISIS state |
| Hostile/angry | ⚠️ EMOTION state (partial) | NO | ⚠️ Add escalation |
| One-word responses | ✅ SILENT/card_game | NO | ✅ Works |
| Rambling | ⚠️ No specific handling | NO | ⚠️ Add interrupt |
| "Not helping" | ⚠️ No specific handling | NO | ⚠️ Add RESISTANCE |
| "I don't know" x3 | ⚠️ No specific handling | NO | ⚠️ Add to card_game |
| Disagrees with vision | ✅ Clarify path | NO | ✅ Works |

---

**Status:** 🔴 **3 Critical Loops Identified** - Need immediate fixes
**Risk Level:** MEDIUM - System can get stuck with certain client types
**Recommendation:** Implement loop counters and escape routes before production

---

*Edge Case Testing Complete*
*Loops Identified | Fixes Proposed | Gaps Documented*
