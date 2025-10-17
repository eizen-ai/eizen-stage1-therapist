# RAG (Retrieval-Augmented Generation) System

This file explains how the RAG system retrieves Dr. Q's therapy examples to guide AI responses.

**Location in code:** `src/utils/embedding_and_retrieval_setup.py`

---

## What is RAG?

**RAG = Retrieval-Augmented Generation**

Instead of making the AI generate responses from scratch, we:
1. **Retrieve** similar examples from Dr. Q's actual therapy transcripts
2. **Augment** the AI prompt with these real examples
3. **Generate** responses that match Dr. Q's proven style

**Why it works:** The AI sees exactly how Dr. Q handled similar situations, then mimics that style.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                 RAG SYSTEM FLOW                      │
└─────────────────────────────────────────────────────┘

1. CLIENT INPUT
   "I'm stressed about work"
          ↓
2. MASTER PLANNING DECISION
   {
     "situation_type": "emotion_to_body",
     "rag_query": "dr_q_body_location_inquiry"
   }
          ↓
3. RAG RETRIEVAL (embedding_and_retrieval_setup.py)
   → Convert query to embedding (384D vector)
   → Search FAISS index for similar exchanges
   → Filter by context: "dr_q_body_location_inquiry"
   → Return top 3 most similar examples
          ↓
4. RETRIEVED EXAMPLES
   [
     "Where in your chest? Upper chest or center?",
     "And where is that tightness? What part of your body?",
     "When you notice that feeling, where is it?"
   ]
          ↓
5. DIALOGUE AGENT PROMPT
   You are Dr. Q. Client mentioned stress.

   Dr. Q examples:
   1. "Where in your chest?..."
   2. "And where is that tightness?..."

   Generate response like Dr. Q.
          ↓
6. GENERATED RESPONSE
   "When you feel that stress from work, where in your
   body do you notice it? What location comes to mind?"
```

---

## Components

### 1. Sentence Transformer Model

**Model:** `all-MiniLM-L6-v2`

**Why this model:**
- Lightweight (80MB)
- Fast inference (<50ms per query)
- High quality embeddings (384 dimensions)
- Excellent for semantic similarity

**Location:** Line 24, 29

```python
self.model = SentenceTransformer("all-MiniLM-L6-v2")
self.dimension = 384  # Embedding size
```

**How to change model:**

```python
# For better quality (slower, larger)
self.model = SentenceTransformer("all-mpnet-base-v2")  # 420MB, 768D

# For faster inference (lower quality)
self.model = SentenceTransformer("all-MiniLM-L12-v2")  # 120MB, 384D
```

---

### 2. FAISS Index

**Index Type:** `IndexFlatIP` (Inner Product for cosine similarity)

**Location:** Line 69

```python
self.index = faiss.IndexFlatIP(self.dimension)  # Inner product search
faiss.normalize_L2(embeddings)  # Normalize for cosine similarity
self.index.add(embeddings)
```

**Why FAISS:**
- Extremely fast similarity search (microseconds)
- Handles large datasets efficiently
- Supports GPU acceleration (if needed)

**Current dataset size:** ~500-1000 therapeutic exchanges

**Search time:** < 5ms for top-k retrieval

---

### 3. Embedding Creation

**Function:** `_create_embedding_text()`

**Location:** Lines 78-97

**What gets embedded:**

```python
embedding_text = f"""
Therapeutic Exchange: {Dr. Q's actual response + patient reply}

TRT Context: {stage} {substate}
Situation: {situation_type}
Technique: {dr_q_technique}

Tags: {goal_inquiry body_awareness emotion_inquiry}
Contexts: {dr_q_goal_clarification dr_q_body_location_inquiry}
"""
```

**Example embedded text:**

```
Therapeutic Exchange:
Doctor: "Where in your chest do you feel that? Upper chest, center, or more to the side?"
Patient: "Upper chest, on the left side."

TRT Context: stage_1_safety_building 1.2_problem_and_body
Situation: body_location_inquiry
Technique: elaborative_questioning

