"""
TRT Session State Management System
Tracks completion status and manages sequential progression through TRT substates
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class TRTSessionState:
    """Manages TRT session state and progression tracking"""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_stage = "stage_1_safety_building"
        self.current_substate = "1.1_goal_and_vision"

        # Stage 1 completion tracking
        self.stage_1_completion = {
            # 1.1 Goal and Vision criteria
            "goal_stated": False,
            "goal_content": "",
            "vision_presented": False,
            "vision_accepted": False,

            # 1.1.5 Psycho-education criteria
            "psycho_education_provided": False,
            "education_understood": False,

                # 1.2 Problem and Body criteria
            "problem_identified": False,
            "problem_content": "",
            "emotion_identified": False,  # NEW: Track if client mentioned emotion (anger, sadness, etc.)
            "emotion_content": "",  # NEW: Store the specific emotion mentioned
            "body_awareness_present": False,
            "present_moment_focus": False,

            # 1.3 Readiness criteria
            "pattern_understood": False,
            "rapport_established": True,  # Assume good from start
            "ready_for_stage_2": False
        }

        # Conversation history
        self.conversation_history = []
        self.completion_events = []
        self.response_history = []  # Track recent responses to avoid loops
        self.vision_attempts = 0

        # NEW: Track question repetition (Dr. Q never asks same question twice)
        self.body_questions_asked = 0
        self.emotion_provided = False  # NEW: Track if client provided emotion word
        self.body_location_provided = False
        self.body_sensation_described = False
        self.anything_else_asked = False  # NEW: Track if we asked "What else?" after body exploration
        self.anything_else_count = 0  # NEW: Count how many times we've asked "What else?"
        self.body_enquiry_cycles = 0  # NEW: Track body enquiry cycles (max 2)
        self.problem_question_asked = False  # NEW: Track if "what's making it hard" was asked
        self.last_client_provided_info = None  # Track what info was just given
        self.pattern_inquiry_asked = False  # Track if "How do you know?" already asked
        self.pattern_response_received = False  # Track if client answered pattern question
        self.questions_asked_set = set()  # Track unique questions to prevent exact repetition
        self.last_question_asked = None  # Track the very last question

        # Alpha sequence tracking
        self.alpha_complete = False
        self.alpha_started = False

        # Session conclusion tracking
        self.session_conclusion_given = False

        # Track most recent emotion/problem for body location questions
        self.most_recent_emotion_or_problem = None

    def add_exchange(self, client_input: str, therapist_response: str, navigation_output: Dict):
        """Add exchange to conversation history"""
        exchange = {
            "turn": len(self.conversation_history) + 1,
            "timestamp": datetime.now().isoformat(),
            "client_input": client_input,
            "therapist_response": therapist_response,
            "substate": self.current_substate,
            "navigation_output": navigation_output
        }
        self.conversation_history.append(exchange)

        # Track response patterns to avoid loops
        self.response_history.append(therapist_response)
        if len(self.response_history) > 3:
            self.response_history.pop(0)  # Keep only last 3 responses

        # Track if "How do you know?" was asked
        response_lower = therapist_response.lower()
        if "how do you know" in response_lower:
            self.pattern_inquiry_asked = True

        # Track if "What else?" was asked (after body exploration)
        # IMPORTANT: Only count "what else" during body exploration, NOT during readiness (3.1)
        if any(phrase in response_lower for phrase in ["what else", "anything else", "is there anything else", "anything i'm missing"]):
            # Check if we're in body exploration substates (not readiness)
            body_exploration_substates = ["1.2_problem_and_body", "2.1_seek", "2.2_location", "2.3_sensation"]

            if self.current_substate in body_exploration_substates:
                # This is a body exploration "what else" - count it
                self.anything_else_asked = True
                self.anything_else_count += 1

                # When "What else?" is asked, complete one body enquiry cycle
                # MAX 2 cycles allowed
                if self.anything_else_count <= 2:
                    self.body_enquiry_cycles = self.anything_else_count
            elif self.current_substate == "3.1_assess_readiness":
                # This is readiness "what else" - just set flag, don't increment cycle
                self.anything_else_asked = True
                # Don't increment anything_else_count or body_enquiry_cycles here

        # Track if "what's making it hard" was asked
        if any(phrase in response_lower for phrase in ["what's been making it hard", "what's been making it difficult", "what's been getting in the way"]):
            self.problem_question_asked = True

        # Check if client answered pattern question
        if self.pattern_inquiry_asked and not self.pattern_response_received:
            client_lower = client_input.lower()
            pattern_answer_indicators = ["when", "starts when", "happens when", "i think", "it feels",
                                        "moment", "it begins", "angry", "sad", "triggered"]
            if any(indicator in client_lower for indicator in pattern_answer_indicators):
                self.pattern_response_received = True

        # Track questions asked to prevent repetition
        # Extract question from response (text ending with ?)
        if '?' in therapist_response:
            # Get all questions in the response
            questions = [q.strip() + '?' for q in therapist_response.split('?') if q.strip()]
            for question in questions:
                # Normalize question for comparison
                normalized_q = self._normalize_question(question)
                self.questions_asked_set.add(normalized_q)
                self.last_question_asked = normalized_q

    def _normalize_question(self, question: str) -> str:
        """Normalize question for comparison (remove extra words, lowercase)"""
        q = question.lower().strip()
        # Remove common variations
        q = q.replace("that's right.", "").replace("yeah.", "").strip()
        return q

    def _reset_body_exploration_flags(self):
        """Reset body exploration flags to start a new enquiry cycle

        This is called when:
        - Client responded to "What else?" with new information
        - We're starting cycle 2 (body_enquiry_cycles < 2)

        We reset the flags but keep the cycle counter so we track we're in cycle 2
        """
        self.anything_else_asked = False  # Reset so "What else?" can be asked again
        self.body_location_provided = False  # Reset to ask about location again
        self.body_sensation_described = False  # Reset to ask about sensation again
        # DON'T reset body_enquiry_cycles - it tracks total cycles completed
        # DON'T reset emotion_provided - emotion persists across cycles

    def was_question_asked_recently(self, question: str) -> bool:
        """Check if this question was asked in last 3 turns"""
        normalized = self._normalize_question(question)

        # Check exact match
        if normalized in self.questions_asked_set:
            return True

        # Check semantic similarity (same core question)
        for asked_q in list(self.questions_asked_set)[-5:]:  # Check last 5 questions
            # Check for core question similarity
            if self._questions_are_similar(normalized, asked_q):
                return True

        return False

    def _questions_are_similar(self, q1: str, q2: str) -> bool:
        """Check if two questions are semantically similar"""
        # Remove common question starters
        for starter in ["what", "how", "where", "when", "why", "are you", "do you"]:
            q1 = q1.replace(starter, "").strip()
            q2 = q2.replace(starter, "").strip()

        # Check for key phrase matches
        key_phrases = {
            "making it hard": ["making it hard", "been difficult", "causing trouble"],
            "feeling that now": ["feeling that now", "feeling it now", "feel that right now", "feeling that right now"],
            "kind of sensation": ["kind of sensation", "what sensation", "type of feeling"],
        }

        for key, similar_phrases in key_phrases.items():
            if any(phrase in q1 for phrase in similar_phrases) and any(phrase in q2 for phrase in similar_phrases):
                return True

        # Check if core phrases match (80% or more of the question is the same)
        q1_words = set(q1.split())
        q2_words = set(q2.split())
        if q1_words and q2_words:
            overlap = len(q1_words & q2_words) / max(len(q1_words), len(q2_words))
            if overlap > 0.7:  # 70% word overlap = similar question
                return True

        return False

    def detect_client_answer_type(self, client_input: str) -> str:
        """Detect what type of information client just provided"""
        client_lower = client_input.lower()

        # CRITICAL: Check if client responded to "What else?" with new information
        # If so, reset flags to start a new body enquiry cycle
        if self.anything_else_asked and self.body_enquiry_cycles < 2:
            # Check if client provided substantive new information (not "nothing")
            nothing_phrases = ["nothing", "no", "that's it", "that's all", "nothing more",
                             "nothing else", "nope", "nah", "i'm good", "all good", "im good"]
            client_said_nothing = any(phrase in client_lower for phrase in nothing_phrases)

            # If client provided new info (not "nothing"), reset cycle flags to start fresh
            if not client_said_nothing and len(client_input.split()) > 2:
                self._reset_body_exploration_flags()

        # Emotion words (check FIRST before body location - emotions are more specific)
        emotion_words = ["angry", "anger", "sad", "sadness", "hurt", "hurting", "anxious", "anxiety",
                        "stressed", "stress", "worried", "worry", "fear", "scared", "afraid", "frightened",
                        "frustrated", "frustration", "annoyed", "irritated", "upset", "mad",
                        "depressed", "depression", "down", "low", "overwhelmed", "helpless", "hopeless",
                        "disappointed", "ashamed", "shame", "guilty", "guilt", "embarrassed",
                        "lonely", "alone", "abandoned", "rejected", "betrayed", "confused", "lost"]

        # Check for emotion FIRST and track it
        for word in emotion_words:
            if word in client_lower:
                self.emotion_provided = True
                # Track the most recent emotion for body location questions
                self.most_recent_emotion_or_problem = word
                return "emotion"

        # Problem/stress words (check AFTER emotions but BEFORE body location)
        # These are stressors that should be tracked for body location questions
        problem_words = ["work", "job", "deadline", "deadlines", "boss", "school", "exam", "exams",
                        "relationship", "relationships", "family", "money", "financial",
                        "bully", "bullied", "bullying", "pressure", "pressured"]

        # Check for problem words and track them
        for word in problem_words:
            if word in client_lower:
                # Track the most recent problem for body location questions
                # Use format "stress from [problem]" if stress mentioned, otherwise just the problem
                if "stress" in client_lower or "stressful" in client_lower or "stressing" in client_lower:
                    self.most_recent_emotion_or_problem = f"stress from {word}"
                else:
                    self.most_recent_emotion_or_problem = word

        # Body location words (expanded to accept more vague locations)
        location_words = ["chest", "head", "forehead", "shoulders", "neck", "stomach", "leg", "arm", "back",
                         "feet", "hands", "throat", "belly", "body", "heart", "gut", "face", "jaw",
                         "everywhere", "all over", "whole body"]
        # Sensation quality words (expanded to accept vague sensations)
        sensation_words = ["ache", "tight", "heavy", "sharp", "dull", "pressure", "tingling", "burning", "throbbing",
                          "smooth", "nice", "weird", "strange", "tense", "relaxed", "warm", "cold", "numb",
                          "uncomfortable", "painful", "sore", "stiff"]

        if any(word in client_lower for word in location_words):
            self.body_location_provided = True
            return "body_location"

        if any(word in client_lower for word in sensation_words):
            self.body_sensation_described = True
            return "sensation_quality"

        if any(phrase in client_lower for phrase in ["i want", "feel calm", "feel peaceful", "feel better"]):
            return "goal"

        if any(phrase in client_lower for phrase in ["yes", "exactly", "that's right", "makes sense"]):
            return "affirmation"

        if any(phrase in client_lower for phrase in ["i don't know", "not sure", "don't understand"]):
            return "confusion"

        # Check for "nothing more" responses (after "What else?" question)
        if any(phrase in client_lower for phrase in ["nothing", "no", "that's it", "that's all",
                                                      "nothing more", "nothing else", "nope", "nah",
                                                      "i'm good", "all good"]):
            return "nothing_more"

        return "general_response"

    def update_completion_status(self, client_input: str, navigation_output: Dict) -> List[str]:
        """Update completion status based on client response"""
        client_lower = client_input.lower()
        events = []

        # Detect what client just provided
        self.last_client_provided_info = self.detect_client_answer_type(client_input)

        # Check for goal stated (1.1)
        # CRITICAL: Detect goal statements like "I want to feel X", "I would like to feel X"
        if not self.stage_1_completion["goal_stated"]:
            # Goal phrases (explicit desire for a future state)
            goal_phrases = [
                "want to feel", "want to be", "would like to feel", "would like to be",
                "need to feel", "need to be", "hope to feel", "hope to be",
                "wanna feel", "wanna be", "wish to feel", "wish to be"
            ]

            # Goal state words (positive states client is seeking)
            goal_states = [
                "peaceful", "calm", "happy", "better", "different",
                "good", "great", "relaxed", "comfortable", "safe",
                "grounded", "centered", "balanced", "free"
            ]

            # Check for explicit goal phrases OR seeking positive state
            if (any(phrase in client_lower for phrase in goal_phrases) or
                any(state in client_lower for state in goal_states)):
                self.stage_1_completion["goal_stated"] = True
                self.stage_1_completion["goal_content"] = client_input
                events.append("goal_stated")

        # Check for vision accepted (1.1) - Both explicit and implicit
        if self.stage_1_completion["goal_stated"] and not self.stage_1_completion["vision_accepted"]:
            # Direct acceptance phrases
            vision_acceptance_phrases = [
                "yes", "exactly", "that sounds", "completely", "absolutely",
                "that's what", "perfect", "right", "what i want", "grounded"
            ]

            # Implicit acceptance through continued emotional sharing
            emotional_sharing_phrases = [
                "feel", "chest", "heavy", "sad", "better", "body", "heart", "tight"
            ]

            # Check for direct acceptance
            if any(phrase in client_lower for phrase in vision_acceptance_phrases):
                if not any(neg in client_lower for neg in ["not", "don't", "no", "but"]):
                    self.stage_1_completion["vision_accepted"] = True
                    events.append("vision_accepted")

            # Check for implicit acceptance through continued emotional sharing
            elif any(phrase in client_lower for phrase in emotional_sharing_phrases):
                # Count emotional sharing turns after goal was stated
                emotional_turns = 0
                for exchange in self.conversation_history[-3:]:  # Check last 3 turns
                    if any(word in exchange.get('client_input', '').lower() for word in emotional_sharing_phrases):
                        emotional_turns += 1

                # If client has shared emotions 2+ times after goal, assume implicit acceptance
                if emotional_turns >= 2:
                    self.stage_1_completion["vision_accepted"] = True
                    events.append("vision_accepted_implicit")

        # Check for emotion identified (1.2) - NEW LOGIC
        # Emotion is identified when client mentions an emotion word
        if not self.stage_1_completion["emotion_identified"]:
            emotion_words = ["angry", "anger", "sad", "sadness", "hurt", "anxious", "anxiety",
                            "stressed", "stress", "worried", "worry", "fear", "scared",
                            "frustrated", "upset", "mad", "depressed", "down", "overwhelmed"]

            for emotion in emotion_words:
                if emotion in client_lower:
                    self.stage_1_completion["emotion_identified"] = True
                    self.stage_1_completion["emotion_content"] = emotion
                    self.emotion_provided = True
                    events.append("emotion_identified")
                    break

        # Check for problem identified (1.2) - SIMPLIFIED & MORE RESPONSIVE
        # Problem is identified when client mentions a stressor (work, stress, etc.)
        # We don't need to wait for body awareness - that's separate
        if not self.stage_1_completion["problem_identified"]:
            # Immediate identification: stressor mentioned in current input
            stressor_mentioned = any(word in client_lower for word in [
                "work", "stress", "pressure", "deadline", "boss", "job",
                "relationship", "family", "money", "health", "anxiety",
                "worry", "overwhelm", "difficult", "hard", "problem", "issue",
                "overwork", "tired", "exhaust", "frustrated", "annoyed"
            ])

            # Also check for specific problem statements
            problem_statements = [
                "because", "can't", "cant", "not able", "unable to",
                "making it hard", "getting in the way", "stopping me"
            ]
            has_problem_statement = any(phrase in client_lower for phrase in problem_statements)

            # If we're in 1.2 substate and stressor is mentioned, mark as identified
            if self.current_substate == "1.2_problem_and_body":
                # IMMEDIATE: If user mentioned a stressor, problem is identified
                if stressor_mentioned:
                    self.stage_1_completion["problem_identified"] = True
                    self.stage_1_completion["problem_content"] = f"Stressor identified: {client_input[:50]}"
                    events.append("problem_identified")

                # OR if user gave a problem explanation (with "because", "can't", etc.)
                elif has_problem_statement and len(client_input.split()) > 3:
                    self.stage_1_completion["problem_identified"] = True
                    self.stage_1_completion["problem_content"] = f"Problem explained: {client_input[:50]}"
                    events.append("problem_identified")

                # OR check recent conversation history for stressor patterns
                elif len(self.conversation_history) > 0:
                    # Check last 3 exchanges for stressor mentions
                    has_stressor_in_history = False
                    for ex in self.conversation_history[-3:]:
                        client_msg = ex.get('client_input', '').lower()
                        if any(word in client_msg for word in [
                            "work", "stress", "pressure", "boss", "job",
                            "worry", "anxious", "overwhelm", "problem", "hard"
                        ]):
                            has_stressor_in_history = True
                            break

                    # If stressor was mentioned in recent history, mark as identified
                    if has_stressor_in_history:
                        self.stage_1_completion["problem_identified"] = True
                        self.stage_1_completion["problem_content"] = "Stressor mentioned in conversation"
                        events.append("problem_identified")

        # Check for body awareness (1.2)
        if not self.stage_1_completion["body_awareness_present"]:
            if any(word in client_lower for word in [
                "tight", "tightness", "pressure", "pain", "ache", "heavy",
                "chest", "stomach", "shoulders", "neck", "feel it", "feeling"
            ]):
                self.stage_1_completion["body_awareness_present"] = True
                events.append("body_awareness_present")

        # Check for present moment focus (1.2)
        if any(phrase in client_lower for phrase in [
            "right now", "currently", "at the moment", "as we speak",
            "i can feel", "feeling it now"
        ]):
            self.stage_1_completion["present_moment_focus"] = True
            events.append("present_moment_focus")

        # Check for pattern understanding (1.3)
        if any(phrase in client_lower for phrase in [
            "when i", "usually", "typically", "always happens", "every time",
            "the pattern", "i notice", "it starts when"
        ]) and len(client_input.split()) > 10:
            self.stage_1_completion["pattern_understood"] = True
            events.append("pattern_understood")

        # Log completion events
        for event in events:
            self.completion_events.append({
                "event": event,
                "turn": len(self.conversation_history) + 1,
                "timestamp": datetime.now().isoformat(),
                "client_input": client_input[:100] + "..." if len(client_input) > 100 else client_input
            })

        return events

    def check_substate_completion(self) -> Tuple[bool, Optional[str]]:
        """Check if current substate is complete and ready to advance"""

        if self.current_substate == "1.1_goal_and_vision":
            if (self.stage_1_completion["goal_stated"] and
                self.stage_1_completion["vision_accepted"]):
                return True, "1.1.5_psycho_education"

        elif self.current_substate == "1.1.5_psycho_education":
            # Advance to 1.2 immediately after psycho-education is provided
            # Don't wait for "education_understood" - Dr. Q moves forward naturally
            if self.stage_1_completion["psycho_education_provided"]:
                return True, "1.2_problem_and_body"

        elif self.current_substate == "1.2_problem_and_body":
            if (self.stage_1_completion["problem_identified"] and
                self.stage_1_completion["body_awareness_present"] and
                self.stage_1_completion["present_moment_focus"]):
                # Advance to 3.1 (Alpha Readiness), not 1.3
                return True, "3.1_assess_readiness"

        elif self.current_substate == "3.1_assess_readiness":
            if (self.stage_1_completion["pattern_understood"] and
                self.stage_1_completion["rapport_established"]):
                # Advance to alpha sequence instead of completing immediately
                return True, "3.2_alpha_sequence"

        elif self.current_substate == "3.2_alpha_sequence":
            # Alpha sequence completion is handled by AlphaSequence class
            # Advance when alpha is complete
            if hasattr(self, 'alpha_complete') and self.alpha_complete:
                self.stage_1_completion["ready_for_stage_2"] = True
                return True, "stage_1_complete"

        return False, None

    def advance_substate(self, next_substate: str) -> bool:
        """Advance to next substate if criteria met"""
        is_ready, target_substate = self.check_substate_completion()

        if is_ready and target_substate == next_substate:
            self.current_substate = next_substate
            self.completion_events.append({
                "event": "substate_advanced",
                "from": self.current_substate,
                "to": next_substate,
                "timestamp": datetime.now().isoformat()
            })
            return True

        return False

    def get_current_navigation_context(self) -> Dict:
        """Get current navigation context for master planning agent"""
        is_ready, next_substate = self.check_substate_completion()

        return {
            "current_stage": self.current_stage,
            "current_substate": self.current_substate,
            "completion_status": self.stage_1_completion.copy(),
            "ready_to_advance": is_ready,
            "next_substate": next_substate,
            "conversation_turn": len(self.conversation_history) + 1,
            "recent_events": self.completion_events[-3:] if len(self.completion_events) >= 3 else self.completion_events
        }

    def get_progress_summary(self) -> Dict:
        """Get human-readable progress summary"""
        progress = {
            "session_id": self.session_id,
            "current_location": f"{self.current_stage} -> {self.current_substate}",
            "turns_completed": len(self.conversation_history),
            "stage_1_progress": {}
        }

        # 1.1 Progress
        if self.current_substate.startswith("1.1") or self.stage_1_completion["vision_accepted"]:
            progress["stage_1_progress"]["1.1_goal_and_vision"] = {
                "goal_stated": "✅" if self.stage_1_completion["goal_stated"] else "⏳",
                "vision_accepted": "✅" if self.stage_1_completion["vision_accepted"] else "⏳"
            }

        # 1.2 Progress
        if self.current_substate.startswith("1.2") or self.current_substate.startswith("1.3"):
            progress["stage_1_progress"]["1.2_problem_and_body"] = {
                "problem_identified": "✅" if self.stage_1_completion["problem_identified"] else "⏳",
                "body_awareness": "✅" if self.stage_1_completion["body_awareness_present"] else "⏳",
                "present_moment": "✅" if self.stage_1_completion["present_moment_focus"] else "⏳"
            }

        # 3.1 Progress (Alpha Readiness)
        if self.current_substate.startswith("3.1") or self.stage_1_completion["ready_for_stage_2"]:
            progress["stage_1_progress"]["3.1_assess_readiness"] = {
                "pattern_understood": "✅" if self.stage_1_completion["pattern_understood"] else "⏳",
                "ready_for_stage_2": "✅" if self.stage_1_completion["ready_for_stage_2"] else "⏳"
            }

        return progress

    def save_session(self, filepath: str):
        """Save session state to JSON file"""
        session_data = {
            "session_id": self.session_id,
            "current_stage": self.current_stage,
            "current_substate": self.current_substate,
            "completion_status": self.stage_1_completion,
            "conversation_history": self.conversation_history,
            "completion_events": self.completion_events,
            "progress_summary": self.get_progress_summary()
        }

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

    @classmethod
    def load_session(cls, filepath: str):
        """Load session state from JSON file"""
        with open(filepath, 'r') as f:
            session_data = json.load(f)

        session_state = cls(session_data["session_id"])
        session_state.current_stage = session_data["current_stage"]
        session_state.current_substate = session_data["current_substate"]
        session_state.stage_1_completion = session_data["completion_status"]
        session_state.conversation_history = session_data["conversation_history"]
        session_state.completion_events = session_data["completion_events"]

        return session_state