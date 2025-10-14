#!/usr/bin/env python3
"""
Test the specific problematic sequence identified by the user
"""

from integrated_trt_system import CompleteTRTSystem
from session_state_manager import TRTSessionState

def test_problematic_sequence():
    """Test the exact sequence that was causing loops"""

    print("🧪 TESTING PROBLEMATIC SEQUENCE")
    print("=" * 60)

    # Initialize system
    trt_system = CompleteTRTSystem()
    session_state = TRTSessionState("problematic_sequence_test")

    # The exact problematic sequence
    test_sequence = [
        "iam feeling low",
        "i want to feel great",
        "i feel sad",
        "i feel it in my chest",
        "i feels heavy",
        "i feel better"
    ]

    print("Testing sequence:")
    for i, inp in enumerate(test_sequence, 1):
        print(f"  {i}. \"{inp}\"")
    print()

    for turn, client_input in enumerate(test_sequence, 1):
        print(f"🔄 TURN {turn}")
        print("=" * 40)
        print(f"👤 CLIENT: \"{client_input}\"")

        # Process through complete system
        system_output = trt_system.process_client_input(client_input, session_state)

        # Show key information
        nav = system_output["navigation"]
        dialogue = system_output["dialogue"]

        print(f"📍 Substate: {nav['current_substate']}")
        print(f"🎯 Decision: {nav['navigation_decision']}")
        if nav.get('recent_events'):
            print(f"📋 Events: {nav['recent_events']}")
        print(f"🩺 THERAPIST: \"{dialogue['therapeutic_response']}\"")

        # Check completion status
        completion = nav['completion_status']
        vision_status = "✅" if completion.get('vision_accepted', False) else "⏳"
        goal_status = "✅" if completion.get('goal_stated', False) else "⏳"
        print(f"🎯 Goal: {goal_status} | Vision: {vision_status}")

        print()

    print("🎉 TEST COMPLETE!")
    print(f"Final substate: {session_state.current_substate}")

    # Check if the specific issues are resolved
    print("\n✅ ISSUE RESOLUTION CHECK:")
    print(f"1. No repetitive vision questions: {'✅ FIXED' if session_state.current_substate != '1.1_goal_and_vision' else '❌ STILL STUCK'}")
    print(f"2. Advanced beyond 1.1: {'✅ YES' if '1.2' in session_state.current_substate or 'stage_1_complete' in session_state.current_substate else '❌ NO'}")
    print(f"3. Handled 'i feel better' appropriately: {'✅ YES' if 'better' not in dialogue['therapeutic_response'] or 'different now' in dialogue['therapeutic_response'] else '❌ NO'}")

if __name__ == "__main__":
    test_problematic_sequence()