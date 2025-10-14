"""
Vision Language Templates
Provides vision language for "I don't know" responses
Following Dr. Q's guidance: Offer universal positive outcomes when clients are uncertain
"""

from typing import Dict, List


class VisionLanguageTemplates:
    """Provides vision language templates for various contexts"""

    def __init__(self):
        # Universal positive outcome states
        self.universal_outcomes = [
            "lighter",
            "at ease",
            "free of the effects",
            "more emotionally present",
            "at peace inside",
            "flexible in your responses",
            "calm",
            "grounded",
            "clear",
            "okay"
        ]

        # Context-specific vision language
        self.vision_by_context = {
            "goal": {
                "templates": [
                    "What if you could feel {outcome}? Would that be what you want?",
                    "Imagine feeling {outcome}, at ease, lighter. Does that appeal to you?",
                    "If our time together helped you feel {outcome}, would that be valuable?",
                    "What if you could be {outcome}, free from these effects? Is that what you're looking for?"
                ],
                "outcomes": ["lighter", "at peace", "calm", "okay", "free"]
            },

            "feelings": {
                "templates": [
                    "Even if you don't know exactly, would feeling {outcome} be better than how you feel now?",
                    "What if instead of this, you felt {outcome}? Would that work?",
                    "Imagine being {outcome}, emotionally present. Does that make sense to you?"
                ],
                "outcomes": ["lighter", "at ease", "calm", "more present", "okay"]
            },

            "body_awareness": {
                "templates": [
                    "That's okay. Many people aren't sure at first. Just notice - is there any sensation in your {body_area}?",
                    "You don't need to know specifically. Just check - do you notice anything in your {body_area} area? Tight? Heavy? Anything at all?",
                    "Let me ask differently: If you put your attention on your {body_area}, what do you notice? Even if it's vague."
                ],
                "body_areas": ["chest", "stomach", "shoulders", "neck", "throat", "head"]
            },

            "general": {
                "templates": [
                    "That's completely okay. What if you could feel {outcome}? Would that be good?",
                    "You don't have to know everything right now. If you could be {outcome}, would that help?",
                    "Let me offer this: What if you were {outcome}, at peace, lighter. Does that resonate?"
                ],
                "outcomes": ["okay", "at ease", "calm", "free", "lighter"]
            }
        }

        # Acknowledgments for "I don't know"
        self.acknowledgments = [
            "That's completely normal.",
            "That makes sense.",
            "Many people feel that way.",
            "That's okay, you don't have to know.",
            "I understand."
        ]

    def get_vision_response(self, context: str = "general", custom_outcome: str = None) -> Dict:
        """
        Generate vision language response for "I don't know" situations

        Args:
            context: Context of the "I don't know" ("goal", "feelings", "body_awareness", "general")
            custom_outcome: Optional custom outcome state

        Returns:
            Dictionary with acknowledgment, vision offer, and metadata
        """
        import random

        # Get context templates
        if context in self.vision_by_context:
            context_data = self.vision_by_context[context]
        else:
            context_data = self.vision_by_context["general"]

        # Select acknowledgment
        acknowledgment = random.choice(self.acknowledgments)

        # Handle body awareness separately (different structure)
        if context == "body_awareness":
            template = random.choice(context_data["templates"])
            body_area = random.choice(context_data["body_areas"])
            vision_offer = template.format(body_area=body_area)

            return {
                "acknowledgment": acknowledgment,
                "vision_offer": vision_offer,
                "full_response": f"{acknowledgment} {vision_offer}",
                "context": context,
                "type": "body_awareness_redirect"
            }

        # Select outcome
        if custom_outcome:
            outcome = custom_outcome
        else:
            outcome = random.choice(context_data["outcomes"])

        # Select template and format
        template = random.choice(context_data["templates"])
        vision_offer = template.format(outcome=outcome)

        return {
            "acknowledgment": acknowledgment,
            "vision_offer": vision_offer,
            "full_response": f"{acknowledgment} {vision_offer}",
            "outcome_offered": outcome,
            "context": context,
            "type": "vision_language_offer"
        }

    def get_multi_outcome_vision(self, context: str = "general") -> str:
        """
        Get vision statement with multiple universal outcomes

        Args:
            context: Context for the vision

        Returns:
            Vision statement string
        """
        import random

        # Select 3 outcomes
        outcomes = random.sample(self.universal_outcomes, 3)

        vision_templates = [
            f"What if you could feel {outcomes[0]}, {outcomes[1]}, {outcomes[2]}? Would that be what you want?",
            f"Imagine being {outcomes[0]}, {outcomes[1]}, and {outcomes[2]}. Does that make sense to you?",
            f"If our time together helped you feel {outcomes[0]}, {outcomes[1]}, more {outcomes[2]} - would that be valuable?"
        ]

        return random.choice(vision_templates)

    def get_generic_outcome_framework(self) -> List[str]:
        """
        Get the generic outcome framework that works universally

        Returns:
            List of universal outcome statements
        """
        return [
            "More emotionally present",
            "At peace inside",
            "Free from past effects",
            "Flexible in your responses to current situations",
            "Lighter and at ease",
            "Clear and grounded"
        ]

    def build_custom_vision(self, client_fragments: List[str]) -> str:
        """
        Build vision from client's vague fragments

        Args:
            client_fragments: Fragments client has mentioned (e.g., ["better", "not so stressed"])

        Returns:
            Constructed vision statement
        """
        # Extract positive elements
        positive_elements = []
        for fragment in client_fragments:
            if "better" in fragment:
                positive_elements.append("feeling better")
            elif "not" in fragment or "less" in fragment:
                # Extract what they don't want, flip to positive
                if "stressed" in fragment:
                    positive_elements.append("calm")
                elif "anxious" in fragment:
                    positive_elements.append("at ease")
                elif "overwhelm" in fragment:
                    positive_elements.append("lighter")
            else:
                positive_elements.append(fragment)

        # Add universal outcomes
        positive_elements.extend(["at peace", "grounded"])

        # Construct vision
        if len(positive_elements) >= 2:
            vision = f"So you want to feel {positive_elements[0]}, {positive_elements[1]}"
            if len(positive_elements) >= 3:
                vision += f", {positive_elements[2]}"
            vision += ". I'm seeing you who's at ease, lighter, free. Does that make sense to you?"
        else:
            # Fallback to generic
            vision = "So you want to feel lighter, at ease, at peace inside. I'm seeing you who's calm, grounded, free from these effects. Does that make sense to you?"

        return vision


