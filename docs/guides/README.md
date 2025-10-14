# TRT AI Therapy System

A multi-agent AI therapy system based on Dr. Jason Quintal's TRT (Trauma Resolution Therapy) methodology, featuring RAG-based retrieval of authentic therapeutic examples.

## 🚀 Quick Start

1. **Activate the environment:**
   ```bash
   source therapy_env/bin/activate
   ```

2. **Test the RAG system:**
   ```bash
   python3 test_rag_validation.py
   ```

3. **For new transcripts:**
   ```bash
   python3 transcript_processing_pipeline.py
   python3 embedding_and_retrieval_setup.py
   ```

## 📁 Core System Files

### 🧠 Master Planning Agent
| File | Purpose | When to Modify |
|------|---------|----------------|
| `optimized_master_agent.txt` | Main navigation prompt for master planning agent | Add new TRT stages or modify navigation logic |
| `simplified_navigation.json` | Substate definitions and completion criteria | Update TRT methodology or add new substates |
| `input_classification_patterns.json` | Pattern matching for client inputs | Add new client presentation patterns |

**Usage:** These 3 files power the master planning agent that determines TRT stage, substate, and navigation decisions.

### 🔍 RAG Retrieval System
| File | Purpose | Size | When to Update |
|------|---------|------|----------------|
| `embedding_and_retrieval_setup.py` | Complete RAG system implementation | 11KB | Modify embedding strategy or search parameters |
| `trt_rag_index.faiss` | Pre-built FAISS index for fast similarity search | 1.5MB | Regenerate when adding new sessions |
| `trt_rag_metadata.json` | Metadata for all embedded exchanges | 900KB | Regenerate with new transcripts |
| `complete_embedding_dataset.json` | All processed exchanges ready for embedding | 1MB | Regenerate when processing new sessions |

**Usage:** Load the pre-built index for instant RAG retrieval:
```python
from embedding_and_retrieval_setup import TRTRAGSystem
rag_system = TRTRAGSystem()
rag_system.load_index("trt_rag_index.faiss", "trt_rag_metadata.json")
examples = rag_system.get_few_shot_examples(navigation_output, client_message)
```

### 📝 Transcript Processing
| File | Purpose | Size | When to Use |
|------|---------|------|-------------|
| `transcript_processing_pipeline.py` | Extracts and labels therapeutic exchanges | 15KB | Process new session transcripts |
| `session_01_labeled_exchanges.json` | Processed exchanges from session 1 | 428KB | Reference for exchange structure |
| `session_02_labeled_exchanges.json` | Processed exchanges from session 2 | 645KB | Reference for exchange structure |
| `session_03_labeled_exchanges.json` | Processed exchanges from session 3 | 237KB | Reference for exchange structure |

**Usage:** Process new session transcripts:
```python
from transcript_processing_pipeline import TRTTranscriptProcessor
processor = TRTTranscriptProcessor()
session_data = processor.process_session_file("new_session.txt", "session_04")
embedding_data = processor.create_embedding_dataset(session_data)
```

## 🔧 Development Environment

### Virtual Environment
- **`therapy_env/`** - Python virtual environment with all dependencies
- **Activate:** `source therapy_env/bin/activate`
- **Packages:** numpy, sentence-transformers, faiss-cpu, torch, scikit-learn

### Testing & Validation
- **`test_rag_validation.py`** - Comprehensive RAG system testing
- **`labeled_exchanges_example.json`** - Example of properly labeled exchanges
- **`complete_stage_1_flow_example.txt`** - Complete Stage 1 therapeutic flow example

## 🔄 Common Tasks

### Adding New Session Transcripts
1. **Add transcript file:** `session_04.txt` (format: `[DOCTOR]: text` and `[PATIENT]: text`)
2. **Process transcript:**
   ```python
   processor = TRTTranscriptProcessor()
   session_data = processor.process_session_file("session_04.txt", "session_04")
   ```
3. **Regenerate embeddings:**
   ```bash
   python3 transcript_processing_pipeline.py
   python3 embedding_and_retrieval_setup.py
   ```

