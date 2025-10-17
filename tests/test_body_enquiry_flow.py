#!/usr/bin/env python3
"""
Test Body Enquiry Flow
Tests the updated body enquiry cycle logic (max 2 cycles, "nothing else" detection)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.session_state_manager import TRTSessionState
from src.agents.ollama_llm_master_planning_agent import OllamaLLMMasterPlanningAgent
from src.agents.improved_ollama_dialogue_agent import ImprovedOllamaDialogueAgent
from src.utils.embedding_and_retrieval_setup import TRTRAGSystem

def test_body_enquiry_flow():
    """Test the body enquiry flow following your reference pattern"""

    print("="*80)
    print("🧪 TESTING BODY ENQUIRY FLOW")
    print("="*80)
    print()

    # Initialize system
    print("🚀 Initializing system...")
    rag_system = TRTRAGSystem()

    # Create embeddings if not already created
    print("📚 Setting up RAG embeddings...")
    try:
        rag_system.create_embeddings()
        print("✅ Embeddings created")
    except Exception as e:
        print(f"⚠️  Warning: Could not create embeddings: {e}")
        print("   Continuing anyway - will use rule-based responses")

    master_agent = OllamaLLMMasterPlanningAgent()
    dialogue_agent = ImprovedOllamaDialogueAgent(rag_system)
    session_state = TRTSessionState()

    print("✅ System initialized")
    print()

    # Simulated conversation following your reference pattern
    test_exchanges = [
        # Turn 1: Initial greeting
        {"user": "i want to feel peaceful", "desc": "Initial goal statement"},

        # Turn 2: Vision acceptance
        {"user": "yes that makes sense", "desc": "Accept vision"},

        # Turn 3: Problem inquiry (SHOULD ONLY HAPPEN ONCE!)
        {"user": "i am feeling stressed out due to many reasons", "desc": "Respond to 'what's making it hard'"},

        # Turn 4: Body location
        {"user": "i feel it in my head and shoulders", "desc": "Provide body location"},

        # Turn 5: Multiple emotions
        {"user": "i feel angry at the same time", "desc": "Another emotion"},

        # Turn 6: Body location for anger
        {"user": "in my forehead", "desc": "Location of anger"},

        # Turn 7: Sensation description
        {"user": "here in head, top of my head", "desc": "Elaborate on location"},

        # Turn 8: Response to "What else?"
        {"user": "i feel so much pressure", "desc": "Describe more sensations"},

        # Turn 9: Response to 2nd "What else?" - CLIENT SAYS NOTHING
        {"user": "nothing else", "desc": "Client says 'nothing else' - SHOULD ADVANCE TO 3.1!"},

        # Turn 10: Readiness confirmation
        {"user": "yes i have shared everything", "desc": "Confirm readiness"},

        # Turn 11: Alpha permission
        {"user": "yes i am ready", "desc": "Give permission for alpha"},
    ]

    print("📝 Running test conversation...")
    print()

    for turn_num, exchange in enumerate(test_exchanges, 1):
        print(f"{'='*80}")
        print(f"TURN {turn_num}: {exchange['desc']}")
        print(f"{'='*80}")

        user_input = exchange['user']
        print(f"👤 USER: {user_input}")
        print()

        # Process with master planning agent
        navigation_output = master_agent.make_navigation_decision(user_input, session_state)

        # Generate therapist response
        response = dialogue_agent.generate_response(user_input, navigation_output, session_state)

        # Update session state
        session_state.add_exchange(
            user_input,
            response['therapeutic_response'],
            navigation_output
        )

        # Display response
        print(f"🩺 THERAPIST: {response['therapeutic_response']}")
        print()
        print(f"📊 State: {navigation_output['current_substate']}")
        print(f"📍 Decision: {navigation_output['navigation_decision']}")
        print(f"🔄 Body Enquiry Cycles: {session_state.body_enquiry_cycles}/2")
        print(f"❓ 'What else?' asked: {session_state.anything_else_count} times")
        print(f"❗ Problem question asked: {session_state.problem_question_asked}")
        print()

        # Check critical transitions
        if turn_num == 3:
            # After first problem response, should NOT repeat "what's making it hard"
            if "making it hard" in response['therapeutic_response'].lower():
                print("⚠️  WARNING: System repeated 'what's making it hard' question!")

        if turn_num == 9 and user_input == "nothing else":
            # Should advance to 3.1_assess_readiness
            if navigation_output['current_substate'] == '3.1_assess_readiness':
                print("✅ SUCCESS: System advanced to 3.1_assess_readiness after 'nothing else'")
            else:
                print(f"❌ FAILURE: System did NOT advance to 3.1 (stuck in {navigation_output['current_substate']})")

        print()

    print("="*80)
    print("🎉 TEST COMPLETE")
    print("="*80)
    print()
    print("📊 FINAL SESSION STATE:")
    print(f"   - Current State: {session_state.current_substate}")
    print(f"   - Body Enquiry Cycles: {session_state.body_enquiry_cycles}/2")
    print(f"   - 'What else?' Count: {session_state.anything_else_count}")
    print(f"   - Problem Question Asked: {session_state.problem_question_asked}")
    print(f"   - Total Turns: {len(session_state.conversation_history)}")
    print()

if __name__ == "__main__":
    test_body_enquiry_flow()
