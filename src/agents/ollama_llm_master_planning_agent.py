"""
Ollama-Based Master Planning Agent
Uses local Ollama with Llama 3.1
"""

import json
import requests
import os
from src.core.session_state_manager import TRTSessionState
from src.utils.input_preprocessing import InputPreprocessor
import logging

class OllamaLLMMasterPlanningAgent:
    """Ollama-powered Master Planning Agent using local Llama 3.1"""

    def __init__(self, ollama_url="http://localhost:11434", model="llama3.1"):
        self.ollama_url = ollama_url
        self.model = model
        self.api_endpoint = f"{ollama_url}/api/generate"

        # Get project root directory
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')

        # Load TRT methodology rules
        nav_path = os.path.join(project_root, 'config/system/core_system/simplified_navigation.json')
        with open(nav_path, 'r') as f:
            self.navigation = json.load(f)

        patterns_path = os.path.join(project_root, 'config/system/core_system/input_classification_patterns.json')
        with open(patterns_path, 'r') as f:
            self.patterns = json.load(f)

        # Initialize input preprocessor
        self.preprocessor = InputPreprocessor()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Test Ollama connection
        self._test_ollama_connection()

    def _test_ollama_connection(self):
        """Test if Ollama is accessible"""
        try:
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": "test",
                    "stream": False
                },
                timeout=10
            )
            if response.status_code == 200:
                self.logger.info(f"✅ Ollama connected: {self.ollama_url} (model: {self.model})")
            else:
                self.logger.warning(f"⚠️ Ollama returned status {response.status_code}")
        except Exception as e:
            self.logger.error(f"❌ Cannot connect to Ollama: {e}")
            self.logger.info("Will use fallback rule-based logic")

    def _check_strict_rule_overrides(self, client_input: str, session_state: TRTSessionState, events: list) -> dict:
        """STRICT RULE-BASED OVERRIDES - Take precedence over LLM"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate
        client_lower = client_input.lower()

        # RULE 1: If in 1.1 and NO goal stated yet → MUST ask for goal (HIGHEST PRIORITY)
        if substate == "1.1_goal_and_vision" and not completion["goal_stated"]:
            # Check if this is first turn or early turns
            if len(session_state.conversation_history) <= 2:
                self.logger.info("🎯 OVERRIDE: Early session, goal not stated → clarify_goal")
                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": substate,
                    "navigation_decision": "clarify_goal",
                    "situation_type": "goal_needs_clarification",
                    "rag_query": "dr_q_goal_clarification",
                    "completion_status": completion,
                    "ready_for_next": False,
                    "advancement_blocked_by": ["goal_not_stated"],
                    "reasoning": "STRICT RULE: Must establish goal first",
                    "recent_events": events,
                    "llm_reasoning": False,
                    "fallback_used": False,
                    "rule_override": True
                }

        # RULE 2: If goal stated but vision NOT accepted → MUST build vision (ABSOLUTE PRIORITY)
        # This prevents skipping vision building and jumping to psycho-education
        if substate == "1.1_goal_and_vision" and completion["goal_stated"] and not completion["vision_accepted"]:
            self.logger.info("🎯 OVERRIDE: Goal stated, vision not accepted → build_vision")
            return {
                "current_stage": session_state.current_stage,
                "current_substate": substate,
                "navigation_decision": "build_vision",
                "situation_type": "goal_stated_needs_vision",
                "rag_query": "dr_q_future_self_vision_building",
                "completion_status": completion,
                "ready_for_next": False,
                "advancement_blocked_by": ["vision_not_accepted"],
                "reasoning": "STRICT RULE: Build vision after goal stated (ALWAYS)",
                "recent_events": events,
                "llm_reasoning": False,
                "fallback_used": False,
                "rule_override": True
            }

        # RULE 3: If asking about problem but goal/vision not complete → redirect to goal
        if substate == "1.1_goal_and_vision":
            if not completion["goal_stated"] or not completion["vision_accepted"]:
                if any(word in client_lower for word in ["problem", "issue", "difficult", "hard"]):
                    # Client mentioned problem but we haven't finished goal/vision
                    if not completion["goal_stated"]:
                        self.logger.info("🎯 OVERRIDE: Client mentioned problem but no goal → redirect to goal")
                        return {
                            "current_stage": session_state.current_stage,
                            "current_substate": substate,
                            "navigation_decision": "clarify_goal",
                            "situation_type": "goal_needs_clarification",
                            "rag_query": "dr_q_redirect_outcome",
                            "completion_status": completion,
                            "ready_for_next": False,
                            "advancement_blocked_by": ["goal_not_stated"],
                            "reasoning": "STRICT RULE: Redirect from problem to goal",
                            "recent_events": events,
                            "llm_reasoning": False,
                            "fallback_used": False,
                            "rule_override": True
                        }

        # RULE 4: If in 1.2_problem_and_body and problem NOT identified yet → MUST explore problem FIRST
        # This ensures we ask "What's been making it hard?" before jumping to body location
        # BUT: Only ask ONCE! Check if we've already asked a problem question
        # ALSO: Don't apply if client is already providing body information (emotion, location, sensation)
        if substate == "1.2_problem_and_body" and not completion["problem_identified"]:
            # Check if client is already providing body-related information
            # If they are, let them continue - don't interrupt to ask about problem again
            client_providing_body_info = (
                session_state.emotion_provided or
                session_state.body_location_provided or
                session_state.body_sensation_described or
                session_state.last_client_provided_info in ["emotion", "body_location", "sensation_quality"]
            )

            # Only apply this rule if:
            # 1. Client is NOT already providing body info
            # 2. We haven't asked about the problem yet
            if not client_providing_body_info:
                # Check if we've already asked about the problem
                # Look at last 3 exchanges to see if therapist asked a problem question
                problem_question_asked = False
                if hasattr(session_state, 'conversation_history') and len(session_state.conversation_history) > 0:
                    for exchange in session_state.conversation_history[-3:]:
                        therapist_response = exchange.get('therapist_response', '').lower()
                        # Check for problem inquiry phrases
                        problem_phrases = ["what's been making it hard", "what's been making it difficult",
                                         "what's been getting in the way", "been making it hard"]
                        if any(phrase in therapist_response for phrase in problem_phrases):
                            problem_question_asked = True
                            break

                # Only apply this rule if we haven't asked about the problem yet
                if not problem_question_asked:
                    self.logger.info("🎯 OVERRIDE: In state 1.2, problem not identified → explore_problem FIRST (initial ask)")
                    return {
                        "current_stage": session_state.current_stage,
                        "current_substate": substate,
                        "navigation_decision": "explore_problem",
                        "situation_type": "problem_needs_exploration",
                        "rag_query": "dr_q_problem_construction",
                        "completion_status": completion,
                        "ready_for_next": False,
                        "advancement_blocked_by": ["problem_not_identified"],
                        "reasoning": "STRICT RULE: Explore problem FIRST before body exploration (state 1.2 entry, first ask)",
                        "recent_events": events,
                        "llm_reasoning": False,
                        "fallback_used": False,
                        "rule_override": True
                    }

        # RULE 5: CRITICAL - If client says "nothing else" after body enquiry → ADVANCE TO 3.1_assess_readiness
        # This happens when client responds "nothing" / "that's it" / "all good" to "What else should I know?"
        # MAX 2 body enquiry cycles OR client says "nothing else" → move to readiness assessment
        if substate == "1.2_problem_and_body":
            # Check if client said "nothing else" OR we've done 2 body enquiry cycles
            client_said_nothing_else = any(phrase in client_lower for phrase in [
                "nothing", "no", "that's it", "that's all", "nothing more", "nothing else",
                "nope", "nah", "i'm good", "all good", "im good", "that is it"
            ])

            # Also check if we've reached max body enquiry cycles (2)
            reached_max_cycles = session_state.body_enquiry_cycles >= 2

            # Check if we just asked "What else?" (therapist's last question)
            just_asked_what_else = False
            if hasattr(session_state, 'conversation_history') and len(session_state.conversation_history) > 0:
                last_exchange = session_state.conversation_history[-1]
                last_therapist_response = last_exchange.get('therapist_response', '').lower()
                what_else_phrases = ["what else", "anything else", "is there anything else", "anything i'm missing"]
                just_asked_what_else = any(phrase in last_therapist_response for phrase in what_else_phrases)

            # Advance to 3.1 if: (client said nothing else AND we asked) OR reached max cycles
            if (client_said_nothing_else and just_asked_what_else) or reached_max_cycles:
                self.logger.info(f"🎯 OVERRIDE: Client said 'nothing else' OR max cycles ({session_state.body_enquiry_cycles}/2) → ADVANCE to 3.1_assess_readiness")

                # Update substate to 3.1
                session_state.current_substate = "3.1_assess_readiness"

                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": "3.1_assess_readiness",  # ADVANCE!
                    "navigation_decision": "assess_readiness",
                    "situation_type": "readiness_for_alpha",
                    "rag_query": "dr_q_ready",
                    "completion_status": completion,
                    "ready_for_next": True,
                    "advancement_blocked_by": [],
                    "reasoning": f"STRICT RULE: Client said 'nothing else' OR reached max cycles ({session_state.body_enquiry_cycles}/2) → Advancing to readiness assessment",
                    "recent_events": events,
                    "llm_reasoning": False,
                    "fallback_used": False,
                    "rule_override": True
                }

        # RULE 6: If in 3.1_assess_readiness → NO MORE BODY QUESTIONS, assess readiness only
        # This prevents looping back to body exploration after we've already done it
        if substate == "3.1_assess_readiness":
            self.logger.info("🎯 OVERRIDE: In state 3.1 (readiness) → assess_readiness (NO body questions)")
            return {
                "current_stage": session_state.current_stage,
                "current_substate": substate,
                "navigation_decision": "assess_readiness",
                "situation_type": "readiness_for_alpha",
                "rag_query": "dr_q_ready",
                "completion_status": completion,
                "ready_for_next": True,
                "advancement_blocked_by": [],
                "reasoning": "STRICT RULE: In state 3.1, assess readiness for alpha (NO more body questions)",
                "recent_events": events,
                "llm_reasoning": False,
                "fallback_used": False,
                "rule_override": True
            }

        # No override needed - let LLM decide
        return None

    def make_navigation_decision(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Make navigation decision using Ollama LLM"""

        # Preprocess input
        processed_input = self.preprocessor.preprocess_input(client_input)
        corrected_input = processed_input['corrected_input']

        # Update session state
        completion_events = session_state.update_completion_status(corrected_input, processed_input)

        # Check advancement
        is_ready, next_substate = session_state.check_substate_completion()
        if is_ready:
            session_state.advance_substate(next_substate)

        # CRITICAL: Apply strict rule-based overrides BEFORE LLM
        rule_override = self._check_strict_rule_overrides(corrected_input, session_state, completion_events)
        if rule_override:
            # Add detections to override
            rule_override['self_harm_detected'] = processed_input.get('self_harm_detected', {'detected': False})
            rule_override['thinking_mode_detected'] = processed_input.get('thinking_mode_detected', {'detected': False})
            rule_override['past_tense_detected'] = processed_input.get('past_tense_detected', {'detected': False})
            rule_override['input_processing'] = {
                'original_input': client_input,
                'corrected_input': corrected_input,
                'emotional_state': processed_input['emotional_state'],
                'input_category': processed_input['input_category'],
                'spelling_corrections': processed_input['spelling_corrections']
            }
            return rule_override

        # Get LLM reasoning via Ollama
        llm_decision = self._get_llm_navigation_decision(
            corrected_input, session_state, completion_events, processed_input
        )

        # Add preprocessing information including PRIORITY DETECTIONS
        llm_decision['input_processing'] = {
            'original_input': client_input,
            'corrected_input': corrected_input,
            'emotional_state': processed_input['emotional_state'],
            'input_category': processed_input['input_category'],
            'spelling_corrections': processed_input['spelling_corrections']
        }

        # Pass through CRITICAL PRIORITY DETECTIONS
        llm_decision['self_harm_detected'] = processed_input.get('self_harm_detected', {'detected': False})
        llm_decision['thinking_mode_detected'] = processed_input.get('thinking_mode_detected', {'detected': False})
        llm_decision['past_tense_detected'] = processed_input.get('past_tense_detected', {'detected': False})

        return llm_decision

    def _get_llm_navigation_decision(self, client_input: str, session_state: TRTSessionState,
                                   events: list, processed_input: dict) -> dict:
        """Get navigation decision using Ollama LLM"""

        prompt = self._construct_therapeutic_prompt(
            client_input, session_state, events, processed_input
        )

        try:
            # Call Ollama
            llm_response = self._call_ollama(prompt)

            # Parse LLM response
            navigation_decision = self._parse_llm_response(
                llm_response, client_input, session_state, events
            )

            return navigation_decision

        except Exception as e:
            self.logger.error(f"Ollama LLM reasoning failed: {e}")
            # Fallback to rule-based decision
            return self._fallback_rule_based_decision(client_input, session_state, events)

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        try:
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 512
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Ollama returned status {response.status_code}: {response.text}")

        except Exception as e:
            self.logger.error(f"Ollama call failed: {e}")
            raise

    def _construct_therapeutic_prompt(self, client_input: str, session_state: TRTSessionState,
                                    events: list, processed_input: dict) -> str:
        """Construct therapeutic reasoning prompt"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate

        # Get recent conversation context
        recent_history = ""
        if hasattr(session_state, 'conversation_history') and session_state.conversation_history:
            recent_exchanges = session_state.conversation_history[-3:]
            for i, exchange in enumerate(recent_exchanges, 1):
                recent_history += f"Turn {i}: Client: \"{exchange.get('client_input', '')}\"\n"
                recent_history += f"         Therapist: \"{exchange.get('therapist_response', '')}\"\n\n"

        prompt = f"""You are Dr. Q, an expert TRT (Trauma Resolution Therapy) therapist. Make a navigation decision for this therapeutic moment.

