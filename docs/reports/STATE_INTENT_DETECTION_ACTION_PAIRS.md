# STATE + INTENT + DETECTION → ACTION PAIRS

**Complete Routing Logic Reference**

---

## 🎯 PRIORITY ROUTING (Overrides Normal Flow)

### **PRIORITY 1: Safety (Highest - From ANY State)**

| Current State | Intent | Detections | Next State | Action |
|--------------|--------|------------|------------|--------|
| **ANY** | any | `self_harm=True` | **SELFHARM** | ⚡`no_harm` framework |

```
Example:
State: 2.3
Client: "I want to hurt myself"
Detection: self_harm=True
→ SELFHARM + trigger no_harm framework
```

---

### **PRIORITY 2: Therapeutic Redirects (From ANY State)**

| Current State | Intent | Detections | Loop Counter | Next State | Action |
|--------------|--------|------------|--------------|------------|--------|
| **ANY** | any | `thinking_mode=True` | < 3 | **THINK** | RAG: `dr_q_think_redirect` |
| **ANY** | any | `thinking_mode=True` | >= 3 | **3.2** | Escape to alpha (grounding) |
| **ANY** | any | `tense='past'` | < 3 | **PAST** | RAG: `dr_q_past_redirect` |
| **ANY** | any | `tense='past'` | >= 3 | **3.2** | Escape to alpha (anchoring) |

```
Example 1:
State: 2.4
Client: "I think it's because of my past"
Detection: thinking_mode=True, loop_counter[THINK]=1
→ THINK state, ask "What are you FEELING?"

Example 2:
State: 2.5
Client: "Back then when I was stressed..."
Detection: tense='past', loop_counter[PAST]=0
→ PAST state, ask "Right now, what are you FEELING?"
```

---

### **PRIORITY 3: Affirmation (From ANY State)**

| Current State | Intent | Detections | Next State | Action |
|--------------|--------|------------|------------|--------|
| **ANY** | any | `body_words=True` + `tense='present'` | **AFFIRM** | RAG: `dr_q_affirm` ("That's right.") |

```
Example:
State: 2.5
Client: "I feel tightness in my chest right now"
Detection: body_words=True, tense='present'
→ AFFIRM state, say "That's right."
→ Then continue normal flow
```

---

### **PRIORITY 4: Special States (From ANY State)**

| Current State | Intent | Detections | Next State | Action |
|--------------|--------|------------|------------|--------|
| **ANY** | crisis_state | `incoherent=True` OR `severe_panic=True` | **CRISIS** | RAG: none, ⚡`no_harm` if unsafe |
| **ANY** | resistant | `skepticism=True` | **RESISTANCE** | RAG: `dr_q_resistance` |
| **ANY** | rambling | `excessive_length=True` | **RAMBLING** | RAG: `dr_q_interrupt` |
| **ANY** | high_intensity | `intensity='high'` + `caps=True` | **EMOTION** | RAG: `dr_q_validate` |
| **ANY** | crying | `crying_detected=True` | **CRY** | RAG: `dr_q_cry` |
| **ANY** | silence | `silence=True` | **SILENT** | RAG: `dr_q_prompt`, ⚡`card_game` if continues |
| **ANY** | off_topic | `off_topic=True` | **OFF** | RAG: `dr_q_redirect` |
| **ANY** | validation | `seeking_validation=True` | **VALID** | RAG: `dr_q_normalize` |
| **ANY** | people_pleasing | `relational_issue=True` | **RELATION** | RAG: `dr_q_relational` |

```
Example 1:
State: 2.2
Client: "I'M SO STRESSED!!! CAN'T TAKE IT!!!"
Detection: intensity='high', caps=True
→ EMOTION state, say "That's right, there's a lot there. Take a breath..."

Example 2:
State: 3.1
Client: "This isn't helping. Waste of time."
Detection: skepticism=True
→ RESISTANCE state, explain process
```

---

## 📊 NORMAL FLOW ROUTING (Priority 5)

### **SECTION 1: Goal & Vision (States 1.x)**

