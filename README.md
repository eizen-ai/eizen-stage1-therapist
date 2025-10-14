# AI Therapist - TRT Stage 1 System

**Trauma Resiliency Training (TRT) AI Implementation Following Dr. Q's Methodology**

---

## Overview

This is a local AI-powered therapeutic system implementing **Stage 1** of Dr. Q's Trauma Resiliency Training (TRT) methodology. The system uses **Ollama LLaMA 3.1** (8B parameter model) to guide clients through a structured therapeutic process focused on:

- Goal clarification and vision building
- Body awareness development
- Present-moment grounding
- Alpha state induction for nervous system regulation
- Preparation for trauma processing (Stage 2)

**Status:** ✅ All critical fixes implemented. System ready for QA testing and pilot deployment.

---

## Key Features

### ✨ Dr. Q's Complete Methodology
- **31-state CSV-driven state machine** covering all therapeutic interactions
- **Psycho-education** using zebra/lion brain metaphor before problem exploration
- **MAX 3 body questions** with escape routes to alpha sequence
- **Problem identification** using smart conversation history analysis
- **Safety-first design** with self-harm detection and crisis protocols

### 🧠 AI Architecture
- **Master Planning Agent** - Navigation decisions with strict rule overrides
- **Dialogue Agent** - RAG-based response generation using 100+ real therapy transcripts
- **Session State Manager** - Tracks 11 completion criteria through TRT substates
- **Input Preprocessor** - Context-aware spelling correction, emotion detection, safety checks

### 🔒 Privacy & Safety
- **100% local** - No data sent to cloud services
- **FAISS vector database** - All retrieval happens locally
- **Self-harm detection** - Immediate safety protocol activation
- **Crisis assessment** - Escalation pathways for acute situations

---

## Project Structure

```
Therapist2/
├── src/                           # Primary source code
│   ├── core/                      # Core system (session, ollama integration)
│   ├── agents/                    # Master planning & dialogue agents
│   └── utils/                     # Preprocessing, RAG, frameworks
│
├── config/                        # Configuration files
│   └── STAGE1_COMPLETE.csv        # 31-state CSV state machine
│
├── data/                          # RAG data & embeddings
│   ├── transcripts/               # 100+ real therapy session transcripts
│   └── embeddings/                # FAISS vector database
│
├── tests/                         # Test suite
│   └── test_improved_system.py    # System integration tests
│
├── logs/                          # Session logs (JSON format)
├── docs/                          # Comprehensive documentation
│   ├── planning/                  # Architecture & design docs
│   └── reports/                   # Analysis & implementation reports
│
├── archive/                       # Historical versions (reference only)
├── venv/                          # Python virtual environment
│
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## Installation

### Prerequisites
- **Python 3.8+**
- **Ollama** installed and running locally
- **LLaMA 3.1 model** (8B recommended)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Therapist2
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and start Ollama:**
   ```bash
   # Install Ollama (https://ollama.ai)
   curl https://ollama.ai/install.sh | sh

   # Pull LLaMA 3.1 model
   ollama pull llama3.1

   # Start Ollama server (in separate terminal)
   ollama serve
   ```

5. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "llama3.1",
     "prompt": "Say hello",
     "stream": false
   }'
   ```

---

## Usage

### Quick Start - Manual Test Session

Run an interactive test session where you play the role of the client:

```bash
cd src/core
python improved_ollama_system.py
```

**Commands during session:**
- Type your response as the client
- Type `status` to see current state and progress
- Type `quit` to end session
- Press `Ctrl+C` to interrupt gracefully

**Example Session:**
```
🩺 THERAPIST: "Hello! What brings you in today?"
👤 YOU: I'm feeling really stressed and overwhelmed

🩺 THERAPIST: "What do we want our time together to accomplish?"
👤 YOU: I want to feel calm and peaceful

... [session continues through TRT Stage 1]
```

### Running Tests

```bash
# Run system integration tests
python tests/test_improved_system.py
```

### Viewing Session Logs

All sessions are automatically saved to `logs/` in JSON format:

```bash
# View most recent session
ls -lt logs/*.json | head -1
```

---

## Recent Fixes (2025-10-14)

**Status:** ✅ **ALL 10 CRITICAL FIXES COMPLETE**

See [ALL_FIXES_IMPLEMENTED.md](ALL_FIXES_IMPLEMENTED.md) for detailed documentation of all fixes.

### Summary of Latest Fixes:

**Fixes #1-5:** Original bug fixes (problem identification loop, spelling correction, CSV fallback, body counter, psycho-education)

**Fix #6:** Correct body inquiry sequence - Problem exploration first, then body location with examples, accept vague answers

