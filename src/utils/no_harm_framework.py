"""
No-Harm Framework for TRT System
Handles self-harm and crisis situations while continuing therapeutic conversation
"""

import logging
from typing import Dict

class NoHarmFramework:
    """Framework for handling self-harm ideation and crisis situations"""

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Safety assessment levels
        self.safety_levels = {
            'immediate_danger': 'Client has plan, means, and intent',
            'high_risk': 'Client has thoughts and plan',
            'moderate_risk': 'Client has thoughts, no plan',
            'low_risk': 'Passive ideation, no intent',
            'safe': 'No current self-harm thoughts'
        }

    def generate_no_harm_response(self, client_input: str, self_harm_detection: Dict,
                                 session_context: Dict) -> Dict:
        """
        Generate therapeutic response that:
        1. Acknowledges the pain
        2. Assesses safety
        3. Continues conversation toward body awareness
        4. Does NOT terminate session
        """

        self.logger.warning(f"🚨 SELF-HARM DETECTED: {self_harm_detection['phrases_found']}")

        # Determine risk level based on language
        risk_level = self._assess_risk_level(client_input, self_harm_detection)

        # Generate appropriate response
        if risk_level in ['immediate_danger', 'high_risk']:
            return self._generate_high_risk_response(client_input, session_context)
        elif risk_level == 'moderate_risk':
            return self._generate_moderate_risk_response(client_input, session_context)
        else:
            return self._generate_low_risk_response(client_input, session_context)

    def _assess_risk_level(self, client_input: str, self_harm_detection: Dict) -> str:
        """Assess risk level from client input"""

        client_lower = client_input.lower()

        # Immediate danger indicators
        immediate_indicators = ['right now', 'going to', 'plan to', 'tonight', 'today']
        if any(indicator in client_lower for indicator in immediate_indicators):
            return 'immediate_danger'

        # High risk indicators
        high_risk_phrases = ['kill myself', 'end my life', 'suicide']
        if any(phrase in client_lower for phrase in high_risk_phrases):
            return 'high_risk'

        # Moderate risk indicators
        moderate_risk_phrases = ['want to die', 'better off dead']
        if any(phrase in client_lower for phrase in moderate_risk_phrases):
            return 'moderate_risk'

        # Low risk (passive ideation)
        return 'low_risk'

    def _generate_high_risk_response(self, client_input: str, session_context: Dict) -> Dict:
        """Response for high-risk situations"""

        response = """I hear you're having really serious thoughts about hurting yourself. Your safety is the most important thing right now.

Are you in a safe place? Do you have a plan to hurt yourself?

I want to help you through this, and we can do that together. But first I need to know you're safe."""

        return {
            'therapeutic_response': response,
            'technique_used': 'no_harm_high_risk',
            'safety_protocol_triggered': True,
            'risk_level': 'high_risk',
            'requires_immediate_assessment': True,
            'continue_session': True,  # Continue but with safety focus
            'navigation_reasoning': 'High-risk self-harm detected - safety assessment required',
            'llm_confidence': 1.0,
            'llm_reasoning': 'No-harm framework activated',
            'fallback_used': False
        }

    def _generate_moderate_risk_response(self, client_input: str, session_context: Dict) -> Dict:
        """Response for moderate-risk situations"""

        # Extract what they're feeling
        response = """I hear you're feeling like you don't want to live. That's a really heavy feeling, and it makes sense that you're here.

Are you safe right now? Are you thinking about hurting yourself?

Whatever's happening that's making you feel this way, we can work with it. But I need to know you're safe first."""

        return {
            'therapeutic_response': response,
            'technique_used': 'no_harm_moderate_risk',
            'safety_protocol_triggered': True,
            'risk_level': 'moderate_risk',
            'requires_immediate_assessment': True,
            'continue_session': True,
            'navigation_reasoning': 'Moderate-risk self-harm detected - safety check required',
            'llm_confidence': 1.0,
            'llm_reasoning': 'No-harm framework activated',
            'fallback_used': False
        }

    def _generate_low_risk_response(self, client_input: str, session_context: Dict) -> Dict:
        """Response for low-risk passive ideation - acknowledge and continue to body"""

        response = """I hear you're feeling really stressed and having thoughts about not wanting to live. That's heavy stuff, and it makes sense you're here.

Are you safe right now?

When you think about feeling stressed and not wanting to live, where do you feel that in your body?"""

        return {
            'therapeutic_response': response,
            'technique_used': 'no_harm_low_risk_continue',
            'safety_protocol_triggered': True,
            'risk_level': 'low_risk',
            'requires_immediate_assessment': False,
            'continue_session': True,
            'navigation_reasoning': 'Low-risk passive ideation - acknowledged and redirecting to body',
            'llm_confidence': 1.0,
            'llm_reasoning': 'No-harm framework activated - continuing therapeutic process',
            'fallback_used': False
        }

    def process_safety_response(self, client_safety_response: str) -> Dict:
        """Process client's response to safety assessment"""

        client_lower = client_safety_response.lower()

        # Check if they say they're safe
        safe_indicators = ['yes', 'i am safe', 'safe', 'no plan', 'not going to']
        unsafe_indicators = ['no', 'not safe', 'have a plan', 'going to', 'tonight']

        is_safe = any(indicator in client_lower for indicator in safe_indicators)
        is_unsafe = any(indicator in client_lower for indicator in unsafe_indicators)

        if is_unsafe or not is_safe:
            # Need more assessment
            return {
                'client_is_safe': False,
                'continue_normal_therapy': False,
                'next_response': """I'm concerned about your safety. Do you have someone there with you? Can you call someone or go to an emergency room?

I'm here with you, and we can talk through this. But I need to know you're not going to hurt yourself.""",
                'escalation_needed': True
            }
        else:
            # Client says they're safe - acknowledge and continue to goal/body work
            return {
                'client_is_safe': True,
                'continue_normal_therapy': True,
                'next_response': """Okay. I'm glad you're safe. Whatever's making you feel this way, we can work with it.

What do you want our time to accomplish? How do you want to feel when we're done?""",
                'escalation_needed': False
            }

    def get_emergency_resources(self) -> str:
        """Emergency resources message"""
        return """
EMERGENCY RESOURCES:
- National Suicide Prevention Lifeline: 988 (US)
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

If you're in immediate danger, please call 911 or go to your nearest emergency room.
"""
