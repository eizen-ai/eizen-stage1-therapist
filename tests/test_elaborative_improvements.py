#!/usr/bin/env python3
"""
Test Elaborative Improvements
Tests all 5 improvements to make the system more like Dr. Q:
1. Expanded vision building (4-5 sentences)
2. Combined questions (emotion + body location)
3. Reflection/validation responses
4. "How do you know?" technique for pattern exploration
5. Elaboration encouragement for long responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.session_state_manager import TRTSessionState
from src.agents.ollama_llm_master_planning_agent import OllamaLLMMasterPlanningAgent
from src.agents.improved_ollama_dialogue_agent import ImprovedOllamaDialogueAgent
from src.utils.embedding_and_retrieval_setup import TRTRAGSystem

def test_elaborative_improvements():
    """Test all elaborative improvements"""

    print("="*80)
    print("🧪 TESTING ELABORATIVE IMPROVEMENTS")
    print("="*80)
    print()

    # Initialize system
    print("🚀 Initializing system...")
    rag_system = TRTRAGSystem()

    # Load pre-built RAG index
    print("📚 Loading RAG index...")
    try:
        index_path = "data/embeddings/trt_rag_index.faiss"
        metadata_path = "data/embeddings/trt_rag_metadata.json"
        rag_system.load_index(index_path, metadata_path)
        print("✅ RAG index loaded successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not load RAG index: {e}")
        print("   Continuing anyway - will use rule-based responses only")

    master_agent = OllamaLLMMasterPlanningAgent()
    dialogue_agent = ImprovedOllamaDialogueAgent(rag_system)
    session_state = TRTSessionState()

    print("✅ System initialized")
    print()

    # Test conversation with elaborative elements
    test_exchanges = [
        # Turn 1: Initial greeting
        {"user": "i want to feel peaceful", "desc": "Initial goal statement"},

        # Turn 2: Vision acceptance (should see 4-5 sentence vision!)
        {"user": "yes that makes sense", "desc": "Accept vision - should get 4-5 sentence response"},

        # Turn 3: Problem with pattern language (should trigger "How do you know?" possibly)
        {"user": "i am always feeling stressed and i keep struggling with my work deadlines and my relationships", "desc": "Long response with pattern words - may get 'How do you know?' or elaboration encouragement"},

        # Turn 4: Continue elaborating
        {"user": "yes i feel it in my chest and shoulders", "desc": "Body location"},

        # Turn 5: Another long elaboration (should encourage more elaboration)
        {"user": "it feels like a tight pressure that never goes away and it gets worse when i think about all the things i need to do and how i'm letting everyone down", "desc": "Very long elaboration (26 words) - should encourage more"},

        # Turn 6: Continue
        {"user": "i also feel angry at myself", "desc": "Another emotion"},

        # Turn 7: Body location
        {"user": "in my forehead", "desc": "Location of anger"},

        # Turn 8: Response to readiness
        {"user": "yes i've shared everything", "desc": "Confirm readiness"},

        # Turn 9: Alpha permission
        {"user": "yes i am ready", "desc": "Give permission for alpha"},
    ]

    print("📝 Running test conversation...")
    print()

    improvements_tested = {
        "vision_4_5_sentences": False,
        "combined_questions": False,
        "reflection_validation": False,
        "how_do_you_know": False,
        "elaboration_encouragement": False
    }

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
        therapist_response = response['therapeutic_response']
        print(f"🩺 THERAPIST: {therapist_response}")
        print()
        print(f"📊 State: {navigation_output['current_substate']}")
        print(f"📍 Decision: {navigation_output['navigation_decision']}")
        print()

        # Check which improvements were used
        if turn_num == 2:
            # Check vision building (4-5 sentences)
            sentences = therapist_response.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            if sentence_count >= 4:
                improvements_tested["vision_4_5_sentences"] = True
                print(f"✅ IMPROVEMENT #1 DETECTED: Vision has {sentence_count} sentences (target: 4-5)")
            else:
                print(f"ℹ️  Vision has {sentence_count} sentences")

        # Check for combined questions (emotion + body together)
        if "feeling" in therapist_response.lower() and "where" in therapist_response.lower() and "body" in therapist_response.lower():
            improvements_tested["combined_questions"] = True
            print("✅ IMPROVEMENT #2 DETECTED: Combined question (emotion + body location together)")

        # Check for reflection/validation
        if any(phrase in therapist_response.lower() for phrase in ["i hear", "so you", "right, i understand"]):
            improvements_tested["reflection_validation"] = True
            print("✅ IMPROVEMENT #3 DETECTED: Reflection/validation response")

        # Check for "How do you know?" technique
        if "how do you know" in therapist_response.lower():
            improvements_tested["how_do_you_know"] = True
            print("✅ IMPROVEMENT #4 DETECTED: 'How do you know?' technique for pattern exploration")

        # Check for elaboration encouragement
        if any(phrase in therapist_response.lower() for phrase in ["so keep going", "tell me more", "go on"]):
            improvements_tested["elaboration_encouragement"] = True
            print("✅ IMPROVEMENT #5 DETECTED: Elaboration encouragement")

        print()

    print("="*80)
    print("🎉 TEST COMPLETE")
    print("="*80)
    print()
    print("📊 IMPROVEMENTS TESTED:")
    print()
    print(f"1. Vision Building (4-5 sentences): {'✅ TESTED' if improvements_tested['vision_4_5_sentences'] else '❌ NOT DETECTED'}")
    print(f"2. Combined Questions (emotion + body): {'✅ TESTED' if improvements_tested['combined_questions'] else '❌ NOT DETECTED'}")
    print(f"3. Reflection/Validation: {'✅ TESTED' if improvements_tested['reflection_validation'] else '❌ NOT DETECTED (probabilistic - 40%)'}")
    print(f"4. 'How do you know?' Technique: {'✅ TESTED' if improvements_tested['how_do_you_know'] else '❌ NOT DETECTED (probabilistic - 30%)'}")
    print(f"5. Elaboration Encouragement: {'✅ TESTED' if improvements_tested['elaboration_encouragement'] else '❌ NOT DETECTED (probabilistic - 40%)'}")
    print()

    tested_count = sum(improvements_tested.values())
    print(f"✅ {tested_count}/5 improvements detected in this test run")
    print()
    print("ℹ️  Note: Improvements #3, #4, and #5 are probabilistic, so they may not appear every time.")
    print("   Run the test multiple times to see different variations.")
    print()

    # Final state check
    print("📊 FINAL SESSION STATE:")
    print(f"   - Current State: {session_state.current_substate}")
    print(f"   - Total Turns: {len(session_state.conversation_history)}")
    print()

if __name__ == "__main__":
    test_elaborative_improvements()
