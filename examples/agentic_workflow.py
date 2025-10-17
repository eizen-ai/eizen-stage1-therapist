"""
Multi-Agent Workflow for TRT AI Therapist
Parent Agent: Code Executor (orchestrates the flow)
Child Agent: Planning Agent (plans therapeutic interventions)

Both agents communicate with the TRT API endpoint
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional


# ============================================================
# CONFIGURATION
# ============================================================

TRT_API_BASE_URL = "http://localhost:8090"


# ============================================================
# CHILD AGENT: PLANNING AGENT
# ============================================================

class PlanningAgent:
    """
    Child Agent: Responsible for planning therapeutic interventions
    Analyzes session progress and determines next steps
    """

    def __init__(self, api_base_url: str = TRT_API_BASE_URL):
        self.api_base_url = api_base_url
        self.agent_name = "PlanningAgent"
        print(f"🧠 {self.agent_name} initialized")

    def analyze_session_progress(self, session_id: str) -> Dict:
        """
        Analyze current session progress via API
        Returns therapeutic plan based on current state
        """
        print(f"\n{'='*60}")
        print(f"🧠 {self.agent_name}: Analyzing session progress...")
        print(f"{'='*60}")

        # Get session status from API
        response = requests.get(f"{self.api_base_url}/api/v1/session/{session_id}/status")
        status = response.json()

        # Analyze progress
        current_state = status['current_substate']
        body_questions = status['body_question_count']
        completion = status['completion_criteria']
        completed_count = sum(completion.values())
        total_criteria = len(completion)

        print(f"📊 Current State: {current_state}")
        print(f"📍 Body Questions: {body_questions}/3")
        print(f"✅ Completion: {completed_count}/{total_criteria} criteria")

        # Create therapeutic plan
        plan = self._create_therapeutic_plan(current_state, completion, body_questions)

        print(f"\n📋 THERAPEUTIC PLAN:")
        print(f"   Strategy: {plan['strategy']}")
        print(f"   Next Steps: {', '.join(plan['next_steps'])}")
        print(f"   Focus Areas: {', '.join(plan['focus_areas'])}")

        return plan

    def _create_therapeutic_plan(self, current_state: str, completion: Dict, body_questions: int) -> Dict:
        """Create therapeutic plan based on session state"""

        plan = {
            "strategy": "",
            "next_steps": [],
            "focus_areas": [],
            "priority": "normal"
        }

        # Determine strategy based on state
        if current_state.startswith("1.1"):
            plan["strategy"] = "Goal Clarification Phase"
            plan["next_steps"] = ["Establish clear therapeutic goal", "Build vision of desired outcome"]
            plan["focus_areas"] = ["Goal Setting", "Vision Building"]

        elif current_state.startswith("1.2") or current_state.startswith("2."):
            plan["strategy"] = "Body Awareness Development"
            plan["next_steps"] = [
                "Explore problem manifestation",
                "Guide to body sensations",
                f"Continue body exploration ({body_questions}/3 questions used)"
            ]
            plan["focus_areas"] = ["Problem Identification", "Body Awareness", "Present Moment"]

        elif current_state.startswith("3.1"):
            plan["strategy"] = "Alpha Readiness Assessment"
            plan["next_steps"] = [
                "Assess client readiness",
                "Request permission for alpha sequence",
                "Prepare for nervous system regulation"
            ]
            plan["focus_areas"] = ["Readiness", "Permission", "Transition"]
            plan["priority"] = "high"

        elif current_state.startswith("3.2"):
            plan["strategy"] = "Alpha State Induction"
            plan["next_steps"] = [
                "Guide through jaw relaxation",
                "Progress through tongue positioning",
                "Complete with breathing awareness"
            ]
            plan["focus_areas"] = ["Alpha Sequence", "Down-regulation", "Integration"]
            plan["priority"] = "critical"

        elif current_state == "stage_1_complete":
            plan["strategy"] = "Stage 1 Complete - Prepare for Stage 2"
            plan["next_steps"] = ["Consolidate learning", "Transition to trauma processing"]
            plan["focus_areas"] = ["Integration", "Stage 2 Preparation"]
            plan["priority"] = "complete"

        else:
            plan["strategy"] = "General Therapeutic Exploration"
            plan["next_steps"] = ["Follow client's process", "Maintain therapeutic rapport"]
            plan["focus_areas"] = ["Active Listening", "Process Following"]

        return plan

    def recommend_client_input(self, plan: Dict, turn_number: int) -> str:
        """Recommend appropriate client input based on therapeutic plan"""

        # Simulated client responses based on plan
        recommendations = {
            "Goal Clarification Phase": [
                "I want to feel more calm and relaxed",
                "I'd like to manage my stress better"
            ],
            "Body Awareness Development": [
                "I feel it in my chest",
                "There's tension in my shoulders",
                "It's a tightness that won't go away",
                "I feel it right now"
            ],
            "Alpha Readiness Assessment": [
                "I think I've covered everything",
                "Nothing more to add",
                "Yes, I'm ready"
            ],
            "Alpha State Induction": [
                "I feel more calm",
                "The tension is releasing",
                "I notice my breathing slowing down"
            ]
        }

        strategy = plan["strategy"]
        if strategy in recommendations:
            responses = recommendations[strategy]
            return responses[min(turn_number % len(responses), len(responses) - 1)]

        return "Yes, that makes sense"


# ============================================================
# PARENT AGENT: CODE EXECUTOR
# ============================================================

class CodeExecutorAgent:
    """
    Parent Agent: Orchestrates the entire therapeutic workflow
    Manages session lifecycle, coordinates with Planning Agent,
    and executes API calls
    """

    def __init__(self, api_base_url: str = TRT_API_BASE_URL):
        self.api_base_url = api_base_url
        self.agent_name = "CodeExecutorAgent"
        self.planning_agent = PlanningAgent(api_base_url)
        self.session_id = None
        self.conversation_history = []

        print(f"⚙️ {self.agent_name} initialized")
        print(f"🔗 API Base URL: {self.api_base_url}")

    def check_system_health(self) -> bool:
        """Check if TRT API is healthy"""
        print(f"\n{'='*60}")
        print(f"⚙️ {self.agent_name}: Checking system health...")
        print(f"{'='*60}")

        try:
            response = requests.get(f"{self.api_base_url}/health")
            health = response.json()

            print(f"🏥 System Status: {health['status']}")
            print(f"   Ollama: {health['services']['ollama']}")
            print(f"   RAG: {health['services']['rag']}")
            print(f"   State Machine: {health['services']['state_machine']}")

            if health['status'] == "healthy":
                print("✅ All systems operational")
                return True
            else:
                print("⚠️ System unhealthy")
                return False

        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def create_therapy_session(self, client_id: str) -> str:
        """Create new therapy session via API"""
        print(f"\n{'='*60}")
        print(f"⚙️ {self.agent_name}: Creating therapy session...")
        print(f"{'='*60}")

        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/session/create",
                json={"client_id": client_id}
            )
            session_data = response.json()
            self.session_id = session_data['session_id']

            print(f"✅ Session created: {self.session_id}")
            print(f"   Client ID: {client_id}")
            print(f"   Status: {session_data['status']}")

            return self.session_id

        except Exception as e:
            print(f"❌ Session creation failed: {e}")
            return None

    def send_client_input(self, user_input: str, turn_number: int) -> Dict:
        """Send client input to TRT API and get therapist response"""
        print(f"\n{'='*60}")
        print(f"⚙️ {self.agent_name}: Processing Turn {turn_number}")
        print(f"{'='*60}")

        print(f"👤 Client Input: \"{user_input}\"")

        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/session/{self.session_id}/input",
                json={"user_input": user_input}
            )
            result = response.json()

            therapist_response = result['therapist_response']
            current_state = result['session_progress']['current_substate']
            emotion = result['preprocessing']['emotional_state']['primary_emotion']

            print(f"🩺 Therapist Response: \"{therapist_response}\"")
            print(f"📍 State: {current_state}")
            print(f"😊 Detected Emotion: {emotion}")

            # Store in history
            self.conversation_history.append({
                "turn": turn_number,
                "client": user_input,
                "therapist": therapist_response,
                "state": current_state
            })

            return result

        except Exception as e:
            print(f"❌ API call failed: {e}")
            return None

    def get_session_summary(self) -> Dict:
        """Get final session summary"""
        print(f"\n{'='*60}")
        print(f"⚙️ {self.agent_name}: Generating session summary...")
        print(f"{'='*60}")

        try:
            response = requests.get(f"{self.api_base_url}/api/v1/session/{self.session_id}/status")
            status = response.json()

            completed = sum(status['completion_criteria'].values())
            total = len(status['completion_criteria'])

            print(f"📊 SESSION SUMMARY")
            print(f"   Total Turns: {status['turn_count']}")
            print(f"   Final State: {status['current_substate']}")
            print(f"   Completion: {completed}/{total} criteria ({completed/total*100:.1f}%)")
            print(f"   Body Questions: {status['body_question_count']}/3")

            return status

        except Exception as e:
            print(f"❌ Summary generation failed: {e}")
            return None

    def close_session(self):
        """Close and cleanup session"""
        print(f"\n{'='*60}")
        print(f"⚙️ {self.agent_name}: Closing session...")
        print(f"{'='*60}")

        try:
            response = requests.delete(f"{self.api_base_url}/api/v1/session/{self.session_id}")
            result = response.json()
            print(f"✅ {result['message']}")

        except Exception as e:
            print(f"⚠️ Session cleanup failed: {e}")

    def run_agentic_workflow(self, client_id: str, max_turns: int = 10):
        """
        Main agentic workflow orchestration
        Coordinates between Parent (Executor) and Child (Planning) agents
        """
        print("\n" + "="*60)
        print("🚀 STARTING MULTI-AGENT WORKFLOW")
        print("="*60)
        print(f"Parent Agent: {self.agent_name}")
        print(f"Child Agent: {self.planning_agent.agent_name}")
        print(f"Client ID: {client_id}")
        print(f"Max Turns: {max_turns}")
        print("="*60)

        # Step 1: Health check
        if not self.check_system_health():
            print("\n❌ System not healthy. Aborting workflow.")
            return

        # Step 2: Create session
        session_id = self.create_therapy_session(client_id)
        if not session_id:
            print("\n❌ Failed to create session. Aborting workflow.")
            return

        # Step 3: Simulated client inputs (in real system, this would be actual client)
        initial_inputs = [
            "I'm feeling really stressed and overwhelmed",
            "I want to feel calm and peaceful",
            "Yes, exactly",
            "I feel it in my chest",
            "It's tight and heavy",
            "Right now",
            "Nothing more from my side",
            "Yes, I'm ready to try",
            "I feel more calm",
            "The tension is releasing"
        ]

        # Step 4: Main conversation loop
        for turn in range(1, min(max_turns + 1, len(initial_inputs) + 1)):

            # Child Agent: Plan next steps
            if turn > 1:  # Skip planning on first turn
                plan = self.planning_agent.analyze_session_progress(session_id)

            # Get client input (simulated based on turn)
            client_input = initial_inputs[turn - 1] if turn <= len(initial_inputs) else "I understand"

            # Parent Agent: Execute API call
            result = self.send_client_input(client_input, turn)

            if not result:
                print(f"\n⚠️ Turn {turn} failed. Continuing...")
                continue

            # Check if session is complete
            if result['session_progress']['current_substate'] == "stage_1_complete":
                print("\n🎉 Stage 1 Complete!")
                break

        # Step 5: Get final summary
        self.get_session_summary()

        # Step 6: Close session
        self.close_session()

        print("\n" + "="*60)
        print("✅ MULTI-AGENT WORKFLOW COMPLETE")
        print("="*60)


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 AGENTIC WORKFLOW DEMO")
    print("="*60)
    print("Parent Agent: Code Executor (Orchestrator)")
    print("Child Agent: Planning Agent (Therapeutic Planner)")
    print("="*60)

    # Create parent agent (which creates child agent)
    parent_agent = CodeExecutorAgent(api_base_url=TRT_API_BASE_URL)

    # Run complete agentic workflow
    parent_agent.run_agentic_workflow(
        client_id="agentic_demo_client",
        max_turns=10
    )

    print("\n🎯 Demo complete! Check the output above for the complete workflow.")
