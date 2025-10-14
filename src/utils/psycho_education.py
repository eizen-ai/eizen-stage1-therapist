"""
Psycho-Education Module
Provides zebra-lion brain explanation before problem inquiry
Helps clients understand how trauma/stress responses work
"""

from typing import Dict


class PsychoEducation:
    """Provides psycho-education about brain functioning and trauma responses"""

    def __init__(self):
        # Animal examples for variety (to avoid monotony)
        import random
        self.animal_examples = [
            {"animal": "zebra", "predator": "lion", "location": "African plains"},
            {"animal": "deer", "predator": "predator", "location": "forest"},
            {"animal": "rabbit", "predator": "hawk", "location": "field"},
            {"animal": "gazelle", "predator": "cheetah", "location": "savanna"}
        ]

        # Zebra-lion explanation templates (now with generic language and random animals)
        self.zebra_lion_explanation = {
            "full": """Let me explain how the brain works, because it'll help understand what's happening.

Think about a {animal} in the {location}. When a {animal} sees a {predator}, its brain immediately triggers a survival response - fight, flight, or freeze. The {animal}'s body floods with stress hormones, heart races, muscles tense up. That's automatic - the {animal} doesn't think about it.

Now here's the important part: Once the {predator} is gone, the {animal} shakes it off. Literally shakes its body, releases that energy, and goes back to normal. The threat is over, so the stress response turns off.

The human brain works the same way. When facing a threat - real or perceived - the brain triggers that same survival response. The problem is, unlike the {animal}, humans often don't "shake it off." The stress response stays activated, sometimes for years, even when the original threat is long gone.

That's what we're working with here. The brain still responding to something that happened, as if it's happening right now. Does that make sense?""",

            "concise": """Here's what's happening in the brain. When facing a threat, the brain activates a survival response - just like a {animal} running from a {predator}. The body floods with stress hormones, muscles tense, heart races.

The difference? The {animal} shakes it off once the {predator} is gone. Humans often don't. The stress response keeps running, sometimes for years, even when the threat is over.

That's what we're addressing - the brain still responding to old threats as if they're happening now. Make sense?""",

            "brief": """The brain has a survival response - like a {animal} fleeing a {predator}. When threats happen, this response activates automatically. The problem? Unlike the {animal}, humans often don't release it. The stress stays active, even when the threat is gone. That's what we're working with."""
        }

        # Follow-up explanations based on client response
        self.clarifications = {
            "what_does_this_mean_for_me": """What this means for you is that the feelings you're experiencing - the anxiety, the tension, the distress - aren't a sign that something's wrong with YOU. They're your brain doing exactly what it's supposed to do when it perceives a threat.

The issue is the threat response is still on, even though you're safe now. We're going to help your brain recognize that and turn it off.""",

            "how_do_we_fix_it": """We don't "fix" it in the traditional sense. What we do is help your brain recognize that the threat is over. We do this by bringing your attention to your body sensations and what's happening RIGHT NOW, in this moment.

When your brain realizes you're safe in the present, that old survival response can finally turn off - just like the zebra shaking it off.""",

            "why_now": """Great question. The timing varies for everyone. Sometimes it's because the current situation triggers the old response. Sometimes it's because you're finally in a safe enough place that your brain can address it. Either way, we're going to work with it now."""
        }

    def provide_education(self, version: str = "concise", session_state=None) -> Dict:
        """
        Provide psycho-education about brain functioning

        Args:
            version: "full", "concise", or "brief"
            session_state: Current session state for context

        Returns:
            Dictionary with education content and metadata
        """
        import random

        # Select random animal example for variety
        example = random.choice(self.animal_examples)

        # Select appropriate explanation template
        if version in self.zebra_lion_explanation:
            template = self.zebra_lion_explanation[version]
        else:
            template = self.zebra_lion_explanation["concise"]  # Default

        # Format template with random animal example
        explanation = template.format(
            animal=example["animal"],
            predator=example["predator"],
            location=example["location"]
        )

        return {
            "psycho_education": explanation,
            "version": version,
            "type": "animal_brain_mechanism",
            "animal_example": f"{example['animal']}/{example['predator']}",
            "purpose": "Normalize stress response and prepare for problem inquiry",
            "next_step": "problem_inquiry_with_context"
        }

    def handle_client_question(self, client_question: str) -> str:
        """
        Handle common client questions after psycho-education

        Args:
            client_question: Client's question or concern

        Returns:
            Appropriate clarification response
        """
        question_lower = client_question.lower()

        # Detect question type
        if any(phrase in question_lower for phrase in ["what does this mean", "what does that mean", "how does this help"]):
            return self.clarifications["what_does_this_mean_for_me"]

        elif any(phrase in question_lower for phrase in ["how do we", "how can we", "what do we do", "fix it", "solve it"]):
            return self.clarifications["how_do_we_fix_it"]

        elif any(phrase in question_lower for phrase in ["why now", "why me", "why is this happening"]):
            return self.clarifications["why_now"]

        else:
            # Generic acknowledgment and continuation
            return "That's a good question. The key is understanding that what you're experiencing is your brain's survival response. Once we help your brain recognize the threat is over, the response can turn off. Does that make sense?"

    def get_transition_to_problem_inquiry(self, education_accepted: bool = True) -> str:
        """
        Transition from psycho-education to problem inquiry

        Args:
            education_accepted: Whether client indicated understanding

        Returns:
            Transition statement
        """
        if education_accepted:
            return "Good. Now, with that in mind, tell me about what's been making it hard for you. What's been triggering that stress response?"
        else:
            # Client still confused, simplify and proceed
            return "Okay, let me put it simply: Your brain is reacting to something. Let's talk about what's been difficult for you, and we'll work through it together."

    def should_provide_education(self, session_state) -> bool:
        """
        Determine if psycho-education should be provided at this point

        Args:
            session_state: Current TRT session state

        Returns:
            Boolean indicating if education should be provided
        """
        if not session_state:
            return False

        # Provide education after vision is accepted, before problem inquiry
        completion = session_state.stage_1_completion

        # CRITICAL: Provide psycho-education IMMEDIATELY after vision accepted
        # This happens in substates: 1.1_goal_and_vision OR 1.1.5_psycho_education
        if (completion.get("goal_stated", False) and
            completion.get("vision_accepted", False) and
            not completion.get("psycho_education_provided", False)):
            # Vision accepted but psycho-education not yet provided
            return True

        return False

    def mark_education_provided(self, session_state):
        """Mark that psycho-education has been provided"""
        session_state.psycho_education_provided = True
        session_state.psycho_education_timestamp = session_state.conversation_history[-1]["turn"] if session_state.conversation_history else 0


