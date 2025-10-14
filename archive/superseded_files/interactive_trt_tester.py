"""
Interactive TRT System Tester with Real-time Logging
Allows sequential queries with detailed step-by-step logging
"""

import json
import datetime
from integrated_trt_system import CompleteTRTSystem
from session_state_manager import TRTSessionState

class TRTInteractiveTester:
    """Interactive tester with comprehensive logging"""

    def __init__(self, session_name=None):
        if session_name is None:
            session_name = f"interactive_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.session_name = session_name
        self.trt_system = CompleteTRTSystem()
        self.session_state = TRTSessionState(session_name)
        self.conversation_log = []
        self.turn_number = 0

        print("🎭 TRT INTERACTIVE TESTER INITIALIZED")
        print("=" * 60)
        print(f"Session ID: {session_name}")
        print(f"Starting Substate: {self.session_state.current_substate}")
        print("=" * 60)

    def process_input(self, client_input):
        """Process client input with detailed logging"""

        self.turn_number += 1

        print(f"\n🔄 TURN {self.turn_number}")
        print("=" * 50)
        print(f"👤 CLIENT: \"{client_input}\"")

        # Process through system
        system_output = self.trt_system.process_client_input(client_input, self.session_state)

        # Extract components
        preprocessing = system_output["navigation"]["input_processing"]
        navigation = system_output["navigation"]
        dialogue = system_output["dialogue"]
        progress = system_output["session_progress"]

        # Real-time logging
        self._log_preprocessing(preprocessing)
        self._log_navigation(navigation)
        self._log_rag_retrieval(dialogue)
        self._log_response(dialogue)
        self._log_session_state(navigation, progress)

        # Store in conversation log
        turn_data = {
            "turn": self.turn_number,
            "timestamp": datetime.datetime.now().isoformat(),
            "client_input": client_input,
            "preprocessing": preprocessing,
            "navigation": navigation,
            "dialogue": dialogue,
            "progress": progress
        }
        self.conversation_log.append(turn_data)

        print("-" * 50)
        return dialogue["therapeutic_response"]

    def _log_preprocessing(self, preprocessing):
        """Log preprocessing details"""
        print("\n🔧 INPUT PREPROCESSING:")
        if preprocessing['spelling_corrections']:
            print("   Spelling Corrections:")
            for old, new in preprocessing['spelling_corrections']:
                print(f"     '{old}' → '{new}'")
            print(f"   Corrected: '{preprocessing['corrected_input']}'")
        else:
            print("   No spelling corrections needed")

        print(f"   Emotional State: {preprocessing['emotional_state']['primary_emotion']}")
        print(f"   Input Category: {preprocessing['input_category']}")

        # Show emotional details if detected
        if preprocessing['emotional_state']['categories']:
            print(f"   Emotional Categories: {preprocessing['emotional_state']['categories']}")
        if preprocessing['emotional_state']['intensity'] > 0:
            print(f"   Intensity Level: {preprocessing['emotional_state']['intensity']}/3")

    def _log_navigation(self, navigation):
        """Log master planning agent decisions"""
        print("\n🧠 MASTER PLANNING AGENT:")
        print(f"   Current Stage: {navigation['current_stage']}")
        print(f"   Current Substate: {navigation['current_substate']}")
        print(f"   Navigation Decision: {navigation['navigation_decision']}")
        print(f"   Situation Type: {navigation['situation_type']}")
        print(f"   TRT Technique: {navigation['rag_query']}")
        print(f"   Ready for Next: {navigation['ready_for_next']}")

        if navigation.get('advancement_blocked_by'):
            print(f"   🚫 Blocked By: {navigation['advancement_blocked_by']}")

        if navigation.get('recent_events'):
            print(f"   Recent Events: {navigation['recent_events']}")

        print(f"   Reasoning: {navigation['reasoning']}")

    def _log_rag_retrieval(self, dialogue):
        """Log RAG system retrieval"""
        print("\n🔍 RAG RETRIEVAL:")
        print(f"   Technique Query: {dialogue['technique_used']}")
        print(f"   Examples Retrieved: {dialogue['examples_used']}")
        if dialogue['rag_similarity_scores']:
            scores_str = [f'{s:.3f}' for s in dialogue['rag_similarity_scores']]
            print(f"   Similarity Scores: {scores_str}")

    def _log_response(self, dialogue):
        """Log final therapeutic response"""
        print("\n🩺 DR. Q RESPONSE:")
        print(f"   \"{dialogue['therapeutic_response']}\"")
        print(f"   Navigation Reasoning: {dialogue['navigation_reasoning']}")

    def _log_session_state(self, navigation, progress):
        """Log current session state"""
        print("\n📊 SESSION STATE:")
        completion = navigation['completion_status']

        print("   Stage 1.1 Completion:")
        print(f"     Goal Stated: {completion['goal_stated']}")
        print(f"     Vision Accepted: {completion['vision_accepted']}")

        if completion['problem_identified'] or completion['body_awareness_present']:
            print("   Stage 1.2 Completion:")
            print(f"     Problem Identified: {completion['problem_identified']}")
            print(f"     Body Awareness: {completion['body_awareness_present']}")

        if completion.get('ready_for_stage_2'):
            print("   Stage 1.3 Completion:")
            print(f"     Ready for Stage 2: {completion['ready_for_stage_2']}")

        print(f"   Current Location: {progress['current_location']}")
        print(f"   Total Turns: {progress['turns_completed']}")

    def get_session_summary(self):
        """Get complete session summary"""
        progress = self.session_state.get_progress_summary()
        return {
            "session_id": self.session_name,
            "total_turns": self.turn_number,
            "current_location": progress['current_location'],
            "stage_1_progress": progress['stage_1_progress'],
            "conversation_log": self.conversation_log
        }

    def save_session_log(self, filename=None):
        """Save session log to file"""
        if filename is None:
            filename = f"logs/{self.session_name}_log.json"

        import os
        os.makedirs("logs", exist_ok=True)

        session_data = self.get_session_summary()

        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        print(f"\n💾 Session log saved to: {filename}")
        return filename

    def show_progression_guide(self):
        """Show what responses are expected at each stage"""
        current_substate = self.session_state.current_substate
        completion = self.session_state.stage_1_completion

        print("\n📋 PROGRESSION GUIDE:")
        print("-" * 30)

        if current_substate == "1.1_goal_and_vision":
            if not completion['goal_stated']:
                print("🎯 CURRENT NEED: Goal clarification")
                print("Expected client responses:")
                print("  • 'I want to feel calm instead of anxious'")
                print("  • 'I want to stop feeling sad'")
                print("  • 'I want to be more confident'")
                print("Next: System will build vision using Generic Outcome State")

            elif not completion['vision_accepted']:
                print("🎯 CURRENT NEED: Vision acceptance")
                print("Expected client responses:")
                print("  • 'Yes, that sounds exactly what I want'")
                print("  • 'That vision feels right to me'")
                print("  • 'Yes, I want to be that way'")
                print("Next: Advance to 1.2 Problem and Body")

        elif current_substate == "1.2_problem_and_body":
            if not completion['problem_identified']:
                print("🎯 CURRENT NEED: Problem identification")
                print("Expected client responses:")
                print("  • 'Work stress makes me anxious'")
                print("  • 'I get triggered by loud noises'")
                print("  • 'Relationships make me feel overwhelmed'")
                print("Next: Body awareness inquiry")

            elif not completion['body_awareness_present']:
                print("🎯 CURRENT NEED: Body awareness")
                print("Expected client responses:")
                print("  • 'I feel tightness in my chest'")
                print("  • 'My stomach gets knotted up'")
                print("  • 'I notice tension in my shoulders'")
                print("Next: Pattern exploration with 'how do you know' technique")

        elif current_substate == "1.3_readiness_assessment":
            print("🎯 CURRENT NEED: Readiness assessment")
            print("Expected client responses:")
            print("  • 'I think I understand the pattern now'")
            print("  • 'I'm ready to work on changing this'")
            print("  • 'Yes, I feel ready to move forward'")
            print("Next: Ready for Stage 2 intervention work")

