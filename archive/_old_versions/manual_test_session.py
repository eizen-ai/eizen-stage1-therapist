"""
Manual Test Session - You type as the patient
Interactive therapy session where you control the client responses
"""

import json
from datetime import datetime
from session_state_manager import TRTSessionState
from ollama_trt_system import OllamaTRTSystem

def run_manual_test_session():
    """Run a manual test session where you type as the patient"""

    print("=" * 80)
    print("🎭 AI THERAPIST - MANUAL TEST SESSION")
    print("=" * 80)
    print()
    print("You will type responses as the PATIENT.")
    print("The AI will respond as the THERAPIST using TRT methodology.")
    print()
    print("Commands:")
    print("  - Type your response normally to continue")
    print("  - Type 'quit' or 'exit' to end session")
    print("  - Type 'status' to see progress")
    print("  - Type 'help' for tips")
    print()
    print("=" * 80)

    # Initialize system
    print("\n🚀 Initializing AI Therapist System...")
    trt_system = OllamaTRTSystem()
    session_state = TRTSessionState("manual_test_session")

    print("\n✅ System ready! Starting therapy session...\n")
    print("=" * 80)

    # Optional: System starts with greeting
    print("\n🩺 THERAPIST: \"Hello! I'm here to help you today. What brings you in?\"")
    print()

    turn = 0

    while True:
        turn += 1
        print("=" * 80)
        print(f"TURN {turn}")
        print("=" * 80)

        # Get patient input
        try:
            patient_input = input("\n👤 YOU (as patient): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Session interrupted. Saving and exiting...")
            break

        # Handle commands
        if patient_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Ending session...")
            break

        if patient_input.lower() == 'status':
            print("\n📊 SESSION STATUS:")
            print(f"   Current State: {session_state.current_substate}")
            print(f"   Total Turns: {turn - 1}")
            print(f"\n   Stage 1 Completion:")
            for key, value in session_state.stage_1_completion.items():
                status = "✅" if value else "❌"
                print(f"      {status} {key}")
            print()
            turn -= 1  # Don't count status check as a turn
            continue

        if patient_input.lower() == 'help':
            print("\n💡 TIPS FOR TESTING:")
            print("   - Express emotions naturally (stressed, anxious, sad)")
            print("   - Mention body sensations (chest tight, shoulders tense)")
            print("   - State goals (want to feel calm, peaceful)")
            print("   - Describe problems (work pressure, relationship issues)")
            print("   - Share patterns (happens when I see email, when I wake up)")
            print()
            turn -= 1  # Don't count help as a turn
            continue

        if not patient_input:
            print("   (Please type something or 'quit' to exit)")
            turn -= 1
            continue

        # Process through AI therapist
        print("\n🤔 AI analyzing...", end='', flush=True)

        try:
            system_output = trt_system.process_client_input(patient_input, session_state)
            print(" Done!")

            # Show therapist response
            print(f"\n🩺 THERAPIST: \"{system_output['dialogue']['therapeutic_response']}\"")

            # Show brief internal state
            print(f"\n📊 [Internal: State={system_output['navigation']['current_substate']}, "
                  f"Confidence={system_output['system_status']['master_confidence']:.2f}, "
                  f"Time={system_output['processing_time']:.1f}s]")

            # Show progress indicators
            completion = session_state.stage_1_completion
            completed_count = sum(1 for v in completion.values() if v)
            print(f"   [Progress: {completed_count}/{len(completion)} criteria met]")

            # Show recently completed checkpoints
            recent_completions = [k for k, v in completion.items() if v]
            if recent_completions and turn > 1:
                last_3 = recent_completions[-3:]
                if last_3:
                    print(f"   [Recent ✅: {', '.join(last_3)}]")

            print()

        except Exception as e:
            print(f"\n\n❌ Error occurred: {e}")
            print("Session will continue...\n")
            turn -= 1
            continue

    # Session summary
    print("\n" + "=" * 80)
    print("📋 SESSION SUMMARY")
    print("=" * 80)
    print(f"\n✅ Final State: {session_state.current_substate}")
    print(f"✅ Total Turns: {turn}")
    print(f"\n✅ Stage 1 Completion:")

    completion = session_state.stage_1_completion
    completed = [k for k, v in completion.items() if v]
    incomplete = [k for k, v in completion.items() if not v]

    if completed:
        print("\n   Completed:")
        for item in completed:
            print(f"      ✅ {item}")

    if incomplete:
        print("\n   Still Needed:")
        for item in incomplete:
            print(f"      ⏳ {item}")

    # Save session log
    if turn > 0 and session_state.conversation_history:
        session_log = {
            "session_id": session_state.session_id,
            "timestamp": datetime.now().isoformat(),
            "turns": len(session_state.conversation_history),
            "final_state": session_state.current_substate,
            "completion": session_state.stage_1_completion,
            "conversation": session_state.conversation_history
        }

        log_filename = f"logs/manual_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_filename, 'w') as f:
            json.dump(session_log, f, indent=2)

        print(f"\n💾 Session saved to: {log_filename}")

    print("\n" + "=" * 80)
    print("🎉 SESSION COMPLETE - Thank you for testing!")
    print("=" * 80)

if __name__ == "__main__":
    run_manual_test_session()
