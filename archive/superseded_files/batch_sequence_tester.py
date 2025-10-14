"""
Batch Sequence Tester for predefined conversation flows
Tests complete TRT sequences with detailed logging
"""

from interactive_trt_tester import TRTInteractiveTester

def test_complete_sequence():
    """Test a complete 1.1 → 1.2 → 1.3 sequence"""

    print("🎭 BATCH SEQUENCE TEST: COMPLETE STAGE 1 PROGRESSION")
    print("=" * 70)

    tester = TRTInteractiveTester("complete_sequence_test")

    # Predefined sequence that covers full Stage 1
    sequence = [
        # 1.1 Goal clarification
        {
            "input": "Hi, I am feeling really anxious and overwhelmed",
            "expected_stage": "1.1_goal_and_vision",
            "expected_action": "goal clarification"
        },
        {
            "input": "I want to feel calm and peaceful instead of anxious",
            "expected_stage": "1.1_goal_and_vision",
            "expected_action": "vision building"
        },
        {
            "input": "Yes, that sounds exactly like what I want to be",
            "expected_stage": "1.2_problem_and_body",
            "expected_action": "advance to problem exploration"
        },
        # 1.2 Problem and body
        {
            "input": "Work deadlines make me panic and my heart races",
            "expected_stage": "1.2_problem_and_body",
            "expected_action": "body awareness inquiry"
        },
        {
            "input": "I can feel my heart racing right now just talking about it",
            "expected_stage": "1.2_problem_and_body",
            "expected_action": "pattern inquiry"
        },
        {
            "input": "It starts when I look at my calendar and see how much I have to do",
            "expected_stage": "1.3_readiness_assessment",
            "expected_action": "readiness assessment"
        },
        # 1.3 Readiness
        {
            "input": "I think I understand the pattern now and I'm ready to work on this",
            "expected_stage": "1.3_readiness_assessment",
            "expected_action": "ready for stage 2"
        }
    ]

    for i, step in enumerate(sequence, 1):
        print(f"\n🎯 SEQUENCE STEP {i}/{len(sequence)}")
        print(f"Expected: {step['expected_action']}")

        response = tester.process_input(step['input'])

        # Verify progression
        current_substate = tester.session_state.current_substate
        if step['expected_stage'] in current_substate:
            print(f"✅ PROGRESSION CORRECT: {current_substate}")
        else:
            print(f"❌ PROGRESSION ISSUE: Expected {step['expected_stage']}, got {current_substate}")

    # Final summary
    print(f"\n🎉 SEQUENCE TEST COMPLETE")
    summary = tester.get_session_summary()
    print(f"Final State: {summary['current_location']}")
    print(f"Total Turns: {summary['total_turns']}")

    # Save log
    log_file = tester.save_session_log("logs/complete_sequence_test.json")
    return tester, log_file

def test_spelling_correction_sequence():
    """Test sequence with multiple spelling errors"""

    print("🎭 SPELLING CORRECTION SEQUENCE TEST")
    print("=" * 70)

    tester = TRTInteractiveTester("spelling_test_sequence")

    # Sequence with spelling errors
    sequence = [
        "Hi, iwll feeling realy overwelmed and anixous about evrything",
        "I want to fel calm and peacful insteed of stresed all the tim",
        "Yes, that vision fils rite to me",
        "Work presure makes me panick and I get tigt chest feling",
        "I can fel that tightnes rite now when I think about it"
    ]

    for i, client_input in enumerate(sequence, 1):
        print(f"\n🔄 SPELLING TEST {i}/{len(sequence)}")
        response = tester.process_input(client_input)

    print(f"\n✅ SPELLING TEST COMPLETE")
    summary = tester.get_session_summary()
    print(f"Final State: {summary['current_location']}")

    log_file = tester.save_session_log("logs/spelling_correction_test.json")
    return tester, log_file

def test_error_handling():
    """Test various edge cases and error scenarios"""

    print("🎭 ERROR HANDLING TEST")
    print("=" * 70)

    tester = TRTInteractiveTester("error_handling_test")

    # Edge cases
    edge_cases = [
        "",  # Empty input
        "   ",  # Whitespace only
        "asdkjhasdkjh",  # Nonsense
        "I feel... um... I don't know how to explain it",  # Unclear
        "Everything is fine",  # Contradiction
        "Why are you asking me these questions?",  # Resistance
        "This isn't working for me"  # Negative feedback
    ]

    for i, client_input in enumerate(edge_cases, 1):
        if client_input.strip():  # Skip empty inputs for logging
            print(f"\n🧪 EDGE CASE {i}: '{client_input}'")
            try:
                response = tester.process_input(client_input)
                print(f"✅ Handled successfully")
            except Exception as e:
                print(f"❌ Error: {e}")

    log_file = tester.save_session_log("logs/error_handling_test.json")
    return tester, log_file

if __name__ == "__main__":
    print("🎮 BATCH TESTING SUITE")
    print("=" * 50)
    print("1. Complete Sequence Test")
    print("2. Spelling Correction Test")
    print("3. Error Handling Test")
    print("4. Run All Tests")

    choice = input("\nSelect test (1-4): ").strip()

    if choice == "1":
        test_complete_sequence()
    elif choice == "2":
        test_spelling_correction_sequence()
    elif choice == "3":
        test_error_handling()
    elif choice == "4":
        print("\n🔄 RUNNING ALL TESTS...")
        test_complete_sequence()
        test_spelling_correction_sequence()
        test_error_handling()
        print("\n✅ ALL TESTS COMPLETE - Check logs/ directory for detailed results")
    else:
        print("Invalid choice")