#### **State 1.1 - Goal Inquiry**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 1.1 | session_start | none | 1.1 | RAG: `dr_q_goal_inquiry` |
| 1.1 | states_goal | none | 1.2 | RAG: `dr_q_vision` |
| 1.1 | describes_problem | none | 1.1_redirect | RAG: `dr_q_redirect_outcome` |

```
Flow:
Client: "I'm so stressed and overwhelmed"
Intent: session_start (describing problem, not goal)
→ Stay at 1.1, ask "What do we want to accomplish?"

Client: "I want to feel calm"
Intent: states_goal
→ Move to 1.2, build vision
```

---

#### **State 1.1_redirect - Redirect to Goal**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 1.1_redirect | states_goal | none | 1.2 | RAG: `dr_q_vision` |
| 1.1_redirect | describes_problem | none | 1.1_redirect | RAG: `dr_q_redirect_outcome` (repeat) |

```
Flow:
Client: "Work is so hectic, too much pressure"
Intent: describes_problem (still not stating goal)
→ Stay at 1.1_redirect, ask "What do you WANT to feel instead?"

Client: "I want to feel peaceful"
Intent: states_goal
→ Move to 1.2
```

---

#### **State 1.2 - Build Vision**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 1.2 | accepts_vision | none | 1.3 | RAG: `dr_q_permission` |
| 1.2 | needs_clarification | none | 1.2 | Explain vision again |

```
Flow:
Therapist: "So we want you to be calm, peaceful, present. Does that make sense?"
Client: "Yes, exactly!"
Intent: accepts_vision
→ Move to 1.3, ask permission
```

---

#### **State 1.3 - Get Permission**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 1.3 | permission_granted | none | 2.1 | RAG: `dr_q_problem` |
| 1.3 | hesitant | none | 1.3 | Reassure, ask again |

```
Flow:
Therapist: "Would it be okay with you to work on this?"
Client: "Yes, absolutely"
Intent: permission_granted
→ Move to 2.1, ask about problem
```

---

### **SECTION 2: Body Awareness (States 2.x)**

#### **State 2.1 - Problem Inquiry**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 2.1 | no_body_awareness | `body_words=False` | 2.1_seek | RAG: `dr_q_to_body` |
| 2.1 | mentions_body | `body_words=True` | 2.2 | RAG: `dr_q_location` |

```
Flow:
Therapist: "What's been making it hard?"
Client: "Work deadlines, too many projects"
Detection: body_words=False (external stressors only)
→ Move to 2.1_seek, guide to body

Client: "My chest feels tight"
Detection: body_words=True
→ Move to 2.2, ask for location
```

---

#### **State 2.1_seek - Seek Body (LOOP PREVENTION)**

| State | Intent | Detections | Loop Counter | Next State | Action |
|-------|--------|------------|--------------|------------|--------|
| 2.1_seek | no_body_awareness | `body_words=False` | < 3 | 2.1_seek | RAG: `dr_q_to_body` (repeat) |
| 2.1_seek | no_body_awareness | `body_words=False` | >= 3 | **ESCAPE** | ⚡`card_game` OR skip to 3.1 |
| 2.1_seek | mentions_body | `body_words=True` | any | 2.2 | RAG: `dr_q_location` |

```
Flow:
Attempt 1:
Therapist: "Where do you feel it in your body?"
Client: "I don't feel anything. It's just work stress."
Loop counter[2.1_seek]=1
→ Stay at 2.1_seek, try different wording

Attempt 2:
Therapist: "Is there any sensation anywhere?"
Client: "No, it's external."
Loop counter[2.1_seek]=2
→ Stay at 2.1_seek, more directive

Attempt 3 - ESCAPE:
Loop counter[2.1_seek]=3
→ Trigger card_game framework OR skip to 3.1 (alpha will develop body awareness)
```

---

#### **State 2.2 - Body Location**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 2.2 | gives_location | none | 2.3 | RAG: `dr_q_sensation` |
| 2.2 | vague_response | none | 2.2 | Clarify, ask again |

```
Flow:
Therapist: "Where in your body?"
Client: "My chest, right in the center"
Intent: gives_location
→ Move to 2.3, ask about sensation quality
```

---

