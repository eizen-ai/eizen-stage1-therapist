"""
LLM-Based Master Planning Agent using Llama 3.1
Advanced reasoning for therapeutic navigation decisions
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from session_state_manager import TRTSessionState
from input_preprocessing import InputPreprocessor
import logging

class LLMMasterPlanningAgent:
    """LLM-powered Master Planning Agent with Llama 3.1 reasoning"""

    def __init__(self, model_name="meta-llama/Llama-3.1-8B-Instruct"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load TRT methodology rules
        with open('core_system/simplified_navigation.json', 'r') as f:
            self.navigation = json.load(f)

        with open('core_system/input_classification_patterns.json', 'r') as f:
            self.patterns = json.load(f)

        # Initialize input preprocessor
        self.preprocessor = InputPreprocessor()

        # Initialize LLM with quantization for efficiency
        self._initialize_llm()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_llm(self):
        """Initialize Llama 3.1 model with optimized settings"""
        try:
            # Quantization config for memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="left"
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16
            )

            self.logger.info(f"✅ LLM initialized: {self.model_name}")

        except Exception as e:
            self.logger.error(f"❌ LLM initialization failed: {e}")
            # Fallback to CPU and no quantization
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
            self.logger.info("🔄 Using fallback model: DialoGPT-medium")

    def make_navigation_decision(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Make LLM-powered navigation decision"""

        # Preprocess input
        processed_input = self.preprocessor.preprocess_input(client_input)
        corrected_input = processed_input['corrected_input']

        # Update session state
        completion_events = session_state.update_completion_status(corrected_input, processed_input)

        # Check advancement
        is_ready, next_substate = session_state.check_substate_completion()
        if is_ready:
            session_state.advance_substate(next_substate)

        # Get LLM reasoning
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
        """Get navigation decision using LLM reasoning"""

        # Construct detailed prompt for LLM reasoning
        prompt = self._construct_therapeutic_prompt(
            client_input, session_state, events, processed_input
        )

        try:
            # Generate LLM response
            llm_response = self._generate_llm_response(prompt)

            # Parse LLM response into structured decision
            navigation_decision = self._parse_llm_response(
                llm_response, client_input, session_state, events
            )

            return navigation_decision

        except Exception as e:
            self.logger.error(f"LLM reasoning failed: {e}")
            # Fallback to rule-based decision
            return self._fallback_rule_based_decision(client_input, session_state, events)

    def _construct_therapeutic_prompt(self, client_input: str, session_state: TRTSessionState,
                                    events: list, processed_input: dict) -> str:
        """Construct detailed therapeutic reasoning prompt"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate

        # Get recent conversation context
        recent_history = ""
        if hasattr(session_state, 'conversation_history') and session_state.conversation_history:
            recent_exchanges = session_state.conversation_history[-3:]
            for i, exchange in enumerate(recent_exchanges, 1):
                recent_history += f"Turn {i}: Client: \"{exchange.get('client_input', '')}\"\n"
                recent_history += f"         Therapist: \"{exchange.get('therapist_response', '')}\"\n\n"

        prompt = f"""You are Dr. Q, an expert TRT (Trauma Resolution Therapy) therapist. You need to make a navigation decision for the current therapeutic moment.

CURRENT THERAPEUTIC CONTEXT:
- Current Stage: {session_state.current_stage}
- Current Substate: {substate}
- Client Input: "{client_input}"
- Emotional State Detected: {processed_input['emotional_state']}
- Input Category: {processed_input['input_category']}

COMPLETION STATUS:
- Goal Stated: {"✅" if completion.get('goal_stated', False) else "❌"}
- Vision Accepted: {"✅" if completion.get('vision_accepted', False) else "❌"}
- Problem Identified: {"✅" if completion.get('problem_identified', False) else "❌"}
- Body Awareness: {"✅" if completion.get('body_awareness_present', False) else "❌"}
- Present Moment Focus: {"✅" if completion.get('present_moment_focus', False) else "❌"}

RECENT CONVERSATION:
{recent_history}

RECENT EVENTS: {events}

TRT METHODOLOGY RULES:
1. Stage 1.1 (Goal & Vision): Must establish clear goal, then build future self vision
2. Stage 1.2 (Problem & Body): Explore specific problems and build present-moment body awareness
3. Stage 1.3 (Readiness): Assess pattern understanding and readiness for Stage 2
4. Always prioritize present-moment awareness and body sensations
5. Use "How do you know?" technique for pattern exploration
6. Don't advance until completion criteria are met
7. Recognize implicit acceptance through continued emotional sharing

