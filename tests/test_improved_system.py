"""
Quick Automated Test for Improved Ollama System
Tests all 6 Dr. Q methodology fixes
"""

import sys
import json
from improved_ollama_system import ImprovedOllamaTRTSystem
from session_state_manager import TRTSessionState

def test_improved_system():
    """Run automated test conversation"""

    print("=" * 80)
    print("🧪 TESTING IMPROVED SYSTEM - Dr. Q Methodology")
    print("=" * 80)
    print()

    # Initialize system
    print("🚀 Initializing...")
    trt_system = ImprovedOllamaTRTSystem()
    session_state = TRTSessionState("automated_test")

    print("✅ System ready!\n")
    print("=" * 80)

    # Test conversation focusing on body awareness
    test_inputs = [
        "I've been feeling really stressed about work lately",
        "I want to feel calm and peaceful",
        "Yes, that sounds perfect",
        "I feel it in my chest",
        "It's tight and heavy",
        "Yes, I'm feeling it right now"
    ]

    for turn, client_input in enumerate(test_inputs, 1):
        print(f"\n{'=' * 80}")
        print(f"TURN {turn}")
        print(f"{'=' * 80}\n")

        print(f"👤 CLIENT: \"{client_input}\"")

        try:
            # Process input
            output = trt_system.process_client_input(client_input, session_state)

            therapist_response = output['dialogue']['therapeutic_response']
            print(f"\n🩺 THERAPIST: \"{therapist_response}\"")

            # Show metrics
            print(f"\n📊 METRICS:")
            print(f"   State: {output['navigation']['current_substate']}")
            print(f"   Decision: {output['navigation']['navigation_decision']}")
            print(f"   Body Q Count: {session_state.body_questions_asked}/3")
            print(f"   Last Info Provided: {session_state.last_client_provided_info}")
            print(f"   Technique: {output['dialogue']['technique_used']}")
            print(f"   Fallback Used: {output['dialogue']['fallback_used']}")
            print(f"   Processing Time: {output['processing_time']:.2f}s")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            break

    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    print(f"\nFinal State: {session_state.current_substate}")
    print(f"Body Questions Asked: {session_state.body_questions_asked}/3")
    print(f"Body Location Provided: {session_state.body_location_provided}")
    print(f"Body Sensation Described: {session_state.body_sensation_described}")

    print("\n✅ COMPLETION STATUS:")
    for key, value in session_state.stage_1_completion.items():
        status = "✅" if value else "⏳"
        print(f"   {status} {key}: {value}")

    print("\n" + "=" * 80)
    print("🎯 DR. Q METHODOLOGY CHECKS:")
    print("=" * 80)

    # Check for repetitive questions
    responses = [ex['therapist_response'] for ex in session_state.conversation_history]

    # Count how many times same question asked
    sensation_questions = sum(1 for r in responses if "sensation" in r.lower() and "?" in r)
    body_location_questions = sum(1 for r in responses if "where" in r.lower() and "body" in r.lower())

    print(f"\n1. Question Repetition Check:")
    print(f"   Sensation questions: {sensation_questions}")
    print(f"   Body location questions: {body_location_questions}")
    print(f"   ✅ PASS" if sensation_questions <= 2 else "   ❌ FAIL: Too many repetitive questions")

    print(f"\n2. Body Question Limit Check:")
    print(f"   Total body questions: {session_state.body_questions_asked}")
    print(f"   ✅ PASS" if session_state.body_questions_asked <= 3 else "   ⚠️ WARNING: Over limit")

    print(f"\n3. Answer Acceptance Check:")
    affirmations = sum(1 for ex in session_state.conversation_history
                      if any(word in ex['therapist_response'].lower()
                            for word in ["that's right", "yeah", "exactly"]))
    print(f"   Affirmations given: {affirmations}")
    print(f"   ✅ PASS" if affirmations > 0 else "   ⚠️ WARNING: No affirmations")

    print(f"\n4. Example Provision Check:")
    examples_given = sum(1 for r in responses
                        if "ache" in r.lower() or "tight" in r.lower() or "sharp" in r.lower())
    print(f"   Responses with sensation examples: {examples_given}")
    print(f"   ✅ PASS" if examples_given > 0 else "   ⚠️ WARNING: No examples given")

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_improved_system()