CURRENT CONTEXT:
- Stage: {session_state.current_stage}
- Substate: {substate}
- Client: "{client_input}"
- Emotional State: {processed_input['emotional_state']}

COMPLETION STATUS:
- Goal Stated: {"✅" if completion.get('goal_stated', False) else "❌"}
- Vision Accepted: {"✅" if completion.get('vision_accepted', False) else "❌"}
- Problem Identified: {"✅" if completion.get('problem_identified', False) else "❌"}
- Body Awareness: {"✅" if completion.get('body_awareness_present', False) else "❌"}
- Present Focus: {"✅" if completion.get('present_moment_focus', False) else "❌"}

RECENT CONVERSATION:
{recent_history}

TRT RULES:
1. Stage 1.1: Establish goal, build future vision
2. Stage 1.2: Explore problem, develop body awareness
3. Stage 1.3: Assess pattern understanding, readiness for Stage 2
4. Always prioritize present-moment body awareness
5. Use "How do you know?" for pattern exploration
6. Don't advance until criteria met

NAVIGATION OPTIONS:
- clarify_goal, build_vision, explore_problem, body_awareness_inquiry, pattern_inquiry, assess_readiness, general_inquiry

SITUATION TYPES:
- goal_needs_clarification, goal_stated_needs_vision, problem_needs_exploration, body_symptoms_exploration, explore_trigger_pattern, readiness_for_stage_2, general_therapeutic_inquiry

