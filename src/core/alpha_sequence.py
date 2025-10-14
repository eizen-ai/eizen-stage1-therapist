"""
Alpha Sequence Module
Implements Dr. Q's alpha sequence for down-regulation:
1. Structured checking at each step (jaw, tongue, breathing)
2. Validation at each checkpoint ("More tense or more calm?")
3. Down-regulation indicator tracking
4. Resistance normalization
"""

from typing import Dict, Optional, List
from enum import Enum


class AlphaStep(Enum):
    """Alpha sequence steps"""
    LOWER_JAW = 1
    RELAX_TONGUE = 2
    BREATHE_SLOWER = 3
    COMPLETE = 4


class DownRegulationIndicator(Enum):
    """Indicators of successful down-regulation"""
    SLOW_DEEP_BREATH = "slow_deep_breath_in"
    LONGER_EXHALE = "longer_exhale"
    UNCONSCIOUS_DEEP_BREATHING = "unconscious_deep_breathing"
    SOFTENING_FACIAL = "softening_facial_features"
    VERBAL_CONFIRMATION = "verbal_calm_confirmation"


class AlphaSequence:
    """Manages alpha sequence progression and down-regulation tracking"""

    def __init__(self):
        self.current_step = AlphaStep.LOWER_JAW
        self.completed_steps = []
        self.checkpoint_responses = {}
        self.down_regulation_indicators = []
        self.resistance_encountered = False
        self.sequence_active = False

    def start_sequence(self) -> Dict:
        """
        Start the alpha sequence

        Returns:
            Initial instruction and checkpoint question
        """
        self.sequence_active = True
        self.current_step = AlphaStep.LOWER_JAW
        self.completed_steps = []
        self.checkpoint_responses = {}
        self.down_regulation_indicators = []
        self.resistance_encountered = False

        return {
            "instruction": "Let's do something simple. Lower your jaw slightly - just let it drop a little. Not all the way, just enough to release the tension.",
            "checkpoint_question": "As you do that, are you feeling more tense or more calm?",
            "step": AlphaStep.LOWER_JAW.name,
            "expects_checkpoint_response": True
        }

    def process_checkpoint_response(self, client_response: str, step: Optional[AlphaStep] = None) -> Dict:
        """
        Process client's response to checkpoint question

        Args:
            client_response: Client's answer to "more tense or more calm?"
            step: Current step (defaults to self.current_step)

        Returns:
            Next action (continue, normalize resistance, or complete)
        """
        if step is None:
            step = self.current_step

        response_lower = client_response.lower()

        # Detect response type
        if any(word in response_lower for word in ["calm", "calmer", "relaxed", "better", "good"]):
            # Positive response - proceed
            self.checkpoint_responses[step] = "calm"
            self.completed_steps.append(step)

            # Detect down-regulation indicators
            self._detect_down_regulation_indicators(client_response)

            # Move to next step
            return self._get_next_step_instruction(step)

        elif any(word in response_lower for word in ["tense", "tension", "worse", "uncomfortable", "weird"]):
            # Resistance detected
            self.checkpoint_responses[step] = "tense"
            self.resistance_encountered = True

            return self._normalize_resistance(step)

        elif any(word in response_lower for word in ["same", "no change", "neutral", "don't know"]):
            # Neutral response - gentle encouragement
            return {
                "response": "That's okay. Just notice what you're experiencing. Take a moment.",
                "action": "wait_and_retry",
                "retry_checkpoint": True
            }

        else:
            # Unclear response - re-ask
            return {
                "response": "I'm asking: as you lower your jaw, are you feeling more tense or more calm?",
                "action": "clarify_checkpoint",
                "retry_checkpoint": True
            }

    def _get_next_step_instruction(self, completed_step: AlphaStep) -> Dict:
        """Get instruction for next step after successful checkpoint"""

        if completed_step == AlphaStep.LOWER_JAW:
            self.current_step = AlphaStep.RELAX_TONGUE
            return {
                "response": "Good. Now, relax your tongue. Let it rest gently in your mouth, not pressed against anything.",
                "checkpoint_question": "More tense or more calm?",
                "step": AlphaStep.RELAX_TONGUE.name,
                "expects_checkpoint_response": True
            }

        elif completed_step == AlphaStep.RELAX_TONGUE:
            self.current_step = AlphaStep.BREATHE_SLOWER
            return {
                "response": "That's right. Now, breathe a little slower. Not forcing it, just allowing your breath to slow down naturally.",
                "checkpoint_question": "More tense or more calm?",
                "step": AlphaStep.BREATHE_SLOWER.name,
                "expects_checkpoint_response": True
            }

        elif completed_step == AlphaStep.BREATHE_SLOWER:
            self.current_step = AlphaStep.COMPLETE
            return {
                "response": "Perfect. Notice how your body feels now compared to when we started. You've just shifted your brain state.",
                "action": "sequence_complete",
                "next_phase": "ready_for_intervention",
                "down_regulation_achieved": True
            }

        else:
            # Shouldn't happen, but fallback
            return {
                "response": "Good. Let's continue.",
                "action": "continue"
            }

    def _normalize_resistance(self, step: AlphaStep) -> Dict:
        """Normalize resistance when client feels more tense"""

        normalization_responses = {
            AlphaStep.LOWER_JAW: "Of course it feels different - you've never done this before. That's completely normal. The unfamiliar feeling is just your brain noticing the change. Can you stay with it for a moment?",
            AlphaStep.RELAX_TONGUE: "That makes sense. Your body is not used to this. The tension you're noticing is just resistance to change. Breathe and stay with it. More tense or more calm now?",
            AlphaStep.BREATHE_SLOWER: "I understand. Slowing down can feel strange at first. Your body is used to being activated. Just allow the breath to slow naturally. Notice now - more tense or more calm?"
        }

        return {
            "response": normalization_responses.get(step, "That's normal. This is new for your body. Stay with it."),
            "action": "normalize_and_retry",
            "resistance_normalized": True,
            "retry_checkpoint": True
        }

    def _detect_down_regulation_indicators(self, client_response: str):
        """Detect physiological down-regulation indicators"""

        response_lower = client_response.lower()

        # Check for indicators
        if any(phrase in response_lower for phrase in ["deep breath", "breathing deep", "took a breath"]):
            self.down_regulation_indicators.append(DownRegulationIndicator.SLOW_DEEP_BREATH)

        if any(phrase in response_lower for phrase in ["exhale", "breathe out", "breathing out"]):
            self.down_regulation_indicators.append(DownRegulationIndicator.LONGER_EXHALE)

        if any(phrase in response_lower for phrase in ["soft", "relax", "loose", "lighter"]):
            self.down_regulation_indicators.append(DownRegulationIndicator.SOFTENING_FACIAL)

        if any(phrase in response_lower for phrase in ["calm", "peaceful", "relaxed", "better"]):
            self.down_regulation_indicators.append(DownRegulationIndicator.VERBAL_CONFIRMATION)

    def detect_indicators_from_observation(self, observations: List[str]):
        """
        Detect down-regulation from external observations (video/audio)

        Args:
            observations: List of observed indicators
                Examples: ["slow_deep_breath", "facial_softening", "longer_exhale"]
        """
        for obs in observations:
            try:
                indicator = DownRegulationIndicator(obs)
                if indicator not in self.down_regulation_indicators:
                    self.down_regulation_indicators.append(indicator)
            except ValueError:
                # Invalid indicator, skip
                pass

    def is_down_regulated(self) -> bool:
        """
        Determine if client has achieved down-regulation

        Returns:
            Boolean indicating down-regulation state
        """
        # Client is down-regulated if:
        # 1. At least 2 checkpoints passed with "calm" response
        calm_responses = sum(1 for resp in self.checkpoint_responses.values() if resp == "calm")

        # 2. At least one physiological indicator observed
        has_physiological_indicator = len(self.down_regulation_indicators) > 0

        return calm_responses >= 2 and has_physiological_indicator

    def get_sequence_summary(self) -> Dict:
        """Get summary of alpha sequence session"""

        return {
            "sequence_active": self.sequence_active,
            "current_step": self.current_step.name if self.sequence_active else None,
            "completed_steps": [step.name for step in self.completed_steps],
            "checkpoint_responses": {step.name: resp for step, resp in self.checkpoint_responses.items()},
            "down_regulation_indicators": [ind.value for ind in self.down_regulation_indicators],
            "down_regulated": self.is_down_regulated(),
            "resistance_encountered": self.resistance_encountered
        }

    def reset(self):
        """Reset sequence for new session"""
        self.current_step = AlphaStep.LOWER_JAW
        self.completed_steps = []
        self.checkpoint_responses = {}
        self.down_regulation_indicators = []
        self.resistance_encountered = False
        self.sequence_active = False


