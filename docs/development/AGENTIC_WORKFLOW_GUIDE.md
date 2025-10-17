# Agentic Workflow Integration Guide

**TRT AI Therapist - Multi-Agent System**

---

## Overview

This guide demonstrates how to integrate the TRT AI Therapist API into a multi-agent workflow with:
- **Parent Agent (Code Executor):** Orchestrates the overall workflow
- **Child Agent (Planning Agent):** Plans therapeutic interventions

Both agents communicate via the FastAPI REST endpoints.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PARENT AGENT                         │
│              (Code Executor Agent)                      │
│                                                         │
│  Responsibilities:                                      │
│  • System health checks                                │
│  • Session lifecycle management                        │
│  • API orchestration                                   │
│  • Conversation flow execution                         │
│  • Error handling & recovery                           │
└────────────┬────────────────────────────────────────────┘
             │
             │ Coordinates with
             ▼
┌─────────────────────────────────────────────────────────┐
│                    CHILD AGENT                          │
│               (Planning Agent)                          │
│                                                         │
│  Responsibilities:                                      │
│  • Analyze session progress                            │
│  • Create therapeutic plans                            │
│  • Recommend interventions                             │
│  • Monitor completion criteria                         │
└────────────┬────────────────────────────────────────────┘
             │
             │ Both communicate via
             ▼
┌─────────────────────────────────────────────────────────┐
│              TRT AI THERAPIST API                       │
│              http://localhost:8090                      │
│                                                         │
│  Endpoints:                                             │
│  • POST /api/v1/session/create                         │
│  • POST /api/v1/session/{id}/input                     │
│  • GET  /api/v1/session/{id}/status                    │
│  • DELETE /api/v1/session/{id}                         │
│  • GET  /health                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation

### File: `examples/agentic_workflow.py`

The complete implementation includes:

1. **PlanningAgent (Child Agent):** 300+ lines
   - Session progress analysis
   - Therapeutic plan generation
   - Strategy recommendations
   - State-based decision making

2. **CodeExecutorAgent (Parent Agent):** 250+ lines
   - Health check orchestration
   - Session creation/management
   - API call execution
   - Workflow coordination

3. **Main Workflow:** 50+ lines
   - End-to-end demo
   - Multi-turn conversation
   - Progress tracking

---

## Quick Start

### 1. Ensure API is Running

```bash
# Check health
curl http://localhost:8090/health

# Should return:
# {
#   "status": "healthy",
#   "services": {
#     "ollama": "connected",
#     "rag": "ready",
#     "state_machine": "loaded"
#   }
# }
```

### 2. Run Agentic Workflow

```bash
cd "/media/eizen-4/2TB/gaurav/AI Therapist/Therapist2"
python examples/agentic_workflow.py
```

---

## Code Examples

### Parent Agent: Code Executor

```python
from examples.agentic_workflow import CodeExecutorAgent

# Initialize parent agent
parent_agent = CodeExecutorAgent(api_base_url="http://localhost:8090")

# Check system health
if parent_agent.check_system_health():
    # Create session
    session_id = parent_agent.create_therapy_session(client_id="my_client")

    # Process client input
    result = parent_agent.send_client_input(
        user_input="I'm feeling stressed",
        turn_number=1
    )

    # Get summary
    summary = parent_agent.get_session_summary()

    # Close session
    parent_agent.close_session()
```

### Child Agent: Planning Agent

```python
from examples.agentic_workflow import PlanningAgent

# Initialize planning agent
planning_agent = PlanningAgent(api_base_url="http://localhost:8090")

# Analyze session progress
plan = planning_agent.analyze_session_progress(session_id)

# Returns:
# {
#     "strategy": "Body Awareness Development",
#     "next_steps": ["Explore problem", "Guide to body"],
#     "focus_areas": ["Problem Identification", "Body Awareness"],
#     "priority": "normal"
# }
```

### Complete Workflow

```python
# Create parent agent (automatically creates child agent)
parent = CodeExecutorAgent(api_base_url="http://localhost:8090")

# Run complete agentic workflow
parent.run_agentic_workflow(
    client_id="demo_client",
    max_turns=10
)
```

---

## API Integration Patterns