POSSIBLE NAVIGATION DECISIONS:
- clarify_goal: Ask what client wants to accomplish
- build_vision: Present future self vision
- explore_problem: Investigate specific problems
- body_awareness_inquiry: Focus on present-moment body sensations
- pattern_inquiry: Use "how do you know" technique
- assess_readiness: Check readiness for Stage 2
- general_inquiry: Continue therapeutic exploration

POSSIBLE SITUATION TYPES:
- goal_needs_clarification
- goal_stated_needs_vision
- problem_needs_exploration
- body_symptoms_exploration
- explore_trigger_pattern
- readiness_for_stage_2
- general_therapeutic_inquiry

POSSIBLE RAG QUERIES:
- dr_q_goal_clarification
- dr_q_future_self_vision_building
- dr_q_problem_construction
- dr_q_body_symptom_present_moment_inquiry
- dr_q_how_do_you_know_technique
- dr_q_transition_to_intervention
- general_dr_q_approach

Based on the current therapeutic context, reasoning through TRT methodology, what is the most appropriate navigation decision?

Respond in this exact JSON format:
{{
    "reasoning": "Your detailed therapeutic reasoning about what's happening and why this decision is appropriate",
    "navigation_decision": "one of the possible navigation decisions",
    "situation_type": "one of the possible situation types",
    "rag_query": "one of the possible RAG queries",
    "ready_for_next": true/false,
    "advancement_blocked_by": ["list", "of", "blocking", "factors"],
    "confidence": 0.0-1.0,
    "therapeutic_focus": "what the therapist should focus on"
}}"""

        return prompt

    def _generate_llm_response(self, prompt: str) -> str:
        """Generate response using LLM"""

        inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = inputs.to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=512,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the generated part (after the prompt)
        if prompt in response:
            response = response.split(prompt)[1].strip()

        return response

    def _parse_llm_response(self, llm_response: str, client_input: str,
                          session_state: TRTSessionState, events: list) -> dict:
        """Parse LLM response into structured navigation decision"""

        try:
            # Try to extract JSON from response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                llm_decision = json.loads(json_str)

                # Validate and add required fields
                base_decision = {
                    "current_stage": session_state.current_stage,
                    "current_substate": session_state.current_substate,
                    "completion_status": session_state.stage_1_completion,
                    "recent_events": events,
                    "llm_reasoning": True,
                    "llm_confidence": llm_decision.get("confidence", 0.8)
                }

                # Merge LLM decision with base
                base_decision.update(llm_decision)

                # Ensure required fields exist
                required_fields = ["navigation_decision", "situation_type", "rag_query",
                                 "ready_for_next", "advancement_blocked_by", "reasoning"]

                for field in required_fields:
                    if field not in base_decision:
                        base_decision[field] = self._get_default_value(field)

                return base_decision

            else:
                raise ValueError("No valid JSON found in LLM response")

        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            self.logger.error(f"LLM Response: {llm_response}")

            # Fallback to rule-based decision
            return self._fallback_rule_based_decision(client_input, session_state, events)

    def _get_default_value(self, field: str):
        """Get default values for missing fields"""
        defaults = {
            "navigation_decision": "general_inquiry",
            "situation_type": "general_therapeutic_inquiry",
            "rag_query": "general_dr_q_approach",
            "ready_for_next": False,
            "advancement_blocked_by": ["llm_parsing_error"],
            "reasoning": "LLM response parsing failed, using fallback decision"
        }
        return defaults.get(field, "unknown")

    def _fallback_rule_based_decision(self, client_input: str, session_state: TRTSessionState,
                                    events: list) -> dict:
        """Fallback to rule-based decision if LLM fails"""

        completion = session_state.stage_1_completion
        substate = session_state.current_substate
        client_lower = client_input.lower()

        # Simple rule-based logic as fallback
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
                    "reasoning": "Fallback: Goal not yet stated, need clarification",
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
                    "reasoning": "Fallback: Goal stated, building vision",
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
            "reasoning": "Fallback: Using general therapeutic inquiry",
            "recent_events": events,
            "llm_reasoning": False,
            "fallback_used": True
        }

    def get_system_status(self) -> dict:
        """Get current system status for monitoring"""
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "model_loaded": hasattr(self, 'model') and self.model is not None,
            "tokenizer_loaded": hasattr(self, 'tokenizer') and self.tokenizer is not None
        }