### Modifying TRT Navigation Logic
1. **Update substates:** Edit `simplified_navigation.json`
2. **Add new patterns:** Update `input_classification_patterns.json`
3. **Modify master agent:** Edit `optimized_master_agent.txt`

### Customizing RAG Retrieval
1. **Change embedding model:** Modify `model_name` in `TRTRAGSystem.__init__()`
2. **Adjust similarity threshold:** Modify search parameters in `retrieve_similar_exchanges()`
3. **Add new retrieval contexts:** Update `_create_rag_contexts()` in transcript processor

### Testing New Scenarios
1. **Add test cases:** Edit `test_rag_validation.py`
2. **Run validation:** `python3 test_rag_validation.py`

## 📊 System Performance

- **Total Exchanges:** 1,000 therapeutic exchanges from 3 sessions
- **Embedding Dimension:** 384 (MiniLM model)
- **Retrieval Speed:** ~50ms per query
- **Memory Usage:** ~2GB (including embeddings)

## 🗂️ Data Sources

### Essential Reference Files
- **`TRT for Staff.pdf`** - Core TRT methodology documentation
- **`session_01.txt`** - Clean Dr. Q transcript (session 1)
- **`session_02.txt`** - Clean Dr. Q transcript (session 2)
- **`session_03.txt`** - Clean Dr. Q transcript (session 3)

### Original Labeled Data (Raw)
- **`session_01_labeled.json`** - Detailed transcript with timing (4.5MB)
- **`session_02_labeled.json`** - Detailed transcript with timing (5.5MB)
- **`session_03_labeled.json`** - Detailed transcript with timing (2.6MB)

*Note: These are the original detailed transcripts with word-level timing. Not used directly by the system but kept as reference.*

## ⚙️ System Architecture

```
Master Planning Agent (Navigation Only)
    ↓ (stage, substate, situation_type, rag_query)
RAG System (Retrieval)
    ↓ (2-3 authentic Dr. Q examples)
Dialogue Agent (Response Generation)
```

### Key Design Principles
1. **Master Agent:** Pure navigation logic, no response generation
2. **RAG System:** Authentic Dr. Q examples only
3. **Dialogue Agent:** Uses RAG examples as few-shot prompts
4. **Stage 1 Focus:** Complete coverage of safety building phase

## 🛠️ Maintenance & Updates

### Regular Maintenance
- **Monthly:** Validate RAG retrieval quality with new test cases
- **Per new session:** Regenerate embeddings and test retrieval
- **Per TRT update:** Update navigation JSON and master agent prompt

### Performance Optimization
- **Index rebuilding:** Regenerate FAISS index if adding >100 new exchanges
- **Memory management:** Monitor embedding cache size
- **Query optimization:** Analyze slow queries and optimize patterns

## 🚨 File Cleanup Recommendations

### Files Safe to Delete
These files are no longer needed for the system operation:
- `FILE_CLEANUP_AND_EMBEDDING_PLAN.txt` - Planning document (temporary)
- `__pycache__/` - Python cache directory
- `.claude/` - Claude code session data

### Critical Files - Never Delete
- All `.py` files (system logic)
- `trt_rag_index.faiss` and `trt_rag_metadata.json` (pre-built RAG system)
- `session_*.txt` files (source transcripts)
- Navigation JSON files (system configuration)

## 📞 Troubleshooting

### Common Issues
1. **"Module not found":** Ensure virtual environment is activated
2. **"NumPy compatibility":** Use `pip install "numpy<2"`
3. **"Index not found":** Run `python3 embedding_and_retrieval_setup.py`
4. **Low similarity scores:** Check if query matches training data domain

### Getting Help
- Check `test_rag_validation.py` for usage examples
- Review `complete_stage_1_flow_example.txt` for therapeutic flow
- Examine `labeled_exchanges_example.json` for data structure

---

**System Status:** ✅ Production Ready
**Last Updated:** October 2025
**Version:** 1.0 - Complete Stage 1 Implementation