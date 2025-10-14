"""
Improved TRT Tester - Shows the fixes for repetitive responses
Tests the enhanced adaptive response system
"""

from integrated_trt_system import CompleteTRTSystem
from session_state_manager import TRTSessionState

def test_improved_system():
    """Test the improved system that avoids repetitive responses"""

    print("🎯 IMPROVED TRT SYSTEM TEST")
    print("Testing adaptive responses and implicit acceptance")
    print("=" * 60)

    # Initialize system
    trt_system = CompleteTRTSystem()
    session_state = TRTSessionState("improved_test")

    # Same problematic sequence from before
    sequence = [
        "iam feeling low",
        "i want to feel great",
        "i feel sad",
        "i feel it in my chest",
        "i feels heavy",
        "i feel better"
    ]

    print("🔄 PROCESSING SEQUENCE:")
    print("Expected: System should adapt responses and advance when appropriate")
    print()

    for turn, client_input in enumerate(sequence, 1):
        print(f"TURN {turn}: '{client_input}'")

        # Process input
        system_output = trt_system.process_client_input(client_input, session_state)

        # Show key changes
        response = system_output["dialogue"]["therapeutic_response"]
        completion = system_output["navigation"]["completion_status"]

        print(f"RESPONSE: \"{response}\"")
        print(f"STATUS: Goal={completion['goal_stated']}, Vision={completion['vision_accepted']}")
        print(f"LOCATION: {session_state.current_substate}")

        # Check for improvements
        if turn > 2 and "vision feel right" not in response:
            print("✅ IMPROVEMENT: System adapted response instead of repeating vision question")

        if completion['vision_accepted']:
            print("✅ IMPROVEMENT: System recognized implicit vision acceptance")

        print("-" * 50)

    print("\n🎯 IMPROVEMENTS ANALYSIS:")
    final_completion = session_state.stage_1_completion

    # Check if vision was accepted through implicit means
    if final_completion['vision_accepted']:
        print("✅ SUCCESS: Vision acceptance detected")
        print(f"✅ Current substate: {session_state.current_substate}")
    else:
        print("⚠️  STILL NEEDS WORK: Vision acceptance not detected")
        print("   System should recognize continued emotional sharing as implicit acceptance")

    # Check response variety
    response_history = getattr(session_state, 'response_history', [])
    unique_responses = set(response_history)

    print(f"📊 Response Variety: {len(unique_responses)}/{len(response_history)} unique responses")

    if len(unique_responses) > len(response_history) * 0.6:
        print("✅ SUCCESS: Good response variety")
    else:
        print("⚠️  STILL REPETITIVE: Need more response adaptation")

    # Show what should happen in real TRT
    print(f"\n💡 REAL TRT BEHAVIOR:")
    print("When client continues sharing emotions/body sensations:")
    print("1. ✅ Acknowledge their sharing (present-moment focus)")
    print("2. ✅ Move to body awareness and problem exploration")
    print("3. ✅ Don't get stuck asking for explicit vision acceptance")
    print("4. ✅ Use client's continued engagement as implicit acceptance")

if __name__ == "__main__":
    test_improved_system()