# How to Add More Dr. Q Transcripts to Improve the System

## Why This Helps

Adding more transcripts will:
1. **Improve RAG retrieval** - More examples = better matching for similar situations
2. **Capture Dr. Q's natural language** - Learn his exact phrasing and style
3. **Better handle edge cases** - See how he handles "I don't know", resistance, etc.
4. **Improve LLM prompting** - More examples for the LLM to learn from

## Where to Put Transcripts

**Option 1: Add to existing structure (Recommended)**
```
data/transcripts/
├── session_01.txt  (existing)
├── session_02.txt  (existing)
├── session_03.txt  (existing)
├── session_04.txt  (NEW)
├── session_05.txt  (NEW)
└── ... (add more)
```

**Option 2: Create labeled exchanges (Better for specific situations)**
```
examples/
├── labeled_exchanges_example.json (existing)
├── labeled_exchanges_i_dont_know.json (NEW - for "I don't know" responses)
├── labeled_exchanges_body_awareness.json (NEW - for body inquiry)
├── labeled_exchanges_vision_building.json (NEW - for vision building)
└── ... (add more by topic)
```

## Format for New Transcripts

### Simple Text Format (data/transcripts/session_XX.txt)
```
THERAPIST: What do we want our time to focus on today?
CLIENT: I don't know, I'm just feeling really down.
THERAPIST: That makes sense. What if you could feel lighter, at ease, more okay in yourself? Would that be good?
CLIENT: Yes, that would be good.
THERAPIST: Good. So we want you feeling lighter, at ease. Does that make sense to you?
CLIENT: Yes.

[Continue with rest of session...]
```

### Labeled JSON Format (examples/labeled_exchanges_*.json)
```json
{
  "i_dont_know_responses": [
    {
      "exchange_id": "idk_001",
      "doctor_input": "That makes sense. What if you could feel lighter, at ease, more okay in yourself? Would that be good?",
      "patient_response": "Yes, that would be good.",
      "context_before": "Client said: 'I don't know, I'm just feeling really down.'",
      "therapeutic_labels": {
        "trt_stage": "stage_1_safety_building",
        "trt_substate": "1.1_goal_and_vision",
        "situation_type": "i_dont_know_goal_offering_menu",
        "dr_q_technique": "vision_language_menu_offering",
        "client_presentation": "uncertain_about_goal",
        "outcome": "accepts_offered_vision"
      },
      "embedding_tags": [
        "i_dont_know", "vision_menu", "lighter", "at_ease",
        "goal_uncertainty", "dr_q_menu_offering"
      ],
      "rag_retrieval_contexts": [
        "client_says_i_dont_know_about_goal",
        "dr_q_offers_vision_language_menu",
        "uncertain_client_accepts_suggestion"
      ]
    }
  ]
}
```

## Steps to Add Transcripts and Rebuild RAG

### 1. Add transcript files to the project
```bash
# Put your new transcript files in:
/media/eizen-4/2TB/gaurav/AI Therapist/Therapist2/data/transcripts/
```

### 2. Update the transcript processing script
The system needs to process these into labeled exchanges. Create a script:

```python
# transcript_processor.py
import json

def process_new_transcripts():
    """Process new transcripts into labeled exchanges"""

    # Read new transcript
    with open('data/transcripts/session_04.txt', 'r') as f:
        transcript = f.read()

    # Parse into exchanges
    exchanges = []
    lines = transcript.split('\n')

    current_therapist = ""
    current_client = ""

    for line in lines:
        if line.startswith('THERAPIST:'):
            current_therapist = line.replace('THERAPIST:', '').strip()
        elif line.startswith('CLIENT:'):
            current_client = line.replace('CLIENT:', '').strip()

            if current_therapist and current_client:
                # Create labeled exchange
                exchange = {
                    "doctor_input": current_therapist,
                    "patient_response": current_client,
                    # Add labels manually or automatically
                }
                exchanges.append(exchange)

                current_therapist = ""
                current_client = ""

    return exchanges
```

### 3. Rebuild the RAG embeddings
```bash
cd "/media/eizen-4/2TB/gaurav/AI Therapist/Therapist2"
source venv/bin/activate

# Run the embedding setup again with new transcripts
python code_implementation/embedding_and_retrieval_setup.py
```

This will:
- Load all transcripts (old + new)
- Generate embeddings for new exchanges
- Update the FAISS index
- Save to `data/embeddings/`

## What Specific Transcripts Would Help Most

Based on your test session, prioritize transcripts showing:

1. **"I don't know" responses** - How Dr. Q offers menu of options
2. **Early goal setting** - First 3-5 exchanges of sessions
3. **Body awareness inquiry** - How he asks about sensations (soft approach)
4. **Vision building** - How he paints the future picture
5. **Thinking mode redirects** - When client is analyzing vs. feeling
6. **Past tense redirects** - When client talks about past
7. **Psycho-education** - Zebra-lion or brain explanations

## Quick Start: Add One Transcript Now

1. **Find a transcript** with good "I don't know" handling
2. **Save it** as `data/transcripts/session_idk_examples.txt`
3. **Label key exchanges** in `examples/labeled_exchanges_i_dont_know.json`
4. **Rebuild RAG**:
   ```bash
   python code_implementation/embedding_and_retrieval_setup.py
   ```
5. **Test** - The system will now retrieve those examples!

## Benefits You'll See

- ✅ More natural responses (matching Dr. Q's exact phrasing)
- ✅ Better handling of "I don't know" (offering menus)
- ✅ Improved body awareness questions (soft, artfully vague)
- ✅ Better vision building (detailed future descriptions)
- ✅ More varied affirmations ("That's right", "Yeah", "Got it")

**Would you like me to create a script to help process new transcripts automatically?**
