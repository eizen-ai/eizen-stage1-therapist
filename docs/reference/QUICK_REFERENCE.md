# TRT Therapy System - Quick Reference

**System Status:** ✅ Production-ready (Port 8090)
**RAG Status:** ✅ Hybrid approach with loop prevention active

---

## 🚀 Quick Start

### Check System Health
```bash
curl http://localhost:8090/health | python3 -m json.tool
```

### Create Session & Test
```bash
# Create session
SID=$(curl -s -X POST http://localhost:8090/api/v1/session/create -H "Content-Type: application/json" -d '{}' | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

# Send message
curl -X POST http://localhost:8090/api/v1/session/$SID/input \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I want to feel calm"}'
```

### View Logs
```bash
# All RAG activity
docker logs trt-app 2>&1 | grep -E "📋|🎯|🔍|✅|⚠️" | tail -30

# Body question counting
docker logs trt-app 2>&1 | grep "📊 Body question" | tail -5

# Escape events
docker logs trt-app 2>&1 | grep "⚠️ ESCAPE" | tail -5
```

---

## 🧠 How It Works

### When RAG is USED (Exploratory)
- Body symptom exploration
- Problem inquiry ("What's making it hard?")
- Pattern recognition
- General therapeutic responses

### When RULES are USED (Consistency)
- Goal clarification (opening)
- Vision building (templated)
- Psycho-education (zebra-lion)
- Safety/crisis responses
- Past/thinking redirects
- Alpha sequence

### Loop Prevention
- **Limit:** 3 body questions max
- **Escape:** After 3, system asks "How are you feeling NOW?"
- **Alpha Protection:** In alpha sequence or readiness, no more body questions

---

## 📊 Key Metrics

Monitor these in logs:

| Log Symbol | Meaning | Good/Bad |
|-----------|---------|----------|
| `📋 BYPASSING` | Using rules (goal, vision) | ✅ Good |
| `🎯 HYBRID` | Using RAG for exploration | ✅ Good |
| `📊 Body question count: 1/3` | Counting body questions | ✅ Good |
| `📊 Body question count: 3/3` | Hit limit | ⚠️ Watch |
| `⚠️ ESCAPE` | Loop prevention triggered | ✅ Good |
| `🔍 RAG RETRIEVAL` | Fetching examples | ✅ Good |
| `✅ RAG RETRIEVED 3 EXAMPLES` | Found examples | ✅ Good |

---

## 🔧 Common Operations

### Restart System
```bash
docker restart trt-app
# Wait 5 seconds, then check health
sleep 5 && curl http://localhost:8090/health
```

### Update Code (Quick)
```bash
# Copy updated file
docker cp /path/to/file.py trt-app:/app/src/.../file.py
# Restart
docker restart trt-app
```

### Rebuild Image (Permanent)
```bash
docker compose build --no-cache trt-app
docker compose up -d trt-app
```

### View RAG Statistics
```bash
echo "RAG Calls: $(docker logs trt-app 2>&1 | grep '🔍 RAG RETRIEVAL' | wc -l)"
echo "Escapes: $(docker logs trt-app 2>&1 | grep '⚠️ ESCAPE' | wc -l)"
echo "Bypasses: $(docker logs trt-app 2>&1 | grep '📋 BYPASSING' | wc -l)"
```

---

## 📁 Important Files

### Core System
- `src/core/improved_ollama_system.py` - Main orchestrator
- `src/agents/improved_ollama_dialogue_agent.py` - Dialogue generation + hybrid logic
- `src/agents/improved_ollama_master_planning_agent.py` - Navigation decisions
- `src/core/session_state_manager.py` - State tracking

### RAG Components
- `src/utils/embedding_and_retrieval_setup.py` - RAG retrieval system
- `data/embeddings/trt_rag_index.faiss` - Vector index (1.5MB)
- `data/embeddings/trt_rag_metadata.json` - Metadata (1.1MB)
- `data/processed/processed_exchanges/complete_embedding_dataset.json` - Clean data (1000 exchanges)

