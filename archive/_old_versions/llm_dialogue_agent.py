"""
LLM-Based Dialogue Agent using Llama 3.1
Advanced response generation with authentic TRT methodology
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from embedding_and_retrieval_setup import TRTRAGSystem
from session_state_manager import TRTSessionState
import logging

class LLMDialogueAgent:
    """LLM-powered Dialogue Agent with authentic Dr. Q style generation"""

    def __init__(self, rag_system: TRTRAGSystem, model_name="meta-llama/Llama-3.1-8B-Instruct"):
        self.rag_system = rag_system
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize LLM
        self._initialize_llm()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_llm(self):
        """Initialize Llama 3.1 model for dialogue generation"""
        try:
            # Use same quantization as master agent
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

            self.logger.info(f"✅ Dialogue LLM initialized: {self.model_name}")

        except Exception as e:
            self.logger.error(f"❌ Dialogue LLM initialization failed: {e}")
            # Use same fallback as master agent
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
            self.logger.info("🔄 Using fallback model for dialogue: DialoGPT-medium")

    def generate_response(self, client_input: str, navigation_output: dict,
                         session_state: TRTSessionState) -> dict:
        """Generate therapeutic response using LLM and RAG examples"""

        # Get RAG examples
        rag_examples = self.rag_system.get_few_shot_examples(
            navigation_output,
            client_input,
            max_examples=3
        )

        # Generate response using LLM
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
        """Generate therapeutic response using LLM reasoning"""

        prompt = self._construct_dialogue_prompt(
            client_input, navigation_output, rag_examples, session_state
        )

        try:
            # Generate LLM response
            llm_response = self._generate_llm_response(prompt)

            # Parse LLM response
            parsed_response = self._parse_dialogue_response(llm_response)

            return parsed_response

        except Exception as e:
            self.logger.error(f"LLM dialogue generation failed: {e}")
            # Fallback to rule-based response
            return self._fallback_response_generation(
                client_input, navigation_output, rag_examples, session_state
            )

    def _construct_dialogue_prompt(self, client_input: str, navigation_output: dict,
                                 rag_examples: list, session_state: TRTSessionState) -> str:
        """Construct detailed dialogue generation prompt"""

        decision = navigation_output["navigation_decision"]
        situation = navigation_output["situation_type"]
        substate = navigation_output["current_substate"]

        # Format RAG examples
        rag_examples_text = ""
        for i, example in enumerate(rag_examples, 1):
            rag_examples_text += f"Example {i} (similarity: {example['similarity_score']:.3f}):\n"
            rag_examples_text += f"  Client: \"{example.get('client_example', 'N/A')}\"\n"
            rag_examples_text += f"  Dr. Q: \"{example.get('doctor_example', 'N/A')}\"\n\n"

        # Get conversation history
        recent_history = ""
        if hasattr(session_state, 'conversation_history') and session_state.conversation_history:
            recent_exchanges = session_state.conversation_history[-2:]
            for i, exchange in enumerate(recent_exchanges, 1):
                recent_history += f"Turn {i}: Client: \"{exchange.get('client_input', '')}\"\n"
                recent_history += f"         Dr. Q: \"{exchange.get('therapist_response', '')}\"\n\n"

        # Check for repetitive responses
        response_history = getattr(session_state, 'response_history', [])
        recent_responses = response_history[-3:] if response_history else []

        # Format recent responses avoiding f-string backslash issue
        recent_responses_text = "\n".join([f"- \"{resp}\"" for resp in recent_responses])

        prompt = f"""You are Dr. Q, a master TRT (Trauma Resolution Therapy) therapist. Generate an authentic, therapeutic response for the current moment.

CURRENT THERAPEUTIC CONTEXT:
- Current Substate: {substate}
- Navigation Decision: {decision}
- Situation Type: {situation}
- Client Input: "{client_input}"
- LLM Reasoning: {navigation_output.get('reasoning', '')}

COMPLETION STATUS:
{navigation_output.get('completion_status', {})}

RECENT CONVERSATION HISTORY:
{recent_history}

RECENT THERAPIST RESPONSES (avoid repetition):
{recent_responses_text}

SIMILAR RAG EXAMPLES FROM DR. Q:
{rag_examples_text}

TRT THERAPEUTIC PRINCIPLES:
1. Always prioritize present-moment awareness
2. Focus on body sensations and somatic experience
3. Use authentic, warm, and empathetic tone
4. Ask specific, clarifying questions rather than general ones
5. Avoid interpretation or analysis - stay with client experience
6. Use "How do you know?" technique for pattern exploration
7. Build future self vision when appropriate
8. Acknowledge emotions before asking questions
9. Keep responses concise and focused
10. Avoid repeating the same questions