def interactive_session():
    """Run interactive testing session"""
    tester = TRTInteractiveTester()

    print("\n🎮 INTERACTIVE MODE STARTED")
    print("Commands:")
    print("  • Type client responses to test the system")
    print("  • Type 'guide' to see progression expectations")
    print("  • Type 'summary' to see session summary")
    print("  • Type 'save' to save session log")
    print("  • Type 'quit' to exit")
    print("\n" + "="*60)

    while True:
        try:
            user_input = input("\n👤 Enter client response: ").strip()

            if user_input.lower() == 'quit':
                print("\n👋 Session ended")
                break
            elif user_input.lower() == 'guide':
                tester.show_progression_guide()
                continue
            elif user_input.lower() == 'summary':
                summary = tester.get_session_summary()
                print(f"\n📊 SESSION SUMMARY:")
                print(f"Turns: {summary['total_turns']}")
                print(f"Location: {summary['current_location']}")
                continue
            elif user_input.lower() == 'save':
                tester.save_session_log()
                continue
            elif not user_input:
                print("Please enter a client response or command")
                continue

            # Process the input
            response = tester.process_input(user_input)

        except KeyboardInterrupt:
            print("\n👋 Session interrupted")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

    # Auto-save on exit
    tester.save_session_log()
    return tester

if __name__ == "__main__":
    interactive_session()