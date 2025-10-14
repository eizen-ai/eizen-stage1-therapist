# TRT AI Therapy System

A multi-agent AI therapy system based on Dr. Jason Quintal's TRT (Trauma Resolution Therapy) methodology, featuring RAG-based retrieval of authentic therapeutic examples.

## 🚀 Quick Start

```bash
# Activate environment
source therapy_env/bin/activate

# Test the system
python3 test_rag_validation.py

# Process new transcripts
python3 transcript_processing_pipeline.py
python3 embedding_and_retrieval_setup.py
```

## 📁 Optimized Folder Structure

```
TRT-AI-Therapy-System/
├── 📁 core_system/                    # Core system configuration
│   ├── optimized_master_agent.txt     # Master planning agent prompt
│   ├── simplified_navigation.json     # TRT navigation logic
│   └── input_classification_patterns.json # Input pattern matching
├── 📁 data/                          # All data files organized by type
│   ├── 📁 raw_transcripts/           # Original source material
│   │   ├── TRT for Staff.pdf         # TRT methodology reference
│   │   ├── session_01.txt            # Clean Dr. Q transcript
│   │   ├── session_02.txt            # Clean Dr. Q transcript
│   │   └── session_03.txt            # Clean Dr. Q transcript
│   ├── 📁 processed_exchanges/       # Labeled therapeutic exchanges
│   │   ├── complete_embedding_dataset.json # All processed exchanges
│   │   ├── session_01_labeled_exchanges.json
│   │   ├── session_02_labeled_exchanges.json
│   │   ├── session_03_labeled_exchanges.json
│   │   ├── session_01_labeled.json   # Original detailed transcripts
│   │   ├── session_02_labeled.json   # (with timing data)
│   │   └── session_03_labeled.json
│   └── 📁 embeddings/               # RAG system files
│       ├── trt_rag_index.faiss      # Pre-built FAISS index (1.5MB)
│       └── trt_rag_metadata.json    # Metadata for embeddings (900KB)
├── 📁 examples/                      # Reference examples and flow
│   ├── labeled_exchanges_example.json # Example labeled exchanges
│   └── complete_stage_1_flow_example.txt # Complete therapeutic flow
├── 📁 docs/                         # Documentation (you're here!)
│   └── README.md                    # This comprehensive guide
├── 📁 therapy_env/                  # Python virtual environment
├── embedding_and_retrieval_setup.py  # RAG system implementation
├── transcript_processing_pipeline.py # Exchange labeling system
├── input_preprocessing.py           # Spelling correction & categorization
├── interactive_trt_tester.py        # Real-time testing with logging
├── batch_sequence_tester.py         # Batch testing suite
├── test_rag_validation.py           # System validation tests
└── TESTING_GUIDE.md                # Complete testing documentation
```

## 🔧 Core System Components

### 🧠 Master Planning Agent with Sequential Progression
- **Location:** `core_system/`
- **Purpose:** **SEQUENTIAL** navigation through TRT substates with completion tracking
- **Key Files:**
  - `optimized_master_agent.txt` - **Updated** with completion criteria enforcement
  - `simplified_navigation.json` - Substate definitions and completion criteria
  - `input_classification_patterns.json` - Client input pattern matching

### 🔄 Session State Management (NEW)
- **File:** `session_state_manager.py` - **Critical addition for proper progression**
- **Purpose:** Tracks completion status across conversation
- **Features:**
  - **1.1 Criteria:** goal_stated ✓ + vision_accepted ✓ → Advance to 1.2
  - **1.2 Criteria:** problem_identified ✓ + body_awareness ✓ + present_moment ✓ → Advance to 1.3
  - **1.3 Criteria:** pattern_understood ✓ + rapport ✓ → Ready for Stage 2

### 🔍 RAG Retrieval System
- **Location:** `data/embeddings/`
- **Purpose:** Fast retrieval of 2-3 authentic Dr. Q examples
- **Usage:**
```python
from embedding_and_retrieval_setup import TRTRAGSystem
rag_system = TRTRAGSystem()
rag_system.load_index("data/embeddings/trt_rag_index.faiss",
                      "data/embeddings/trt_rag_metadata.json")
examples = rag_system.get_few_shot_examples(navigation_output, client_message)
```

### 📝 Data Processing Pipeline
- **Input:** Raw transcripts from `data/raw_transcripts/`
- **Output:** Processed exchanges in `data/processed_exchanges/`
- **System Performance:**
  - **1,000 therapeutic exchanges** from 3 sessions
  - **Embedding dimension:** 384 (MiniLM model)
  - **Retrieval speed:** ~50ms per query