Tags: body_awareness location_specificity multiple_options
Contexts: dr_q_body_location_inquiry dr_q_body_symptom_inquiry
```

**Why this structure:** Includes context + content for better matching

---

## Retrieval Process

### Primary Retrieval Method

**Function:** `get_few_shot_examples()`

**Location:** Lines 192-258

**Input:**
```python
navigation_output = {
    "current_stage": "stage_1_safety_building",
    "current_substate": "1.2_problem_and_body",
    "situation_type": "emotion_to_body",
    "rag_query": "dr_q_body_location_inquiry"  # CONTEXT FILTER
}
client_message = "I'm stressed about work"
max_examples = 3
```

**Process:**

1. **Step 1: Context-Filtered Search** (Lines 217-225)
   ```python
   # Search with specific context filter
   results = retrieve_similar_exchanges(
       f"{client_message} {situation_type}",
       top_k=3,
       context_filter="dr_q_body_location_inquiry"  # FILTER!
   )
   ```
   **Only returns exchanges tagged with "dr_q_body_location_inquiry"**

2. **Step 2: Fallback to General Search** (Lines 228-239)
   ```python
   # If not enough results, search by therapeutic context
   if len(results) < max_examples:
       results = retrieve_by_therapeutic_context(
           trt_stage="stage_1_safety_building",
           situation_type="emotion_to_body",
           client_input=client_message,
           top_k=3
       )
   ```

3. **Step 3: Return Formatted Examples** (Lines 248-256)
   ```python
   few_shot_examples = [
       {
           "doctor_example": "Where in your chest?...",
           "similarity_score": 0.87,
           "therapeutic_context": {...},
           "usage_note": "Use this Dr. Q style for emotion_to_body"
       }
   ]
   ```

---

## RAG Query Types

Each navigation decision includes a RAG query for retrieving relevant examples:

| RAG Query | Retrieves Examples Of | Used When |
|-----------|----------------------|-----------|
| `dr_q_goal_clarification` | Goal inquiry questions | Client hasn't stated goal |
| `dr_q_future_self_vision_building` | Vision building dialogue | Building future self image |
| `dr_q_problem_construction` | Problem exploration | Identifying core problem |
| `dr_q_body_location_inquiry` | Body location questions | Ask where in body |
| `dr_q_body_symptom_present_moment_inquiry` | Present moment body focus | General body awareness |
| `dr_q_sensation_quality_inquiry` | Sensation quality questions | "What kind of sensation?" |
| `dr_q_how_do_you_know_technique` | Pattern exploration | "How do you know?" |
| `dr_q_ready` | Readiness assessment | Before alpha sequence |
| `dr_q_alpha_jaw_focus` | Jaw release guidance | Alpha step 1 |
| `dr_q_alpha_tongue_focus` | Tongue release guidance | Alpha step 2 |
| `dr_q_alpha_breathing_focus` | Breathing guidance | Alpha step 3 |
| `general_dr_q_approach` | General therapeutic style | Fallback |

---

## Similarity Search

**Function:** `retrieve_similar_exchanges()`

**Location:** Lines 99-157

**How it works:**

1. **Convert query to embedding**
   ```python
   query_embedding = self.model.encode([query])  # → 384D vector
   faiss.normalize_L2(query_embedding)
   ```

2. **Search FAISS index**
   ```python
   similarities, indices = self.index.search(
       query_embedding,
       top_k * 2  # Get more for filtering
   )
   ```

3. **Apply context filter**
   ```python
   if context_filter:  # e.g., "dr_q_body_location_inquiry"
       contexts = metadata_entry.get("retrieval_contexts", [])
       if context_filter not in contexts:
           continue  # Skip this result
   ```

4. **Return top results**
   ```python
   return results[:top_k]  # Top 3 by default
   ```

---

## Similarity Scoring

**Method:** Cosine similarity (0.0 to 1.0)

**Interpretation:**
- **0.9 - 1.0:** Near-identical situations
- **0.8 - 0.9:** Very similar situations
- **0.7 - 0.8:** Similar situations
- **0.6 - 0.7:** Somewhat similar
- **< 0.6:** Low similarity (usually filtered out)

**Example:**

```
Query: "I feel stressed about work deadlines"

Results:
1. Similarity: 0.89 | "I'm stressed about my job performance"
   → Dr. Q: "Where in your body do you feel that stress?"

2. Similarity: 0.85 | "Work is making me anxious"
   → Dr. Q: "When you feel that work anxiety, where do you notice it?"

3. Similarity: 0.81 | "My boss is stressing me out"
   → Dr. Q: "And where is that stress in your body?"