#### **State 2.3 - Sensation Quality**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 2.3 | describes_sensation | none | 2.4 | RAG: `dr_q_present_check` |
| 2.3 | unclear | none | 2.3 | Ask again with examples |

```
Flow:
Therapist: "What kind of sensation? Ache? Tight? Heavy?"
Client: "It's heavy, like a weight pressing down"
Intent: describes_sensation
→ Move to 2.4, check present awareness
```

---

#### **State 2.4 - Present Check**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 2.4 | present_aware | `body_aware=True` + `tense='present'` | 2.5 | RAG: `dr_q_how_know` |
| 2.4 | not_present | `tense='past'` OR uncertain | 2.4 | Guide to present moment |

```
Flow:
Therapist: "That's right, heavy. You're feeling that right now, aren't you?"
Client: "Yes, I feel it right now"
Detection: body_aware=True, tense='present'
→ Move to 2.5, identify pattern
```

---

#### **State 2.5 - Pattern Inquiry**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 2.5 | pattern_identified | pattern_complete | 3.1 | RAG: `dr_q_ready` |
| 2.5 | unclear_pattern | none | 2.5 | Guide to identify trigger→thought→body |

```
Flow:
Therapist: "How do you know when this happens?"
Client: "When I see my calendar, I think 'I can't do this', then the tightness starts"
Intent: pattern_identified (trigger→thought→body chain clear)
→ Move to 3.1, assess readiness for alpha
```

---

### **SECTION 3: Alpha Sequence (States 3.x)**

#### **State 3.1 - Assess Readiness**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 3.1 | ready_for_alpha | all_criteria_met | 3.2 | RAG: `dr_q_alpha_intro` |
| 3.1 | more_to_discuss | none | 2.5 | Continue exploring pattern |

```
Flow:
Therapist: "Anything else I should understand?"
Client: "No, that's it"
Intent: ready_for_alpha
→ Move to 3.2, introduce alpha
```

---

#### **State 3.2 - Introduce Alpha**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 3.2 | accepts_alpha | willing | 3.3 | RAG: none (framework takes over) |
| 3.2 | hesitant | uncertain | 3.2 | Explain alpha process, reassure |

```
Flow:
Therapist: "We'll do a short process to put your body in rest state. Willing to try?"
Client: "Okay, I'm ready"
Intent: accepts_alpha
→ Move to 3.3, execute alpha
```

---

#### **State 3.3 - Execute Alpha**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 3.3 | alpha_complete | framework_finished | 3.4 | RAG: `dr_q_post_alpha` |
| 3.3 | interrupted | client_stopped | Handle | Return or resume |

```
Flow:
State 3.3 triggered
→ ⚡ alpha_sequence framework takes control
→ Framework handles all 6 steps + body checks
→ When complete, framework returns control
→ Move to 3.4, ask about experience
```

---

#### **State 3.4 - Post-Alpha**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 3.4 | positive_response | extract_experience | 3.5 | RAG: `dr_q_link` |
| 3.4 | neutral_response | none | 3.6 | RAG: `dr_q_compare` |

```
Flow:
Therapist: "What did you notice with your eyes closed?"
Client: "I felt lighter, freer. The weight got smaller."
Intent: positive_response
→ Move to 3.5, link to vision
```

---

#### **State 3.5 - Link to Vision**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 3.5 | linked | vision_connection_made | 3.6 | RAG: `dr_q_compare` |
| 3.5 | needs_more | unclear | 3.5 | Explore experience more |

```
Flow:
Therapist: "You felt lighter and freer. That's where we're headed - you who's calm, peaceful, present."
Client: "Yes, I can see that"
Intent: linked
→ Move to 3.6, compare progress
```

---

#### **State 3.6 - Compare Progress**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 3.6 | improved | sentiment_better | 4.1 | RAG: `dr_q_transition` |
| 3.6 | same_or_worse | no_improvement | 3.1 | More work needed, reassess |

```
Flow:
Therapist: "How's your body now compared to when we started?"
Client: "Much better. The tightness is almost gone."
Intent: improved
→ Move to 4.1, transition to Stage 2
```

---

### **SECTION 4: Transition**