# Example usage and testing
if __name__ == "__main__":
    vl = VisionLanguageTemplates()

    print("=" * 80)
    print("VISION LANGUAGE TEMPLATES TEST")
    print("=" * 80)

    # Test different contexts
    contexts = ["goal", "feelings", "body_awareness", "general"]

    for context in contexts:
        print(f"\n{context.upper()} CONTEXT:")
        print("-" * 80)

        # Generate 2 examples
        for i in range(2):
            response = vl.get_vision_response(context)
            print(f"\nExample {i+1}:")
            print(f"  {response['full_response']}")

    # Test multi-outcome vision
    print("\n\nMULTI-OUTCOME VISION:")
    print("-" * 80)
    for i in range(3):
        print(f"{i+1}. {vl.get_multi_outcome_vision()}")

    # Test generic framework
    print("\n\nGENERIC OUTCOME FRAMEWORK:")
    print("-" * 80)
    framework = vl.get_generic_outcome_framework()
    for outcome in framework:
        print(f"  - {outcome}")

    # Test custom vision building
    print("\n\nCUSTOM VISION BUILDING:")
    print("-" * 80)
    test_fragments = [
        ["I want to feel better", "not so stressed"],
        ["less anxious", "not overwhelmed"],
        ["just okay"]
    ]

    for fragments in test_fragments:
        print(f"\nClient fragments: {fragments}")
        vision = vl.build_custom_vision(fragments)
        print(f"Constructed vision: \"{vision}\"")
