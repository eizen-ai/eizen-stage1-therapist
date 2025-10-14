"""
Lightweight LLM-Based TRT System
Uses smaller models for demonstration and testing purposes
"""

import json
import time
from datetime import datetime
from session_state_manager import TRTSessionState
from embedding_and_retrieval_setup import TRTRAGSystem
from input_preprocessing import InputPreprocessor

class LightweightLLMMasterAgent:
    """Lightweight Master Planning Agent with simulated LLM reasoning"""

    def __init__(self):
        # Load navigation rules
        with open('core_system/simplified_navigation.json', 'r') as f:
            self.navigation = json.load(f)

        with open('core_system/input_classification_patterns.json', 'r') as f:
            self.patterns = json.load(f)

        self.preprocessor = InputPreprocessor()

    def make_navigation_decision(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Make navigation decision with enhanced reasoning"""

        # Preprocess input
        processed_input = self.preprocessor.preprocess_input(client_input)
        corrected_input = processed_input['corrected_input']

        # Update session state
        completion_events = session_state.update_completion_status(corrected_input, processed_input)

        # Check advancement
        is_ready, next_substate = session_state.check_substate_completion()
        if is_ready:
            session_state.advance_substate(next_substate)

        # Enhanced reasoning (simulated LLM analysis)
        decision = self._enhanced_navigation_reasoning(
            corrected_input, session_state, completion_events, processed_input
        )

        # Add preprocessing info
        decision['input_processing'] = {
            'original_input': client_input,
            'corrected_input': corrected_input,
            'emotional_state': processed_input['emotional_state'],
            'input_category': processed_input['input_category'],
            'spelling_corrections': processed_input['spelling_corrections']
        }

        return decision

    def _enhanced_navigation_reasoning(self, client_input: str, session_state: TRTSessionState,
                                     events: list, processed_input: dict) -> dict:
        """Enhanced reasoning logic (simulates LLM decision making)"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate
        client_lower = client_input.lower()
        emotional_state = processed_input.get('emotional_state', 'neutral')

        # Enhanced reasoning based on multiple factors
        reasoning_factors = {
            'emotional_intensity': self._assess_emotional_intensity(client_input, emotional_state),
            'body_awareness_present': any(word in client_lower for word in
                ['chest', 'body', 'feel', 'heavy', 'tight', 'pressure', 'sensation']),
            'resistance_indicators': any(word in client_lower for word in
                ['don\'t', 'can\'t', 'won\'t', 'not', 'never', 'stop', 'quit']),
            'positive_indicators': any(word in client_lower for word in
                ['better', 'good', 'great', 'yes', 'right', 'exactly', 'helpful']),
            'confusion_indicators': any(phrase in client_lower for phrase in
                ['don\'t understand', 'confused', 'what do you mean', 'explain']),
            'goal_language': any(word in client_lower for word in
                ['want', 'need', 'goal', 'hope', 'wish', 'would like'])
        }

        # Generate enhanced reasoning based on factors
        reasoning = self._generate_contextual_reasoning(
            substate, completion, reasoning_factors, events, client_input
        )

        # Make decision based on enhanced analysis
        if substate == "1.1_goal_and_vision":
            return self._handle_goal_vision_substate(
                completion, reasoning_factors, events, session_state, reasoning
            )
        elif substate == "1.2_problem_and_body":
            return self._handle_problem_body_substate(
                completion, reasoning_factors, events, session_state, reasoning
            )
        elif substate == "1.3_readiness_assessment":
            return self._handle_readiness_substate(
                completion, reasoning_factors, events, session_state, reasoning
            )
        else:
            return self._handle_general_substate(
                completion, reasoning_factors, events, session_state, reasoning
            )

    def _assess_emotional_intensity(self, client_input: str, emotional_state: str) -> str:
        """Assess emotional intensity from input"""
        high_intensity_words = ['extremely', 'very', 'really', 'so', 'completely', 'totally']
        client_lower = client_input.lower()

        if any(word in client_lower for word in high_intensity_words):
            return 'high'
        elif emotional_state != 'neutral':
            return 'moderate'
        else:
            return 'low'

    def _generate_contextual_reasoning(self, substate: str, completion: dict,
                                     factors: dict, events: list, client_input: str) -> str:
        """Generate detailed contextual reasoning"""

        reasoning_parts = []

        # Analyze current state
        reasoning_parts.append(f"Client is in {substate}")

        # Analyze emotional factors
        if factors['emotional_intensity'] == 'high':
            reasoning_parts.append("High emotional intensity detected - prioritize validation")
        elif factors['body_awareness_present']:
            reasoning_parts.append("Body awareness present - excellent opportunity for somatic focus")

        # Analyze resistance/engagement
        if factors['resistance_indicators']:
            reasoning_parts.append("Resistance indicators present - use gentle, non-confrontational approach")
        elif factors['positive_indicators']:
            reasoning_parts.append("Positive engagement - acknowledge and build on this")

        # Analyze goal clarification
        if not completion.get('goal_stated', False) and factors['goal_language']:
            reasoning_parts.append("Goal language detected but not yet clearly stated")

        # Analyze recent events
        if 'vision_accepted_implicit' in events:
            reasoning_parts.append("Implicit vision acceptance through emotional sharing")

        return ". ".join(reasoning_parts)

    def _handle_goal_vision_substate(self, completion: dict, factors: dict, events: list,
                                   session_state: TRTSessionState, reasoning: str) -> dict:
        """Handle 1.1 goal and vision substate with enhanced reasoning"""

        if not completion["goal_stated"]:
            if factors['confusion_indicators']:
                decision = "clarify_goal"
                situation = "goal_needs_clarification_gentle"
                blocked_by = ["goal_not_stated", "client_confusion"]
            elif factors['resistance_indicators']:
                decision = "clarify_goal"
                situation = "goal_needs_clarification_resistance"
                blocked_by = ["goal_not_stated", "client_resistance"]
            else:
                decision = "clarify_goal"
                situation = "goal_needs_clarification"
                blocked_by = ["goal_not_stated"]

            return {
                "current_stage": session_state.current_stage,
                "current_substate": session_state.current_substate,
                "navigation_decision": decision,
                "situation_type": situation,
                "rag_query": "dr_q_goal_clarification",
                "completion_status": completion,
                "ready_for_next": False,
                "advancement_blocked_by": blocked_by,
                "reasoning": reasoning,
                "recent_events": events,
                "enhanced_reasoning": True,
                "reasoning_factors": factors
            }

        elif completion["goal_stated"] and not completion["vision_accepted"]:
            if factors['positive_indicators']:
                # Check if this is implicit acceptance
                if 'vision_accepted_implicit' in events:
                    decision = "explore_problem"
                    situation = "vision_accepted_explore_problem"
                    blocked_by = []
                else:
                    decision = "build_vision"
                    situation = "goal_stated_needs_vision_positive"
                    blocked_by = ["vision_not_accepted"]
            else:
                decision = "build_vision"
                situation = "goal_stated_needs_vision"
                blocked_by = ["vision_not_accepted"]

            return {
                "current_stage": session_state.current_stage,
                "current_substate": session_state.current_substate,
                "navigation_decision": decision,
                "situation_type": situation,
                "rag_query": "dr_q_future_self_vision_building",
                "completion_status": completion,
                "ready_for_next": False,
                "advancement_blocked_by": blocked_by,
                "reasoning": reasoning,
                "recent_events": events,
                "enhanced_reasoning": True,
                "reasoning_factors": factors
            }

    def _handle_problem_body_substate(self, completion: dict, factors: dict, events: list,
                                    session_state: TRTSessionState, reasoning: str) -> dict:
        """Handle 1.2 problem and body substate"""

        if factors['body_awareness_present']:
            decision = "body_awareness_inquiry"
            situation = "body_symptoms_exploration"
            rag_query = "dr_q_body_symptom_present_moment_inquiry"
        elif factors['positive_indicators']:
            decision = "explore_problem"
            situation = "positive_response_exploration"
            rag_query = "dr_q_problem_construction"
        elif not completion.get("problem_identified", False):
            decision = "explore_problem"
            situation = "problem_needs_exploration"
            rag_query = "dr_q_problem_construction"
        else:
            decision = "pattern_inquiry"
            situation = "explore_trigger_pattern"
            rag_query = "dr_q_how_do_you_know_technique"

        return {
            "current_stage": session_state.current_stage,
            "current_substate": session_state.current_substate,
            "navigation_decision": decision,
            "situation_type": situation,
            "rag_query": rag_query,
            "completion_status": completion,
            "ready_for_next": False,
            "advancement_blocked_by": ["present_moment_focus_needed"],
            "reasoning": reasoning,
            "recent_events": events,
            "enhanced_reasoning": True,
            "reasoning_factors": factors
        }

    def _handle_readiness_substate(self, completion: dict, factors: dict, events: list,
                                 session_state: TRTSessionState, reasoning: str) -> dict:
        """Handle 1.3 readiness assessment"""

        return {
            "current_stage": session_state.current_stage,
            "current_substate": session_state.current_substate,
            "navigation_decision": "assess_readiness",
            "situation_type": "readiness_for_stage_2",
            "rag_query": "dr_q_transition_to_intervention",
            "completion_status": completion,
            "ready_for_next": completion.get("ready_for_stage_2", False),
            "advancement_blocked_by": [] if completion.get("ready_for_stage_2", False) else ["pattern_understanding_needed"],
            "reasoning": reasoning,
            "recent_events": events,
            "enhanced_reasoning": True,
            "reasoning_factors": factors
        }

    def _handle_general_substate(self, completion: dict, factors: dict, events: list,
                               session_state: TRTSessionState, reasoning: str) -> dict:
        """Handle general/other substates"""

        return {
            "current_stage": session_state.current_stage,
            "current_substate": session_state.current_substate,
            "navigation_decision": "general_inquiry",
            "situation_type": "general_therapeutic_inquiry",
            "rag_query": "general_dr_q_approach",
            "completion_status": completion,
            "ready_for_next": False,
            "reasoning": reasoning,
            "recent_events": events,
            "enhanced_reasoning": True,
            "reasoning_factors": factors
        }

class LightweightLLMDialogueAgent:
    """Lightweight Dialogue Agent with enhanced response generation"""

    def __init__(self, rag_system: TRTRAGSystem):
        self.rag_system = rag_system

    def generate_response(self, client_input: str, navigation_output: dict,
                         session_state: TRTSessionState) -> dict:
        """Generate enhanced therapeutic response"""

        # Get RAG examples
        rag_examples = self.rag_system.get_few_shot_examples(
            navigation_output,
            client_input,
            max_examples=3
        )

        # Enhanced response generation
        response = self._enhanced_response_generation(
            client_input, navigation_output, rag_examples, session_state
        )

        return {
            "therapeutic_response": response["response"],
            "technique_used": navigation_output["rag_query"],
            "examples_used": len(rag_examples),
            "rag_similarity_scores": [ex["similarity_score"] for ex in rag_examples],
            "navigation_reasoning": navigation_output["reasoning"],
            "enhanced_reasoning": True,
            "response_reasoning": response["reasoning"],
            "adaptation_used": response.get("adaptation_used", False)
        }

    def _enhanced_response_generation(self, client_input: str, navigation_output: dict,
                                    rag_examples: list, session_state: TRTSessionState) -> dict:
        """Enhanced response generation with contextual adaptation"""

        decision = navigation_output["navigation_decision"]
        situation = navigation_output["situation_type"]
        factors = navigation_output.get("reasoning_factors", {})

        # Get response based on enhanced factors
        if factors.get('resistance_indicators', False):
            response = self._handle_resistance_response(client_input, decision, rag_examples)
        elif factors.get('confusion_indicators', False):
            response = self._handle_confusion_response(client_input, decision, rag_examples)
        elif factors.get('positive_indicators', False):
            response = self._handle_positive_response(client_input, decision, rag_examples)
        elif factors.get('body_awareness_present', False):
            response = self._handle_body_awareness_response(client_input, decision, rag_examples)
        else:
            response = self._handle_standard_response(client_input, decision, rag_examples, session_state)

        return response

    def _handle_resistance_response(self, client_input: str, decision: str, rag_examples: list) -> dict:
        """Handle resistance with validation"""

        responses = {
            "clarify_goal": "I hear that this feels difficult right now. What would feel most helpful to focus on?",
            "explore_problem": "It sounds like you're feeling stuck. What's making this feel hard right now?",
            "body_awareness_inquiry": "I understand this might feel uncomfortable. What do you notice happening in your body as we talk?",
            "general_inquiry": "I hear you. What would be most useful right now?"
        }

        response = responses.get(decision, "I understand. What feels most important right now?")

        return {
            "response": response,
            "reasoning": "Responded to resistance with validation and gentle inquiry",
            "adaptation_used": True
        }

    def _handle_confusion_response(self, client_input: str, decision: str, rag_examples: list) -> dict:
        """Handle confusion with clarification"""

        responses = {
            "clarify_goal": "Let me ask it differently - if our time together could help you feel different in some way, what would that be?",
            "build_vision": "What I mean is, can you imagine a version of yourself who doesn't struggle with this anymore?",
            "explore_problem": "I'm asking about what specifically has been bothering you. What's been the hardest part?",
            "body_awareness_inquiry": "I'm wondering what physical sensations you might notice right now in your body.",
            "general_inquiry": "Let me be clearer - what's been troubling you most?"
        }

        response = responses.get(decision, "Let me ask that in a different way - what's been most difficult for you?")

        return {
            "response": response,
            "reasoning": "Provided clarification for client confusion",
            "adaptation_used": True
        }

    def _handle_positive_response(self, client_input: str, decision: str, rag_examples: list) -> dict:
        """Handle positive responses with appropriate acknowledgment"""

        client_lower = client_input.lower()

        if any(word in client_lower for word in ["better", "good", "great", "helpful"]):
            if decision == "explore_problem":
                response = "That's good to hear. What's different now? How do you know you're feeling better?"
            else:
                response = "I'm glad that feels right to you. What's making the difference?"
        elif any(word in client_lower for word in ["yes", "exactly", "right"]):
            response = "Good. What's happening for you now as we focus on this?"
        else:
            response = "That sounds positive. What do you notice about that?"

        return {
            "response": response,
            "reasoning": "Acknowledged positive response and explored the change",
            "adaptation_used": True
        }

    def _handle_body_awareness_response(self, client_input: str, decision: str, rag_examples: list) -> dict:
        """Handle body awareness with present-moment focus"""

        client_lower = client_input.lower()

        if any(word in client_lower for word in ["chest", "tight", "heavy", "pressure"]):
            response = "And even as you're talking about that right now, what do you notice in your body? What's that feeling like?"
        elif any(word in client_lower for word in ["feel", "feeling", "sensation"]):
            response = "What's happening now? How's your body feeling as you're sharing this?"
        else:
            response = "What do you notice in your body right now?"

        return {
            "response": response,
            "reasoning": "Focused on present-moment body awareness",
            "adaptation_used": True
        }

    def _handle_standard_response(self, client_input: str, decision: str, rag_examples: list,
                                session_state: TRTSessionState) -> dict:
        """Handle standard therapeutic responses"""

        # Use the existing TRT response logic with enhancements
        from integrated_trt_system import DialogueAgent

        # Create temporary dialogue agent for standard responses
        temp_agent = DialogueAgent(self.rag_system)

        # Generate navigation output format for compatibility
        nav_output = {
            "navigation_decision": decision,
            "situation_type": "enhanced_standard_response"
        }

        response = temp_agent._craft_response(client_input, nav_output, rag_examples, session_state)

        return {
            "response": response,
            "reasoning": f"Used standard TRT response for {decision}",
            "adaptation_used": False
        }

class LightweightLLMTRTSystem:
    """Complete lightweight LLM-enhanced TRT system"""

    def __init__(self):
        print("🚀 Initializing Lightweight LLM-Enhanced TRT System...")

        # Initialize components
        self.rag_system = TRTRAGSystem()
        self.rag_system.load_index("data/embeddings/trt_rag_index.faiss",
                                  "data/embeddings/trt_rag_metadata.json")

        self.master_agent = LightweightLLMMasterAgent()
        self.dialogue_agent = LightweightLLMDialogueAgent(self.rag_system)

        print("✅ Lightweight LLM-Enhanced TRT System Ready!")

    def process_client_input(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Process input through enhanced system"""

        start_time = time.time()

        # Enhanced master planning
        navigation_output = self.master_agent.make_navigation_decision(client_input, session_state)

        # Enhanced dialogue generation
        dialogue_output = self.dialogue_agent.generate_response(client_input, navigation_output, session_state)

        # Update session
        session_state.add_exchange(
            client_input=client_input,
            therapist_response=dialogue_output["therapeutic_response"],
            navigation_output=navigation_output
        )

        processing_time = time.time() - start_time

        return {
            "navigation": navigation_output,
            "dialogue": dialogue_output,
            "session_progress": session_state.get_progress_summary(),
            "processing_time": processing_time,
            "system_status": {
                "enhanced_reasoning": True,
                "reasoning_factors": navigation_output.get("reasoning_factors", {}),
                "adaptation_used": dialogue_output.get("adaptation_used", False)
            }
        }

def run_lightweight_test():
    """Test the lightweight enhanced system"""

    print("🧪 LIGHTWEIGHT LLM-ENHANCED TRT SYSTEM TEST")
    print("=" * 70)

    system = LightweightLLMTRTSystem()
    session_state = TRTSessionState("lightweight_test")

    # Test the problematic sequence plus edge cases
    test_inputs = [
        "iam feeling low",
        "i want to feel great",
        "i feel sad",
        "i feel it in my chest",
        "i feels heavy",
        "i feel better",
        "I don't understand what you mean",
        "This isn't helping me",
        "I'm confused"
    ]

    for turn, client_input in enumerate(test_inputs, 1):
        print(f"\n🔄 TURN {turn}")
        print("-" * 50)
        print(f"👤 CLIENT: \"{client_input}\"")

        output = system.process_client_input(client_input, session_state)

        nav = output["navigation"]
        dialogue = output["dialogue"]
        status = output["system_status"]

        print(f"🧠 ENHANCED MASTER PLANNING:")
        print(f"   Substate: {nav['current_substate']}")
        print(f"   Decision: {nav['navigation_decision']}")
        print(f"   Enhanced: {'✅' if nav.get('enhanced_reasoning') else '❌'}")
        print(f"   Reasoning: {nav.get('reasoning', 'N/A')}")

        print(f"💬 ENHANCED DIALOGUE:")
        print(f"   Adaptation: {'✅' if status.get('adaptation_used') else '❌'}")
        print(f"   Response: \"{dialogue['therapeutic_response']}\"")

        print(f"⏱️  Processing: {output['processing_time']:.3f}s")

    print(f"\n🎉 LIGHTWEIGHT TEST COMPLETE!")
    print(f"Final substate: {session_state.current_substate}")

if __name__ == "__main__":
    run_lightweight_test()