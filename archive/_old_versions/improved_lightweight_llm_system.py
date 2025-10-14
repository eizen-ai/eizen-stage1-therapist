"""
Improved Lightweight LLM-Based TRT System
Fixes identified issues from comprehensive testing
"""

import json
import time
from datetime import datetime
from session_state_manager import TRTSessionState
from embedding_and_retrieval_setup import TRTRAGSystem
from input_preprocessing import InputPreprocessor

class ImprovedLLMMasterAgent:
    """Improved Master Planning Agent with enhanced reasoning"""

    def __init__(self):
        # Load navigation rules
        with open('core_system/simplified_navigation.json', 'r') as f:
            self.navigation = json.load(f)

        with open('core_system/input_classification_patterns.json', 'r') as f:
            self.patterns = json.load(f)

        self.preprocessor = InputPreprocessor()

    def make_navigation_decision(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Make navigation decision with improved reasoning"""

        # Preprocess input
        processed_input = self.preprocessor.preprocess_input(client_input)
        corrected_input = processed_input['corrected_input']

        # Update session state
        completion_events = session_state.update_completion_status(corrected_input, processed_input)

        # Check advancement
        is_ready, next_substate = session_state.check_substate_completion()
        if is_ready:
            session_state.advance_substate(next_substate)

        # Improved reasoning with better detection
        decision = self._improved_navigation_reasoning(
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

    def _improved_navigation_reasoning(self, client_input: str, session_state: TRTSessionState,
                                     events: list, processed_input: dict) -> dict:
        """Improved reasoning with better factor detection"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate
        client_lower = client_input.lower()
        emotional_state = processed_input.get('emotional_state', 'neutral')

        # Enhanced reasoning factors with improved detection
        reasoning_factors = {
            'emotional_intensity': self._assess_emotional_intensity(client_input, emotional_state),
            'body_awareness_present': self._detect_body_awareness(client_lower),
            'resistance_indicators': self._detect_resistance(client_lower),
            'positive_indicators': self._detect_positive_language(client_lower),
            'confusion_indicators': self._detect_confusion(client_lower),
            'goal_language': self._detect_goal_language(client_lower)
        }

        # Generate enhanced reasoning
        reasoning = self._generate_contextual_reasoning(
            substate, completion, reasoning_factors, events, client_input
        )

        # Make decision with improved logic
        if substate == "1.1_goal_and_vision":
            return self._handle_goal_vision_substate_improved(
                completion, reasoning_factors, events, session_state, reasoning
            )
        elif substate == "1.2_problem_and_body":
            return self._handle_problem_body_substate_improved(
                completion, reasoning_factors, events, session_state, reasoning
            )
        elif substate == "1.3_readiness_assessment":
            return self._handle_readiness_substate_improved(
                completion, reasoning_factors, events, session_state, reasoning
            )
        else:
            return self._handle_general_substate_improved(
                completion, reasoning_factors, events, session_state, reasoning
            )

    def _detect_body_awareness(self, client_lower: str) -> bool:
        """Improved body awareness detection"""
        body_words = [
            'chest', 'body', 'feel', 'heavy', 'tight', 'pressure', 'sensation',
            'shoulders', 'stomach', 'throat', 'hands', 'head', 'heart',
            'breathing', 'tense', 'relaxed', 'shaking', 'knot', 'ache',
            'pain', 'warm', 'cold', 'numb', 'tingling'
        ]
        return any(word in client_lower for word in body_words)

    def _detect_resistance(self, client_lower: str) -> bool:
        """Improved resistance detection"""
        resistance_patterns = [
            "don't want", "can't", "won't", "not", "never", "stop",
            "quit", "this isn't", "this doesn't", "nothing works",
            "tried everything", "don't believe", "too hard", "pointless",
            "waste of time", "doesn't help"
        ]
        return any(pattern in client_lower for pattern in resistance_patterns)

    def _detect_positive_language(self, client_lower: str) -> bool:
        """Improved positive language detection"""
        positive_words = [
            'better', 'good', 'great', 'yes', 'right', 'exactly', 'helpful',
            'wonderful', 'amazing', 'excellent', 'perfect', 'happy',
            'confident', 'relaxed', 'calm', 'peaceful', 'relieved',
            'understand', 'makes sense', 'resonates', 'clarity'
        ]
        return any(word in client_lower for word in positive_words)

    def _detect_confusion(self, client_lower: str) -> bool:
        """Improved confusion detection"""
        confusion_patterns = [
            "don't understand", "confused", "what do you mean", "explain",
            "not sure", "don't know", "unclear", "lost", "repeat",
            "what are you asking", "don't get it", "clarify"
        ]
        return any(pattern in client_lower for pattern in confusion_patterns)

    def _detect_goal_language(self, client_lower: str) -> bool:
        """Improved goal language detection"""
        goal_words = [
            'want', 'need', 'goal', 'hope', 'wish', 'would like',
            'aim', 'desire', 'seek', 'looking for', 'trying to',
            'want to be', 'want to feel'
        ]
        return any(word in client_lower for word in goal_words)

    def _assess_emotional_intensity(self, client_input: str, emotional_state: str) -> str:
        """Improved emotional intensity assessment"""
        client_lower = client_input.lower()

        # High intensity indicators
        high_intensity = ['extremely', 'very', 'really', 'so', 'completely', 'totally',
                         'incredibly', 'absolutely', 'utterly', 'entirely', 'desperately']

        # Medium intensity indicators
        medium_intensity = ['quite', 'pretty', 'fairly', 'somewhat', 'rather', 'kind of']

        if any(word in client_lower for word in high_intensity):
            return 'high'
        elif any(word in client_lower for word in medium_intensity):
            return 'moderate'
        elif emotional_state != 'neutral' and 'primary_emotion' in str(emotional_state):
            # Check emotional state intensity
            if 'crisis' in str(emotional_state) or 'high' in str(emotional_state):
                return 'high'
            elif 'moderate' in str(emotional_state):
                return 'moderate'
            else:
                return 'low'
        else:
            return 'low'

    def _generate_contextual_reasoning(self, substate: str, completion: dict,
                                     factors: dict, events: list, client_input: str) -> str:
        """Enhanced contextual reasoning generation"""

        reasoning_parts = []

        # Analyze current state
        reasoning_parts.append(f"Client is in {substate}")

        # Analyze emotional factors with more detail
        if factors['emotional_intensity'] == 'high':
            reasoning_parts.append("High emotional intensity detected - prioritize validation and containment")
        elif factors['emotional_intensity'] == 'moderate':
            reasoning_parts.append("Moderate emotional intensity - balance validation with exploration")
        elif factors['body_awareness_present']:
            reasoning_parts.append("Body awareness present - excellent opportunity for somatic focus")

        # Analyze resistance/engagement with specificity
        if factors['resistance_indicators']:
            reasoning_parts.append("Resistance indicators present - use gentle, non-confrontational validation")
        elif factors['confusion_indicators']:
            reasoning_parts.append("Confusion detected - provide clear, simple clarification")
        elif factors['positive_indicators']:
            reasoning_parts.append("Positive engagement detected - acknowledge and build on progress")

        # Analyze goal language
        if not completion.get('goal_stated', False) and factors['goal_language']:
            reasoning_parts.append("Goal language detected but not clearly stated - facilitate clarification")

        # Analyze recent events with context
        if 'vision_accepted_implicit' in events:
            reasoning_parts.append("Implicit vision acceptance through emotional sharing - advance therapeutically")

        return ". ".join(reasoning_parts)

    def _handle_goal_vision_substate_improved(self, completion: dict, factors: dict, events: list,
                                           session_state: TRTSessionState, reasoning: str) -> dict:
        """Improved handling of goal and vision substate"""

        if not completion["goal_stated"]:
            if factors['confusion_indicators']:
                decision = "clarify_goal"
                situation = "goal_needs_clarification_gentle"
                blocked_by = ["goal_not_stated", "client_confusion"]
                rag_query = "dr_q_goal_clarification"
            elif factors['resistance_indicators']:
                decision = "clarify_goal"
                situation = "goal_needs_clarification_resistance"
                blocked_by = ["goal_not_stated", "client_resistance"]
                rag_query = "dr_q_goal_clarification"
            else:
                decision = "clarify_goal"
                situation = "goal_needs_clarification"
                blocked_by = ["goal_not_stated"]
                rag_query = "dr_q_goal_clarification"

        elif completion["goal_stated"] and not completion["vision_accepted"]:
            if factors['positive_indicators'] or 'vision_accepted_implicit' in events:
                decision = "explore_problem"
                situation = "vision_accepted_explore_problem"
                blocked_by = []
                rag_query = "dr_q_problem_construction"
            elif factors['confusion_indicators']:
                decision = "build_vision"
                situation = "goal_stated_needs_vision_clarification"
                blocked_by = ["vision_not_accepted", "client_confusion"]
                rag_query = "dr_q_future_self_vision_building"
            else:
                decision = "build_vision"
                situation = "goal_stated_needs_vision"
                blocked_by = ["vision_not_accepted"]
                rag_query = "dr_q_future_self_vision_building"
        else:
            # Both goal and vision completed
            decision = "explore_problem"
            situation = "transition_to_problem_exploration"
            blocked_by = []
            rag_query = "dr_q_problem_construction"

        return {
            "current_stage": session_state.current_stage,
            "current_substate": session_state.current_substate,
            "navigation_decision": decision,
            "situation_type": situation,
            "rag_query": rag_query,
            "completion_status": completion,
            "ready_for_next": len(blocked_by) == 0,
            "advancement_blocked_by": blocked_by,
            "reasoning": reasoning,
            "recent_events": events,
            "enhanced_reasoning": True,
            "reasoning_factors": factors
        }

    def _handle_problem_body_substate_improved(self, completion: dict, factors: dict, events: list,
                                             session_state: TRTSessionState, reasoning: str) -> dict:
        """Improved handling of problem and body substate"""

        # Prioritize body awareness when present
        if factors['body_awareness_present'] and not factors['positive_indicators']:
            decision = "body_awareness_inquiry"
            situation = "body_symptoms_exploration"
            rag_query = "dr_q_body_symptom_present_moment_inquiry"
        elif factors['positive_indicators']:
            decision = "explore_problem"
            situation = "positive_response_exploration"
            rag_query = "dr_q_problem_construction"
        elif factors['resistance_indicators']:
            decision = "explore_problem"
            situation = "resistance_in_problem_exploration"
            rag_query = "dr_q_problem_construction"
        elif not completion.get("problem_identified", False):
            decision = "explore_problem"
            situation = "problem_needs_exploration"
            rag_query = "dr_q_problem_construction"
        else:
            decision = "pattern_inquiry"
            situation = "explore_trigger_pattern"
            rag_query = "dr_q_how_do_you_know_technique"

        # Determine advancement readiness
        ready_for_next = (completion.get("problem_identified", False) and
                         completion.get("body_awareness_present", False) and
                         completion.get("present_moment_focus", False))

        blocked_by = []
        if not ready_for_next:
            blocked_by = ["present_moment_focus_needed"]

        return {
            "current_stage": session_state.current_stage,
            "current_substate": session_state.current_substate,
            "navigation_decision": decision,
            "situation_type": situation,
            "rag_query": rag_query,
            "completion_status": completion,
            "ready_for_next": ready_for_next,
            "advancement_blocked_by": blocked_by,
            "reasoning": reasoning,
            "recent_events": events,
            "enhanced_reasoning": True,
            "reasoning_factors": factors
        }

    def _handle_readiness_substate_improved(self, completion: dict, factors: dict, events: list,
                                          session_state: TRTSessionState, reasoning: str) -> dict:
        """Improved handling of readiness assessment"""

        ready_for_stage_2 = completion.get("ready_for_stage_2", False)

        return {
            "current_stage": session_state.current_stage,
            "current_substate": session_state.current_substate,
            "navigation_decision": "assess_readiness",
            "situation_type": "readiness_for_stage_2",
            "rag_query": "dr_q_transition_to_intervention",
            "completion_status": completion,
            "ready_for_next": ready_for_stage_2,
            "advancement_blocked_by": [] if ready_for_stage_2 else ["pattern_understanding_needed"],
            "reasoning": reasoning,
            "recent_events": events,
            "enhanced_reasoning": True,
            "reasoning_factors": factors
        }

    def _handle_general_substate_improved(self, completion: dict, factors: dict, events: list,
                                        session_state: TRTSessionState, reasoning: str) -> dict:
        """Improved handling of general substates"""

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

class ImprovedLLMDialogueAgent:
    """Improved Dialogue Agent with enhanced response adaptation"""

    def __init__(self, rag_system: TRTRAGSystem):
        self.rag_system = rag_system

    def generate_response(self, client_input: str, navigation_output: dict,
                         session_state: TRTSessionState) -> dict:
        """Generate improved therapeutic response with better adaptation"""

        # Get RAG examples
        rag_examples = self.rag_system.get_few_shot_examples(
            navigation_output,
            client_input,
            max_examples=3
        )

        # Enhanced response generation with better pattern detection
        response = self._improved_response_generation(
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
            "adaptation_used": response.get("adaptation_used", False),
            "response_category": response.get("response_category", "standard")
        }

    def _improved_response_generation(self, client_input: str, navigation_output: dict,
                                    rag_examples: list, session_state: TRTSessionState) -> dict:
        """Improved response generation with better contextual adaptation"""

        decision = navigation_output["navigation_decision"]
        situation = navigation_output["situation_type"]
        factors = navigation_output.get("reasoning_factors", {})

        # Check for repetitive inputs
        repetition_count = self._check_repetitive_patterns(client_input, session_state)

        # Enhanced adaptation logic
        if repetition_count >= 3:
            response = self._handle_repetitive_input(client_input, decision, repetition_count)
        elif factors.get('resistance_indicators', False):
            response = self._handle_resistance_response_improved(client_input, decision, factors)
        elif factors.get('confusion_indicators', False):
            response = self._handle_confusion_response_improved(client_input, decision, factors)
        elif factors.get('positive_indicators', False):
            response = self._handle_positive_response_improved(client_input, decision, factors)
        elif factors.get('body_awareness_present', False):
            response = self._handle_body_awareness_response_improved(client_input, decision, factors)
        else:
            response = self._handle_standard_response_improved(client_input, decision, rag_examples, session_state)

        return response

    def _check_repetitive_patterns(self, client_input: str, session_state: TRTSessionState) -> int:
        """Check for repetitive input patterns"""
        if not hasattr(session_state, 'conversation_history'):
            return 0

        recent_inputs = [exchange.get('client_input', '') for exchange in session_state.conversation_history[-5:]]
        # Count exact and similar matches
        exact_matches = sum(1 for inp in recent_inputs if inp.strip().lower() == client_input.strip().lower())
        similar_inputs = sum(1 for inp in recent_inputs if inp != client_input and self._inputs_similar(client_input, inp))

        return exact_matches + similar_inputs

    def _inputs_similar(self, input1: str, input2: str) -> bool:
        """Check if two inputs are similar"""
        # Simple similarity check
        words1 = set(input1.lower().split())
        words2 = set(input2.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union > 0.6

    def _handle_repetitive_input(self, client_input: str, decision: str, count: int) -> dict:
        """Handle repetitive inputs with varied responses"""

        varied_responses = {
            "body_awareness_inquiry": [
                "What do you notice in your body right now?",
                "How's your body feeling as you're talking about that?",
                "What's that sensation like for you?",
                "What else do you notice happening in your body?",
                "How do you know when that feeling starts?"
            ],
            "explore_problem": [
                "What's been making this difficult for you?",
                "Help me understand what's been most challenging.",
                "What made that disturbing for you?",
                "What would be useful for me to know?",
                "What else is important about this?"
            ],
            "clarify_goal": [
                "What do you want our time to accomplish?",
                "If this could feel different, what would that be like?",
                "What would help you feel better?",
                "What's most important to focus on?",
                "What do we want to get better for you?"
            ]
        }

        responses = varied_responses.get(decision, [
            "What else would be helpful to explore?",
            "What's most important right now?",
            "Help me understand better.",
            "What made that significant for you?",
            "What would be useful to focus on?"
        ])

        response_index = min(count - 1, len(responses) - 1)
        selected_response = responses[response_index]

        return {
            "response": selected_response,
            "reasoning": f"Handled repetitive input (count: {count}) with varied response #{response_index + 1}",
            "adaptation_used": True,
            "response_category": "repetition_variant"
        }

    def _handle_resistance_response_improved(self, client_input: str, decision: str, factors: dict) -> dict:
        """Improved resistance handling with better validation"""

        client_lower = client_input.lower()

        # More specific resistance responses
        if "don't want" in client_lower:
            response = "I hear that this feels difficult right now. What would feel most comfortable to focus on?"
        elif "isn't helping" in client_lower or "doesn't work" in client_lower:
            response = "It sounds like you're feeling stuck. What would be most helpful right now?"
        elif "don't understand" in client_lower:
            response = "I understand this might feel confusing. What part feels unclear?"
        elif "too hard" in client_lower:
            response = "I hear that this feels overwhelming. What would make it feel more manageable?"
        else:
            response = "I understand. What feels most important to you right now?"

        return {
            "response": response,
            "reasoning": "Responded to resistance with specific validation and gentle redirection",
            "adaptation_used": True,
            "response_category": "resistance_handling"
        }

    def _handle_confusion_response_improved(self, client_input: str, decision: str, factors: dict) -> dict:
        """Improved confusion handling with clearer clarification"""

        client_lower = client_input.lower()

        if "what do you mean" in client_lower:
            if decision == "clarify_goal":
                response = "I'm asking what you hope our time together will help you accomplish."
            elif decision == "build_vision":
                response = "I'm wondering if you can imagine yourself not struggling with this anymore."
            elif decision == "body_awareness_inquiry":
                response = "I'm asking what physical sensations you notice in your body right now."
            else:
                response = "I'm asking about what's been most difficult for you."
        elif "explain" in client_lower or "confused" in client_lower:
            response = "Let me ask it differently - what's been troubling you most?"
        else:
            response = "What I'm wondering about is what's been hardest for you recently."

        return {
            "response": response,
            "reasoning": "Provided clear clarification for client confusion with specific reframing",
            "adaptation_used": True,
            "response_category": "confusion_clarification"
        }

    def _handle_positive_response_improved(self, client_input: str, decision: str, factors: dict) -> dict:
        """Improved positive response handling with better acknowledgment"""

        client_lower = client_input.lower()

        if any(word in client_lower for word in ["better", "good", "great"]):
            response = "That's good to hear. What's different now? How do you know you're feeling better?"
        elif any(word in client_lower for word in ["helpful", "makes sense", "understand"]):
            response = "I'm glad that feels right to you. What's making the difference?"
        elif any(word in client_lower for word in ["yes", "exactly", "right"]):
            response = "Good. What's happening for you now as we focus on this?"
        elif any(word in client_lower for word in ["relaxed", "calm", "peaceful"]):
            response = "That sounds positive. What do you notice about feeling that way?"
        else:
            response = "That's wonderful to hear. What's contributing to that feeling?"

        return {
            "response": response,
            "reasoning": "Acknowledged positive response and explored the beneficial change",
            "adaptation_used": True,
            "response_category": "positive_acknowledgment"
        }

    def _handle_body_awareness_response_improved(self, client_input: str, decision: str, factors: dict) -> dict:
        """Improved body awareness with more varied present-moment focus"""

        client_lower = client_input.lower()

        if any(word in client_lower for word in ["chest", "tight", "heavy", "pressure"]):
            response = "And even as you're talking about that right now, what do you notice in your body? What's that feeling like?"
        elif any(word in client_lower for word in ["shoulders", "tense", "knot"]):
            response = "What's happening with that tension right now? How does it feel in this moment?"
        elif any(word in client_lower for word in ["stomach", "throat", "head"]):
            response = "What do you notice about that sensation as you're sitting here with me?"
        elif any(word in client_lower for word in ["feel", "feeling", "sensation"]):
            response = "What's happening now? How's your body feeling as you're sharing this?"
        else:
            response = "What do you notice in your body right now as we talk about this?"

        return {
            "response": response,
            "reasoning": "Focused on present-moment body awareness with specific attention to mentioned sensations",
            "adaptation_used": True,
            "response_category": "body_awareness_focus"
        }

    def _handle_standard_response_improved(self, client_input: str, decision: str, rag_examples: list,
                                         session_state: TRTSessionState) -> dict:
        """Improved standard therapeutic responses"""

        # Enhanced standard responses based on decision type
        standard_responses = {
            "clarify_goal": "What do you want our time to get accomplished? What do we want to get better for you?",
            "build_vision": "I'm seeing you who used to have that problem now wouldn't be able to get it. The you I'm seeing is free, emotionally present, connecting to what is happening, dealing with things with more flexibility and experiencing more joy. Does that vision feel right to you?",
            "explore_problem": "What do you think would be useful for me to know to better understand? Help me understand what's been making it hard for you to feel that way.",
            "body_awareness_inquiry": "What's happening now? How's your body feeling right now as you're talking about that?",
            "pattern_inquiry": "How do you know when that feeling starts? What is it that lets you know it's beginning?",
            "assess_readiness": "From what you've said so far, what haven't I understood? Is there more I should know before beginning to assist you with this?",
            "general_inquiry": "What made that disturbing for you?"
        }

        response = standard_responses.get(decision, "What else would be useful for me to know to really understand?")

        return {
            "response": response,
            "reasoning": f"Used enhanced standard TRT response for {decision}",
            "adaptation_used": False,
            "response_category": "standard_trt"
        }

class ImprovedLLMTRTSystem:
    """Complete improved LLM-enhanced TRT system"""

    def __init__(self):
        print("🚀 Initializing Improved LLM-Enhanced TRT System...")

        # Initialize components
        self.rag_system = TRTRAGSystem()
        self.rag_system.load_index("data/embeddings/trt_rag_index.faiss",
                                  "data/embeddings/trt_rag_metadata.json")

        self.master_agent = ImprovedLLMMasterAgent()
        self.dialogue_agent = ImprovedLLMDialogueAgent(self.rag_system)

        print("✅ Improved LLM-Enhanced TRT System Ready!")

    def process_client_input(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Process input through improved system"""

        start_time = time.time()

        # Improved master planning
        navigation_output = self.master_agent.make_navigation_decision(client_input, session_state)

        # Improved dialogue generation
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
                "adaptation_used": dialogue_output.get("adaptation_used", False),
                "response_category": dialogue_output.get("response_category", "standard")
            }
        }

def run_improved_test():
    """Test the improved enhanced system"""

    print("🧪 IMPROVED LLM-ENHANCED TRT SYSTEM TEST")
    print("=" * 70)

    system = ImprovedLLMTRTSystem()
    session_state = TRTSessionState("improved_test")

    # Test the challenging cases from the test results
    test_inputs = [
        # Normal progression
        "I've been feeling really anxious",
        "I want to feel calm and peaceful",
        "Yes, that sounds exactly right",
        "It's work stress, I get chest tightness",
        "I can feel that tightness right now",

        # Edge cases that need improvement
        "I don't understand what you mean",  # Confusion
        "This isn't helping me",  # Resistance
        "I feel much better now",  # Positive
        "I feel sad",  # Repetitive test
        "I feel sad",  # Same input again
        "I feel sad",  # Same input third time
    ]

    for turn, client_input in enumerate(test_inputs, 1):
        print(f"\n🔄 TURN {turn}")
        print("-" * 50)
        print(f"👤 CLIENT: \"{client_input}\"")

        output = system.process_client_input(client_input, session_state)

        nav = output["navigation"]
        dialogue = output["dialogue"]
        status = output["system_status"]

        print(f"🧠 IMPROVED MASTER PLANNING:")
        print(f"   Substate: {nav['current_substate']}")
        print(f"   Decision: {nav['navigation_decision']}")
        print(f"   Factors: {list(factor for factor, detected in nav.get('reasoning_factors', {}).items() if detected)}")

        print(f"💬 IMPROVED DIALOGUE:")
        print(f"   Category: {status.get('response_category', 'N/A')}")
        print(f"   Adaptation: {'✅' if status.get('adaptation_used') else '❌'}")
        print(f"   Response: \"{dialogue['therapeutic_response']}\"")

        print(f"⏱️  Processing: {output['processing_time']:.3f}s")

    print(f"\n🎉 IMPROVED TEST COMPLETE!")
    print(f"Final substate: {session_state.current_substate}")

if __name__ == "__main__":
    run_improved_test()