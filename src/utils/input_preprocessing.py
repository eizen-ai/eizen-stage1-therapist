"""
Input Preprocessing System for TRT
Handles spelling corrections and input normalization
"""

import re
from difflib import get_close_matches
from typing import List, Dict, Tuple

class InputPreprocessor:
    """Preprocesses user input for spelling errors and normalization"""

    def __init__(self):
        # Common therapeutic terms dictionary
        self.therapeutic_vocabulary = {
            'feeling', 'feelings', 'feel', 'felt', 'anxiety', 'anxious', 'stress', 'stressed',
            'depressed', 'depression', 'overwhelmed', 'overwhelming', 'panic', 'worried',
            'upset', 'angry', 'sad', 'happy', 'calm', 'peaceful', 'relaxed', 'tension',
            'tight', 'heavy', 'pressure', 'chest', 'stomach', 'head', 'heart', 'breathing',
            'work', 'family', 'relationship', 'relationships', 'problem', 'problems',
            'difficult', 'hard', 'tough', 'challenging', 'struggle', 'struggling',
            'want', 'need', 'help', 'better', 'different', 'change', 'improve',
            'therapy', 'therapist', 'session', 'talk', 'talking', 'discuss',
            'body', 'physical', 'emotional', 'mental', 'thoughts', 'thinking'
        }

        # Common misspellings and corrections
        self.common_corrections = {
            'iwll': 'will',
            'folows': 'follows',
            'fealing': 'feeling',
            'feling': 'feeling',
            'anixous': 'anxious',
            'anxius': 'anxious',
            'stresed': 'stressed',
            'stresd': 'stressed',
            'overwelmed': 'overwhelmed',
            'overwelm': 'overwhelm',
            'dificult': 'difficult',
            'diferent': 'different',
            'discus': 'discuss',
            'realy': 'really',
            'actualy': 'actually',
            'usualy': 'usually',
            'basicaly': 'basically',
            'generaly': 'generally',
            'especialy': 'especially',
            'definitly': 'definitely',
            'finaly': 'finally',
            'literaly': 'literally',
            'probaly': 'probably',
            'seperate': 'separate',
            'necesary': 'necessary',
            'occuring': 'occurring',
            'begining': 'beginning',
            'recieve': 'receive',
            'beleive': 'believe',
            'achive': 'achieve'
        }

        # Emotional state keywords for categorization
        self.emotional_categories = {
            'negative_high': ['overwhelmed', 'panic', 'terrified', 'devastated', 'crisis'],
            'negative_moderate': ['stressed', 'anxious', 'worried', 'upset', 'frustrated', 'angry'],
            'negative_low': ['low', 'down', 'sad', 'tired', 'disappointed', 'discouraged'],
            'neutral': ['okay', 'fine', 'alright', 'normal', 'average'],
            'positive': ['good', 'better', 'calm', 'peaceful', 'relaxed', 'happy']
        }

        # CRITICAL SAFETY: Self-harm and crisis phrases
        self.self_harm_phrases = [
            'kill myself', 'hurt myself', 'end it all', 'end my life', 'want to die',
            'dont want to live', 'do not want to live', 'not worth living',
            'better off dead', 'suicide', 'suicidal', 'kill me', 'end it'
        ]

        # Thinking mode phrases (redirect to feeling)
        self.thinking_mode_phrases = [
            'i think', 'because', 'i believe', 'in my opinion', 'i thought',
            'thinking about', 'i suppose'
        ]

        # Past tense phrases (redirect to present)
        self.past_tense_phrases = [
            'back then', 'when i was', 'years ago', 'in the past', 'used to',
            'before', 'long time ago', 'previously', 'earlier in my life'
        ]

        # "I don't know" phrases (offer vision language)
        self.i_dont_know_phrases = [
            'i do not know', 'i dont know', "i don't know", 'not sure',
            'no idea', 'dont know', "don't know", 'i am not sure',
            'i cannot say', 'i cant say', "i can't say", 'not certain',
            'unclear', 'unsure', 'hard to say', 'difficult to say'
        ]

    def preprocess_input(self, user_input: str) -> Dict[str, any]:
        """Main preprocessing function"""

        # Basic cleanup
        cleaned_input = self._basic_cleanup(user_input)

        # Spelling correction
        corrected_input = self._correct_spelling(cleaned_input)

        # CRITICAL SAFETY CHECKS
        self_harm_detected = self._detect_self_harm(corrected_input)
        thinking_mode_detected = self._detect_thinking_mode(corrected_input)
        past_tense_detected = self._detect_past_tense(corrected_input)
        i_dont_know_detected = self._detect_i_dont_know(corrected_input)

        # Extract emotional indicators
        emotional_state = self._detect_emotional_state(corrected_input)

        # Categorize input type
        input_category = self._categorize_input(corrected_input)

        return {
            'original_input': user_input,
            'cleaned_input': cleaned_input,
            'corrected_input': corrected_input,
            'emotional_state': emotional_state,
            'input_category': input_category,
            'spelling_corrections': self._get_corrections_made(cleaned_input, corrected_input),
            'self_harm_detected': self_harm_detected,
            'thinking_mode_detected': thinking_mode_detected,
            'past_tense_detected': past_tense_detected,
            'i_dont_know_detected': i_dont_know_detected
        }

    def _basic_cleanup(self, text: str) -> str:
        """Basic text cleanup"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Fix basic punctuation
        text = re.sub(r'\.+', '.', text)
        text = re.sub(r'\?+', '?', text)
        text = re.sub(r'!+', '!', text)

        # Handle common contractions
        contractions = {
            "i'm": "i am",
            "i've": "i have",
            "i'll": "i will",
            "i'd": "i would",
            "don't": "do not",
            "can't": "cannot",
            "won't": "will not",
            "shouldn't": "should not",
            "couldn't": "could not",
            "wouldn't": "would not"
        }

        text_lower = text.lower()
        for contraction, expansion in contractions.items():
            text_lower = text_lower.replace(contraction, expansion)

        return text_lower

    def _correct_spelling(self, text: str) -> str:
        """Correct spelling errors with context awareness"""
        words = text.split()
        corrected_words = []

        for i, word in enumerate(words):
            # Remove punctuation for checking
            clean_word = re.sub(r'[^\w]', '', word.lower())

            # Get context (next word)
            next_word = words[i + 1].lower() if i + 1 < len(words) else ""

            # CRITICAL: Don't "correct" words that are correct in context
            # Example: "right now" should stay "right", not become "tight"
            context_protected_words = {
                'right': ['now', 'there', 'here', 'away'],  # "right now", "right there"
                'light': ['weight', 'headed', 'up'],         # "light weight", "light headed"
            }

            # Check if word is protected by context
            is_protected = False
            if clean_word in context_protected_words:
                if any(next_word.startswith(protected) for protected in context_protected_words[clean_word]):
                    is_protected = True

            # If word is context-protected, don't attempt correction
            if is_protected:
                corrected_words.append(word)
                continue

            # Check common corrections first
            if clean_word in self.common_corrections:
                corrected_word = word.replace(clean_word, self.common_corrections[clean_word])
                corrected_words.append(corrected_word)
            # Check against therapeutic vocabulary
            elif clean_word not in self.therapeutic_vocabulary and len(clean_word) > 2:
                # Use stricter cutoff to avoid false positives like "right" → "tight"
                matches = get_close_matches(clean_word, self.therapeutic_vocabulary, n=1, cutoff=0.85)
                if matches:
                    corrected_word = word.replace(clean_word, matches[0])
                    corrected_words.append(corrected_word)
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)

        return ' '.join(corrected_words)

    def _detect_emotional_state(self, text: str) -> Dict[str, any]:
        """Detect emotional state from text"""
        text_words = set(text.lower().split())

        detected_emotions = {}
        intensity_score = 0

        for category, keywords in self.emotional_categories.items():
            matches = [word for word in keywords if word in text_words]
            if matches:
                detected_emotions[category] = matches

                # Calculate intensity
                if category == 'negative_high':
                    intensity_score = max(intensity_score, 3)
                elif category == 'negative_moderate':
                    intensity_score = max(intensity_score, 2)
                elif category == 'negative_low':
                    intensity_score = max(intensity_score, 1)

        return {
            'categories': detected_emotions,
            'intensity': intensity_score,
            'primary_emotion': self._get_primary_emotion(detected_emotions)
        }

    def _get_primary_emotion(self, detected_emotions: Dict) -> str:
        """Get primary emotional category"""
        if 'negative_high' in detected_emotions:
            return 'crisis_level'
        elif 'negative_moderate' in detected_emotions:
            return 'moderate_distress'
        elif 'negative_low' in detected_emotions:
            return 'mild_distress'
        elif 'positive' in detected_emotions:
            return 'positive_state'
        else:
            return 'neutral_unclear'

    def _categorize_input(self, text: str) -> str:
        """Categorize the type of input"""
        text_lower = text.lower()

        # Goal/want statements
        if any(phrase in text_lower for phrase in ['i want', 'i need', 'i would like', 'i wish']):
            return 'goal_statement'

        # Problem descriptions
        elif any(phrase in text_lower for phrase in ['problem', 'difficult', 'hard', 'struggle', 'issue']):
            return 'problem_description'

        # Feeling statements
        elif any(phrase in text_lower for phrase in ['i feel', 'feeling', 'i am']):
            return 'feeling_statement'

        # Questions
        elif '?' in text or any(phrase in text_lower for phrase in ['what', 'how', 'why', 'when', 'where']):
            return 'question'

        # Affirmations/agreements
        elif any(phrase in text_lower for phrase in ['yes', 'yeah', 'okay', 'right', 'exactly', 'that sounds']):
            return 'affirmation'

        # Greetings
        elif any(phrase in text_lower for phrase in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
            return 'greeting'

        else:
            return 'general_statement'

    def _get_corrections_made(self, original: str, corrected: str) -> List[Tuple[str, str]]:
        """Track what corrections were made"""
        if original == corrected:
            return []

        original_words = original.split()
        corrected_words = corrected.split()

        corrections = []
        for i, (orig, corr) in enumerate(zip(original_words, corrected_words)):
            if orig != corr:
                corrections.append((orig, corr))

        return corrections

    def _detect_self_harm(self, text: str) -> Dict[str, any]:
        """CRITICAL: Detect self-harm and suicidal ideation"""
        text_lower = text.lower()

        detected_phrases = []
        for phrase in self.self_harm_phrases:
            if phrase in text_lower:
                detected_phrases.append(phrase)

        return {
            'detected': len(detected_phrases) > 0,
            'phrases_found': detected_phrases,
            'severity': 'high' if detected_phrases else 'none'
        }

    def _detect_thinking_mode(self, text: str) -> Dict[str, any]:
        """Detect thinking mode (vs feeling mode)"""
        text_lower = text.lower()

        detected_phrases = []
        for phrase in self.thinking_mode_phrases:
            if phrase in text_lower:
                detected_phrases.append(phrase)

        return {
            'detected': len(detected_phrases) > 0,
            'phrases_found': detected_phrases
        }

    def _detect_past_tense(self, text: str) -> Dict[str, any]:
        """Detect past tense (vs present moment)"""
        text_lower = text.lower()

        # CRITICAL: Don't trigger past tense if client is talking about NOW
        # Example: "feeling good now, better than before" should NOT trigger
        if any(present_word in text_lower for present_word in ['right now', 'now', 'currently', 'at the moment', 'today']):
            # Client is talking about present moment, ignore past references
            return {
                'detected': False,
                'phrases_found': [],
                'note': 'Present moment indicators found - ignoring past references'
            }

        detected_phrases = []
        for phrase in self.past_tense_phrases:
            if phrase in text_lower:
                detected_phrases.append(phrase)

        return {
            'detected': len(detected_phrases) > 0,
            'phrases_found': detected_phrases
        }

    def _detect_i_dont_know(self, text: str) -> Dict[str, any]:
        """Detect 'I don't know' responses (offer vision language)"""
        text_lower = text.lower()

        detected_phrases = []
        for phrase in self.i_dont_know_phrases:
            if phrase in text_lower:
                detected_phrases.append(phrase)

        # Determine context - what are they unsure about?
        context = "general"
        if any(word in text_lower for word in ["feel", "feeling", "emotion"]):
            context = "feelings"
        elif any(word in text_lower for word in ["want", "goal", "outcome"]):
            context = "goal"
        elif any(word in text_lower for word in ["body", "sensation", "physical"]):
            context = "body_awareness"

        return {
            'detected': len(detected_phrases) > 0,
            'phrases_found': detected_phrases,
            'context': context,
            'note': "Client expressing uncertainty - may need vision language support"
        }


def test_preprocessor():
    """Test the input preprocessor"""

    print("🔧 INPUT PREPROCESSING TEST")
    print("=" * 50)

    preprocessor = InputPreprocessor()

    test_inputs = [
        "Hi, iwll feeling realy low and stresed",
        "I want to fel beter and les anixous",
        "Everythng is overwelming me right now",
        "I'm having dificult time with work presure",
        "Can you halp me discus this probem?"
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}: '{test_input}'")
        result = preprocessor.preprocess_input(test_input)

        print(f"Cleaned: '{result['cleaned_input']}'")
        print(f"Corrected: '{result['corrected_input']}'")
        print(f"Emotional State: {result['emotional_state']['primary_emotion']}")
        print(f"Input Category: {result['input_category']}")
        if result['spelling_corrections']:
            print(f"Corrections: {result['spelling_corrections']}")
        print("-" * 40)

if __name__ == "__main__":
    test_preprocessor()