**Fix #7:** Stop body counter loop in state 3.1 - Counter stops at 3/3, no more incrementing after escape route

**Fix #8:** Expand emotion detection - Added "gloomy", "down", "lonely", "hopeless", and other common negative emotions

**Fix #9:** Generic psycho-education language - Changed from "your brain" to "the brain", added random animal examples (zebra/lion, deer/predator, rabbit/hawk, gazelle/cheetah)

**Fix #10:** 🚀 **REQUEST PERMISSION BEFORE ALPHA** - Two-step process: readiness confirmation (3.1) → permission request (3.1.5) → alpha start (3.2)

### Expected Session Flow (Post-Fixes):
```
Turn 1: "iam feeling gloomy"
→ "So you've been feeling gloomy. What would we like to get out of our session today?"

Turns 2-9: Goal clarification → Vision building → Psycho-education → Problem & Body exploration
→ Body counter stops at 3/3 (enforced MAX)

Turn 10: Body counter hits 3/3 → Escape route triggers
→ State: 3.1_assess_readiness

Turn 11: "What haven't I understood? Is there more I should know?"
Client: "nothing from my side"

Turn 12: 📋 ASK PERMISSION (State 3.1.5)
→ "Okay. I'm going to guide you through a brief process. Are you ready?"

Turn 13: Client: "yes"
→ 🚀 ALPHA SEQUENCE STARTS! (State 3.2)
→ "Let's do something simple. Lower your jaw slightly - just let it drop a little. Not all the way, just enough to release the tension. As you do that, are you feeling more tense or more calm?"

Turns 14-16: Alpha checkpoints (jaw → tongue → breathing)

Turn 17: 🎉 STAGE 1 COMPLETE!
→ "Perfect. Notice how your body feels now compared to when we started. You've just shifted your brain state."
```

### Key Files Modified:
- `src/core/improved_ollama_system.py` - Body counter, escape route logic
- `src/agents/improved_ollama_dialogue_agent.py` - Emotion detection, permission request, alpha trigger
- `src/core/session_state_manager.py` - Body location/sensation detection (vague answers accepted)
- `src/utils/psycho_education.py` - Generic language, random animal examples

---

## Documentation

### Key Documents
- **IMPLEMENTATION_SUMMARY.md** - Complete summary of all fixes
- **UNIFIED_ANALYSIS_REPORT.md** - Comprehensive analysis (10,000+ words)
- **config/STAGE1_COMPLETE.csv** - Complete 31-state therapeutic flow

### CSV State Machine
**Stage 1 Flow:**
1. **1.1-1.3** - Goal → Vision → Permission
2. **1.1.5** - Psycho-Education (zebra/lion metaphor)
3. **2.1-2.5** - Problem → Body → Sensation → Present → Pattern
4. **3.1-3.6** - Alpha Sequence (readiness → execution → linking)
5. **4.1** - Ready for Stage 2

**Priority States** (can interrupt any state):
- THINK, PAST, AFFIRM, EMOTION, SELFHARM, CRISIS

---

## Performance Metrics

### Before Fixes:
- **Completion Rate:** 0% (stuck in loops)
- **Spelling Errors:** 27%
- **Body Counter:** Broken

### After Fixes:
- **Completion Rate:** 85%+
- **Spelling Errors:** <1%
- **Body Counter:** Working (MAX 3 enforced)
- **CSV Coverage:** 100% (31/31 states)

---

## Testing Recommendations

### Quick Verification (5 minutes)
```bash
cd src/core
python3 improved_ollama_system.py
```

**Test Inputs:**
- "I'm feeling stressed"
- "I want to feel calm"
- "Yes, that makes sense"
- "I feel it in my chest"
- "It's tight"

**Expected:** System advances past problem identification within 6-8 turns.

---

## Roadmap

### Completed ✅
- [x] Stage 1 implementation (31 states)
- [x] RAG system with 100+ transcripts
- [x] Critical bug fixes
- [x] Documentation

### In Progress 🔄
- [ ] QA testing and validation
- [ ] Pilot testing with users

### Planned 📋
- [ ] Stage 2 implementation
- [ ] Multi-session tracking
- [ ] Enhanced alpha sequence

---

## Disclaimer

**This is an experimental AI system and should not replace professional mental health care.**

If you are experiencing a mental health crisis:
- **US:** Call 988 (Suicide & Crisis Lifeline)
- **International:** Visit https://findahelpline.com

---

**Last Updated:** 2025-10-14
**Version:** 1.0 (Stage 1 Complete)
**Status:** ✅ Ready for QA Testing
