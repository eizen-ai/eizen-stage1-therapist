"""
Complete Ollama-Based TRT AI Therapy System
Uses local Ollama with Llama 3.1
"""

import json
import time
from datetime import datetime
from session_state_manager import TRTSessionState
from embedding_and_retrieval_setup import TRTRAGSystem
from input_preprocessing import InputPreprocessor
from ollama_llm_master_planning_agent import OllamaLLMMasterPlanningAgent
from ollama_llm_dialogue_agent import OllamaLLMDialogueAgent

class OllamaTRTSystem:
    """Complete Ollama-powered TRT therapy system"""

    def __init__(self, ollama_url="http://localhost:11434", model="llama3.1"):
        print("🚀 Initializing Ollama-Based TRT System...")
        print(f"📡 Ollama URL: {ollama_url}")
        print(f"🤖 Model: {model}")

        # Initialize RAG system
        print("📚 Loading RAG system...")
        self.rag_system = TRTRAGSystem()
        self.rag_system.load_index("data/embeddings/trt_rag_index.faiss",
                                  "data/embeddings/trt_rag_metadata.json")

        # Initialize Ollama-based LLM agents
        print("🧠 Initializing Ollama Master Planning Agent...")
        self.master_agent = OllamaLLMMasterPlanningAgent(ollama_url=ollama_url, model=model)

        print("💬 Initializing Ollama Dialogue Agent...")
        self.dialogue_agent = OllamaLLMDialogueAgent(self.rag_system, ollama_url=ollama_url, model=model)

        # Initialize preprocessor
        self.preprocessor = InputPreprocessor()

        print("✅ Ollama-Based TRT System Initialized Successfully!")
        print("=" * 80)

    def process_client_input(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Process client input through Ollama-powered TRT system"""

        start_time = time.time()

        # Step 1: Ollama Master Planning Agent
        print(f"🧠 Ollama Master Agent analyzing: \"{client_input}\"")
        navigation_output = self.master_agent.make_navigation_decision(client_input, session_state)

        # Step 2: Ollama Dialogue Agent with RAG
        print(f"💬 Ollama Dialogue Agent generating response...")
        dialogue_output = self.dialogue_agent.generate_response(client_input, navigation_output, session_state)

        # Step 3: Update session history
        session_state.add_exchange(
            client_input=client_input,
            therapist_response=dialogue_output["therapeutic_response"],
            navigation_output=navigation_output
        )

        processing_time = time.time() - start_time

        # Return complete system output
        return {
            "navigation": navigation_output,
            "dialogue": dialogue_output,
            "session_progress": session_state.get_progress_summary(),
            "processing_time": processing_time,
            "system_status": {
                "master_agent_ollama": navigation_output.get("llm_reasoning", False),
                "dialogue_agent_ollama": not dialogue_output.get("fallback_used", False),
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

def run_ollama_system_test():
    """Test the complete Ollama-based TRT system"""

    print("🎭 OLLAMA-BASED TRT SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)

    # Initialize system
    trt_system = OllamaTRTSystem()
    session_state = TRTSessionState("ollama_test_session")

    # Test sequence
    test_conversations = [
        # Normal progression
        "I've been feeling really stressed and don't know what to do",
        "I want to feel calm and at peace",
        "Yes, that sounds exactly like what I want",
        "It's work pressure, I get this tight feeling in my chest",
        "I can feel it right now, it's heavy and uncomfortable",
        "It starts when I see my calendar full of meetings",
    ]

    for turn, client_input in enumerate(test_conversations, 1):
        print(f"\n🔄 TURN {turn}")
        print("=" * 60)
        print(f"👤 CLIENT: \"{client_input}\"")
        print()

        # Process through Ollama system
        system_output = trt_system.process_client_input(client_input, session_state)

        # Show comprehensive output
        nav = system_output["navigation"]
        dialogue = system_output["dialogue"]
        progress = system_output["session_progress"]
        status = system_output["system_status"]

        print("🧠 OLLAMA MASTER PLANNING:")
        print(f"   Substate: {nav['current_substate']}")
        print(f"   Decision: {nav['navigation_decision']}")
        print(f"   Ollama Reasoning: {'✅' if status['master_agent_ollama'] else '❌ (fallback)'}")
        print(f"   Confidence: {status['master_confidence']:.2f}")
        print(f"   Reasoning: {nav.get('reasoning', 'N/A')[:100]}...")
        print()

        print("💬 OLLAMA DIALOGUE GENERATION:")
        print(f"   Technique: {dialogue['technique_used']}")
        print(f"   Ollama Generated: {'✅' if status['dialogue_agent_ollama'] else '❌ (fallback)'}")
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

    print("\n🎉 OLLAMA SYSTEM TEST COMPLETE!")
    print(f"Final substate: {session_state.current_substate}")
    print(f"Total turns: {len(session_state.conversation_history)}")

    # Show system diagnostics
    diagnostics = trt_system.get_system_diagnostics()
    print(f"\n🔧 SYSTEM DIAGNOSTICS:")
    print(f"   Master Agent: {diagnostics['master_agent_status']}")
    print(f"   Dialogue Agent: {diagnostics['dialogue_agent_status']}")
    print(f"   RAG System: {'✅' if diagnostics['rag_system_loaded'] else '❌'}")

def run_interactive_session():
    """Run interactive therapy session with Ollama-based system"""

    print("🎭 OLLAMA TRT THERAPY - INTERACTIVE SESSION")
    print("=" * 80)
    print("Type 'quit' to exit")
    print("=" * 80)

    # Initialize
    trt_system = OllamaTRTSystem()
    session_state = TRTSessionState("interactive_session")

    turn = 0
    while True:
        turn += 1
        print(f"\n{'='*60}")
        print(f"TURN {turn}")
        print("="*60)

        # Get client input
        client_input = input("\n👤 YOU (as client): ").strip()

        if client_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Ending session...")
            break

        if not client_input:
            continue

        # Process
        system_output = trt_system.process_client_input(client_input, session_state)

        # Show therapist response
        print(f"\n🩺 THERAPIST: \"{system_output['dialogue']['therapeutic_response']}\"")

        # Show progress
        print(f"\n📊 Progress: {session_state.current_substate}")
        completion = session_state.stage_1_completion
        completed_count = sum(1 for v in completion.values() if v)
        print(f"   Stage 1: {completed_count}/5 criteria met")

    # Save session log
    session_log = {
        "session_id": session_state.session_id,
        "turns": len(session_state.conversation_history),
        "final_state": session_state.current_substate,
        "completion": session_state.stage_1_completion,
        "conversation": session_state.conversation_history
    }

    log_filename = f"logs/ollama_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w') as f:
        json.dump(session_log, f, indent=2)

    print(f"\n💾 Session saved to: {log_filename}")
    print("\n✅ Session complete!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        run_interactive_session()
    else:
        run_ollama_system_test()
