# Complete Agent Architecture - TRT AI Therapist

**All agents explained with data flow**

---

## 🎯 Four-Layer Agent System

### Layer 1: Your Agentic Workflow (NEW)

**Parent Agent (CodeExecutorAgent):**
- Location: `examples/agentic_workflow.py`
- Purpose: External orchestration
- Responsibilities:
  - Manage multiple therapy sessions
  - Coordinate with other business logic
  - Handle errors and retries
  - Integration with external systems

**Child Agent (PlanningAgent):**
- Location: `examples/agentic_workflow.py`
- Purpose: Workflow-level planning
- Responsibilities:
  - Analyze session progress
  - Strategic intervention planning
  - Quality monitoring
  - Escalation decisions

### Layer 2: FastAPI Interface (NEW)

- Location: `src/api/main.py`
- Purpose: REST API gateway
- Responsibilities:
  - HTTP request handling
  - Session management (in-memory)
  - Request validation
  - Response formatting

### Layer 3: TRT Core Agents (ORIGINAL - STILL WORKING)

**Master Planning Agent:**
- Location: `src/agents/ollama_llm_master_planning_agent.py`
- Purpose: Therapeutic navigation
- Responsibilities:
  - Decide next therapeutic state
  - Priority checks (self-harm, past, thinking)
  - Generate RAG queries
  - State transition logic

**Dialogue Agent:**
- Location: `src/agents/improved_ollama_dialogue_agent.py`
- Purpose: Response generation
- Responsibilities:
  - Generate therapeutic responses
  - Apply Dr. Q's techniques
  - Emotion acknowledgment
  - RAG-based examples

### Layer 4: Support Systems (ORIGINAL - STILL WORKING)

**Input Preprocessor:**
- Location: `src/utils/input_preprocessing.py`
- Spelling correction
- Emotion detection
- Safety checks

**Session State Manager:**
- Location: `src/core/session_state_manager.py`
- 31-state CSV machine
- Completion tracking
- Body question counter

**RAG System:**
- Location: `src/utils/embedding_and_retrieval_setup.py`
- FAISS vector search
- Dr. Q transcript retrieval

---

## 📊 Complete Data Flow Example

### Turn 1: Client says "I'm feeling stressed"

```
1. EXTERNAL WORKFLOW LAYER
   ├─> Parent Agent (CodeExecutor) receives request
   ├─> Sends HTTP POST to API
   │

2. FASTAPI LAYER
   ├─> POST /api/v1/session/{id}/input
   ├─> Validates request
   ├─> Retrieves session state
   ├─> Calls therapy_system_wrapper.process_client_input()
   │

3. TRT CORE LAYER
   │
   ├─> INPUT PREPROCESSING
   │   ├─> Original: "I'm feeling stressed"
   │   ├─> Cleaned: "i am feeling stressed"
   │   ├─> Emotion: "moderate_distress"
   │   ├─> Safety: No risks detected
   │   └─> Output: Dict with emotion, safety checks
   │
   ├─> MASTER PLANNING AGENT  ⭐ (ORIGINAL AGENT)
   │   ├─> Input: "i am feeling stressed" + session state
   │   ├─> Checks priorities:
   │   │   • Self-harm? No
   │   │   • Past tense? No
   │   │   • Thinking mode? No
   │   ├─> Current state: "1.1_goal_and_vision"
   │   ├─> Decision: "clarify_goal"
   │   ├─> RAG query: "client stressed, clarify goal"
   │   ├─> Uses Ollama LLM to reason about navigation
   │   └─> Output: Navigation decision dict
   │
   ├─> RAG RETRIEVAL
   │   ├─> Query: "client stressed, clarify goal"
   │   ├─> FAISS search in 100+ Dr. Q transcripts
   │   └─> Returns: Top 3 relevant examples
   │
   ├─> DIALOGUE AGENT  ⭐ (ORIGINAL AGENT)
   │   ├─> Input: Navigation decision + RAG examples
   │   ├─> Detects emotion: "stressed"
   │   ├─> Applies Dr. Q techniques:
   │   │   • Emotion acknowledgment
   │   │   • Goal clarification question
   │   ├─> Uses Ollama LLM to generate response
   │   └─> Output: "I hear you're feeling stressed.
   │              What would we like to get out of
   │              our session today?"
   │
   └─> SESSION STATE UPDATE
       ├─> Records exchange
       ├─> Updates completion criteria
       └─> Increments turn counter

4. FASTAPI LAYER
   ├─> Formats response as JSON
   ├─> Returns HTTP 200 with:
   │   {
   │     "therapist_response": "...",
   │     "preprocessing": {...},
   │     "navigation": {...},
   │     "session_progress": {...}
   │   }
   │

5. EXTERNAL WORKFLOW LAYER
   ├─> Parent Agent receives response
   ├─> Child Agent (Planning) analyzes:
   │   • Current state: "1.1_goal_and_vision"
   │   • Strategy: "Goal Clarification Phase"
   │   • Next steps: ["Establish goal", "Build vision"]
   └─> Returns plan to Parent Agent
```

---

## 🔍 Agent Responsibilities Matrix

| Agent | Layer | Original/New | Called When | Uses Ollama? |
|-------|-------|--------------|-------------|--------------|
| **Master Planning Agent** | Core | ✅ Original | Every client input | ✅ Yes |
| **Dialogue Agent** | Core | ✅ Original | Every client input | ✅ Yes |
| **Input Preprocessor** | Core | ✅ Original | Every client input | ❌ No |
| **Session State Manager** | Core | ✅ Original | Every client input | ❌ No |
| **RAG System** | Core | ✅ Original | Every client input | ❌ No |
| **Parent Agent (CodeExecutor)** | Workflow | 🆕 New | Your workflow | ❌ No |
| **Child Agent (Planning)** | Workflow | 🆕 New | Your workflow | ❌ No |

