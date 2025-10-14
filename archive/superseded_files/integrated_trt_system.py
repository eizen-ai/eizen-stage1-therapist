"""
Complete TRT AI Therapy System with Sequential Progression
Integrates Master Planning Agent + Session State + RAG + Dialogue Generation
"""

import json
from session_state_manager import TRTSessionState
from embedding_and_retrieval_setup import TRTRAGSystem
from input_preprocessing import InputPreprocessor

class MasterPlanningAgent:
    """Master Planning Agent with proper completion tracking"""

    def __init__(self):
        # Load navigation rules
        with open('core_system/simplified_navigation.json', 'r') as f:
            self.navigation = json.load(f)

        with open('core_system/input_classification_patterns.json', 'r') as f:
            self.patterns = json.load(f)

        # Initialize input preprocessor
        self.preprocessor = InputPreprocessor()

    def make_navigation_decision(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Make navigation decision based on completion status and client input"""

        # Preprocess input for spelling errors and categorization
        processed_input = self.preprocessor.preprocess_input(client_input)
        corrected_input = processed_input['corrected_input']

        # Update session state based on corrected input
        completion_events = session_state.update_completion_status(corrected_input, processed_input)

        # Check if ready to advance
        is_ready, next_substate = session_state.check_substate_completion()

        # Advance if criteria met
        if is_ready:
            session_state.advance_substate(next_substate)

        # Get current navigation context
        nav_context = session_state.get_current_navigation_context()

        # Make decision based on current substate and completion status
        navigation_decision = self._determine_navigation_action(corrected_input, session_state, completion_events)

        # Add preprocessing information
        navigation_decision['input_processing'] = {
            'original_input': client_input,
            'corrected_input': corrected_input,
            'emotional_state': processed_input['emotional_state'],
            'input_category': processed_input['input_category'],
            'spelling_corrections': processed_input['spelling_corrections']
        }

        return navigation_decision

    def _determine_navigation_action(self, client_input: str, session_state: TRTSessionState, events: list) -> dict:
        """Determine specific navigation action based on current state"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate
        client_lower = client_input.lower()

        if substate == "1.1_goal_and_vision":
            if not completion["goal_stated"]:
                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": substate,
                    "navigation_decision": "clarify_goal",
                    "situation_type": "goal_needs_clarification",
                    "rag_query": "dr_q_goal_clarification",
                    "completion_status": completion,
                    "ready_for_next": False,
                    "advancement_blocked_by": ["goal_not_stated"],
                    "reasoning": "Goal not yet stated, need Dr. Q's triple question approach",
                    "recent_events": events
                }

            elif completion["goal_stated"] and not completion["vision_accepted"]:
                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": substate,
                    "navigation_decision": "build_vision",
                    "situation_type": "goal_stated_needs_vision",
                    "rag_query": "dr_q_future_self_vision_building",
                    "completion_status": completion,
                    "ready_for_next": False,
                    "advancement_blocked_by": ["vision_not_accepted"],
                    "reasoning": "Goal stated, now build detailed future self vision",
                    "recent_events": events
                }

        elif substate == "1.2_problem_and_body":
            if not completion["problem_identified"]:
                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": substate,
                    "navigation_decision": "explore_problem",
                    "situation_type": "problem_needs_exploration",
                    "rag_query": "dr_q_problem_construction",
                    "completion_status": completion,
                    "ready_for_next": False,
                    "advancement_blocked_by": ["problem_not_identified"],
                    "reasoning": "Need to understand specific problem patterns",
                    "recent_events": events
                }

            elif not completion["body_awareness_present"]:
                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": substate,
                    "navigation_decision": "body_awareness_inquiry",
                    "situation_type": "body_symptoms_exploration",
                    "rag_query": "dr_q_body_symptom_present_moment_inquiry",
                    "completion_status": completion,
                    "ready_for_next": False,
                    "advancement_blocked_by": ["body_awareness_missing"],
                    "reasoning": "Build present moment somatic awareness",
                    "recent_events": events
                }

            else:
                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": substate,
                    "navigation_decision": "pattern_inquiry",
                    "situation_type": "explore_trigger_pattern",
                    "rag_query": "dr_q_how_do_you_know_technique",
                    "completion_status": completion,
                    "ready_for_next": False,
                    "advancement_blocked_by": ["present_moment_focus_needed"],
                    "reasoning": "Explore emotional/physical patterns with how-do-you-know inquiry",
                    "recent_events": events
                }

        elif substate == "1.3_readiness_assessment":
            return {
                "current_stage": session_state.current_stage,
                "current_substate": substate,
                "navigation_decision": "assess_readiness",
                "situation_type": "readiness_for_stage_2",
                "rag_query": "dr_q_transition_to_intervention",
                "completion_status": completion,
                "ready_for_next": completion["ready_for_stage_2"],
                "advancement_blocked_by": [] if completion["ready_for_stage_2"] else ["pattern_understanding_needed"],
                "reasoning": "Assess readiness for Stage 2 intervention work",
                "recent_events": events
            }

        # Default fallback
        return {
            "current_stage": session_state.current_stage,
            "current_substate": substate,
            "navigation_decision": "general_inquiry",
            "situation_type": "general_therapeutic_inquiry",
            "rag_query": "general_dr_q_approach",
            "completion_status": completion,
            "ready_for_next": False,
            "reasoning": "Continue general therapeutic inquiry",
            "recent_events": events
        }

