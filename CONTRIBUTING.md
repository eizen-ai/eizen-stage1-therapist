# Contributing to AI Therapist - TRT System

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

---

## 🎯 Project Goals

This project implements Dr. Q's Trauma Resiliency Training (TRT) methodology using local AI (Ollama + LLaMA 3.1). Our goals are:

1. **Fidelity to methodology**: Stay true to Dr. Q's TRT approach
2. **Privacy-first**: All processing happens locally
3. **Safety-first**: Crisis detection and appropriate responses
4. **Research & education**: NOT a replacement for professional care

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Ollama installed and running
- LLaMA 3.1 model (8B recommended)
- Git

### Setup Development Environment

1. **Fork and clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI-Therapist-TRT.git
   cd AI-Therapist-TRT
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

4. **Run tests:**
   ```bash
   python tests/test_improved_system.py
   ```

---

## 📝 How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
- Check existing issues to avoid duplicates
- Test with latest version
- Collect session logs (`logs/*.json`)

**Bug report should include:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Session log (if applicable)
- System info (OS, Python version, Ollama version)

**Example:**
```markdown
**Bug:** System loops on body questions despite MAX limit

**Steps to reproduce:**
1. Start session: `python improved_ollama_system.py`
2. Provide inputs: "stressed", "chest", "tight"
3. System asks body questions 7 times (should stop at 3)

**Expected:** Body counter stops at 3, advances to alpha
**Actual:** Counter goes to 7/3, loops indefinitely

**Session log:** `logs/improved_manual_20251014_095712.json`
**System:** Ubuntu 20.04, Python 3.9, Ollama 0.1.20
```

### Suggesting Enhancements

**Enhancement proposals should include:**
- Clear description of the feature
- Use case / problem it solves
- How it aligns with TRT methodology
- Proposed implementation approach (if applicable)

### Pull Requests

**PR Guidelines:**
1. **One feature per PR** - Keep changes focused
2. **Follow existing code style** - Match the project's conventions
3. **Add tests** - Cover new functionality
4. **Update documentation** - README, docstrings, comments
5. **Include session logs** - If changing dialogue behavior

**PR Checklist:**
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Session logs included (if applicable)
- [ ] No breaking changes (or clearly documented)
- [ ] All tests pass

**Example PR:**
```markdown
**Title:** Fix: Stop body counter loop in state 3.1

**Problem:**
Body counter exceeded MAX limit (3) and kept incrementing in state 3.1 (alpha readiness).

**Solution:**
Added check to stop incrementing counter when current_state is in ["3.1_assess_readiness", "3.2_alpha_sequence", "stage_1_complete"].

**Testing:**
- Session log shows counter stops at 3/3
- Advances to alpha correctly
- See: `logs/test_body_counter_fix.json`

**Files changed:**
- `src/core/improved_ollama_system.py` (lines 79-89)
- `ALL_FIXES_IMPLEMENTED.md` (documented as Fix #7)
```

---

## 🏗️ Project Structure

```
Therapist2/
├── src/                           # Source code
│   ├── core/                      # Core system
│   │   ├── improved_ollama_system.py      # Main orchestration
│   │   ├── session_state_manager.py       # State tracking
│   │   └── alpha_sequence.py              # Alpha sequence logic
│   │
│   ├── agents/                    # AI agents
│   │   ├── ollama_llm_master_planning_agent.py   # Navigation
│   │   └── improved_ollama_dialogue_agent.py     # Response generation
│   │
│   └── utils/                     # Utilities
│       ├── embedding_and_retrieval_setup.py      # RAG system
│       ├── input_preprocessing.py                # Spelling, detection
│       ├── psycho_education.py                   # Zebra/lion metaphor
│       ├── no_harm_framework.py                  # Crisis handling
│       └── engagement_tracker.py                 # Engagement monitoring
│
├── config/                        # Configuration
│   └── STAGE1_COMPLETE.csv        # 31-state CSV state machine
│
├── data/                          # Data
│   ├── transcripts/               # Therapy transcripts (RAG source)
│   └── embeddings/                # FAISS vector database
│
├── tests/                         # Tests
├── logs/                          # Session logs
└── docs/                          # Documentation
```

