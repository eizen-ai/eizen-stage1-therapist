"""
API-Based Dialogue Agent
Uses external LLM API endpoint for response generation
"""

import json
import requests
from embedding_and_retrieval_setup import TRTRAGSystem
from session_state_manager import TRTSessionState
import logging

class APILLMDialogueAgent:
    """API-powered Dialogue Agent using external LLM endpoint"""

    def __init__(self, rag_system: TRTRAGSystem, api_endpoint="http://192.168.0.90:8098/complete-generate"):
        self.rag_system = rag_system
        self.api_endpoint = api_endpoint

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"✅ API Dialogue Agent initialized: {api_endpoint}")

    def generate_response(self, client_input: str, navigation_output: dict,
                         session_state: TRTSessionState) -> dict:
        """Generate therapeutic response using API LLM and RAG"""

        # Get RAG examples
        rag_examples = self.rag_system.get_few_shot_examples(
            navigation_output,
            client_input,
            max_examples=3
        )

        # Generate response using API LLM
        llm_response = self._generate_llm_therapeutic_response(
            client_input, navigation_output, rag_examples, session_state
        )

        return {
            "therapeutic_response": llm_response["response"],
            "technique_used": navigation_output["rag_query"],
            "examples_used": len(rag_examples),
            "rag_similarity_scores": [ex["similarity_score"] for ex in rag_examples],
            "navigation_reasoning": navigation_output["reasoning"],
            "llm_confidence": llm_response.get("confidence", 0.8),
            "llm_reasoning": llm_response.get("reasoning", ""),
            "fallback_used": llm_response.get("fallback_used", False)
        }

    def _generate_llm_therapeutic_response(self, client_input: str, navigation_output: dict,
                                         rag_examples: list, session_state: TRTSessionState) -> dict:
        """Generate response using API LLM"""

        prompt = self._construct_dialogue_prompt(
            client_input, navigation_output, rag_examples, session_state
        )

        try:
            # Call API
            llm_response = self._call_api(prompt, max_tokens=256)

            # Parse response
            parsed_response = self._parse_dialogue_response(llm_response)

            return parsed_response

        except Exception as e:
            self.logger.error(f"API dialogue generation failed: {e}")
            # Fallback
            return self._fallback_response_generation(
                client_input, navigation_output, rag_examples, session_state
            )

    def _call_api(self, prompt: str, max_tokens: int = 256) -> str:
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
                if isinstance(result, dict):
                    return result.get('generated_text', result.get('answer', result.get('text', str(result))))
                return str(result)
            else:
                raise Exception(f"API returned status {response.status_code}: {response.text}")

        except Exception as e:
            self.logger.error(f"API call failed: {e}")
            raise

    def _construct_dialogue_prompt(self, client_input: str, navigation_output: dict,
                                 rag_examples: list, session_state: TRTSessionState) -> str:
        """Construct dialogue generation prompt"""

        decision = navigation_output["navigation_decision"]
        situation = navigation_output["situation_type"]
        substate = navigation_output["current_substate"]

        # Format RAG examples
        rag_examples_text = ""
        for i, example in enumerate(rag_examples, 1):
            rag_examples_text += f"Example {i} (similarity: {example['similarity_score']:.3f}):\n"
            rag_examples_text += f"  Dr. Q: \"{example.get('doctor_example', 'N/A')}\"\n\n"

        # Conversation history
        recent_history = ""
        if hasattr(session_state, 'conversation_history') and session_state.conversation_history:
            recent_exchanges = session_state.conversation_history[-2:]
            for i, exchange in enumerate(recent_exchanges, 1):
                recent_history += f"Turn {i}: Client: \"{exchange.get('client_input', '')}\"\n"
                recent_history += f"         Dr. Q: \"{exchange.get('therapist_response', '')}\"\n\n"

        prompt = f"""You are Dr. Q, a master TRT therapist. Generate an authentic therapeutic response.

CONTEXT:
- Substate: {substate}
- Decision: {decision}
- Situation: {situation}
- Client: "{client_input}"

RECENT CONVERSATION:
{recent_history}

DR. Q EXAMPLES:
{rag_examples_text}

TRT PRINCIPLES:
1. Present-moment awareness
2. Focus on body sensations
3. Warm, empathetic tone
4. Specific clarifying questions
5. Stay with client experience
6. "How do you know?" technique
7. Build future vision
8. Acknowledge emotions first
9. Concise responses
10. Avoid repetition

RESPONSE GUIDELINES:

clarify_goal:
- "What do you want our time to accomplish? What do we want to get better for you?"

build_vision:
- Present specific future vision
- "Does that vision feel right to you?"

explore_problem:
- Ask about patterns and triggers
- "What's happening now?"

body_awareness_inquiry:
- "What do you notice in your body right now?"

pattern_inquiry:
- "How do you know?"
- "What lets you know it's beginning?"

assess_readiness:
- "What haven't I understood?"

REQUIREMENTS:
- Use Dr. Q's style from examples
- Keep under 2 sentences
- Natural and conversational
- Show empathy
- Avoid jargon

JSON format:
{{
    "response": "Your therapeutic response",
    "reasoning": "Why appropriate",
    "confidence": 0.0-1.0,
    "technique_focus": "technique used"
}}"""

        return prompt

    def _parse_dialogue_response(self, llm_response: str) -> dict:
        """Parse API dialogue response"""

        try:
            # Extract JSON
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)

                if "response" not in parsed or not parsed["response"].strip():
                    raise ValueError("No response in output")

                return {
                    "response": parsed.get("response", "").strip(),
                    "reasoning": parsed.get("reasoning", ""),
                    "confidence": parsed.get("confidence", 0.7),
                    "technique_focus": parsed.get("technique_focus", ""),
                    "fallback_used": False
                }

            else:
                # Try extracting without JSON
                lines = llm_response.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('{') and not line.startswith('"'):
                        return {
                            "response": line.strip(),
                            "reasoning": "Extracted from non-JSON",
                            "confidence": 0.6,
                            "technique_focus": "general_inquiry",
                            "fallback_used": True
                        }

                raise ValueError("Could not extract response")

        except Exception as e:
            self.logger.error(f"Failed to parse dialogue: {e}")
            raise

    def _fallback_response_generation(self, client_input: str, navigation_output: dict,
                                    rag_examples: list, session_state: TRTSessionState) -> dict:
        """Fallback rule-based responses"""

        decision = navigation_output["navigation_decision"]
        client_lower = client_input.lower()

        fallback_responses = {
            "clarify_goal": "What do you want our time to get accomplished?",
            "build_vision": "I'm seeing you who used to have that problem now wouldn't be able to get it. Does that vision feel right to you?",
            "explore_problem": "What's been making it hard for you to feel that way?",
            "body_awareness_inquiry": "What do you notice in your body right now?",
            "pattern_inquiry": "How do you know when that feeling starts?",
            "assess_readiness": "What haven't I understood? Is there more I should know?",
            "general_inquiry": "What made that disturbing for you?"
        }

        # Add emotional acknowledgment
        response = ""
        if any(word in client_lower for word in ["sad", "depressed", "low"]):
            response = "I hear that you're feeling low right now. "
        elif any(word in client_lower for word in ["stressed", "anxious", "overwhelmed"]):
            response = "I can hear the stress you're experiencing. "

        response += fallback_responses.get(decision, "What else would be useful for me to know?")

        return {
            "response": response,
            "reasoning": f"Fallback for {decision}",
            "confidence": 0.5,
            "technique_focus": decision,
            "fallback_used": True
        }

    def get_system_status(self) -> dict:
        """System status"""
        return {
            "api_endpoint": self.api_endpoint,
            "mode": "api_based"
        }
