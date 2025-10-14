# How to Rebuild RAG with All Your Transcripts

## What This Does

These scripts will:
1. **Process ALL your transcripts** (20+ files found in `data/Session Transcripts/`)
2. **Automatically identify** `[DOCTOR]` (Dr. Q) vs `[PATIENT]`
3. **Extract exchanges** (Doctor question → Patient response pairs)
4. **Auto-label** each exchange (goal setting, body awareness, vision building, etc.)
5. **Generate embeddings** for RAG retrieval
6. **Rebuild FAISS index** with ALL Dr. Q examples

## Step-by-Step Instructions

### Step 1: Process All Transcripts
```bash
cd "/media/eizen-4/2TB/gaurav/AI Therapist/Therapist2"
source venv/bin/activate

# Process all raw transcripts into labeled exchanges
python code_implementation/process_all_transcripts.py
```

**Expected output:**
```
Found 23 transcript files

Processing: session_01.txt
  ✅ Extracted 45 exchanges
Processing: Madison B 10-04-21 Initial_transcript.txt
  ✅ Extracted 67 exchanges
...

✅ Saved 1,234 exchanges to data/processed_exchanges/all_dr_q_exchanges.json
```

### Step 2: Rebuild RAG with All Exchanges
```bash
# Rebuild FAISS index with all processed exchanges
python code_implementation/rebuild_rag_with_all_transcripts.py
```

**Expected output:**
```
📚 Loading processed exchanges...
✅ Loaded 1,234 exchanges from 23 files

🤖 Loading embedding model...
✅ Model loaded

🧮 Generating embeddings...
✅ Generated embeddings with shape: (1234, 384)

📊 Creating FAISS index...
✅ FAISS index created with 1234 vectors

💾 Saving...
✅ Saved FAISS index to data/embeddings/trt_rag_index.faiss
✅ Saved metadata to data/embeddings/trt_rag_metadata.json

📊 DISTRIBUTION BY DR. Q TECHNIQUE:
  goal_clarification: 187
  specific_somatic_questioning: 156
  how_do_you_know_questioning: 143
  vision_acceptance_check: 98
  ...
```

### Step 3: Test the Updated System
```bash
# Run manual test to see improved responses
python code_implementation/test_integrated_system.py
```

## What You'll Notice After Rebuilding

### Before (with only 3-5 examples):
```
YOU: I don't know
THERAPIST: "What do we want our time to focus on today?"
(Generic, keeps repeating)
```

### After (with 1000+ examples):
```
YOU: I don't know
THERAPIST: "That makes sense. What if you could feel lighter, at ease, more peaceful? Would that be good?"
(Offers menu, matches Dr. Q's exact style from similar situations)
```

## What Gets Auto-Labeled

The script automatically identifies:

### 1. **Dr. Q Techniques**
- `goal_clarification` - "What do we want our time to focus on?"
- `specific_somatic_questioning` - "Where in your body? What kind of sensation?"
- `how_do_you_know_questioning` - "How do you know when that starts?"
- `vision_acceptance_check` - "Does that make sense to you?"
- `present_moment_somatic_observation` - "You're feeling that right now"

### 2. **TRT Substates**
- `1.1_goal_and_vision` - Goal setting and future vision
- `1.2_problem_and_body` - Problem exploration and body awareness
- `general_therapeutic_exchange` - Other therapeutic moments

### 3. **Client Presentations**
- `client_uncertain_or_confused` - "I don't know"
- `body_awareness_present` - Mentions chest, head, leg, etc.
- `goal_statement` - "I want to feel peaceful"
- `client_agreement_or_acceptance` - "Yes, exactly, that's right"

### 4. **Embedding Tags**
- `i_dont_know_response` - For "I don't know" situations
- `body_location_mentioned` - When client mentions body parts
- `affirmative_response` - When client agrees
- `present_moment` - When talking about "right now"

## File Locations

After processing:
```
data/
├── Session Transcripts/          (Your raw transcripts - unchanged)
│   ├── Madison B 10-04-21 Initial_transcript.txt
│   ├── Nikki S 04-17-23 1 month follow up_transcript.txt
│   └── ... (20+ more files)
│
├── processed_exchanges/           (NEW - Created by script)
│   └── all_dr_q_exchanges.json   (All labeled exchanges)
│
└── embeddings/                    (UPDATED - RAG index)
    ├── trt_rag_index.faiss       (FAISS vector index - UPDATED)
    └── trt_rag_metadata.json     (Exchange metadata - UPDATED)
```

## Checking What Was Processed

To see what exchanges were extracted:
```bash
# View the processed exchanges file
cat data/processed_exchanges/all_dr_q_exchanges.json | jq '.metadata'

# Or use Python
python -c "
import json
with open('data/processed_exchanges/all_dr_q_exchanges.json') as f:
    data = json.load(f)
print(f'Total exchanges: {len(data[\"exchanges\"])}')
print(f'Files processed: {len(data[\"metadata\"][\"source_files\"])}')
"
```

## Troubleshooting

### If process_all_transcripts.py fails:
- Check that transcript files have `[DOCTOR]` and `[PATIENT]` labels
- Check for encoding issues (script uses UTF-8)

### If rebuild_rag_with_all_transcripts.py fails:
- Make sure you ran `process_all_transcripts.py` first
- Check that `data/processed_exchanges/all_dr_q_exchanges.json` exists

### If responses don't improve:
- Check the distribution stats after rebuild
- Make sure the system is loading the new index (restart test script)

## Expected Improvements

With 1000+ real Dr. Q exchanges, the system will:
- ✅ Match Dr. Q's exact phrasing for similar situations
- ✅ Offer menu options when client says "I don't know"
- ✅ Use his natural affirmations ("That's right", "Yeah", "Got it")
- ✅ Ask body awareness questions with his soft, artfully vague style
- ✅ Build vision with his detailed future descriptions
- ✅ Use "How do you know?" technique naturally

**Your system will sound much more like the real Dr. Q!**