#### **State 4.1 - Ready Stage 2**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| 4.1 | ready | improvement_confirmed | **STAGE 2** | RAG: `dr_q_transition` |
| 4.1 | not_ready | needs_more_work | 3.1 | Return to alpha or explore more |

```
Flow:
Therapist: "Good. Whatever's causing this tightness, we want to stop it. Ready to understand what's happening?"
Client: "Yes, I'm ready"
→ Begin Stage 2 (metaphors triggered strategically based on trauma type)
```

---

## 🔄 PRIORITY REDIRECT STATES

### **State THINK - Redirect Thinking**

| State | Intent | Detections | Loop Counter | Next State | Action |
|-------|--------|------------|--------------|------------|--------|
| THINK | feeling_response | `thinking_mode=False` | any | **continue** | Return to previous state |
| THINK | thinking_response | `thinking_mode=True` | < 3 | THINK | RAG: `dr_q_think_redirect` (repeat) |
| THINK | thinking_response | `thinking_mode=True` | >= 3 | 3.2 | Escape to alpha grounding |

```
Flow:
Attempt 1:
Therapist: "Rather than thinking, what are you FEELING?"
Client: "I think it's because of my childhood..."
Loop counter[THINK]=1
→ Stay at THINK, try again

Attempt 3 - ESCAPE:
Loop counter[THINK]=3
→ "Let's do a grounding exercise..." → Move to 3.2 (alpha)
```

---

### **State PAST - Redirect Past**

| State | Intent | Detections | Loop Counter | Next State | Action |
|-------|--------|------------|--------------|------------|--------|
| PAST | present_response | `tense='present'` | any | **continue** | Return to previous state |
| PAST | past_response | `tense='past'` | < 3 | PAST | RAG: `dr_q_past_redirect` (repeat) |
| PAST | past_response | `tense='past'` | >= 3 | 3.2 | Escape to alpha anchoring |

```
Flow:
Attempt 1:
Therapist: "That was then. Right now, what are you FEELING?"
Client: "Back then when I was alone..."
Loop counter[PAST]=1
→ Stay at PAST, stronger redirect

Attempt 3 - ESCAPE:
Loop counter[PAST]=3
→ "Let's bring you to present..." → Move to 3.2 (alpha)
```

---

### **State AFFIRM - Just Affirm**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| AFFIRM | any | `body_aware=True` + `tense='present'` | **continue** | RAG: `dr_q_affirm` ("That's right.") |

```
Flow:
Client: "I feel tightness in my chest right now"
→ AFFIRM triggered
Therapist: "That's right."
→ Return to previous state, continue flow
(Use 60%+ of time instead of asking questions)
```

---

## 🚨 SPECIAL STATES

### **State SELFHARM - Self-Harm Mention**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| SELFHARM | engaged | client_talking_about_it | assess_safety | RAG: none, ⚡`no_harm` framework |
| SELFHARM | crisis_escalation | escalating | CRISIS | RAG: none, ⚡`no_harm` framework |

```
Flow:
Client: "I want to hurt myself"
→ SELFHARM state
→ ⚡ no_harm framework (safety assessment)
Therapist: "I hear you're having thoughts of hurting yourself. Your safety is important. Let's talk about this."
```

---

### **State CRISIS - Acute Crisis**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| CRISIS | safe_calm | calming_down | continue | Return to flow or 3.2 (alpha) |
| CRISIS | unsafe | danger_present | emergency | ⚡`no_harm` framework + resources |

```
Flow:
Client: "HEART RACING can't BREATHE everything spinning CAN'T STOP!!!"
→ CRISIS state
Therapist: "I hear you're having a really hard time right now. Take a breath with me. Are you safe?"
```

---

### **State RESISTANCE - Client Resistant**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| RESISTANCE | willing | re_engaged | continue | Return to previous state |
| RESISTANCE | still_resistant | skepticism_continues | explain_method | Provide more explanation |

```
Flow:
Client: "This isn't helping. Waste of time."
→ RESISTANCE state
Therapist: "I hear this doesn't feel helpful yet. Trust the process for a moment..."
Client: "Fine, I'll try"
→ Return to previous state, continue flow
```