# Example usage and testing
if __name__ == "__main__":
    pe = PsychoEducation()

    print("=" * 80)
    print("PSYCHO-EDUCATION MODULE TEST")
    print("=" * 80)

    # Test different versions
    print("\n1. BRIEF VERSION:")
    print("-" * 80)
    brief = pe.provide_education("brief")
    print(brief["psycho_education"])

    print("\n\n2. CONCISE VERSION:")
    print("-" * 80)
    concise = pe.provide_education("concise")
    print(concise["psycho_education"])

    print("\n\n3. FULL VERSION:")
    print("-" * 80)
    full = pe.provide_education("full")
    print(full["psycho_education"])

    # Test client questions
    print("\n\n4. HANDLING CLIENT QUESTIONS:")
    print("-" * 80)

    test_questions = [
        "What does this mean for me?",
        "How do we fix it?",
        "Why is this happening now?",
        "I don't understand"
    ]

    for question in test_questions:
        print(f"\nClient: \"{question}\"")
        response = pe.handle_client_question(question)
        print(f"Therapist: \"{response[:150]}...\"")

    # Test transition
    print("\n\n5. TRANSITION TO PROBLEM INQUIRY:")
    print("-" * 80)
    transition = pe.get_transition_to_problem_inquiry(education_accepted=True)
    print(f"Transition: \"{transition}\"")