class DialogueAgent:
    """Dialogue Agent that uses RAG examples to generate Dr. Q style responses"""

    def __init__(self, rag_system: TRTRAGSystem):
        self.rag_system = rag_system

    def generate_response(self, client_input: str, navigation_output: dict, session_state: TRTSessionState) -> dict:
        """Generate therapeutic response using RAG examples"""

        # Get RAG examples
        rag_examples = self.rag_system.get_few_shot_examples(
            navigation_output,
            client_input,
            max_examples=2
        )

        # Generate response based on navigation decision and Dr. Q style
        response = self._craft_response(client_input, navigation_output, rag_examples, session_state)

        return {
            "therapeutic_response": response,
            "technique_used": navigation_output["rag_query"],
            "examples_used": len(rag_examples),
            "rag_similarity_scores": [ex["similarity_score"] for ex in rag_examples],
            "navigation_reasoning": navigation_output["reasoning"]
        }

    def _craft_response(self, client_input: str, navigation_output: dict, rag_examples: list, session_state: TRTSessionState) -> str:
        """Craft response in Dr. Q's authentic TRT style using PDF patterns"""

        decision = navigation_output["navigation_decision"]
        situation = navigation_output["situation_type"]
        client_lower = client_input.lower()

        # Use authentic TRT language patterns from the PDF
        if decision == "clarify_goal":
            # Acknowledge first with present-moment awareness, then use Dr. Q's exact questions
            acknowledgment = ""

            if any(word in client_lower for word in ["low", "down", "sad", "depressed"]):
                acknowledgment = "I hear that you're feeling low right now. "
            elif any(word in client_lower for word in ["stressed", "overwhelmed", "anxious"]):
                acknowledgment = "I can hear the stress and overwhelm you're experiencing. "
            elif any(word in client_lower for word in ["difficult", "hard", "tough"]):
                acknowledgment = "It sounds like things have been really difficult. "
            elif any(word in client_lower for word in ["bad", "awful", "terrible"]):
                acknowledgment = "I hear you're going through a really tough time. "

            # Use Dr. Q's exact goal clarification questions from PDF
            return acknowledgment + "What do you want our time to get accomplished? What do we want to get better for you?"

        elif decision == "build_vision":
            # Check if we've been repeating the same vision response
            vision_response = "I'm seeing you who used to have that problem now wouldn't be able to get it. The you I'm seeing is free, emotionally present, connecting to what is happening, dealing with things with more flexibility and experiencing more joy. Does that vision feel right to you?"

            # If we've already presented the vision multiple times, adapt
            if hasattr(session_state, 'response_history') and len(session_state.response_history) > 0:
                recent_responses = session_state.response_history[-2:] if len(session_state.response_history) >= 2 else session_state.response_history

                # If we've been asking the same vision question, try different approaches
                if any("vision feel right" in resp for resp in recent_responses):
                    # Client is continuing to share feelings - acknowledge and move forward
                    if any(word in client_lower for word in ["feel", "chest", "heavy", "sad", "better"]):
                        return "What's happening now? How's your body feeling as you're sharing this with me?"
                    # Client seems stuck - try different vision approach
                    else:
                        return "I'm hearing you want to feel different. Help me understand what's been making it hard for you to feel that way?"

            return vision_response

        elif decision == "explore_problem":
            # Handle positive responses differently
            if any(word in client_lower for word in ["better", "good", "fine", "okay", "improved"]):
                return "That's good to hear. What's different now? How do you know you're feeling better?"

            # Check for repetitive responses and vary approach
            if hasattr(session_state, 'response_history') and len(session_state.response_history) > 0:
                recent_responses = session_state.response_history[-3:]  # Check last 3 responses

                # If we've been asking body awareness questions, vary the approach
                if any("what do you notice in your body" in resp.lower() for resp in recent_responses):
                    if any(word in client_lower for word in ["chest", "heavy", "tight"]):
                        return "How do you know when that feeling starts? What is it that lets you know it's beginning?"
                    else:
                        return "What made that disturbing for you? Help me understand what's happening."

                # If we've been asking the same problem question, switch to body awareness
                elif any("what's been making it hard" in resp.lower() for resp in recent_responses):
                    if any(word in client_lower for word in ["chest", "heavy", "tight", "feel", "body"]):
                        return "And even as you're talking about that right now, what do you notice in your body? What's that feeling like?"
                    else:
                        return "What made that disturbing for you? Help me understand what's happening."

            # Default problem exploration
            return "What do you think would be useful for me to know to better understand? Help me understand what's been making it hard for you to feel that way."

        elif decision == "body_awareness_inquiry":
            # Keep focus on present moment - key TRT principle
            return "What's happening now? How's your body feeling right now as you're talking about that?"

        elif decision == "pattern_inquiry":
            # Use Dr. Q's "How do you know?" technique from PDF
            return "How do you know when that feeling starts? What is it that lets you know it's beginning?"

        elif decision == "assess_readiness":
            # Check for understanding before moving forward
            return "From what you've said so far, what haven't I understood? Is there more I should know before beginning to assist you with this?"

        else:
            # Use present-moment focus and clarifying questions (avoid curiosity questions)
            if rag_examples:
                return f"What else would be useful for me to know to really understand? {rag_examples[0]['doctor_example'].split('.')[0]}."
            return "What made that disturbing for you?"