---

## 🎨 Code Style

### Python Style
- Follow **PEP 8**
- Use **type hints** for function signatures
- Write **docstrings** for all functions/classes
- Keep functions **< 50 lines** when possible

**Example:**
```python
def process_client_input(self, client_input: str, session_state: TRTSessionState) -> dict:
    """
    Process client input through improved system

    Args:
        client_input: Raw client text input
        session_state: Current TRT session state

    Returns:
        Dictionary containing:
        - navigation: Navigation decision output
        - dialogue: Generated therapeutic response
        - session_progress: Current progress summary
    """
    # Implementation
```

### Naming Conventions
- **Functions**: `snake_case` (e.g., `generate_response`)
- **Classes**: `PascalCase` (e.g., `SessionStateManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_BODY_QUESTIONS`)
- **Private methods**: `_leading_underscore` (e.g., `_internal_helper`)

### Comments
- Use **clear, concise comments** for complex logic
- Explain **WHY**, not **WHAT** (code shows what)
- Reference **Dr. Q methodology** when implementing therapeutic logic

**Example:**
```python
# Dr. Q method: acknowledge negative emotions in PAST tense
# This helps externalize the problem and reduce present activation
if is_negative_emotion:
    return f"So you've been feeling {emotion}. "
```

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python tests/test_improved_system.py

# Run manual test session
cd src/core
python improved_ollama_system.py
```

### Test Scenarios
When adding features, test with:
1. **Happy path** - Normal therapeutic conversation
2. **Edge cases** - Short answers, confusion, resistance
3. **Safety scenarios** - Self-harm mentions, crisis language
4. **State transitions** - Ensure proper flow through substates

### Session Logs
- All sessions saved to `logs/*.json`
- Include relevant logs in PRs
- Useful for debugging and validation

---

## 📚 Documentation

### Where to Document
- **Code**: Docstrings, inline comments
- **README.md**: High-level overview, setup
- **MANUAL_TESTING_GUIDE.md**: Testing instructions
- **ALL_FIXES_IMPLEMENTED.md**: Implementation details
- **CSV (`config/STAGE1_COMPLETE.csv`)**: State machine flow

### Documentation Standards
- **Clear and concise** - Easy to understand
- **Examples included** - Show, don't just tell
- **Updated with changes** - Keep docs in sync with code

---

## 🔒 Privacy & Safety

### Privacy Guidelines
- **NO cloud services** - All processing must be local
- **NO data collection** - System doesn't track or store user data
- **NO external API calls** - Except to local Ollama instance

### Safety Guidelines
- **Self-harm detection** - Always active, cannot be disabled
- **Crisis protocols** - Immediate safety responses
- **Disclaimers** - Prominently displayed

**If modifying safety code:**
- Document changes thoroughly
- Test extensively
- Get review from multiple contributors

---

## 🤝 Community

### Communication Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions

### Code of Conduct
- **Be respectful** - Treat all contributors with respect
- **Be constructive** - Provide helpful feedback
- **Be patient** - Remember this is volunteer work
- **Be professional** - This is a mental health project

---

## 📋 Review Process

1. **Submit PR** with clear description
2. **Automated checks** run (if configured)
3. **Maintainer review** - May request changes
4. **Testing** - Verify functionality
5. **Merge** - Once approved

**Review time:** Usually 1-7 days (be patient!)

---

## ❓ Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Security concerns**: Email maintainers directly

---

## 🙏 Thank You!

Every contribution helps make this project better. Whether you're fixing a typo, reporting a bug, or adding a feature - thank you for contributing!

---

**Remember:** This is an experimental research project. Always prioritize safety and fidelity to TRT methodology.
