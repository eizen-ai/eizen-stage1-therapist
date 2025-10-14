"""
API-Based Master Planning Agent
Uses external LLM API endpoint instead of loading models locally
"""

import json
import requests
from session_state_manager import TRTSessionState
from input_preprocessing import InputPreprocessor
import logging

class APILLMMasterPlanningAgent:
    """API-powered Master Planning Agent using external LLM endpoint"""

    def __init__(self, api_endpoint="http://192.168.0.90:8098/complete-generate"):
        self.api_endpoint = api_endpoint

        # Load TRT methodology rules
        with open('core_system/simplified_navigation.json', 'r') as f:
            self.navigation = json.load(f)

        with open('core_system/input_classification_patterns.json', 'r') as f:
            self.patterns = json.load(f)

        # Initialize input preprocessor
        self.preprocessor = InputPreprocessor()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Test API connection
        self._test_api_connection()

    def _test_api_connection(self):
        """Test if API endpoint is accessible"""
        try:
            response = requests.post(
                self.api_endpoint,
                json={"prompt": "test", "max_tokens": 5},
                timeout=5
            )
            if response.status_code == 200:
                self.logger.info(f"✅ API endpoint connected: {self.api_endpoint}")
            else:
                self.logger.warning(f"⚠️ API returned status {response.status_code}")
        except Exception as e:
            self.logger.error(f"❌ Cannot connect to API: {e}")
            self.logger.info("Will use fallback rule-based logic")

    def make_navigation_decision(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Make navigation decision using API LLM"""

        # Preprocess input
        processed_input = self.preprocessor.preprocess_input(client_input)
        corrected_input = processed_input['corrected_input']

        # Update session state
        completion_events = session_state.update_completion_status(corrected_input, processed_input)

        # Check advancement
        is_ready, next_substate = session_state.check_substate_completion()
        if is_ready:
            session_state.advance_substate(next_substate)

        # Get LLM reasoning via API
        llm_decision = self._get_llm_navigation_decision(
            corrected_input, session_state, completion_events, processed_input
        )

        # Add preprocessing information
        llm_decision['input_processing'] = {
            'original_input': client_input,
            'corrected_input': corrected_input,
            'emotional_state': processed_input['emotional_state'],
            'input_category': processed_input['input_category'],
            'spelling_corrections': processed_input['spelling_corrections']
        }

        return llm_decision

    def _get_llm_navigation_decision(self, client_input: str, session_state: TRTSessionState,
                                   events: list, processed_input: dict) -> dict:
        """Get navigation decision using API LLM"""

        prompt = self._construct_therapeutic_prompt(
            client_input, session_state, events, processed_input
        )

        try:
            # Call API
            llm_response = self._call_api(prompt)

            # Parse LLM response
            navigation_decision = self._parse_llm_response(
                llm_response, client_input, session_state, events
            )

            return navigation_decision

        except Exception as e:
            self.logger.error(f"API LLM reasoning failed: {e}")
            # Fallback to rule-based decision
            return self._fallback_rule_based_decision(client_input, session_state, events)

    def _call_api(self, prompt: str, max_tokens: int = 512) -> str:
        """Call external LLM API"""
        try:
            response = requests.post(
                self.api_endpoint,
                json={
                    "complete_input": prompt  # Your API expects 'complete_input'
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                # Handle different possible response formats
                if isinstance(result, dict):
                    return result.get('generated_text', result.get('answer', result.get('text', str(result))))
                return str(result)
            else:
                raise Exception(f"API returned status {response.status_code}: {response.text}")

        except Exception as e:
            self.logger.error(f"API call failed: {e}")
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
        """Parse API LLM response"""

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
                raise ValueError("No valid JSON in API response")

        except Exception as e:
            self.logger.error(f"Failed to parse API response: {e}")
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
            "api_endpoint": self.api_endpoint,
            "mode": "api_based"
        }
