"""
Improved Ollama TRT System - Following Dr. Q's Real Methodology
Uses improved dialogue agent with Dr. Q fixes
"""

import json
import time
import signal
import sys
import os
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from session_state_manager import TRTSessionState
from embedding_and_retrieval_setup import TRTRAGSystem
from input_preprocessing import InputPreprocessor
from ollama_llm_master_planning_agent import OllamaLLMMasterPlanningAgent
from improved_ollama_dialogue_agent import ImprovedOllamaDialogueAgent

class ImprovedOllamaTRTSystem:
    """Improved Ollama TRT system following Dr. Q methodology"""

    def __init__(self, ollama_url="http://localhost:11434", model="llama3.1"):
        print("🚀 Initializing IMPROVED Ollama TRT System (Dr. Q Style)...")
        print(f"📡 Ollama URL: {ollama_url}")
        print(f"🤖 Model: {model}")

        # Initialize RAG system
        print("📚 Loading RAG system...")
        self.rag_system = TRTRAGSystem()

        # Get paths relative to project root
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        faiss_path = os.path.join(project_root, "data/embeddings/trt_rag_index.faiss")
        metadata_path = os.path.join(project_root, "data/embeddings/trt_rag_metadata.json")

        self.rag_system.load_index(faiss_path, metadata_path)

        # Initialize agents
        print("🧠 Initializing Ollama Master Planning Agent...")
        self.master_agent = OllamaLLMMasterPlanningAgent(ollama_url=ollama_url, model=model)

        print("💬 Initializing IMPROVED Ollama Dialogue Agent...")
        self.dialogue_agent = ImprovedOllamaDialogueAgent(self.rag_system, ollama_url=ollama_url, model=model)

        # Initialize preprocessor
        self.preprocessor = InputPreprocessor()

        print("✅ Improved Ollama TRT System Ready!")
        print("=" * 80)

    def process_client_input(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Process client input through improved system"""

        start_time = time.time()

        # Step 1: Master Planning
        print(f"🧠 Analyzing: \"{client_input}\"")
        navigation_output = self.master_agent.make_navigation_decision(client_input, session_state)

        # Track body questions (improved logic)
        # Increment counter when asking about body location, sensation, or guiding to body
        body_question_decisions = [
            "body_awareness_inquiry",
            "guide_to_body",
            "body_location",
            "body_sensation"
        ]

        # Also check for specific substates where body questions are asked
        body_question_substates = [
            "2.1_seek",  # Seeking body awareness
            "1.2_problem_and_body"  # Problem + body exploration
        ]

        # Increment if asking body-related questions
        # BUT STOP incrementing once we've escaped to state 3.1 or beyond
        current_state = navigation_output.get("current_substate", "")
        if current_state not in ["3.1_assess_readiness", "3.2_alpha_sequence", "stage_1_complete"]:
            if (navigation_output.get("navigation_decision") in body_question_decisions or
                (navigation_output.get("current_substate") in body_question_substates and
                 "body" in navigation_output.get("navigation_decision", "").lower())):
                # Don't increment if client JUST provided body info
                if session_state.last_client_provided_info not in ["body_location", "sensation_quality"]:
                    session_state.body_questions_asked += 1
                    print(f"   📍 Body questions asked: {session_state.body_questions_asked}/3")

        # Check MAX body question limit (implement escape route)
        if session_state.body_questions_asked >= 3:
            current_sub = navigation_output.get("current_substate")
            # Trigger escape in ANY state where body questions are being asked
            if current_sub in ["2.1_seek", "1.2_problem_and_body", "2.2_location", "2.3_sensation"]:
                # MAX attempts reached → advance to readiness for alpha
                print("   ⚠️  MAX body questions (3) reached. Triggering escape route...")
                print("   🚀 Advancing to alpha readiness (state 3.1)...")

                # Force advancement to alpha readiness
                session_state.current_substate = "3.1_assess_readiness"
                navigation_output["navigation_decision"] = "assess_readiness"
                navigation_output["current_substate"] = "3.1_assess_readiness"
                navigation_output["situation_type"] = "readiness_for_alpha"
                navigation_output["rag_query"] = "dr_q_ready"
                navigation_output["ready_for_next"] = True
                navigation_output["reasoning"] = "MAX body question attempts (3) - advancing to alpha sequence for body awareness development"

        # Step 2: Improved Dialogue Generation
        print(f"💬 Generating improved response...")
        dialogue_output = self.dialogue_agent.generate_response(client_input, navigation_output, session_state)

        # Step 3: Update session
        session_state.add_exchange(
            client_input=client_input,
            therapist_response=dialogue_output["therapeutic_response"],
            navigation_output=navigation_output
        )

        processing_time = time.time() - start_time

        return {
            "navigation": navigation_output,
            "dialogue": dialogue_output,
            "session_progress": session_state.get_progress_summary(),
            "processing_time": processing_time,
            "system_status": {
                "master_agent_ollama": navigation_output.get("llm_reasoning", False),
                "dialogue_agent_ollama": not dialogue_output.get("fallback_used", False),
                "master_confidence": navigation_output.get("llm_confidence", 0.0),
                "dialogue_confidence": dialogue_output.get("llm_confidence", 0.0),
                "body_questions_asked": session_state.body_questions_asked
            }
        }

    def get_system_diagnostics(self) -> dict:
        """Get system diagnostics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "master_agent_status": self.master_agent.get_system_status(),
            "dialogue_agent_status": self.dialogue_agent.get_system_status(),
            "rag_system_loaded": hasattr(self.rag_system, 'index') and self.rag_system.index is not None
        }

