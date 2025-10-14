# INTENTS, DETECTIONS, STATES & ACTIONS - QUICK REFERENCE

---

## 🎯 DETECTIONS (Priority Flags)

```
1. self_harm          → Words: "hurt myself", "kill myself", "end it"
2. thinking_mode      → Words: "I think", "because", "probably", "analyzing"
3. tense              → Values: 'present', 'past'
4. body_words         → Words: chest, tight, shoulders, stomach, ache, heavy
5. intensity          → Values: 'low', 'medium', 'high'
6. incoherent         → Jumbled speech, manic, severe panic
7. skepticism         → Words: "not helping", "waste of time", "don't see point"
8. excessive_length   → Message >200 words with no body reference
9. silence            → Empty or "um..." responses
10. off_topic         → Unrelated to therapy
```

---

## 🏷️ INTENTS (31 Total)

### Goal & Vision (States 1.x)
```
session_start         → Describes problem, not goal
describes_problem     → External stressors
states_goal           → "I want to feel X"
accepts_vision        → "Yes, that's what I want"
permission_granted    → "Yes" / "Okay"
```

### Body Awareness (States 2.x)
```
no_body_awareness     → No body words
mentions_body         → Body words present
gives_location        → Specific location: "chest", "right leg"
describes_sensation   → Quality: "ache", "tight", "heavy"
present_aware         → Body + present tense
pattern_identified    → Trigger→thought→body chain
```

### Alpha Sequence (States 3.x)
```
ready_for_alpha       → "That's it" / "I'm ready"
accepts_alpha         → "Okay" / "Yes"
alpha_complete        → Framework finished
positive_response     → "Felt lighter", "calmer"
linked                → Vision connection made
improved              → Sentiment better
```

### Priority Redirects
```
thinking_mode         → Analyzing vs feeling
past_tense            → "Back then", "was"
body_present          → Body words + present
```

### Special States
```
high_intensity        → CAPS, !!!
crying                → [crying]
silence               → Long pauses
off_topic             → Unrelated talk
validation            → "Is this normal?"
people_pleasing       → "Make everyone happy"
self_harm_detected    → Self-harm language
crisis_state          → Incoherent/severe panic
resistant             → "Not helping"
rambling              → Excessive detail
```

---

## 🎬 31 STATES

### Section 1: Goal & Vision
```
1.1           Goal Inquiry
1.1_redirect  Redirect to Goal
1.2           Build Vision
1.3           Get Permission
```

### Section 2: Body Awareness
```
2.1           Problem Inquiry
2.1_seek      Seek Body (loop: max 3→card_game/3.1)
2.2           Body Location
2.3           Sensation Quality
2.4           Present Check
2.5           Pattern Inquiry
```

### Section 3: Alpha Sequence
```
3.1           Assess Readiness
3.2           Introduce Alpha
3.3           Execute Alpha (⚡alpha_sequence)
3.4           Post-Alpha
3.5           Link to Vision
3.6           Compare Progress
```

### Section 4: Transition
```
4.1           Ready Stage 2
```

### Priority Redirects
```
THINK         Redirect Thinking (loop: max 3→3.2)
PAST          Redirect Past (loop: max 3→3.2)
AFFIRM        Just Affirm
```

### Special States
```
EMOTION       Strong Emotion
CRY           Client Crying
SILENT        Not Speaking (⚡card_game)
OFF           Off Topic
VALID         Seek Validation
RELATION      Relational Pattern
SELFHARM      Self-Harm Mention (⚡no_harm)
CRISIS        Acute Crisis (⚡no_harm)
RESISTANCE    Client Resistant
RAMBLING      Excessive Detail
```

---

## ⚡ ACTIONS (Framework Triggers + Responses)

### Framework Triggers
```
alpha_sequence    → State 3.3 only
no_harm           → SELFHARM, CRISIS (if unsafe)
card_game         → SILENT (after 2 attempts), 2.1_seek (after 3 attempts)
metaphors_A       → When client confused (vector DB query)
metaphors_B       → Stage 2 strategic (per TRT PDF)
```

### RAG Queries (28 Total)
```
dr_q_goal_inquiry       → "What do we want to accomplish?"
dr_q_redirect_outcome   → "What do you WANT to feel?"
dr_q_vision             → "So we want you to be X"
dr_q_permission         → "Would it be okay?"
dr_q_problem            → "What's been making it hard?"
dr_q_to_body            → "Where do you feel it?"
dr_q_location           → "Where in your body?"
dr_q_sensation          → "What kind of sensation?"
dr_q_present_check      → "You're feeling that now?"
dr_q_how_know           → "How do you know when it happens?"
dr_q_ready              → "Anything else?"
dr_q_alpha_intro        → "We'll do a process..."
dr_q_post_alpha         → "What did you notice?"
dr_q_link               → "That's where we're headed"
dr_q_compare            → "How's your body now vs before?"
dr_q_transition         → "Ready to understand what's happening?"
dr_q_think_redirect     → "What are you FEELING?"
dr_q_past_redirect      → "Right now, what are you FEELING?"
dr_q_affirm             → "That's right."
dr_q_validate           → "That's right, there's a lot there"
dr_q_cry                → "This is difficult stuff"
dr_q_prompt             → "Take your time..."
dr_q_redirect           → "Back to what we're working on"
dr_q_normalize          → "Absolutely. Makes sense."
dr_q_relational         → "What do you feel? Where?"
dr_q_resistance         → "Trust the process..."
dr_q_interrupt          → "Let me ask - where do you feel it?"
```

