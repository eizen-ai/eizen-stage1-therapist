# Configuration Storage Strategy: Redis vs File System

**Date:** 2025-10-15
**Topic:** Should JSON configs (rules, classification, navigation) go in Redis?

---

## 📋 Current Configuration Files

### 1. `simplified_navigation.json` (4 KB)
```json
{
  "stage_1_navigation": {
    "1.1_goal_and_vision": {
      "objective": "Get therapeutic goal AND future self vision",
      "completion_criteria": ["goal_stated", "vision_accepted"],
      "triggers": {...},
      "rag_queries": {...}
    }
  }
}
```

**Usage:** Loaded once on startup, used in LLM prompt construction

### 2. `input_classification_patterns.json` (7 KB)
```json
{
  "situation_classifications": {
    "goal_related": ["want to feel", "need to", "hope to"],
    "body_symptoms": ["pain", "ache", "tension"],
    "emotional_patterns": ["feel like", "always feel"]
  }
}
```

**Usage:** Loaded once on startup, pattern matching in preprocessing

### 3. `all_dr_q_exchanges.json` (Large - Source Data)
```json
[
  {
    "client_input": "I want to feel calm",
    "therapist_response": "So you want to feel calm...",
    "substate": "1.1_goal_and_vision"
  }
]
```

**Usage:** Used ONLY during embedding generation, not at runtime

---

## 🤔 Should They Go in Redis?

### Decision Matrix

| Factor | File System | Redis |
|--------|-------------|-------|
| **Read Frequency** | Once on startup | Every access |
| **Update Frequency** | Rarely (weeks/months) | - |
| **Size** | Small (< 10 KB) | - |
| **Latency Impact** | None (cached in memory) | None (but unnecessary) |
| **Version Control** | ✅ Git tracks changes | ❌ Need separate versioning |
| **Deployment** | ✅ Part of codebase | ❌ Separate deployment step |
| **Rollback** | ✅ Git revert | ❌ Manual restore |
| **Multi-tenant** | ❌ Same for all | ✅ Different per tenant |
| **Runtime Updates** | ❌ Restart needed | ✅ Dynamic updates |

---

## 🎯 Recommendation: **Keep in File System**

### Why File System is Better for Config:

#### 1. **Configuration is Code**
```
Rules/patterns change = Code change
→ Should go through same review process
→ Should be version controlled
→ Should be tested before deployment
```

#### 2. **Infrequent Changes**
- Navigation rules: Change monthly or quarterly
- Classification patterns: Change when adding features
- NOT changed per-user or per-session

#### 3. **Small Size + Read Once**
```python
# On startup (once)
with open('simplified_navigation.json') as f:
    self.navigation = json.load(f)

# Then used from memory for all requests
# No file I/O during request processing
```

#### 4. **Version Control Critical**
```bash
# See what changed
git diff config/system/core_system/simplified_navigation.json

# Rollback if needed
git checkout HEAD~1 config/system/core_system/

# Track who changed what and why
git log config/system/
```

#### 5. **Deployment Simplicity**
```bash
# Config files are part of Docker image
docker build .  # Includes all config files

# No separate "deploy config to Redis" step needed
```

---

## 🔄 When Redis WOULD Make Sense for Config

### Scenario 1: Multi-Tenant System
```python
# Different rules per client/organization
client_a_rules = redis.get("config:client_a:navigation")
client_b_rules = redis.get("config:client_b:navigation")

# Use case: White-label SaaS offering TRT to multiple organizations
# Each org can customize their rules
```

### Scenario 2: A/B Testing
```python
# Different rules for different user groups
if user_group == "experiment":
    rules = redis.get("config:navigation:experiment")
else:
    rules = redis.get("config:navigation:control")

# Use case: Testing new therapeutic approaches
```

### Scenario 3: Runtime Configuration Updates
```python
# Update rules without restarting servers
redis.set("config:navigation", new_rules)

# All servers pick up changes immediately
# Use case: Need to adjust rules during production without downtime
```

### Scenario 4: Per-Therapist Customization
```python
# Different therapists have different styles
therapist_id = get_therapist_for_session(session_id)
rules = redis.get(f"config:therapist:{therapist_id}:rules")

# Use case: Platform with multiple human therapists + AI assistance
```

---

## 🎯 Hybrid Approach (Best of Both)

### Use File System for Base Config + Redis for Overrides