RAG QUERIES:
- dr_q_goal_clarification, dr_q_future_self_vision_building, dr_q_problem_construction, dr_q_body_symptom_present_moment_inquiry, dr_q_how_do_you_know_technique, dr_q_transition_to_intervention, general_dr_q_approach

Respond in JSON format:
{{
    "reasoning": "detailed therapeutic reasoning",
    "navigation_decision": "one navigation option",
    "situation_type": "one situation type",
    "rag_query": "one rag query",
    "ready_for_next": true/false,
    "advancement_blocked_by": ["blocking factors"],
    "confidence": 0.0-1.0,
    "therapeutic_focus": "what to focus on"
}}"""

        return prompt

    def _parse_llm_response(self, llm_response: str, client_input: str,
                          session_state: TRTSessionState, events: list) -> dict:
        """Parse Ollama LLM response"""

        try:
            # Extract JSON
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                llm_decision = json.loads(json_str)

                # Add required fields
                base_decision = {
                    "current_stage": session_state.current_stage,
                    "current_substate": session_state.current_substate,
                    "completion_status": session_state.stage_1_completion,
                    "recent_events": events,
                    "llm_reasoning": True,
                    "llm_confidence": llm_decision.get("confidence", 0.8)
                }

                base_decision.update(llm_decision)

                # Ensure required fields
                required_fields = ["navigation_decision", "situation_type", "rag_query",
                                 "ready_for_next", "advancement_blocked_by", "reasoning"]

                for field in required_fields:
                    if field not in base_decision:
                        base_decision[field] = self._get_default_value(field)

                return base_decision

            else:
                raise ValueError("No valid JSON in Ollama response")

        except Exception as e:
            self.logger.error(f"Failed to parse Ollama response: {e}")
            return self._fallback_rule_based_decision(client_input, session_state, events)

    def _get_default_value(self, field: str):
        """Default values for missing fields"""
        defaults = {
            "navigation_decision": "general_inquiry",
            "situation_type": "general_therapeutic_inquiry",
            "rag_query": "general_dr_q_approach",
            "ready_for_next": False,
            "advancement_blocked_by": ["parsing_error"],
            "reasoning": "Using fallback decision"
        }
        return defaults.get(field, "unknown")

    def _fallback_rule_based_decision(self, client_input: str, session_state: TRTSessionState,
                                    events: list) -> dict:
        """Fallback rule-based logic"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate

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
                    "reasoning": "Fallback: Goal not stated",
                    "recent_events": events,
                    "llm_reasoning": False,
                    "fallback_used": True
                }
            else:
                return {
                    "current_stage": session_state.current_stage,
                    "current_substate": substate,
                    "navigation_decision": "build_vision",
                    "situation_type": "goal_stated_needs_vision",
                    "rag_query": "dr_q_future_self_vision_building",
                    "completion_status": completion,
                    "ready_for_next": False,
                    "advancement_blocked_by": ["vision_not_accepted"],
                    "reasoning": "Fallback: Building vision",
                    "recent_events": events,
                    "llm_reasoning": False,
                    "fallback_used": True
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
            "advancement_blocked_by": ["fallback_mode"],
            "reasoning": "Fallback: General inquiry",
            "recent_events": events,
            "llm_reasoning": False,
            "fallback_used": True
        }

    def get_system_status(self) -> dict:
        """System status"""
        return {
            "ollama_url": self.ollama_url,
            "model": self.model,
            "mode": "ollama"
        }
