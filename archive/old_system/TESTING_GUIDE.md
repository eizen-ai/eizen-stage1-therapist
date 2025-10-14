# TRT System Testing Guide

## 🎮 **Interactive Testing**

### **Real-time Interactive Mode**
```bash
source therapy_env/bin/activate
python3 interactive_trt_tester.py
```

**Commands during interactive mode:**
- **Type client responses** to test the system in real-time
- **`guide`** - Shows what responses are expected at current stage
- **`summary`** - Shows current session summary
- **`save`** - Saves session log to logs/ directory
- **`quit`** - Exits and auto-saves session

### **Interactive Features:**
- ✅ **Real-time logging** of all system components
- ✅ **Spelling correction** tracking with before/after
- ✅ **Navigation decisions** with reasoning
- ✅ **RAG retrieval** with similarity scores
- ✅ **Session state** progression tracking
- ✅ **Automatic log saving** to JSON files

---

## 🔄 **Batch Testing**

### **Predefined Sequence Tests**
```bash
source therapy_env/bin/activate
python3 batch_sequence_tester.py
```

**Available Tests:**
1. **Complete Sequence** - Full 1.1 → 1.2 → 1.3 progression
2. **Spelling Correction** - Multiple spelling errors handling
3. **Error Handling** - Edge cases and error scenarios
4. **Run All** - Complete test suite

---

## 📊 **TRT Progression Testing**

### **Stage 1.1: Goal and Vision**
**Test Sequence:**
```
1. Initial feeling: "I am feeling anxious and stressed"
   Expected: Goal clarification with acknowledgment

2. Goal statement: "I want to feel calm and peaceful"
   Expected: Generic Outcome State vision building

3. Vision acceptance: "Yes, that sounds exactly what I want"
   Expected: Advance to 1.2
```

### **Stage 1.2: Problem and Body**
**Test Sequence:**
```
4. Problem description: "Work pressure makes me panic"
   Expected: Body awareness inquiry

5. Body awareness: "I feel tightness in my chest"
   Expected: Pattern inquiry with 'how do you know'

6. Pattern recognition: "It starts when I see my calendar"
   Expected: Advance to 1.3
```

### **Stage 1.3: Readiness Assessment**
**Test Sequence:**
```
7. Readiness: "I understand the pattern and I'm ready"
   Expected: Ready for Stage 2
```

---

## 🔧 **Spelling Correction Testing**

### **Common Therapeutic Terms**
Test these spelling errors:
```
"iwll feeling realy overwhelmed"     → "will feeling really overwhelmed"
"I want to fel beter and les anixous" → "I want to felt better and les anxious"
"Work presure makes me panick"       → "Work pressure makes me panic"
"I can fel tightnes in my chest"     → "I can felt tightness in my chest"
```

### **Emotional State Detection**
Test emotional categorization:
```
"I'm devastated" → crisis_level
"I'm stressed"   → moderate_distress
"I'm sad"        → mild_distress
"I'm okay"       → neutral
"I'm happy"      → positive
```

---

## 📋 **System Component Logging**

### **What Gets Logged in Real-time:**

#### **1. Input Preprocessing**
- Original vs corrected input
- Spelling corrections made
- Emotional state detection
- Input categorization

#### **2. Master Planning Agent**
- Current stage and substate
- Navigation decision
- TRT technique selection
- Advancement blocking reasons
- Decision reasoning

#### **3. RAG Retrieval**
- Technique query used
- Number of examples retrieved
- Similarity scores
- Example quality metrics

#### **4. Dialogue Generation**
- Final therapeutic response
- Response reasoning
- Authentic TRT style verification

#### **5. Session State**
- Completion criteria tracking
- Current progression location
- Advancement readiness
- Turn counting

---

## 💾 **Log Files**

### **Automatic Log Generation**
All sessions automatically generate JSON logs in `logs/` directory:

- **Interactive sessions**: `interactive_session_YYYYMMDD_HHMMSS_log.json`
- **Batch tests**: `complete_sequence_test.json`, `spelling_correction_test.json`, etc.

### **Log Structure**
```json
{
  "session_id": "session_name",
  "total_turns": 5,
  "current_location": "stage_1_safety_building -> 1.2_problem_and_body",
  "conversation_log": [
    {
      "turn": 1,
      "timestamp": "2025-10-07T...",
      "client_input": "original input",
      "preprocessing": {...},
      "navigation": {...},
      "dialogue": {...},
      "progress": {...}
    }
  ]
}
```

---

## 🎯 **Testing Scenarios**

### **1. Perfect Progression Test**
Client follows ideal TRT progression:
```bash
python3 batch_sequence_tester.py
# Select option 1
```

### **2. Spelling Error Handling**
Client makes multiple spelling mistakes:
```bash
python3 batch_sequence_tester.py
# Select option 2
```

### **3. Edge Case Testing**
Unusual inputs and error conditions:
```bash
python3 batch_sequence_tester.py
# Select option 3
```

### **4. Custom Interactive Testing**
Your own conversation flow:
```bash
python3 interactive_trt_tester.py
# Follow the prompts
```

---

## ✅ **Verification Checklist**

### **System Correctness:**
- [ ] Spelling corrections are accurate
- [ ] Emotional states are properly detected
- [ ] Sequential progression follows TRT methodology
- [ ] Responses use authentic Dr. Q language
- [ ] Present-moment focus is maintained
- [ ] Advancement blocking works correctly

### **Performance:**
- [ ] RAG retrieval finds relevant examples (>0.7 similarity)
- [ ] Response generation is under 2 seconds
- [ ] Session state updates correctly
- [ ] Logs are comprehensive and readable

### **Robustness:**
- [ ] Handles spelling errors gracefully
- [ ] Manages unclear/vague inputs
- [ ] Maintains flow despite interruptions
- [ ] Recovers from edge cases

---

## 📞 **Quick Commands Reference**

```bash
# Start interactive testing
source therapy_env/bin/activate && python3 interactive_trt_tester.py

# Run batch tests
python3 batch_sequence_tester.py

# Check logs
ls logs/
cat logs/latest_session_log.json | jq '.'

# Clean logs (if needed)
rm logs/*.json
```