### 🎯 Complete Integrated System (NEW)
- **File:** `integrated_trt_system.py` - **Production-ready complete system**
- **Purpose:** Combines Master Planning + Session State + RAG + Dialogue Generation
- **Usage:**
```python
from integrated_trt_system import CompleteTRTSystem
from session_state_manager import TRTSessionState

# Initialize system
trt_system = CompleteTRTSystem()
session_state = TRTSessionState("client_session_01")

# Process client input
system_output = trt_system.process_client_input(
    "I want to feel calm instead of anxious",
    session_state
)

# Get therapist response
therapist_response = system_output["dialogue"]["therapeutic_response"]
```

## 🔄 Common Operations

### Testing Complete System

#### **🎮 Interactive Real-time Testing**
```bash
# Interactive mode with real-time logging
source therapy_env/bin/activate
python3 interactive_trt_tester.py

# Commands: 'guide', 'summary', 'save', 'quit'
```

#### **🔄 Batch Testing**
```bash
# Predefined sequence tests
python3 batch_sequence_tester.py

# Options: Complete sequence, spelling tests, error handling
```

#### **📊 System Validation**
```bash
# Test RAG system
python3 test_rag_validation.py

# Test input preprocessing
python3 input_preprocessing.py
```

**📋 See [TESTING_GUIDE.md](TESTING_GUIDE.md) for complete testing documentation**

### Adding New Session Transcripts

1. **Add transcript:** Place `session_04.txt` in `data/raw_transcripts/`
2. **Process exchanges:**
   ```bash
   source therapy_env/bin/activate
   python3 transcript_processing_pipeline.py
   ```
3. **Regenerate embeddings:**
   ```bash
   python3 embedding_and_retrieval_setup.py
   ```

### Modifying TRT Navigation

1. **Update substates:** Edit `core_system/simplified_navigation.json`
2. **Add patterns:** Update `core_system/input_classification_patterns.json`
3. **Modify master agent:** Edit `core_system/optimized_master_agent.txt`

### Testing System Changes

```bash
# Run comprehensive validation
python3 test_rag_validation.py

# Check specific scenarios
python3 -c "
from embedding_and_retrieval_setup import TRTRAGSystem
rag = TRTRAGSystem()
rag.load_index('data/embeddings/trt_rag_index.faiss', 'data/embeddings/trt_rag_metadata.json')
results = rag.retrieve_similar_exchanges('client feels anxious about work')
for r in results: print(f'{r.similarity_score:.3f}: {r.doctor_response[:80]}...')
"
```

## 📊 System Architecture

```
Client Input (with potential spelling errors)
    ↓
Input Preprocessor (input_preprocessing.py)
    ↓ (corrected input + categorization + emotional state)
Master Planning Agent (core_system/)
    ↓ (stage, substate, situation_type, rag_query)
RAG System (data/embeddings/)
    ↓ (2-3 authentic Dr. Q examples)
Dialogue Agent (authentic TRT language patterns)
    ↓
Therapeutic Response (Dr. Q style)
```

## 🛠️ Maintenance

### File Size Management
| Component | Size | Cleanup Safe |
|-----------|------|--------------|
| `data/processed_exchanges/session_*_labeled.json` | 12.1 MB | ⚠️  Reference only |
| `data/embeddings/` | 2.4 MB | ❌ Critical |
| `therapy_env/` | ~2 GB | ❌ Critical |
| `examples/` | 20 KB | ✅ Regenerable |
| `input_preprocessing.py` | 15 KB | ✅ Critical - Spelling/categorization |
| `interactive_trt_tester.py` | 25 KB | ✅ Critical - Real-time testing system |
| `batch_sequence_tester.py` | 12 KB | ✅ Testing - Batch validation suite |
| `TESTING_GUIDE.md` | 8 KB | ✅ Documentation - Testing procedures |
| `logs/` directory | Variable | ✅ Auto-generated - Session logs |

### Performance Monitoring
- **Monitor:** Embedding index size grows with new transcripts
- **Rebuild:** FAISS index when adding >100 new exchanges
- **Validate:** RAG retrieval quality monthly

## 🚨 Troubleshooting

### Common Issues
```bash
# Module not found
source therapy_env/bin/activate

# Path errors (old structure)
# Update any custom scripts to use new paths:
# OLD: "session_01.txt"
# NEW: "data/raw_transcripts/session_01.txt"

# Index not found
python3 embedding_and_retrieval_setup.py

# Low similarity scores
# Check if query domain matches training data
```