---

### **State RAMBLING - Excessive Detail**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| RAMBLING | body_mentioned | `body_words=True` | 2.2 | RAG: `dr_q_location` (redirect successful) |
| RAMBLING | still_rambling | excessive_detail | firmer | Firmer interrupt |

```
Flow:
Client: "Well back in 1987 when I was at TechCorp..." [5 minutes]
→ RAMBLING state
Therapist: "I appreciate that context. Let me ask - when you think about all that, where do you feel it?"
Client: "Oh, my chest"
→ Move to 2.2 (got body awareness during interrupt!)
```

---

### **State EMOTION - Strong Emotion**

| State | Intent | Detections | Next State | Action |
|-------|--------|------------|------------|--------|
| EMOTION | calm | intensity_reduced | continue | Return to previous state |
| EMOTION | escalated | intensity_increasing | CRISIS | Escalate to crisis handling |

```
Flow:
Client: "I'M SO STRESSED!!! CAN'T TAKE IT!!!"
→ EMOTION state
Therapist: "That's right, there's a lot there. Take a breath..."
Client: [calms down]
→ Return to previous state
```

---

### **State SILENT - Not Speaking**

| State | Intent | Detections | Attempts | Next State | Action |
|-------|--------|------------|----------|------------|--------|
| SILENT | speaks | client_responds | any | continue | Return to previous state |
| SILENT | still_silent | no_response | < 2 | SILENT | RAG: `dr_q_prompt` (gentle) |
| SILENT | still_silent | no_response | >= 2 | card_game | ⚡`card_game` framework |

```
Flow:
Client: "Um... [long pause]"
→ SILENT state
Therapist: "Take your time... What are you noticing?"
Client: [still silent]
→ ⚡ card_game framework (non-verbal communication)
```

---

## 📊 COMPLETE ROUTING ALGORITHM