```python
class ConfigManager:
    def __init__(self):
        # Load base config from files (version controlled)
        with open('config/navigation.json') as f:
            self.base_navigation = json.load(f)

        # Connect to Redis for overrides
        self.redis = redis.Redis()

    def get_navigation_rules(self, context: dict = None):
        """Get navigation rules with optional overrides"""

        # Start with base rules
        rules = self.base_navigation.copy()

        # Check for Redis overrides
        if context and context.get('tenant_id'):
            # Tenant-specific override
            override = self.redis.get(f"config:tenant:{context['tenant_id']}:navigation")
            if override:
                rules.update(json.loads(override))

        if context and context.get('experiment_group'):
            # A/B test override
            override = self.redis.get(f"config:experiment:{context['experiment_group']}:navigation")
            if override:
                rules.update(json.loads(override))

        return rules
```

**Benefits:**
- ✅ Base config version controlled
- ✅ Can override per tenant/experiment
- ✅ Defaults always available (file system)
- ✅ Flexibility when needed (Redis)

---

## 📊 What Should Go Where?

### ✅ Keep in File System (Git)

1. **Base Navigation Rules**
   - File: `simplified_navigation.json`
   - Reason: Core TRT methodology, infrequent changes

2. **Classification Patterns**
   - File: `input_classification_patterns.json`
   - Reason: Part of preprocessing logic, stable

3. **System Configuration**
   - File: `.env` or `config.yaml`
   - Reason: Deployment-specific, version controlled

4. **RAG Source Data**
   - File: `all_dr_q_exchanges.json`
   - Reason: Training data, should be versioned

### ✅ Store in Redis

1. **Session State** (per user)
   - Current substate, completion status
   - Reason: Dynamic, per-session, needs persistence

2. **Conversation History** (per user)
   - Client-therapist exchanges
   - Reason: Dynamic, needs to survive restarts

3. **User Preferences** (per user)
   - Language, notification settings
   - Reason: User-specific, frequently read

4. **Rate Limiting** (per user/IP)
   - Request counters
   - Reason: Real-time, needs to be shared across servers

5. **Session Analytics** (aggregated)
   - Daily/hourly metrics
   - Reason: Real-time aggregation needed

6. **Cache** (RAG results, LLM responses)
   - Temporary performance optimization
   - Reason: Fast access, shared across servers

### 🤔 Could Go Either Way (Context Dependent)

1. **Feature Flags**
   - File: Simple, single-tenant
   - Redis: Complex, need runtime toggle

2. **RAG Embeddings**
   - File: Current approach (FAISS index file)
   - Redis: If using Redis vector search (RedisSearch)

3. **Prompt Templates**
   - File: If templates rarely change
   - Redis: If want to A/B test prompts

---

## 🔧 Current System Recommendation

### Keep Current Approach ✅

```
File System (Git):
├── config/system/core_system/
│   ├── simplified_navigation.json        ← Keep here
│   └── input_classification_patterns.json ← Keep here
├── data/embeddings/
│   ├── trt_rag_index.faiss               ← Keep here
│   └── trt_rag_metadata.json             ← Keep here
└── data/state_actions/
    └── all_dr_q_exchanges.json           ← Keep here

Redis:
├── trt:session:{id}:state                ← Session state
├── trt:session:{id}:history              ← Conversation
├── trt:session:{id}:meta                 ← Metadata
└── trt:active_sessions                   ← Index
```

**Why:**
1. ✅ You're single-tenant currently
2. ✅ Rules change infrequently
3. ✅ Version control is critical for therapeutic rules
4. ✅ Simpler deployment (config in Docker image)
5. ✅ No runtime config updates needed

---

## 🚀 Future Migration Path

### When to Move Config to Redis:

#### Trigger 1: Multi-Tenancy
```
Need: Different clients want different rules
→ Move base rules to Redis
→ Keep defaults in files as fallback
```

#### Trigger 2: A/B Testing
```
Need: Test new therapeutic approaches
→ Create experiment system
→ Store experiment configs in Redis
→ Keep production config in files
```

#### Trigger 3: Dynamic Rule Updates
```
Need: Adjust rules without restart
→ Move hot-swappable rules to Redis
→ Keep critical rules in files
```

#### Trigger 4: Multiple Therapist Styles
```
Need: Platform with many therapists
→ Each therapist has custom rules in Redis
→ Base TRT methodology stays in files
```

---

## 💡 Practical Example

### Scenario: You Want to Test a New Rule