### Pattern 1: Health Check Before Operations

```python
class MyAgent:
    def __init__(self, api_url):
        self.api_url = api_url

    def execute_task(self):
        # Always check health first
        health = requests.get(f"{self.api_url}/health").json()
        if health['status'] != 'healthy':
            raise Exception("System not ready")

        # Proceed with task...
```

### Pattern 2: Session Lifecycle Management

```python
# Create session
response = requests.post(
    f"{API_URL}/api/v1/session/create",
    json={"client_id": "client_123"}
)
session_id = response.json()["session_id"]

try:
    # Use session for multiple turns
    for user_input in conversation:
        result = requests.post(
            f"{API_URL}/api/v1/session/{session_id}/input",
            json={"user_input": user_input}
        ).json()

        # Process result...

finally:
    # Always cleanup
    requests.delete(f"{API_URL}/api/v1/session/{session_id}")
```

### Pattern 3: Progress Monitoring

```python
# Get session status
status = requests.get(
    f"{API_URL}/api/v1/session/{session_id}/status"
).json()

# Check completion
completed = sum(status['completion_criteria'].values())
total = len(status['completion_criteria'])
progress_percent = (completed / total) * 100

if progress_percent >= 80:
    print("Session nearing completion")
```

---

## Agent Communication Flow

### Turn-by-Turn Workflow

```
1. Parent Agent: Check system health
   └─> GET /health

2. Parent Agent: Create session
   └─> POST /api/v1/session/create

3. LOOP for each turn:

   a. Child Agent: Analyze progress
      └─> GET /api/v1/session/{id}/status
      └─> Generate therapeutic plan

   b. Child Agent: Recommend next input
      └─> Based on current state & plan

   c. Parent Agent: Send client input
      └─> POST /api/v1/session/{id}/input
      └─> Get therapist response

   d. Parent Agent: Check if complete
      └─> If stage_1_complete, exit loop

4. Parent Agent: Get final summary
   └─> GET /api/v1/session/{id}/status

5. Parent Agent: Close session
   └─> DELETE /api/v1/session/{id}
```

---

## Extending the System

### Adding New Agents

```python
class MonitoringAgent:
    """New agent that monitors session quality"""

    def __init__(self, api_base_url):
        self.api_url = api_base_url

    def monitor_session_quality(self, session_id):
        """Monitor therapeutic quality metrics"""
        status = requests.get(
            f"{self.api_url}/api/v1/session/{session_id}/status"
        ).json()

        # Analyze quality
        body_questions = status['body_question_count']
        completion = status['completion_criteria']

        quality_score = self._calculate_quality(body_questions, completion)
        return quality_score
```

### Multi-Agent Coordination

```python
class CoordinatorAgent:
    """Coordinates multiple agents"""

    def __init__(self, api_url):
        self.executor = CodeExecutorAgent(api_url)
        self.planner = PlanningAgent(api_url)
        self.monitor = MonitoringAgent(api_url)

    def run_coordinated_workflow(self):
        # Create session via executor
        session_id = self.executor.create_therapy_session("client_123")

        for turn in range(10):
            # Planner suggests next step
            plan = self.planner.analyze_session_progress(session_id)

            # Monitor checks quality
            quality = self.monitor.monitor_session_quality(session_id)

            if quality < 0.5:
                # Adjust strategy
                plan = self.planner.create_corrective_plan()

            # Executor runs the turn
            self.executor.send_client_input(plan['suggested_input'], turn)
```

---

## Real-World Use Cases

### Use Case 1: Automated Therapy Sessions

```python
# Schedule automated check-ins
class AutomatedCheckInSystem:
    def __init__(self, api_url):
        self.agent = CodeExecutorAgent(api_url)

    def run_daily_checkin(self, client_id):
        session_id = self.agent.create_therapy_session(client_id)

        # Predefined check-in questions
        questions = [
            "How are you feeling today?",
            "What's been on your mind?",
            "Any progress on your goals?"
        ]

        for q in questions:
            # Could integrate with messaging system
            client_response = get_client_response_from_app(q)
            self.agent.send_client_input(client_response, turn)
```

### Use Case 2: Training Simulator