# Example usage and testing
if __name__ == "__main__":
    alpha = AlphaSequence()

    print("=" * 80)
    print("ALPHA SEQUENCE TEST")
    print("=" * 80)

    # Start sequence
    print("\n1. STARTING SEQUENCE:")
    print("-" * 80)
    start = alpha.start_sequence()
    print(f"Therapist: \"{start['instruction']}\"")
    print(f"Therapist: \"{start['checkpoint_question']}\"")

    # Simulate client responses
    print("\n2. CLIENT RESPONSES:")
    print("-" * 80)

    # Step 1: Lower jaw - calm response
    print("\nClient: \"I feel calmer\"")
    response1 = alpha.process_checkpoint_response("I feel calmer")
    print(f"Therapist: \"{response1['response']}\"")
    if response1.get('checkpoint_question'):
        print(f"Therapist: \"{response1['checkpoint_question']}\"")

    # Step 2: Relax tongue - resistance
    print("\nClient: \"It feels weird, more tense\"")
    response2 = alpha.process_checkpoint_response("It feels weird, more tense")
    print(f"Therapist: \"{response2['response']}\"")

    # Retry after normalization
    print("\nClient: \"Okay, actually calmer now\"")
    response2_retry = alpha.process_checkpoint_response("Okay, actually calmer now")
    print(f"Therapist: \"{response2_retry['response']}\"")
    if response2_retry.get('checkpoint_question'):
        print(f"Therapist: \"{response2_retry['checkpoint_question']}\"")

    # Step 3: Breathe slower - calm with deep breath
    print("\nClient: \"Much calmer, I took a deep breath\"")
    response3 = alpha.process_checkpoint_response("Much calmer, I took a deep breath")
    print(f"Therapist: \"{response3['response']}\"")

    # Summary
    print("\n\n3. SEQUENCE SUMMARY:")
    print("-" * 80)
    summary = alpha.get_sequence_summary()
    print(f"Completed Steps: {summary['completed_steps']}")
    print(f"Down-regulation Indicators: {summary['down_regulation_indicators']}")
    print(f"Down-regulated: {summary['down_regulated']}")
    print(f"Resistance Encountered: {summary['resistance_encountered']}")