#### Current Approach (File System)
```bash
# 1. Edit file
vim config/system/core_system/simplified_navigation.json

# 2. Commit change
git commit -m "test: try new body awareness threshold"

# 3. Deploy
docker-compose build
docker-compose up -d

# 4. Monitor results

# 5. Rollback if needed
git revert HEAD
docker-compose build
docker-compose up -d
```

#### With Redis (If You Had It)
```python
# 1. Update Redis (no code change)
redis.set(
    "config:navigation:experiment",
    json.dumps(new_rules)
)

# 2. Route 10% of traffic to experiment
if random.random() < 0.1:
    rules = redis.get("config:navigation:experiment")

# 3. Monitor results

# 4. Rollback instantly
redis.delete("config:navigation:experiment")
```

**Which is better?** Depends:
- Small changes, thorough testing → File system
- Need instant rollback, A/B testing → Redis

---

## 🎯 Final Recommendation

### For Your Current System:

```
✅ Keep JSON configs in file system (Git)
✅ Move session data to Redis
❌ Don't move navigation/rules to Redis (yet)
```

### Reasons:
1. **Single tenant** - No need for per-client rules
2. **Stable rules** - TRT methodology doesn't change daily
3. **Version control critical** - Therapeutic rules need audit trail
4. **Simpler deployment** - Config bundled with code
5. **No runtime updates needed** - Can restart for rule changes

### When to Reconsider:
- Multi-tenant SaaS offering
- A/B testing therapeutic approaches
- Need zero-downtime config updates
- Multiple therapist styles on one platform

---

## 📊 Performance Comparison

### File System (Current)
```python
# Startup: Load once
with open('config.json') as f:
    self.config = json.load(f)  # 1ms

# Request: Read from memory
rules = self.config['navigation']  # 0.001ms (memory access)
```

### Redis (If You Used It)
```python
# Startup: Nothing to load

# Request: Read from Redis
rules = json.loads(redis.get('config:navigation'))  # 1-2ms (network + parse)
```

**Impact per request:**
- File system: ~0.001ms (negligible)
- Redis: ~1-2ms (1000x slower, but still fast)

**Verdict:** For rarely-changing config read on every request, file system is actually faster!

---

## 🔒 Security Considerations

### File System
- ✅ Config encrypted at rest (disk encryption)
- ✅ Access controlled by file permissions
- ✅ Audit trail via Git
- ❌ Harder to rotate secrets dynamically

### Redis
- ✅ Can encrypt in transit (TLS)
- ✅ Can encrypt at rest (Redis encryption)
- ✅ Dynamic secret rotation possible
- ❌ Need to secure Redis access
- ❌ Need backup strategy

---

## 🎯 Summary Table

| Config Type | Current Location | Keep There? | Move to Redis? | Reason |
|------------|------------------|-------------|----------------|--------|
| Navigation rules | File | ✅ Yes | ❌ No | Stable, need version control |
| Classification patterns | File | ✅ Yes | ❌ No | Stable, need version control |
| Session state | Memory | ❌ No | ✅ Yes | Dynamic, needs persistence |
| Conversation history | Memory | ❌ No | ✅ Yes | Dynamic, needs persistence |
| RAG embeddings | File (FAISS) | ✅ Yes | ❌ No | Large, loaded once |
| RAG source data | File | ✅ Yes | ❌ No | Training data, versioned |
| System config (.env) | File | ✅ Yes | 🤔 Maybe | Could use Redis for secrets |
| Feature flags | None | - | 🤔 Maybe | If you add A/B testing |
| User preferences | None | - | ✅ Yes | If you add user accounts |
| Cache | None | - | ✅ Yes | If you add caching |

---

## 💬 Bottom Line

**For JSON config files (rules, navigation, classification):**

### Keep in File System Because:
1. ✅ They're **code**, not data
2. ✅ They change **rarely** (weeks/months)
3. ✅ They need **version control**
4. ✅ They're **small** (< 10 KB)
5. ✅ They're loaded **once** on startup
6. ✅ You're **single-tenant** currently

### Move to Redis Only If:
1. ❓ You become **multi-tenant** (different rules per client)
2. ❓ You need **A/B testing** (experiment with rules)
3. ❓ You need **zero-downtime** config updates
4. ❓ You have **multiple therapist styles**

**Current answer: Keep in files! 📁**

---

**Last Updated:** 2025-10-15
**Recommendation:** File system for config, Redis for session data
**Review:** When you add multi-tenancy or A/B testing
