# Prompts Configuration

This directory contains all system prompts used by the TRT AI Therapist system.

## 📁 Files

- **system_prompts.json** - Main configuration file containing all prompts

## 🎯 Purpose

All prompts are now externalized to JSON files so you can:
- Edit prompts without touching the code
- Version control prompt changes separately
- A/B test different prompts easily
- Hot-reload prompts without restarting (future feature)

## 📝 How to Edit Prompts

### 1. Open the configuration file
```bash
nano config/prompts/system_prompts.json
```

### 2. Find the prompt you want to edit

The file is organized by category:

```json
{
  "master_planning_agent": {
    "therapeutic_reasoning": {
      "template": "Your prompt here with {placeholders}"
    }
  },
  "dialogue_agent": {
    "emotion_detection": {...},
    "emotion_inquiry": {...},
    "general_therapeutic": {...}
  },
  "redirects": {
    "thinking_mode": "Direct response text",
    "past_tense": "Direct response text"
  }
}
```

### 3. Edit the prompt

Prompts use placeholders like `{client_input}`, `{emotion_content}`, etc.
These will be replaced with actual values at runtime.

**Example:**
```json
"emotion_to_body": {
  "template": "You are Dr. Q. Client just mentioned: {emotion_content}\n\nCLIENT: \"{client_input}\"\n\nYour response:"
}
```

### 4. Save and restart the Docker container

```bash
docker-compose restart
```

## 🔄 Prompt Categories

### Master Planning Agent
- `therapeutic_reasoning` - Main navigation decision prompt

### Dialogue Agent
- `emotion_detection` - Detects client's emotional state
- `emotion_inquiry` - Asks about emotions when problem mentioned
- `emotion_to_body` - Connects emotion to body location
- `what_else_inquiry` - Asks for additional information
- `sensation_quality` - Explores sensation details
- `present_moment` - Grounds client in present moment
- `general_therapeutic` - General therapeutic responses

### Redirects
- `thinking_mode` - Redirects from thinking to feeling
- `past_tense` - Redirects from past to present
- `alpha_permission` - Asks permission for alpha sequence
- `alpha_permission_reassurance` - Reassures hesitant clients

## 💡 Tips for Editing

1. **Keep placeholders intact** - Don't remove `{variable_name}` tags
2. **Test after changes** - Always verify prompts work as expected
3. **Back up before major changes** - Copy the file before editing
4. **Follow Dr. Q's style** - Maintain warm, conversational tone
5. **Keep it concise** - Shorter prompts work better with LLMs

## 🚀 Future: Hot Reload

In the future, you'll be able to reload prompts without restarting:

```python
from src.utils.prompt_loader import get_prompt_loader

# Reload prompts from config
get_prompt_loader().reload()
```

## 📚 Example: Customizing a Redirect

Want to change how the system redirects from thinking to feeling?

**Current:**
```json
"thinking_mode": "Yeah, I hear you thinking about it. Rather than thinking, what are you FEELING right now? Where do you feel that?"
```

**Custom version:**
```json
"thinking_mode": "I notice you're analyzing this. Let's shift from your thoughts to your feelings. What do you notice in your body right now?"
```

Save the file and restart - that's it!
