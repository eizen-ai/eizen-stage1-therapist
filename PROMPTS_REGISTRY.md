# TRT AI Therapist - Prompts Registry

## Overview
This document provides a complete map of all prompts used in the TRT AI Therapist system.

## Current Status
✅ **Centralized Registry Complete**: `config/prompts/system_prompts.json`
✅ **All Prompts Extracted**: 100% of prompts are now in the registry
⚠️ **Code Migration Pending**: Some agent methods still use hardcoded prompts (but duplicates exist in registry)

---

## Prompt Locations

### 1. **Master Planning Agent** (Navigation Decisions)
**Location**: `src/agents/ollama_llm_master_planning_agent.py`

**Prompts**:
- **therapeutic_reasoning**: Main navigation decision prompt
  - **Stored in**: `config/prompts/system_prompts.json` → `master_planning_agent.therapeutic_reasoning`
  - **Status**: ✅ Using prompt registry (line 447)
  - **Purpose**: Guides LLM to make therapy navigation decisions based on current state

---

### 2. **Dialogue Agent** (Therapeutic Responses)
**Location**: `src/agents/improved_ollama_dialogue_agent.py`

| Prompt Name | Config Location | Code Method | Status |
|-------------|----------------|-------------|---------|
| **emotion_detection** | `dialogue_agent.emotion_detection` | N/A | ✅ In registry |
| **emotion_inquiry** | `dialogue_agent.emotion_inquiry` | `_construct_emotion_inquiry_prompt()` (line 1367) | ✅ In registry (hardcoded duplicate exists) |
| **emotion_to_body** | `dialogue_agent.emotion_to_body` | `_construct_emotion_to_body_prompt()` (line 1394) | ✅ In registry (hardcoded duplicate exists) |
| **what_else_inquiry** | `dialogue_agent.what_else_inquiry` | `_construct_what_else_prompt()` (line 1424) | ✅ In registry (hardcoded duplicate exists) |
| **sensation_quality** | `dialogue_agent.sensation_quality` | `_construct_sensation_quality_prompt()` (line 1451) | ✅ In registry (hardcoded duplicate exists) |
| **present_moment** | `dialogue_agent.present_moment` | `_construct_present_moment_prompt()` (line 1489) | ✅ In registry (hardcoded duplicate exists) |
| **body_location_followup** | `dialogue_agent.body_location_followup` | `_construct_body_location_followup_prompt()` (line 1503) | ✅ In registry (hardcoded duplicate exists) |
| **sensation_followup** | `dialogue_agent.sensation_followup` | `_construct_sensation_followup_prompt()` (line 1533) | ✅ In registry (hardcoded duplicate exists) |
| **sensation_to_present** | `dialogue_agent.sensation_to_present` | `_construct_sensation_followup_prompt()` (line 1546) | ✅ In registry (hardcoded duplicate exists) |
| **problem_to_body** | `dialogue_agent.problem_to_body` | `_construct_problem_to_body_prompt()` (line 1558) | ✅ In registry (hardcoded duplicate exists) |
| **initial_body_location** | `dialogue_agent.initial_body_location` | `_construct_initial_body_location_prompt()` (line 1582) | ✅ In registry (hardcoded duplicate exists) |
| **general_therapeutic** | `dialogue_agent.general_therapeutic` | `_construct_general_therapeutic_prompt()` (line 1605) | ✅ In registry (hardcoded duplicate exists) |

---

### 3. **Redirects** (Safety & Special Cases)
**Location**: `config/prompts/system_prompts.json` → `redirects`

**Prompts**:
- `thinking_mode`: "Yeah, I hear you thinking about it. Rather than thinking, what are you FEELING right now?"
- `past_tense`: "Got it. That was then. Right now, in this moment, what are you FEELING?"
- `alpha_permission`: "Okay. I'm going to guide you through a brief process. Are you ready?"
- `alpha_permission_reassurance`: "It's very simple, just a few minutes. I'll guide you through it. Ready to try?"

**Status**: ✅ Loaded via `prompt_loader.get_redirect()`