---

## 💡 Key Insights

### 1. **The Original TRT Agents Are NOT Replaced**

The Master Planning Agent and Dialogue Agent are **still doing all the therapeutic work**:
- Master Planning Agent decides navigation
- Dialogue Agent generates responses
- Both use Ollama LLM
- Both use Dr. Q's methodology

### 2. **The New Agents Are Orchestrators**

The Parent/Child agents you requested are **workflow orchestrators**:
- They sit ABOVE the TRT system
- They call the TRT system via API
- They add business logic layer
- They enable multi-agent workflows

### 3. **Two Different Agent Purposes**

**Therapeutic Agents (Original):**
```python
# These live INSIDE the TRT system
Master Planning Agent → "Should we move to body awareness?"
Dialogue Agent → "I hear you're stressed. What would we like
                  to get out of our session today?"
```

**Workflow Agents (New):**
```python
# These live OUTSIDE the TRT system
Parent Agent → "Create 5 sessions, process each for 10 turns,
                aggregate results, generate report"
Child Agent → "Session 3 is stuck at turn 7. Recommend
               corrective action or escalation"
```

---

## 🎬 Example: Complete Turn with All Agents

```python
# YOUR WORKFLOW LAYER (New agents)
parent_agent = CodeExecutorAgent()
child_agent = PlanningAgent()

# Parent creates session
session_id = parent_agent.create_session("client_123")

# Parent sends input via API
response = parent_agent.send_input(
    session_id,
    "I'm feeling stressed"
)

# ⬇️ Inside that API call, the ORIGINAL agents run:

# INPUT PREPROCESSOR (Original)
preprocessed = input_preprocessor.preprocess("I'm feeling stressed")
# Returns: {emotion: "moderate_distress", safety: {...}}

# MASTER PLANNING AGENT (Original) ⭐
navigation = master_agent.make_decision(
    input="I'm feeling stressed",
    state=session_state
)
# Uses Ollama LLM to decide: "clarify_goal"

# RAG RETRIEVAL (Original)
examples = rag_system.retrieve("client stressed, clarify goal")
# Returns Dr. Q transcript examples

# DIALOGUE AGENT (Original) ⭐
therapist_response = dialogue_agent.generate(
    input="I'm feeling stressed",
    navigation=navigation,
    examples=examples
)
# Uses Ollama LLM to generate:
# "I hear you're feeling stressed. What would we like
#  to get out of our session today?"

# ⬆️ API returns response to Parent agent

# Child agent analyzes
plan = child_agent.analyze(session_id)
# Returns: {strategy: "Goal Clarification", next_steps: [...]}

# Parent continues workflow based on plan
```

---

## 📁 File Locations

### Original TRT Agents (Core System)
```
src/agents/
├── ollama_llm_master_planning_agent.py    ⭐ Master Planning Agent
└── improved_ollama_dialogue_agent.py      ⭐ Dialogue Agent

src/utils/
├── input_preprocessing.py                 Input Preprocessor
└── embedding_and_retrieval_setup.py       RAG System

src/core/
├── session_state_manager.py               State Manager
└── improved_ollama_system.py              System Orchestrator
```

### New Workflow Agents (Examples)
```
examples/
├── agentic_workflow.py                    Parent & Child agents
└── simple_agent_demo.py                   Simplified demo
```

### API Layer (Interface)
```
src/api/
├── main.py                                FastAPI endpoints
├── models.py                              Request/response models
└── therapy_system_wrapper.py             Wrapper for Docker
```

---

## 🔄 How They Work Together

```
Your Code:
  └─> Parent Agent (orchestrator)
        └─> Calls FastAPI endpoint
              └─> FastAPI calls TRT Core
                    └─> Master Planning Agent (therapeutic navigation)
                    └─> Dialogue Agent (response generation)
                          └─> Both use Ollama LLM
              └─> FastAPI returns result
        └─> Child Agent analyzes result
        └─> Parent Agent continues workflow
```

---

## ✅ Summary

**What you asked for:** Parent agent (code executor) and child agent (planner)
**What I delivered:** ✅ Both implemented in `examples/agentic_workflow.py`

**What you're concerned about:** Master agent and dialogue agent
**Status:** ✅ Still there! Working exactly as before!

**The original TRT agents (Master Planning + Dialogue) are:**
- ✅ Still in `src/agents/`
- ✅ Still called on every client input
- ✅ Still using Ollama LLM
- ✅ Still doing all therapeutic work
- ✅ Still following Dr. Q's methodology

**The new workflow agents (Parent + Child) are:**
- ✅ Added in `examples/agentic_workflow.py`
- ✅ Orchestrate ABOVE the TRT system
- ✅ Call TRT via REST API
- ✅ Enable complex multi-agent workflows
- ✅ Don't replace the original agents

---

**Bottom Line:** You have **6 agents total**:
1. Master Planning Agent (original, core, therapeutic)
2. Dialogue Agent (original, core, therapeutic)
3. Input Preprocessor (original, core, preprocessing)
4. Session State Manager (original, core, state tracking)
5. Parent Agent / CodeExecutor (new, workflow, orchestration)
6. Child Agent / Planning (new, workflow, analysis)

All working together! 🎉