### Documentation
- `HYBRID_RAG_IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `RAG_IMPLEMENTATION_STATUS.md` - RAG usage patterns
- `EMBEDDING_CLEANUP_SUMMARY.md` - Data cleaning process
- `API_DOCUMENTATION.md` - API endpoints
- `DEPLOYMENT_GUIDE.md` - Deployment instructions

---

## 🐛 Troubleshooting

### System Not Responding
```bash
# Check container status
docker ps | grep trt-app

# Check logs for errors
docker logs trt-app 2>&1 | grep -i error | tail -10

# Restart
docker restart trt-app
```

### RAG Not Working
```bash
# Check if embeddings loaded
docker logs trt-app 2>&1 | grep "Loaded index from"

# Check RAG calls
docker logs trt-app 2>&1 | grep "🔍 RAG RETRIEVAL" | tail -5

# If no RAG calls, check navigation decisions
docker logs trt-app 2>&1 | grep "navigation_decision"
```

### Loop Not Escaping
```bash
# Check body question count
docker logs trt-app 2>&1 | grep "📊 Body question count" | tail -10

# Should see: 1/3 → 2/3 → 3/3 → ⚠️ ESCAPE

# If not, check substate
docker logs trt-app 2>&1 | grep "current_substate" | tail -5
```

---

## 🎯 Expected Session Flow

1. **Goal Clarification** → Rule-based
   ```
   📋 BYPASSING RAG: Using rule-based goal clarification
   Therapist: "What do we want our time to focus on today?"
   ```

2. **Vision Building** → Rule-based
   ```
   📋 BYPASSING RAG: Using rule-based vision building
   Therapist: "Got it. So you want to feel calm..."
   ```

3. **Psycho-Education** → Rule-based
   ```
   Therapist: "Here's what's happening in the brain. When facing a threat..."
   ```

4. **Body Exploration** → RAG (count 1)
   ```
   🎯 HYBRID: Using RAG+LLM for explore_problem
   📊 Body question count: 1/3
   Therapist: "Where do you feel that in your body?"
   ```

5. **Body Exploration** → RAG (count 2)
   ```
   🎯 HYBRID: Using RAG+LLM for body_symptoms_exploration
   📊 Body question count: 2/3
   Therapist: "What kind of sensation is it?"
   ```

6. **Body Exploration** → RAG (count 3)
   ```
   🎯 HYBRID: Using RAG+LLM for explore_problem
   📊 Body question count: 3/3
   Therapist: "Where do you notice that?"
   ```

7. **Escape Triggered** → Loop prevention
   ```
   ⚠️ ESCAPE: Body exploration limit reached (count=3)
   Therapist: "Got it. How are you feeling NOW?"
   ```

8. **Present Moment** → Continue to readiness
   ```
   Therapist: "What haven't I understood? Is there more I should know?"
   ```

9. **Readiness Confirmed** → Alpha permission
   ```
   Therapist: "Okay. I'm going to guide you through a brief process. Are you ready?"
   ```

10. **Alpha Sequence** → Structured process
    ```
    Therapist: "Find a spot on the wall slightly above eye level..."
    ```

---

## ✅ System Status

| Component | Status | Notes |
|-----------|--------|-------|
| API Server | ✅ Running | Port 8090 |
| Ollama LLM | ✅ Connected | llama3.1 |
| RAG System | ✅ Active | 1000 embeddings |
| Loop Prevention | ✅ Working | 3 question limit |
| Logging | ✅ Comprehensive | Full visibility |
| Docker | ✅ Deployed | trt-app container |

---

## 📞 Support

For issues or questions:
1. Check logs: `docker logs trt-app 2>&1 | tail -50`
2. Review documentation in project root
3. Test with `/tmp/test_loop_prevention.sh` script

**Last Updated:** 2025-10-15
**Version:** Hybrid RAG with Loop Prevention v1.0
