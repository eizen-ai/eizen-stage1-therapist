"""
Simple Agentic Demo - Parent & Child Agents
Works with TRT AI Therapist API on localhost:8090
"""

import requests
import json

API_URL = "http://localhost:8090"


class PlanningAgent:
    """Child Agent: Plans therapeutic interventions"""

    def __init__(self):
        self.name = "PlanningAgent"
        print(f"🧠 {self.name} initialized")

    def analyze_and_plan(self, session_id):
        """Analyze session and create plan"""
        print(f"\n{'='*50}")
        print(f"🧠 {self.name}: Analyzing session...")
        print(f"{'='*50}")

        # Get session status
        response = requests.get(f"{API_URL}/api/v1/session/{session_id}/status")
        status = response.json()

        # Simple analysis
        state = status.get('current_substate', 'unknown')
        completed = sum(status.get('completion_criteria', {}).values())
        total = len(status.get('completion_criteria', {}))

        print(f"📊 Current State: {state}")
        print(f"✅ Progress: {completed}/{total}")

        # Create simple plan
        plan = {
            "recommendation": "Continue therapeutic process",
            "priority": "normal"
        }

        print(f"📋 Plan: {plan['recommendation']}")
        return plan


class CodeExecutorAgent:
    """Parent Agent: Executes the workflow"""

    def __init__(self):
        self.name = "CodeExecutorAgent"
        self.planning_agent = PlanningAgent()
        print(f"⚙️ {self.name} initialized")

    def check_health(self):
        """Check API health"""
        print(f"\n{'='*50}")
        print(f"⚙️ {self.name}: Health check...")
        print(f"{'='*50}")

        response = requests.get(f"{API_URL}/health")
        health = response.json()

        print(f"Status: {health['status']}")
        return health['status'] == 'healthy'

    def create_session(self, client_id):
        """Create new session"""
        print(f"\n{'='*50}")
        print(f"⚙️ {self.name}: Creating session...")
        print(f"{'='*50}")

        response = requests.post(
            f"{API_URL}/api/v1/session/create",
            json={"client_id": client_id}
        )
        data = response.json()
        session_id = data['session_id']

        print(f"✅ Session: {session_id}")
        return session_id

    def process_turn(self, session_id, user_input, turn_num):
        """Process one conversation turn"""
        print(f"\n{'='*50}")
        print(f"⚙️ {self.name}: Turn {turn_num}")
        print(f"{'='*50}")
        print(f"👤 Client: {user_input}")

        response = requests.post(
            f"{API_URL}/api/v1/session/{session_id}/input",
            json={"user_input": user_input}
        )

        result = response.json()
        therapist = result.get('therapist_response', 'No response')

        print(f"🩺 Therapist: {therapist}")
        return result

    def run_workflow(self, client_id="demo_client"):
        """Run complete workflow"""
        print("\n" + "="*50)
        print("🚀 STARTING AGENTIC WORKFLOW")
        print("="*50)

        # Step 1: Health check
        if not self.check_health():
            print("❌ System not healthy")
            return

        # Step 2: Create session
        session_id = self.create_session(client_id)

        # Step 3: Run conversation
        conversation = [
            "I'm feeling stressed",
            "I want to feel calm",
            "Yes, that helps"
        ]

        for i, user_input in enumerate(conversation, 1):
            # Process turn
            self.process_turn(session_id, user_input, i)

            # Let planning agent analyze (after first turn)
            if i > 1:
                plan = self.planning_agent.analyze_and_plan(session_id)

        # Step 4: Summary
        print(f"\n{'='*50}")
        print("✅ WORKFLOW COMPLETE")
        print(f"{'='*50}")

        # Step 5: Cleanup
        requests.delete(f"{API_URL}/api/v1/session/{session_id}")
        print("🗑️ Session cleaned up")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 SIMPLE AGENTIC DEMO")
    print("="*50)
    print("Parent: CodeExecutorAgent")
    print("Child: PlanningAgent")
    print("="*50)

    # Create parent agent (which creates child)
    parent = CodeExecutorAgent()

    # Run workflow
    parent.run_workflow()

    print("\n✅ Demo complete!")
