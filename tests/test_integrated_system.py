"""
Manual Testing Script for Integrated Dr. Q Enhanced System
Run this in a separate terminal to test all new features
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from improved_ollama_system import ImprovedOllamaTRTSystem
from session_state_manager import TRTSessionState
import signal
from datetime import datetime
import json


def run_manual_test_with_enhancements():
    """Run manual test session with all Dr. Q enhancements"""

    # Global flag for graceful shutdown
    interrupted = {'value': False}

    def signal_handler(sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n👋 Session interrupted by Ctrl+C.")
        interrupted['value'] = True

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 80)
    print("🎭 AI THERAPIST - ENHANCED WITH DR. Q RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("✅ ACTIVE ENHANCEMENTS:")
    print("  1. Language Techniques (tense shifting, feeling insertions)")
    print("  2. Engagement Tracking (intervention triggers)")
    print("  3. 'I Don't Know' Handling (vision language auto-offer)")
    print("  4. Psycho-Education (zebra-lion brain explanation)")
    print("  5. Alpha Sequence (down-regulation with checkpoints)")
    print()
    print("You type responses as the PATIENT.")
    print("AI responds as THERAPIST using Dr. Q's enhanced methodology.")
    print()
    print("Commands:")
    print("  - Type your response to continue")
    print("  - Type 'quit' to end")
    print("  - Type 'status' for progress")
    print("  - Type 'engagement' to see engagement summary")
    print("  - Press Ctrl+C to stop at any time")
    print()
    print("=" * 80)

    # Initialize
    print("\n🚀 Initializing Enhanced System...")
    trt_system = ImprovedOllamaTRTSystem()
    session_state = TRTSessionState("enhanced_manual_test")

    print("\n✅ Ready! Starting session...\n")
    print("=" * 80)
    print("\n🩺 THERAPIST: \"Hello! What brings you in today?\"\n")

    turn = 0

    while True:
        # Check if interrupted
        if interrupted['value']:
            break

        turn += 1
        print("=" * 80)
        print(f"TURN {turn}")
        print("=" * 80)

        try:
            patient_input = input("\n👤 YOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Session interrupted.")
            break

        # Check again after input
        if interrupted['value']:
            break

        if patient_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Ending session...")
            break

        if patient_input.lower() == 'status':
            print("\n📊 SESSION STATUS:")
            print(f"   Current State: {session_state.current_substate}")
            print(f"   Body Q's Asked: {session_state.body_questions_asked}/3")

            completion = session_state.stage_1_completion
            print(f"\n   Completion Progress:")
            print(f"     Goal Stated: {'✅' if completion['goal_stated'] else '❌'}")
            print(f"     Vision Accepted: {'✅' if completion['vision_accepted'] else '❌'}")
            print(f"     Psycho-Education: {'✅' if completion.get('psycho_education_provided', False) else '❌'}")
            print(f"     Problem Identified: {'✅' if completion['problem_identified'] else '❌'}")
            print(f"     Body Awareness: {'✅' if completion['body_awareness_present'] else '❌'}")
            print(f"     Present Moment: {'✅' if completion['present_moment_focus'] else '❌'}")
            print()
            turn -= 1
            continue

        if patient_input.lower() == 'engagement':
            print("\n📊 ENGAGEMENT SUMMARY:")
            engagement = trt_system.dialogue_agent.engagement_tracker.get_engagement_summary()
            print(f"   Total Turns: {engagement['total_turns']}")
            print(f"   Overall Engagement: {engagement['overall_engagement']}")
            print(f"   Confusion Instances: {engagement['confusion_instances']}")
            print(f"   Consecutive Minimal: {engagement['consecutive_minimal_responses']}")
            print(f"   Handoff Recommended: {engagement['handoff_recommended']}")
            print()
            turn -= 1
            continue

        if not patient_input:
            turn -= 1
            continue

        # Process
        print("\n🤔 Processing...", end='', flush=True)

        try:
            output = trt_system.process_client_input(patient_input, session_state)

            # Check if interrupted during processing
            if interrupted['value']:
                print("\n")
                break

            print(" Done!\n")

            # Display therapist response
            print(f"🩺 THERAPIST: \"{output['dialogue']['therapeutic_response']}\"\n")

            # Show technique used
            technique = output['dialogue'].get('technique_used', 'unknown')
            print(f"💡 [Technique: {technique}]")

            # Show if any special detections
            navigation = output['navigation']
            detections = []

            if navigation.get('self_harm_detected', {}).get('detected'):
                detections.append("🚨 Self-Harm")
            if navigation.get('thinking_mode_detected', {}).get('detected'):
                detections.append("🧠 Thinking Mode")
            if navigation.get('past_tense_detected', {}).get('detected'):
                detections.append("⏮️ Past Tense")
            if navigation.get('i_dont_know_detected', {}).get('detected'):
                detections.append("❓ I Don't Know")

            if detections:
                print(f"🔍 [Detections: {', '.join(detections)}]")

            # Show engagement level
            engagement_level = trt_system.dialogue_agent.engagement_tracker.engagement_history[-1]['assessment']['engagement_level'] if trt_system.dialogue_agent.engagement_tracker.engagement_history else 'unknown'
            engagement_emoji = {
                'high': '🟢',
                'medium': '🟡',
                'low': '🟠',
                'critical': '🔴'
            }.get(engagement_level, '⚪')

            print(f"{engagement_emoji} [Engagement: {engagement_level}]")

            # Show handoff warning if recommended
            if output['dialogue'].get('handoff_recommended', False):
                print("⚠️ [HANDOFF TO HUMAN RECOMMENDED]")

            # Show brief status
            print(f"📊 [State: {output['navigation']['current_substate']}, "
                  f"Time: {output['processing_time']:.1f}s]")
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted during processing.")
            break
        except Exception as e:
            print(f"\n\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
            turn -= 1
            continue

    # Summary
    print("\n" + "=" * 80)
    print("📋 SESSION SUMMARY")
    print("=" * 80)

    completion = session_state.stage_1_completion
    print(f"\n✅ COMPLETION STATUS:")
    print(f"   Goal Stated: {'✅' if completion['goal_stated'] else '❌'}")
    print(f"   Vision Accepted: {'✅' if completion['vision_accepted'] else '❌'}")
    print(f"   Psycho-Education Provided: {'✅' if completion.get('psycho_education_provided', False) else '❌'}")
    print(f"   Problem Identified: {'✅' if completion['problem_identified'] else '❌'}")
    print(f"   Body Awareness: {'✅' if completion['body_awareness_present'] else '❌'}")
    print(f"   Present Moment Focus: {'✅' if completion['present_moment_focus'] else '❌'}")

    print(f"\n📊 SESSION METRICS:")
    print(f"   Final State: {session_state.current_substate}")
    print(f"   Total Turns: {turn}")
    print(f"   Body Questions Asked: {session_state.body_questions_asked}")

    # Engagement summary
    engagement = trt_system.dialogue_agent.engagement_tracker.get_engagement_summary()
    print(f"\n👥 ENGAGEMENT SUMMARY:")
    print(f"   Overall: {engagement['overall_engagement']}")
    print(f"   High: {engagement['engagement_levels'].get('high', 0)}")
    print(f"   Medium: {engagement['engagement_levels'].get('medium', 0)}")
    print(f"   Low: {engagement['engagement_levels'].get('low', 0)}")
    print(f"   Critical: {engagement['engagement_levels'].get('critical', 0)}")
    print(f"   Confusion Instances: {engagement['confusion_instances']}")
    print(f"   Handoff Recommended: {'YES ⚠️' if engagement['handoff_recommended'] else 'No'}")

    # Save
    if turn > 0:
        log_file = f"logs/enhanced_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        session_log = {
            "session_id": session_state.session_id,
            "timestamp": datetime.now().isoformat(),
            "turns": len(session_state.conversation_history),
            "body_questions_asked": session_state.body_questions_asked,
            "final_state": session_state.current_substate,
            "completion": session_state.stage_1_completion,
            "engagement_summary": engagement,
            "conversation": session_state.conversation_history,
            "enhancements_active": {
                "language_techniques": True,
                "engagement_tracking": True,
                "vision_templates": True,
                "psycho_education": True,
                "alpha_sequence": True
            }
        }

        with open(log_file, 'w') as f:
            json.dump(session_log, f, indent=2)

        print(f"\n💾 Session saved to: {log_file}")

    print("\n" + "=" * 80)
    print("✅ SESSION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🔧 Starting Enhanced AI Therapist Manual Test...\n")
    run_manual_test_with_enhancements()