```

---

## Embedding Dataset

**Location:** `data/embeddings/`

### Files

```
data/embeddings/
├── trt_rag_index.faiss           # FAISS index (binary, ~5-10MB)
├── trt_rag_metadata.json         # Metadata (JSON, ~2-5MB)
└── complete_embedding_dataset.json  # Source data (JSON, ~10-20MB)
```

### Metadata Structure

Each entry in `trt_rag_metadata.json`:

```json
{
  "id": "exchange_0001",
  "content": "Doctor: Where in your chest?\nPatient: Upper left.",
  "metadata": {
    "trt_stage": "stage_1_safety_building",
    "trt_substate": "1.2_problem_and_body",
    "situation_type": "body_location_inquiry",
    "dr_q_technique": "elaborative_questioning"
  },
  "tags": [
    "body_awareness",
    "location_specificity",
    "chest_symptoms"
  ],
  "retrieval_contexts": [
    "dr_q_body_location_inquiry",
    "dr_q_body_symptom_present_moment_inquiry"
  ]
}
```

---

## Performance

### Retrieval Speed

- **Query embedding:** ~10-20ms
- **FAISS search:** ~2-5ms
- **Filtering & formatting:** ~1-2ms
- **Total:** ~15-30ms per retrieval

### Accuracy

- **Context-filtered search:** ~95% relevant examples
- **Fallback search:** ~85% relevant examples
- **Overall:** High quality Dr. Q examples

---

## Rebuilding Embeddings

If you modify the therapy transcripts or want to add new examples:

**Script:** `scripts/rebuild_embeddings_from_clean_data.py`

**Usage:**

```bash
cd /path/to/project
python scripts/rebuild_embeddings_from_clean_data.py
```

**Process:**

1. Load therapy transcripts from `data/transcripts/`
2. Extract Dr. Q exchanges
3. Tag with contexts (goal_inquiry, body_exploration, etc.)
4. Create embeddings using SentenceTransformer
5. Build FAISS index
6. Save to `data/embeddings/`

**Time:** ~2-5 minutes for 1000 exchanges

---

## Customization

### Change Number of Examples

**Default:** 3 examples per query

**To change:**

```python
# In dialogue agent (line ~1220 in improved_ollama_dialogue_agent.py)
few_shot_examples = self.rag_system.get_few_shot_examples(
    navigation_output,
    client_input,
    max_examples=5  # Changed from 3 to 5
)
```

**Trade-offs:**
- **More examples (4-5):** Better style matching, longer prompts, slower
- **Fewer examples (1-2):** Faster, but less consistent style

---

### Add Custom RAG Queries

**Step 1:** Add context tag to exchanges

Edit `data/embeddings/complete_embedding_dataset.json`:

```json
{
  "id": "exchange_0123",
  "retrieval_contexts": [
    "dr_q_body_location_inquiry",
    "your_custom_context"  // NEW
  ]
}
```

**Step 2:** Use in master planning

```python
# In master_planning_agent.py
return {
    "rag_query": "your_custom_context"
}
```

**Step 3:** Rebuild embeddings

```bash
python scripts/rebuild_embeddings_from_clean_data.py
```

---

### Change Embedding Model

**For better quality (slower):**

```python
# Line 24 in embedding_and_retrieval_setup.py
def __init__(self, model_name: str = "all-mpnet-base-v2"):  # Changed
    self.model = SentenceTransformer(model_name)
    self.dimension = 768  # Update dimension!
```

**For faster inference:**

```python
def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2"):
    self.model = SentenceTransformer(model_name)
    self.dimension = 384  # Same dimension
```

**Important:** After changing model, rebuild embeddings!

---

## RAG Logging

The system logs all RAG retrievals for debugging:

**Location:** Console output / logs

**Example log:**

```
🔍 RAG RETRIEVAL CALLED
   Query Context: dr_q_body_location_inquiry
   Situation: emotion_to_body
   Client Message: I'm stressed about work...
   Max Examples: 3

   → Searching with context filter: dr_q_body_location_inquiry
   → Found 3 results with context filter