---

## 🔄 DETECTION → ACTION COMBINATIONS

### Priority Level 1 (HIGHEST - Overrides Everything)
```
self_harm=True
  → SELFHARM state
  → ⚡no_harm framework
  → RAG: none (safety protocol)
```

### Priority Level 2 (Redirects)
```
thinking_mode=True
  → THINK state
  → RAG: dr_q_think_redirect
  → Loop counter++
  → If counter>=3: escape to 3.2 (alpha grounding)

tense='past'
  → PAST state
  → RAG: dr_q_past_redirect
  → Loop counter++
  → If counter>=3: escape to 3.2 (alpha anchoring)
```

### Priority Level 3 (Affirmation)
```
body_words=True + tense='present'
  → AFFIRM state
  → RAG: dr_q_affirm
  → Response: "That's right."
  → Use 60%+ of time
```

### Special Detection Combos
```
incoherent=True + severe_panic=True
  → CRISIS state
  → ⚡no_harm (if unsafe)

skepticism=True
  → RESISTANCE state
  → RAG: dr_q_resistance

excessive_length=True + no_body_reference=True
  → RAMBLING state
  → RAG: dr_q_interrupt

silence=True
  → SILENT state
  → Gentle prompt first
  → If continues: ⚡card_game

intensity='high' + caps=True
  → EMOTION state
  → RAG: dr_q_validate
```

---

## 📊 STATE + INTENT → NEXT STATE

### Section 1: Goal & Vision
```
1.1 + session_start      → 1.1 (ask goal)
1.1 + states_goal        → 1.2
1.1 + describes_problem  → 1.1_redirect

1.1_redirect + states_goal    → 1.2
1.1_redirect + continues      → repeat

1.2 + accepts_vision     → 1.3
1.2 + clarify            → explain

1.3 + permission_granted → 2.1
1.3 + hesitant           → reassure
```

### Section 2: Body Awareness
```
2.1 + has_body           → 2.2
2.1 + no_body            → 2.1_seek

2.1_seek + body_mentioned     → 2.2
2.1_seek + 3_attempts         → card_game OR 3.1

2.2 + gives_location     → 2.3
2.2 + vague              → clarify

2.3 + describes_sensation → 2.4
2.3 + unclear            → repeat

2.4 + present_aware      → 2.5
2.4 + not_present        → guide

2.5 + pattern_identified → 3.1
2.5 + unclear            → guide
```

### Section 3: Alpha
```
3.1 + ready              → 3.2
3.1 + more               → continue

3.2 + willing            → 3.3
3.2 + hesitant           → explain

3.3 + alpha_complete     → 3.4

3.4 + positive_response  → 3.5
3.4 + neutral            → 3.6

3.5 + linked             → 3.6
3.5 + needs_more         → explore

3.6 + improved           → 4.1
3.6 + same               → more_work

4.1 + ready              → STAGE 2
```

---

## 🎯 COMPLETE ROUTING LOGIC (Simplified)

```python
def route(current_state, intent, detections, loop_counters):

    # PRIORITY 1: Safety
    if detections['self_harm']:
        return 'SELFHARM', 'no_harm_framework'

    # PRIORITY 2: Redirects
    if detections['thinking_mode']:
        loop_counters['THINK'] += 1
        if loop_counters['THINK'] >= 3:
            return '3.2', 'escape_to_alpha'
        return 'THINK', 'dr_q_think_redirect'

    if detections['tense'] == 'past':
        loop_counters['PAST'] += 1
        if loop_counters['PAST'] >= 3:
            return '3.2', 'escape_to_alpha'
        return 'PAST', 'dr_q_past_redirect'

    # PRIORITY 3: Affirm
    if detections['body_words'] and detections['tense'] == 'present':
        return 'AFFIRM', 'dr_q_affirm'

    # SPECIAL STATES
    if detections['incoherent'] or detections['severe_panic']:
        return 'CRISIS', 'no_harm_if_unsafe'

    if detections['skepticism']:
        return 'RESISTANCE', 'dr_q_resistance'

    if detections['excessive_length']:
        return 'RAMBLING', 'dr_q_interrupt'

    if detections['silence']:
        return 'SILENT', 'gentle_prompt_or_card_game'

    if detections['intensity'] == 'high':
        return 'EMOTION', 'dr_q_validate'

    # NORMAL STATE FLOW
    next_state = state_intent_map[(current_state, intent)]

    # CHECK LOOP COUNTER
    if current_state == next_state:
        loop_counters[current_state] += 1
        if loop_counters[current_state] >= 3:
            return escape_routes[current_state]

    return next_state, csv[next_state]['RAG_Query']
```

---

## 📋 ESCAPE ROUTES

```
2.1_seek (loop>=3)  → card_game OR skip to 3.1
THINK (loop>=3)     → 3.2 (alpha grounding)
PAST (loop>=3)      → 3.2 (alpha anchoring)
```

---

**Total Counts:**
- **Detections:** 10
- **Intents:** 31
- **States:** 31
- **Actions:** 28 RAG queries + 4 frameworks
- **Priority Levels:** 3
- **Escape Routes:** 3

---

*Quick Reference - AI Therapist Stage 1*
*State + Intent + Detections → Action*
