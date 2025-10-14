"""
Demo Conversation with Ollama TRT System
Simulates a realistic therapy session
"""

import json
from datetime import datetime
from session_state_manager import TRTSessionState
from ollama_trt_system import OllamaTRTSystem

def run_demo_conversation():
    """Run a realistic demo therapy conversation"""

    print("=" * 80)
    print("🎭 AI THERAPIST DEMO - REALISTIC THERAPY SESSION")
    print("=" * 80)
    print()

    # Initialize system
    print("Initializing system...\n")
    trt_system = OllamaTRTSystem()
    session_state = TRTSessionState("demo_session")

    # Realistic conversation
    conversations = [
        {
            "client": "Hi, I've been feeling really overwhelmed with work lately",
            "pause": True
        },
        {
            "client": "I guess I want to feel more relaxed and in control",
            "pause": True
        },
        {
            "client": "Yes, that sounds good. I want to feel calm",
            "pause": True
        },
        {
            "client": "It's mainly the constant emails and meetings. I get anxious",
            "pause": True
        },
        {
            "client": "I feel it in my shoulders and neck. They're really tense right now",
            "pause": True
        },
        {
            "client": "It happens every morning when I open my inbox and see all the unread messages",
            "pause": True
        },
        {
            "client": "I think so. It's the feeling of falling behind",
            "pause": True
        },
        {
            "client": "No, I think that covers it",
            "pause": True
        },
    ]

    turn = 0
    for conv in conversations:
        turn += 1
        print("\n" + "=" * 70)
        print(f"TURN {turn}")
        print("=" * 70)

        # Client speaks
        print(f"\n👤 CLIENT: \"{conv['client']}\"")
        print()

        # Process
        print("🤔 AI analyzing...")
        system_output = trt_system.process_client_input(conv['client'], session_state)

        # Therapist responds
        print(f"\n🩺 THERAPIST: \"{system_output['dialogue']['therapeutic_response']}\"")

        # Show internal state
        print(f"\n📊 Internal State:")
        print(f"   Substate: {system_output['navigation']['current_substate']}")
        print(f"   Decision: {system_output['navigation']['navigation_decision']}")
        print(f"   Ollama Confidence: {system_output['system_status']['master_confidence']:.2f}")
        print(f"   Processing Time: {system_output['processing_time']:.2f}s")

        # Show progress
        completion = session_state.stage_1_completion
        completed = [k for k, v in completion.items() if v]
        if completed:
            print(f"\n✅ Checkpoints Completed: {', '.join(completed)}")

    # Final summary
    print("\n" + "=" * 80)
    print("📋 SESSION SUMMARY")
    print("=" * 80)
    print(f"\n✅ Final State: {session_state.current_substate}")
    print(f"\n✅ Total Turns: {turn}")
    print(f"\n✅ Stage 1 Progress:")
    for key, value in session_state.stage_1_completion.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}")

    # Save log
    session_log = {
        "session_id": session_state.session_id,
        "timestamp": datetime.now().isoformat(),
        "turns": len(session_state.conversation_history),
        "final_state": session_state.current_substate,
        "completion": session_state.stage_1_completion,
        "conversation": session_state.conversation_history
    }

    log_filename = f"logs/demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w') as f:
        json.dump(session_log, f, indent=2)

    print(f"\n💾 Session saved to: {log_filename}")
    print("\n" + "=" * 80)
    print("🎉 DEMO COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    run_demo_conversation()