```python
def determine_next_state(current_state, intent, detections, loop_counters, collected_data):
    """
    Complete routing logic with all priorities
    """

    # ===== PRIORITY 1: SAFETY =====
    if detections['self_harm']:
        return 'SELFHARM', 'trigger_no_harm'

    # ===== PRIORITY 2: THERAPEUTIC REDIRECTS =====
    if detections['thinking_mode']:
        loop_counters['THINK'] += 1
        if loop_counters['THINK'] >= 3:
            return '3.2', 'escape_to_alpha_grounding'
        return 'THINK', 'dr_q_think_redirect'

    if detections['tense'] == 'past':
        loop_counters['PAST'] += 1
        if loop_counters['PAST'] >= 3:
            return '3.2', 'escape_to_alpha_anchoring'
        return 'PAST', 'dr_q_past_redirect'

    # ===== PRIORITY 3: AFFIRMATION =====
    if detections['body_words'] and detections['tense'] == 'present':
        return 'AFFIRM', 'dr_q_affirm'

    # ===== PRIORITY 4: SPECIAL STATES =====
    if detections['incoherent'] or detections['severe_panic']:
        return 'CRISIS', 'no_harm_if_unsafe'

    if detections['skepticism']:
        return 'RESISTANCE', 'dr_q_resistance'

    if detections['rambling']:
        return 'RAMBLING', 'dr_q_interrupt'

    if detections['intensity'] == 'high':
        return 'EMOTION', 'dr_q_validate'

    if detections['crying']:
        return 'CRY', 'dr_q_cry'

    if detections['silence']:
        return 'SILENT', 'dr_q_prompt_or_card_game'

    if detections['off_topic']:
        return 'OFF', 'dr_q_redirect'

    if detections['validation']:
        return 'VALID', 'dr_q_normalize'

    if detections['relational']:
        return 'RELATION', 'dr_q_relational'

    # ===== PRIORITY 5: NORMAL STATE FLOW =====
    return normal_flow_routing(current_state, intent, loop_counters, collected_data)


def normal_flow_routing(current_state, intent, loop_counters, collected_data):
    """
    Normal state machine logic
    """

    routing_map = {
        # Section 1: Goal & Vision
        ('1.1', 'session_start'): ('1.1', 'dr_q_goal_inquiry'),
        ('1.1', 'states_goal'): ('1.2', 'dr_q_vision'),
        ('1.1', 'describes_problem'): ('1.1_redirect', 'dr_q_redirect_outcome'),

        ('1.1_redirect', 'states_goal'): ('1.2', 'dr_q_vision'),
        ('1.1_redirect', 'describes_problem'): ('1.1_redirect', 'dr_q_redirect_outcome'),

        ('1.2', 'accepts_vision'): ('1.3', 'dr_q_permission'),
        ('1.2', 'needs_clarification'): ('1.2', 'explain_vision'),

        ('1.3', 'permission_granted'): ('2.1', 'dr_q_problem'),
        ('1.3', 'hesitant'): ('1.3', 'reassure'),

        # Section 2: Body Awareness
        ('2.1', 'no_body_awareness'): ('2.1_seek', 'dr_q_to_body'),
        ('2.1', 'mentions_body'): ('2.2', 'dr_q_location'),

        ('2.2', 'gives_location'): ('2.3', 'dr_q_sensation'),
        ('2.2', 'vague'): ('2.2', 'clarify'),

        ('2.3', 'describes_sensation'): ('2.4', 'dr_q_present_check'),
        ('2.3', 'unclear'): ('2.3', 'repeat_with_examples'),

        ('2.4', 'present_aware'): ('2.5', 'dr_q_how_know'),
        ('2.4', 'not_present'): ('2.4', 'guide_to_present'),

        ('2.5', 'pattern_identified'): ('3.1', 'dr_q_ready'),
        ('2.5', 'unclear_pattern'): ('2.5', 'guide_pattern'),

        # Section 3: Alpha
        ('3.1', 'ready_for_alpha'): ('3.2', 'dr_q_alpha_intro'),
        ('3.1', 'more_to_discuss'): ('2.5', 'continue_exploring'),

        ('3.2', 'accepts_alpha'): ('3.3', 'trigger_alpha_sequence'),
        ('3.2', 'hesitant'): ('3.2', 'explain_alpha'),

        ('3.3', 'alpha_complete'): ('3.4', 'dr_q_post_alpha'),

        ('3.4', 'positive_response'): ('3.5', 'dr_q_link'),
        ('3.4', 'neutral_response'): ('3.6', 'dr_q_compare'),

        ('3.5', 'linked'): ('3.6', 'dr_q_compare'),
        ('3.5', 'needs_more'): ('3.5', 'explore_more'),

        ('3.6', 'improved'): ('4.1', 'dr_q_transition'),
        ('3.6', 'same_or_worse'): ('3.1', 'more_work_needed'),

        # Section 4: Transition
        ('4.1', 'ready'): ('STAGE_2', 'dr_q_transition'),
        ('4.1', 'not_ready'): ('3.1', 'continue_work'),
    }

    # Loop prevention for 2.1_seek
    if current_state == '2.1_seek':
        loop_counters['2.1_seek'] += 1
        if loop_counters['2.1_seek'] >= 3:
            return 'ESCAPE', 'card_game_or_skip_to_3.1'
        if intent == 'mentions_body':
            return '2.2', 'dr_q_location'
        return '2.1_seek', 'dr_q_to_body'

    # Default routing
    key = (current_state, intent)
    if key in routing_map:
        return routing_map[key]
    else:
        # Fallback
        return current_state, 'clarify_or_repeat'
```

---

## 📈 STATISTICS

**Total Combinations:**
- **States:** 31
- **Intents:** 31
- **Detections:** 10
- **Priority Levels:** 5
- **Possible Routes:** 200+ (with priorities and special cases)

**Framework Triggers:**
- `alpha_sequence`: 1 state (3.3)
- `no_harm`: 2 states (SELFHARM, CRISIS)
- `card_game`: 2 states (SILENT, 2.1_seek escape)
- `metaphors`: On-demand (confusion detected)

**Loop Prevention:**
- States with counters: 3 (2.1_seek, THINK, PAST)
- Max attempts: 3
- Escape routes: 3

---

*Complete State + Intent + Detection → Action Reference*
*AI Therapist Stage 1*