SPECIFIC RESPONSE GUIDELINES BY DECISION:

clarify_goal:
- Use Dr. Q's exact questions: "What do you want our time to get accomplished? What do we want to get better for you?"
- Acknowledge emotional state first if present

build_vision:
- Present specific future self vision
- Check if vision resonates: "Does that vision feel right to you?"
- Adapt if vision has been presented multiple times

explore_problem:
- Ask about specific patterns and triggers
- Focus on present moment: "What's happening now?"
- Handle positive responses appropriately

body_awareness_inquiry:
- Direct attention to body: "What do you notice in your body right now?"
- Present moment focus: "How's your body feeling as you're talking about that?"

pattern_inquiry:
- Use "How do you know?" technique
- Explore onset patterns: "What lets you know it's beginning?"

assess_readiness:
- Check understanding: "What haven't I understood?"
- Assess readiness for next stage

RESPONSE REQUIREMENTS:
- Be authentic to Dr. Q's style from the RAG examples
- Keep response under 2 sentences typically
- Sound natural and conversational
- Show empathy and understanding
- Avoid therapeutic jargon
- Make it feel like a real therapeutic conversation

Generate your response in this JSON format:
{{
    "response": "Your therapeutic response as Dr. Q",
    "reasoning": "Why this response is appropriate for this moment",
    "confidence": 0.0-1.0,
    "technique_focus": "What therapeutic technique you're using"
}}"""

        return prompt

    def _generate_llm_response(self, prompt: str) -> str:
        """Generate response using LLM"""

        inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=3072)
        inputs = inputs.to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=256,
                temperature=0.4,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.2
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the generated part
        if prompt in response:
            response = response.split(prompt)[1].strip()

        return response

    def _parse_dialogue_response(self, llm_response: str) -> dict:
        """Parse LLM dialogue response"""

        try:
            # Extract JSON from response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)

                # Ensure response exists
                if "response" not in parsed or not parsed["response"].strip():
                    raise ValueError("No response found in LLM output")

                return {
                    "response": parsed.get("response", "").strip(),
                    "reasoning": parsed.get("reasoning", ""),
                    "confidence": parsed.get("confidence", 0.7),
                    "technique_focus": parsed.get("technique_focus", ""),
                    "fallback_used": False
                }

            else:
                # Try to extract response without JSON
                lines = llm_response.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('{') and not line.startswith('"'):
                        return {
                            "response": line.strip(),
                            "reasoning": "Extracted from non-JSON LLM response",
                            "confidence": 0.6,
                            "technique_focus": "general_inquiry",
                            "fallback_used": True
                        }

                raise ValueError("Could not extract response from LLM output")

        except Exception as e:
            self.logger.error(f"Failed to parse dialogue response: {e}")
            raise

    def _fallback_response_generation(self, client_input: str, navigation_output: dict,
                                    rag_examples: list, session_state: TRTSessionState) -> dict:
        """Fallback to rule-based response generation"""

        decision = navigation_output["navigation_decision"]
        client_lower = client_input.lower()

        # Simple rule-based responses as fallback
        fallback_responses = {
            "clarify_goal": "What do you want our time to get accomplished?",
            "build_vision": "I'm seeing you who used to have that problem now wouldn't be able to get it. Does that vision feel right to you?",
            "explore_problem": "What's been making it hard for you to feel that way?",
            "body_awareness_inquiry": "What do you notice in your body right now?",
            "pattern_inquiry": "How do you know when that feeling starts?",
            "assess_readiness": "What haven't I understood? Is there more I should know?",
            "general_inquiry": "What made that disturbing for you?"
        }

        # Add emotional acknowledgment for certain inputs
        response = ""
        if any(word in client_lower for word in ["sad", "depressed", "low"]):
            response = "I hear that you're feeling low right now. "
        elif any(word in client_lower for word in ["stressed", "anxious", "overwhelmed"]):
            response = "I can hear the stress you're experiencing. "

        response += fallback_responses.get(decision, "What else would be useful for me to know?")

        return {
            "response": response,
            "reasoning": f"Fallback response for {decision}",
            "confidence": 0.5,
            "technique_focus": decision,
            "fallback_used": True
        }

    def get_system_status(self) -> dict:
        """Get current system status"""
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "model_loaded": hasattr(self, 'model') and self.model is not None,
            "tokenizer_loaded": hasattr(self, 'tokenizer') and self.tokenizer is not None
        }