class CompleteTRTSystem:
    """Complete integrated TRT therapy system with authentic Dr. Q methodology"""

    def __init__(self):
        # Initialize components with input preprocessing
        self.rag_system = TRTRAGSystem()
        self.rag_system.load_index("data/embeddings/trt_rag_index.faiss",
                                  "data/embeddings/trt_rag_metadata.json")

        self.master_agent = MasterPlanningAgent()
        self.dialogue_agent = DialogueAgent(self.rag_system)
        self.preprocessor = InputPreprocessor()

    def process_client_input(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Process client input through complete TRT system"""

        # Step 1: Master Planning Agent
        navigation_output = self.master_agent.make_navigation_decision(client_input, session_state)

        # Step 2: RAG + Dialogue Agent
        dialogue_output = self.dialogue_agent.generate_response(client_input, navigation_output, session_state)

        # Step 3: Update session history
        session_state.add_exchange(
            client_input=client_input,
            therapist_response=dialogue_output["therapeutic_response"],
            navigation_output=navigation_output
        )

        # Return complete system output
        return {
            "navigation": navigation_output,
            "dialogue": dialogue_output,
            "session_progress": session_state.get_progress_summary()
        }

def run_realistic_session_test():
    """Test complete system with realistic conversation flow"""

    print("🎭 COMPLETE TRT SYSTEM - REALISTIC SESSION TEST")
    print("=" * 70)

    # Initialize system
    trt_system = CompleteTRTSystem()
    session_state = TRTSessionState("realistic_test_session")

    # Realistic conversation sequence
    conversation = [
        "I've been feeling really stressed lately and I don't know what to do about it.",
        "I want to feel calm and peaceful instead of anxious all the time.",
        "Yes, that sounds exactly like what I want - to be grounded and not overwhelmed.",
        "It's mainly work pressure. My boss keeps giving me impossible deadlines and I get this tight feeling in my chest.",
        "Yeah, I can feel that tightness right now just talking about it. It's like a heavy pressure.",
        "It usually starts when I look at my calendar in the morning and see how much I have to do. Then I start thinking 'what if I don't finish in time' and the chest pressure begins.",
        "I think I understand the pattern now. I'm ready to work on changing this."
    ]

    for turn, client_input in enumerate(conversation, 1):
        print(f"🔄 TURN {turn}")
        print("=" * 50)
        print(f"👤 CLIENT: \"{client_input}\"")
        print()

        # Process through complete system
        system_output = trt_system.process_client_input(client_input, session_state)

        # Show system components
        nav = system_output["navigation"]
        dialogue = system_output["dialogue"]
        progress = system_output["session_progress"]

        print("🧠 MASTER PLANNING:")
        print(f"   Substate: {nav['current_substate']}")
        print(f"   Decision: {nav['navigation_decision']}")
        print(f"   Blocked by: {nav.get('advancement_blocked_by', [])}")
        if nav.get('recent_events'):
            print(f"   Recent events: {nav['recent_events']}")
        print()

        print("🔍 RAG + DIALOGUE:")
        print(f"   Technique: {dialogue['technique_used']}")
        print(f"   Examples used: {dialogue['examples_used']} (similarity: {[f'{s:.3f}' for s in dialogue['rag_similarity_scores']]})")
        print()

        print(f"🩺 THERAPIST: \"{dialogue['therapeutic_response']}\"")
        print()

        print("📊 SESSION PROGRESS:")
        for substate, criteria in progress["stage_1_progress"].items():
            print(f"   {substate}: {criteria}")
        print()

        print("=" * 70)
        print()

    print("🎉 COMPLETE SESSION TEST FINISHED")
    print(f"Final substate: {session_state.current_substate}")
    print(f"Total turns: {len(session_state.conversation_history)}")

if __name__ == "__main__":
    run_realistic_session_test()