---

### 4. **Rule-Based Responses** (Hardcoded in Code)
**Location**: `src/agents/improved_ollama_dialogue_agent.py`

These are NOT LLM prompts but fixed therapeutic responses:

| Response Type | Method | Line |
|--------------|--------|------|
| Vision building | `_generate_vision_building_response()` | 1082 |
| Problem inquiry | `_generate_problem_inquiry_response()` | 926 |
| Readiness assessment | `_generate_readiness_assessment_response()` | 973 |
| Affirmation responses | `_get_affirmation_response()` | 684 |

---

## Prompt Registry Structure

### File: `config/prompts/system_prompts.json`

```json
{
  "master_planning_agent": {
    "therapeutic_reasoning": {
      "template": "You are Dr. Q, an expert TRT therapist..."
    }
  },
  "dialogue_agent": {
    "emotion_detection": { "template": "..." },
    "emotion_inquiry": { "template": "..." },
    "emotion_to_body": { "template": "..." },
    "what_else_inquiry": { "template": "..." },
    "sensation_quality": { "template": "..." },
    "present_moment": { "template": "..." },
    "general_therapeutic": { "template": "..." }
  },
  "redirects": {
    "thinking_mode": "...",
    "past_tense": "...",
    "alpha_permission": "...",
    "alpha_permission_reassurance": "..."
  }
}
```

---

## How to Update Prompts

### Option 1: Edit Config File (Recommended)
Edit `config/prompts/system_prompts.json` and restart the Docker container:
```bash
docker compose restart trt-app
```

### Option 2: Edit Hardcoded Prompts (Not Recommended)
Edit the Python files directly:
- `src/agents/ollama_llm_master_planning_agent.py`
- `src/agents/improved_ollama_dialogue_agent.py`

---

## Accessing Prompts in Code

### Using Prompt Loader (Recommended)
```python
from src.utils.prompt_loader import get_prompt_loader

prompt_loader = get_prompt_loader()

# Load a template
template = prompt_loader.get_prompt('dialogue_agent', 'emotion_inquiry')

# Format with variables
prompt = template.format(
    client_input="I feel stressed",
    rag_examples="Example 1...",
    emotion_content="stress"
)

# Load a redirect
redirect = prompt_loader.get_redirect('thinking_mode')
```

---

## Extraction Complete ✅

All prompts have been successfully extracted to the registry!

**Recently Added** (2025-10-21):
1. ✅ `body_location_followup` - Ask sensation after client gives body location
2. ✅ `sensation_followup` - Follow up after sensation described
3. ✅ `sensation_to_present` - Present moment after sensation
4. ✅ `problem_to_body` - Ask about body location when problem mentioned
5. ✅ `initial_body_location` - General body awareness inquiry

---

## RAG Examples

**Location**: `data/embeddings/`
- `trt_rag_index.faiss` - Vector embeddings of Dr. Q's therapy transcripts
- `trt_rag_metadata.json` - Metadata for RAG examples

**Usage**: Retrieved dynamically based on therapeutic context (not static prompts)

---

## GitHub Repository

**Main Branch**: (Add your repo URL here)

**Prompt Files**:
- `config/prompts/system_prompts.json` - Main prompt registry
- `config/prompts/README.md` - Prompt documentation

---

## Next Steps (Recommendations)

1. ✅ **COMPLETE: All prompts extracted** to `system_prompts.json`
2. **TODO: Refactor dialogue agent** to load prompts from registry instead of hardcoded methods
   - This requires updating ~10 methods in `improved_ollama_dialogue_agent.py`
   - Low priority: System works with current duplicates
3. **TODO: Version control prompts** separately from code for easier iteration
4. **TODO: Create prompt versioning** (e.g., `v1`, `v2`) for A/B testing
5. **TODO: Add prompt evaluation metrics** to track effectiveness
6. **TODO: Document prompt change history** for team visibility

---

## Contact

For prompt updates or questions, contact the development team.

**Last Updated**: 2025-10-21