def run_manual_test():
    """Run manual test session with improved system"""

    # Global flag for graceful shutdown
    interrupted = {'value': False}

    def signal_handler(sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n👋 Session interrupted by Ctrl+C.")
        interrupted['value'] = True

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 80)
    print("🎭 IMPROVED AI THERAPIST - MANUAL TEST SESSION")
    print("=" * 80)
    print()
    print("You type responses as the PATIENT.")
    print("AI responds as THERAPIST using Dr. Q's methodology.")
    print()
    print("Commands:")
    print("  - Type your response to continue")
    print("  - Type 'quit' to end")
    print("  - Type 'status' for progress")
    print("  - Press Ctrl+C to stop at any time")
    print()
    print("=" * 80)

    # Initialize
    print("\n🚀 Initializing...")
    trt_system = ImprovedOllamaTRTSystem()
    session_state = TRTSessionState("improved_manual_test")

    print("\n✅ Ready! Starting session...\n")
    print("=" * 80)
    print("\n🩺 THERAPIST: \"Hello! What brings you in today?\"\n")

    turn = 0

    while True:
        # Check if interrupted
        if interrupted['value']:
            break

        turn += 1
        print("=" * 80)
        print(f"TURN {turn}")
        print("=" * 80)

        try:
            patient_input = input("\n👤 YOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Session interrupted.")
            break

        # Check again after input
        if interrupted['value']:
            break

        if patient_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Ending session...")
            break

        if patient_input.lower() == 'status':
            print("\n📊 STATUS:")
            print(f"   State: {session_state.current_substate}")
            print(f"   Body Q's Asked: {session_state.body_questions_asked}/3")
            print(f"   Completion: {sum(1 for v in session_state.stage_1_completion.values() if v)}/11")
            print()
            turn -= 1
            continue

        if not patient_input:
            turn -= 1
            continue

        # Process
        print("\n🤔 Processing...", end='', flush=True)

        try:
            output = trt_system.process_client_input(patient_input, session_state)

            # Check if interrupted during processing
            if interrupted['value']:
                print("\n")
                break

            print(" Done!\n")

            print(f"🩺 THERAPIST: \"{output['dialogue']['therapeutic_response']}\"\n")

            # Show brief status
            print(f"📊 [State: {output['navigation']['current_substate']}, "
                  f"Body Q's: {session_state.body_questions_asked}/3, "
                  f"Time: {output['processing_time']:.1f}s]")
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted during processing.")
            break
        except Exception as e:
            print(f"\n\n❌ Error: {e}\n")
            turn -= 1
            continue

    # Summary
    print("\n" + "=" * 80)
    print("📋 SESSION SUMMARY")
    print("=" * 80)
    print(f"\nFinal State: {session_state.current_substate}")
    print(f"Total Turns: {turn}")
    print(f"Body Questions Asked: {session_state.body_questions_asked}")

    completion = session_state.stage_1_completion
    completed = [k for k, v in completion.items() if v]
    if completed:
        print(f"\nCompleted Criteria: {', '.join(completed)}")

    # Save
    if turn > 0:
        # Ensure logs directory exists
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        logs_dir = os.path.join(project_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        log_file = os.path.join(logs_dir, f"improved_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        session_log = {
            "session_id": session_state.session_id,
            "timestamp": datetime.now().isoformat(),
            "turns": len(session_state.conversation_history),
            "body_questions_asked": session_state.body_questions_asked,
            "final_state": session_state.current_substate,
            "completion": session_state.stage_1_completion,
            "conversation": session_state.conversation_history
        }

        with open(log_file, 'w') as f:
            json.dump(session_log, f, indent=2)

        print(f"\n💾 Saved to: {log_file}")

    print("\n" + "=" * 80)
    print("✅ SESSION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_manual_test()