### Data Integrity Checks
```bash
# Verify core files exist
ls core_system/
ls data/embeddings/
ls data/raw_transcripts/

# Test RAG system
python3 test_rag_validation.py
```

## 📈 System Status

✅ **Production Ready** - Complete sequential progression system
✅ **1,000 Exchanges** - Complete Stage 1 coverage
✅ **Sequential Navigation** - **FIXED** - Proper substate advancement
✅ **Session State Tracking** - **NEW** - Completion criteria enforcement
✅ **Authentic TRT Style** - **NEW** - Uses exact Dr. Q language patterns from PDF
✅ **Spelling Correction** - **NEW** - Handles misspelled therapeutic terms
✅ **Robust Input Processing** - **NEW** - Categorizes and normalizes all inputs
✅ **Clean Architecture** - Optimized folder structure
✅ **Easy Maintenance** - Clear file organization
✅ **Scalable** - Ready for additional sessions

## 🔧 **Key Fixes Implemented**

### ✅ **Sequential Progression Fixed**
- **Problem:** System jumped between substates without completion tracking
- **Solution:** Added `session_state_manager.py` with completion criteria
- **Result:** System now stays in 1.1 until goal ✓ + vision ✓, then advances to 1.2

### ✅ **Master Planning Agent Updated**
- **Updated:** `core_system/optimized_master_agent.txt`
- **New Logic:** Completion-based navigation instead of reactive pattern matching
- **Features:** Advancement blocking until all criteria met

### ✅ **Complete Integration**
- **New File:** `integrated_trt_system.py` - Production-ready complete system
- **Components:** Master Planning + Session State + RAG + Dialogue Generation
- **Testing:** `quick_advancement_test.py` demonstrates proper progression

### ✅ **Authentic TRT Style Implementation** (NEW)
- **Problem:** System responses didn't match authentic Dr. Q language patterns
- **Solution:** Updated dialogue responses using exact TRT PDF language
- **Features:**
  - Dr. Q's exact goal clarification questions: "What do you want our time to get accomplished?"
  - Generic Outcome State template: "I'm seeing you who used to have that problem..."
  - Present-moment focus: "What's happening now? How's your body feeling?"
  - Clarifying vs curiosity questions: "How do you know?" technique

### ✅ **Spelling Correction & Robust Input Processing** (NEW)
- **Problem:** System couldn't handle spelling mistakes or categorize misspelled inputs
- **Solution:** Added `input_preprocessing.py` with comprehensive error correction
- **Features:**
  - Common therapeutic vocabulary dictionary (400+ words)
  - Fuzzy matching for misspelled emotional terms
  - Input categorization (goal_statement, feeling_statement, problem_description, etc.)
  - Emotional state detection (crisis_level, moderate_distress, mild_distress, etc.)
  - Correction tracking and reporting

### ✅ **Enhanced Master Agent Categorization** (NEW)
- **Problem:** Master agent couldn't properly categorize variant or misspelled inputs
- **Solution:** Integrated preprocessing into master planning pipeline
- **Features:**
  - Processes corrected input for better categorization
  - Tracks original vs corrected input for transparency
  - Maintains emotional context through preprocessing

---

**Version:** 4.0 - Authentic TRT with Robust Input Processing
**Last Updated:** October 2025
**Status:** ✅ **AUTHENTIC DR. Q STYLE + ROBUST ERROR HANDLING**
**Next Steps:** Add Stage 2 TRT methodology support

## 🆕 **Version 4.0 Features**

### **Authentic TRT Language Patterns**
- Uses Dr. Q's exact questions from TRT PDF
- Implements Generic Outcome State template
- Present-moment focus with "What's happening now?"
- Proper clarifying vs curiosity question distinction

### **Robust Input Processing**
- Handles 400+ therapeutic vocabulary terms
- Corrects common spelling mistakes automatically
- Categorizes input types for better navigation
- Detects emotional intensity levels
- Maintains correction transparency

### **Enhanced System Integration**
- Seamless preprocessing → navigation → dialogue pipeline
- Maintains original and corrected input tracking
- Preserves emotional context through processing
- Compatible with existing RAG and session management

### **Example Improvements**
```
BEFORE: "Tell me more about what's been going on."
AFTER:  "What do you want our time to get accomplished? What do we want to get better for you?"

BEFORE: [System fails on "iwll feeling realy stresed"]
AFTER:  [Corrects to "will feeling really stressed" → responds appropriately]
```