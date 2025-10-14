"""
Complete LLM-Based TRT AI Therapy System
Integrates Llama 3.1 Master Planning Agent + Llama 3.1 Dialogue Agent + RAG + Session State
"""

import json
import time
from datetime import datetime
from session_state_manager import TRTSessionState
from embedding_and_retrieval_setup import TRTRAGSystem
from input_preprocessing import InputPreprocessor
from llm_master_planning_agent import LLMMasterPlanningAgent
from llm_dialogue_agent import LLMDialogueAgent

class LLMCompleteTRTSystem:
    """Complete LLM-powered TRT therapy system with advanced reasoning"""

    def __init__(self):
        print("🚀 Initializing LLM-Based TRT System...")

        # Initialize RAG system
        print("📚 Loading RAG system...")
        self.rag_system = TRTRAGSystem()
        self.rag_system.load_index("data/embeddings/trt_rag_index.faiss",
                                  "data/embeddings/trt_rag_metadata.json")

        # Initialize LLM agents
        print("🧠 Initializing LLM Master Planning Agent...")
        self.master_agent = LLMMasterPlanningAgent()

        print("💬 Initializing LLM Dialogue Agent...")
        self.dialogue_agent = LLMDialogueAgent(self.rag_system)

        # Initialize preprocessor
        self.preprocessor = InputPreprocessor()

        print("✅ LLM-Based TRT System Initialized Successfully!")

    def process_client_input(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Process client input through complete LLM-powered TRT system"""

        start_time = time.time()

        # Step 1: LLM Master Planning Agent
        print(f"🧠 LLM Master Agent analyzing: \"{client_input}\"")
        navigation_output = self.master_agent.make_navigation_decision(client_input, session_state)

        # Step 2: LLM Dialogue Agent with RAG
        print(f"💬 LLM Dialogue Agent generating response...")
        dialogue_output = self.dialogue_agent.generate_response(client_input, navigation_output, session_state)

        # Step 3: Update session history
        session_state.add_exchange(
            client_input=client_input,
            therapist_response=dialogue_output["therapeutic_response"],
            navigation_output=navigation_output
        )

        processing_time = time.time() - start_time

        # Return complete system output with LLM insights
        return {
            "navigation": navigation_output,
            "dialogue": dialogue_output,
            "session_progress": session_state.get_progress_summary(),
            "processing_time": processing_time,
            "system_status": {
                "master_agent_llm": navigation_output.get("llm_reasoning", False),
                "dialogue_agent_llm": not dialogue_output.get("fallback_used", False),
                "master_confidence": navigation_output.get("llm_confidence", 0.0),
                "dialogue_confidence": dialogue_output.get("llm_confidence", 0.0)
            }
        }

    def get_system_diagnostics(self) -> dict:
        """Get comprehensive system diagnostics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "master_agent_status": self.master_agent.get_system_status(),
            "dialogue_agent_status": self.dialogue_agent.get_system_status(),
            "rag_system_loaded": hasattr(self.rag_system, 'index') and self.rag_system.index is not None
        }

def run_llm_system_test():
    """Test the complete LLM-based TRT system"""

    print("🎭 LLM-BASED TRT SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)

    # Initialize system
    trt_system = LLMCompleteTRTSystem()
    session_state = TRTSessionState("llm_test_session")

    # Test sequence including edge cases
    test_conversations = [
        # Normal progression
        "I've been feeling really stressed and don't know what to do",
        "I want to feel calm and at peace",
        "Yes, that sounds exactly like what I want",
        "It's work pressure, I get this tight feeling in my chest",
        "I can feel it right now, it's heavy and uncomfortable",
        "It starts when I see my calendar full of meetings",
        "I think I understand the pattern now",

        # Edge cases
        "I feel better actually",
        "Wait, now I'm confused again",
        "Can you repeat that?",
        "I don't understand what you mean",
        "This isn't helping"
    ]

    for turn, client_input in enumerate(test_conversations, 1):
        print(f"\n🔄 TURN {turn}")
        print("=" * 60)
        print(f"👤 CLIENT: \"{client_input}\"")
        print()

        # Process through LLM system
        system_output = trt_system.process_client_input(client_input, session_state)

        # Show comprehensive output
        nav = system_output["navigation"]
        dialogue = system_output["dialogue"]
        progress = system_output["session_progress"]
        status = system_output["system_status"]

        print("🧠 LLM MASTER PLANNING:")
        print(f"   Substate: {nav['current_substate']}")
        print(f"   Decision: {nav['navigation_decision']}")
        print(f"   LLM Reasoning: {'✅' if status['master_agent_llm'] else '❌ (fallback)'}")
        print(f"   Confidence: {status['master_confidence']:.2f}")
        print(f"   Reasoning: {nav.get('reasoning', 'N/A')[:100]}...")
        print()

        print("💬 LLM DIALOGUE GENERATION:")
        print(f"   Technique: {dialogue['technique_used']}")
        print(f"   LLM Generated: {'✅' if status['dialogue_agent_llm'] else '❌ (fallback)'}")
        print(f"   Confidence: {status['dialogue_confidence']:.2f}")
        print(f"   Examples used: {dialogue['examples_used']}")
        print()

        print(f"🩺 THERAPIST: \"{dialogue['therapeutic_response']}\"")
        print()

        print("📊 SESSION PROGRESS:")
        for substate, criteria in progress.get("stage_1_progress", {}).items():
            print(f"   {substate}: {criteria}")
        print()

        print(f"⏱️  Processing Time: {system_output['processing_time']:.3f}s")
        print("=" * 80)

    print("\n🎉 LLM SYSTEM TEST COMPLETE!")
    print(f"Final substate: {session_state.current_substate}")
    print(f"Total turns: {len(session_state.conversation_history)}")

    # Show system diagnostics
    diagnostics = trt_system.get_system_diagnostics()
    print(f"\n🔧 SYSTEM DIAGNOSTICS:")
    print(f"   Master Agent: {diagnostics['master_agent_status']}")
    print(f"   Dialogue Agent: {diagnostics['dialogue_agent_status']}")

if __name__ == "__main__":
    run_llm_system_test()