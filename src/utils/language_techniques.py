"""
Language Techniques for Therapeutic Responses
Following Dr. Q's recommendations for subtle linguistic interventions:
1. Tense shifting ("I am depressed" → "So you've been feeling depressed?")
2. Feeling insertions (separate identity from state)
3. Past tense enforcement for problems
4. Metaphor detection and awareness
"""

import re
from typing import Dict, Tuple


class LanguageTechniques:
    """Language transformation techniques for therapeutic responses"""

    def __init__(self):
        # Metaphors that create physical sensations (to be aware of)
        self.physical_metaphors = {
            "under stress": "stressed",
            "under pressure": "pressured",
            "weighed down": "heavy",
            "crushed": "overwhelmed",
            "drowning": "overwhelmed",
            "buried": "overwhelmed",
            "trapped": "stuck",
            "lost": "uncertain",
            "broken": "hurt",
            "shattered": "devastated"
        }

        # Identity statements to transform
        self.identity_patterns = {
            "i am depressed": "depression",
            "i am anxious": "anxiety",
            "i am stressed": "stress",
            "i am overwhelmed": "overwhelm",
            "i am broken": "hurt",
            "i am lost": "feeling lost",
            "i am stuck": "feeling stuck",
            "i am angry": "anger",
            "i am sad": "sadness"
        }

    def apply_tense_shift(self, client_statement: str) -> str:
        """
        Transform present tense "I am X" to past tense "You've been feeling X?"
        Separates identity from temporary state
        """
        statement_lower = client_statement.lower().strip()

        # Check for identity patterns
        for pattern, emotion in self.identity_patterns.items():
            if pattern in statement_lower:
                # Transform: "I am depressed" → "So you've been feeling depressed?"
                transformed = f"So you've been feeling {emotion}?"
                return transformed

        # Generic transformation for "I am [emotion]"
        if statement_lower.startswith("i am "):
            emotion = statement_lower[5:].strip()  # Extract emotion after "i am "
            return f"So you've been feeling {emotion}?"

        return None  # No transformation needed

    def add_feeling_insertion(self, response: str) -> str:
        """
        Add 'feeling' to separate state from identity
        "You've been depressed" → "You've been feeling depressed"
        """
        # Pattern: "you've been [emotion]" → "you've been feeling [emotion]"
        patterns = [
            (r"(you've been|you have been) (depressed|anxious|stressed|overwhelmed|sad|angry|lost|stuck)",
             r"\1 feeling \2"),
            (r"(you're|you are) (depressed|anxious|stressed|overwhelmed|sad|angry|lost|stuck)",
             r"\1 feeling \2")
        ]

        for pattern, replacement in patterns:
            response = re.sub(pattern, replacement, response, flags=re.IGNORECASE)

        return response

    def enforce_past_tense_for_problems(self, response: str) -> str:
        """
        Ensure problems are discussed in past tense
        "the problem is having" → "the problem has had"
        """
        # Transform present continuous to present perfect for problems
        patterns = [
            (r"(the problem|this issue|the situation) is having", r"\1 has had"),
            (r"(the problem|this issue|the situation) is causing", r"\1 has caused"),
            (r"(the problem|this issue|the situation) is making", r"\1 has made"),
            (r"(it|that) is affecting", r"\1 has affected"),
            (r"(it|that) is impacting", r"\1 has impacted")
        ]

        for pattern, replacement in patterns:
            response = re.sub(pattern, replacement, response, flags=re.IGNORECASE)

        return response

    def detect_metaphors(self, client_input: str) -> Dict:
        """
        Detect metaphorical language that creates physical sensations
        Returns metaphor info for awareness
        """
        input_lower = client_input.lower()
        detected = []

        for metaphor, meaning in self.physical_metaphors.items():
            if metaphor in input_lower:
                detected.append({
                    "metaphor": metaphor,
                    "meaning": meaning,
                    "creates_sensation": True
                })

        if detected:
            return {
                "detected": True,
                "metaphors": detected,
                "note": "Client using metaphorical language that may create physical sensations"
            }

        return {"detected": False, "metaphors": []}

    def transform_client_statement(self, client_input: str) -> Tuple[str, Dict]:
        """
        Apply appropriate transformations to client statement for therapeutic echo
        Returns: (transformed_statement, transformation_info)
        """
        transformations = []

        # 1. Check for identity statement → tense shift
        tense_shifted = self.apply_tense_shift(client_input)
        if tense_shifted:
            transformations.append("tense_shift")
            result = tense_shifted
        else:
            result = client_input

        # 2. Add feeling insertion if needed
        result_with_feeling = self.add_feeling_insertion(result)
        if result_with_feeling != result:
            transformations.append("feeling_insertion")
            result = result_with_feeling

        # 3. Enforce past tense for problems
        result_with_past = self.enforce_past_tense_for_problems(result)
        if result_with_past != result:
            transformations.append("past_tense_enforcement")
            result = result_with_past

        # 4. Detect metaphors (awareness only, not transformation)
        metaphor_detection = self.detect_metaphors(client_input)

        transformation_info = {
            "transformations_applied": transformations,
            "metaphor_detection": metaphor_detection,
            "original": client_input,
            "transformed": result
        }

        return result, transformation_info

    def create_acknowledgment_with_shift(self, client_input: str) -> str:
        """
        Create therapeutic acknowledgment with subtle tense shift
        Example: "I am depressed" → "So you've been feeling depressed?"
        """
        transformed, _ = self.transform_client_statement(client_input)
        return transformed

    def prepare_response_language(self, draft_response: str) -> str:
        """
        Prepare therapeutic response with proper language techniques
        - Add feeling insertions
        - Enforce past tense for problems
        """
        response = draft_response

        # Apply feeling insertion
        response = self.add_feeling_insertion(response)

        # Enforce past tense
        response = self.enforce_past_tense_for_problems(response)

        return response


# Example usage and testing
if __name__ == "__main__":
    lt = LanguageTechniques()

    # Test cases
    test_inputs = [
        "I am depressed",
        "I am so anxious all the time",
        "I feel like I'm under stress",
        "I'm drowning in work",
        "I am stuck and don't know what to do"
    ]

    print("=" * 80)
    print("LANGUAGE TECHNIQUES TEST")
    print("=" * 80)

    for test_input in test_inputs:
        print(f"\nClient: \"{test_input}\"")
        transformed, info = lt.transform_client_statement(test_input)
        print(f"Transformed: \"{transformed}\"")
        print(f"Techniques applied: {', '.join(info['transformations_applied'])}")
        if info['metaphor_detection']['detected']:
            print(f"Metaphors detected: {[m['metaphor'] for m in info['metaphor_detection']['metaphors']]}")

    # Test response preparation
    print("\n" + "=" * 80)
    print("RESPONSE PREPARATION TEST")
    print("=" * 80)

    test_responses = [
        "The problem is having a big impact on you.",
        "You're depressed and that's affecting your work.",
        "You've been anxious about this situation."
    ]

    for test_response in test_responses:
        print(f"\nOriginal: \"{test_response}\"")
        prepared = lt.prepare_response_language(test_response)
        print(f"Prepared: \"{prepared}\"")