```python
# Train human therapists
class TherapyTrainingSimulator:
    def __init__(self, api_url):
        self.agent = CodeExecutorAgent(api_url)

    def simulate_client(self, therapist_trainee):
        """Trainee practices with AI-simulated client"""
        session_id = self.agent.create_therapy_session("training_session")

        # AI provides client responses based on TRT methodology
        # Trainee provides therapist responses
        # System evaluates trainee's therapeutic approach
```

### Use Case 3: Research & Analytics

```python
# Analyze therapeutic patterns
class ResearchAnalyticsAgent:
    def run_analysis(self, num_sessions=100):
        results = []

        for i in range(num_sessions):
            session_id = self.create_session(f"research_{i}")

            # Run standardized interaction
            completion = self.run_standardized_session(session_id)
            results.append(completion)

        # Analyze completion rates, common patterns, etc.
        return self.analyze_results(results)
```

---

## Testing Your Agentic Workflow

### Unit Test Example

```python
import unittest
from examples.agentic_workflow import CodeExecutorAgent, PlanningAgent

class TestAgenticWorkflow(unittest.TestCase):

    def setUp(self):
        self.api_url = "http://localhost:8090"
        self.executor = CodeExecutorAgent(self.api_url)

    def test_health_check(self):
        """Test system health check"""
        result = self.executor.check_system_health()
        self.assertTrue(result)

    def test_session_creation(self):
        """Test session creation"""
        session_id = self.executor.create_therapy_session("test_client")
        self.assertIsNotNone(session_id)
        self.executor.close_session()

    def test_planning_agent(self):
        """Test planning agent analysis"""
        planner = PlanningAgent(self.api_url)
        session_id = self.executor.create_therapy_session("test_client")

        plan = planner.analyze_session_progress(session_id)
        self.assertIn('strategy', plan)
        self.assertIn('next_steps', plan)
```

---

## Troubleshooting

### Issue: API Connection Refused

```python
# Solution: Check if API is running
import requests

try:
    response = requests.get("http://localhost:8090/health", timeout=5)
    print("API is accessible")
except requests.exceptions.ConnectionError:
    print("API not running. Start with: docker compose up -d")
```

### Issue: Session Not Found

```python
# Solution: Verify session was created successfully
response = requests.post(f"{API_URL}/api/v1/session/create")
if response.status_code == 200:
    session_id = response.json()["session_id"]
    # Use immediately, don't store for long periods
else:
    print(f"Session creation failed: {response.text}")
```

### Issue: Agent Timeout

```python
# Solution: Add timeout handling
import requests
from requests.exceptions import Timeout

try:
    response = requests.post(
        f"{API_URL}/api/v1/session/{session_id}/input",
        json={"user_input": "Hello"},
        timeout=30  # 30 second timeout
    )
except Timeout:
    print("Request timed out. Ollama might be processing.")
```

---

## Performance Optimization

### Tip 1: Reuse Agent Instances

```python
# Good: Create once, reuse
executor = CodeExecutorAgent(API_URL)
for client in clients:
    executor.create_therapy_session(client.id)

# Bad: Create new instance each time
for client in clients:
    executor = CodeExecutorAgent(API_URL)  # Expensive!
```

### Tip 2: Parallel Session Processing

```python
import concurrent.futures

def process_session(client_id):
    agent = CodeExecutorAgent(API_URL)
    agent.run_agentic_workflow(client_id, max_turns=5)

# Process multiple clients in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(process_session, client_ids)
```

### Tip 3: Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create session with retry logic
session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)

# Use session for all requests
response = session.get(f"{API_URL}/health")
```

---

## Next Steps

1. **Customize Agents:** Modify `PlanningAgent` to match your therapeutic approach
2. **Add Persistence:** Integrate database to store session history
3. **Build UI:** Create web/mobile interface that uses these agents
4. **Expand Analytics:** Add agents that analyze trends across multiple sessions
5. **Production Deploy:** Scale with multiple API instances behind load balancer

---

## Additional Resources

- **API Documentation:** http://localhost:8090/docs
- **Example Code:** `examples/agentic_workflow.py`
- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **API Reference:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

**Status:** ✅ Ready for Integration
**Last Updated:** 2025-10-14
**Version:** 1.0.0