✅ RAG RETRIEVED 3 EXAMPLES:
   1. Similarity: 0.872 | exchange_0042
      Dr. Q: Where in your chest do you feel that? Upper chest, center, or more to...
   2. Similarity: 0.845 | exchange_0156
      Dr. Q: And where is that stress? What part of your body?...
   3. Similarity: 0.821 | exchange_0089
      Dr. Q: When you notice that feeling, where is it? Chest, shoulders?...
```

**How to enable:**

Logging is enabled by default in `embedding_and_retrieval_setup.py` (lines 209-245).

To disable:

```python
# Comment out logger statements in get_few_shot_examples()
# Lines 209-245
```

---

## Fallback Mechanism

RAG has two levels of fallback:

### Level 1: Context Filter → General Search

```python
# Try specific context first
results = retrieve_similar_exchanges(
    query,
    context_filter="dr_q_body_location_inquiry"
)

# If not enough, fallback to general therapeutic search
if len(results) < max_examples:
    results = retrieve_by_therapeutic_context(...)
```

### Level 2: No RAG Examples → Use Prompt Without Examples

If RAG returns 0 results (rare), dialogue agent still generates response using prompt rules without Dr. Q examples.

---

## Data Sources

### Primary Source

**File:** `data/transcripts/TRT for Staff.pdf`

**Content:** Dr. Q's actual therapy sessions (anonymized)

**Processing:**
1. Extract text from PDF
2. Identify Dr. Q responses
3. Tag by therapeutic context
4. Create embeddings
5. Build searchable index

### Transcript Structure

Each transcript contains:
- Dr. Q's questions and interventions
- Client responses (anonymized)
- Stage/substate context
- Therapeutic techniques used

---

## Testing RAG

**Script:** `test_rag_system()` in `embedding_and_retrieval_setup.py`

**Usage:**

```python
from src.utils.embedding_and_retrieval_setup import test_rag_system

# Run test
test_rag_system()
```

**What it tests:**

1. Loading embedding dataset
2. Creating embeddings
3. Sample queries:
   - Goal clarification
   - Body symptom exploration
   - Vision building
4. Retrieval accuracy
5. Similarity scores

---

## Best Practices

### 1. Always Use Context Filters

```python
# GOOD
rag_query = "dr_q_body_location_inquiry"

# BAD (too generic)
rag_query = "general_dr_q_approach"
```

**Why:** Specific contexts return more relevant examples.

### 2. Keep Dataset Clean

- Only include high-quality Dr. Q examples
- Tag accurately with retrieval contexts
- Remove duplicates
- Anonymize all patient information

### 3. Monitor Similarity Scores

- **> 0.85:** Excellent match
- **0.75-0.85:** Good match
- **< 0.75:** Consider improving dataset

### 4. Update Embeddings After Changes

Rebuild index whenever you:
- Add new transcripts
- Change tagging
- Modify contexts
- Update source data

---

## Troubleshooting

### Problem: Low similarity scores (< 0.6)

**Cause:** Query doesn't match dataset well

**Solution:**
- Add more diverse examples to dataset
- Use more general context filter
- Check query construction

### Problem: No results returned

**Cause:** Context filter too specific

**Solution:**
- Use fallback to general search
- Check context tag spelling
- Verify dataset has examples with that context

### Problem: Slow retrieval (> 100ms)

**Cause:** Large dataset or inefficient search

**Solution:**
- Use FAISS GPU index (if available)
- Reduce top_k search multiplier (line 116)
- Optimize embedding model

### Problem: Irrelevant examples

**Cause:** Poor tagging or wrong context filter

**Solution:**
- Review and retag dataset
- Use more specific RAG queries
- Add quality filters

---

## Advanced: GPU Acceleration

For very large datasets (10,000+ exchanges):

```python
# Use GPU-accelerated FAISS index
import faiss

res = faiss.StandardGpuResources()
index_cpu = faiss.IndexFlatIP(dimension)
self.index = faiss.index_cpu_to_gpu(res, 0, index_cpu)
```

**Speedup:** 10-100x faster for large datasets

**Requirements:** NVIDIA GPU with CUDA support

---

## See Also

- [Dialogue Agent Prompts](./dialogue_prompts.md) - How RAG examples are used
- [Master Planning Prompts](./master_planning_prompts.md) - RAG query generation
- [Embedding Rebuild Script](../scripts/rebuild_embeddings_from_clean_data.py)

---

**Last Updated:** 2025-10-17
**Version:** 1.0
