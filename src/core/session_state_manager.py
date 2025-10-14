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
        self.body_location_provided = False
        self.body_sensation_described = False
        self.last_client_provided_info = None  # Track what info was just given
        self.pattern_inquiry_asked = False  # Track if "How do you know?" already asked
        self.pattern_response_received = False  # Track if client answered pattern question
        self.questions_asked_set = set()  # Track unique questions to prevent exact repetition
        self.last_question_asked = None  # Track the very last question

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

        return "general_response"

    def update_completion_status(self, client_input: str, navigation_output: Dict) -> List[str]:
        """Update completion status based on client response"""
        client_lower = client_input.lower()
        events = []

        # Detect what client just provided
        self.last_client_provided_info = self.detect_client_answer_type(client_input)

        # Check for goal stated (1.1)
        if not self.stage_1_completion["goal_stated"]:
            if any(phrase in client_lower for phrase in [
                "want to feel", "want to be", "need to", "hope to",
                "peaceful", "calm", "happy", "better", "different"
            ]):
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

        # Check for problem identified (1.2) - IMPROVED LOGIC
        # Problem is identified when client mentions stressor + body awareness together
        # OR when we've been in 1.2 state for 3+ exchanges with body + stressor mentioned
        if not self.stage_1_completion["problem_identified"]:
            # Immediate identification: stressor mentioned
            stressor_mentioned = any(word in client_lower for word in [
                "work", "stress", "pressure", "deadline", "boss", "job",
                "relationship", "family", "money", "health", "anxiety",
                "worry", "overwhelm", "difficult", "hard", "problem", "issue"
            ])

            # If we're in 1.2 substate and have body awareness + any stressor mentioned in history
            if self.current_substate == "1.2_problem_and_body":
                # Check last 5 exchanges for problem indicators
                problem_indicators = 0
                has_stressor = False
                has_body_reference = False

                for ex in self.conversation_history[-5:]:
                    client_msg = ex.get('client_input', '').lower()

                    # Check for stressor mention
                    if any(word in client_msg for word in [
                        "work", "stress", "pressure", "deadline", "boss",
                        "relationship", "people", "worry", "anxious", "overwhelm"
                    ]):
                        has_stressor = True
                        problem_indicators += 1

                    # Check for body reference
                    if any(word in client_msg for word in [
                        "chest", "head", "stomach", "shoulders", "tight", "ache",
                        "heavy", "pain", "feel it", "feeling"
                    ]):
                        has_body_reference = True
                        problem_indicators += 1

                # Problem identified if: body awareness + stressor mentioned + at least 3 exchanges
                if (self.stage_1_completion["body_awareness_present"] and
                    (has_stressor or stressor_mentioned) and
                    len(self.conversation_history) >= 3):
                    self.stage_1_completion["problem_identified"] = True
                    self.stage_1_completion["problem_content"] = "Client stress/body pattern identified"
                    events.append("problem_identified")

                # OR if we have enough problem indicators (2+) in recent history
                elif problem_indicators >= 2:
                    self.stage_1_completion["problem_identified"] = True
                    self.stage_1_completion["problem_content"] = "Problem pattern established through exchanges"
                    events.append("problem_identified")

                # OR if we have body location + sensation + been in state 1.2 for 6+ turns
                # This handles clients who provide body info but vague problem descriptions
                elif (self.body_location_provided and
                      self.body_sensation_described and
                      len(self.conversation_history) >= 8):
                    self.stage_1_completion["problem_identified"] = True
                    self.stage_1_completion["problem_content"] = "Body awareness established with sufficient context"
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
                return True, "1.3_readiness_assessment"

        elif self.current_substate == "1.3_readiness_assessment":
            if (self.stage_1_completion["pattern_understood"] and
                self.stage_1_completion["rapport_established"]):
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

        # 1.3 Progress
        if self.current_substate.startswith("1.3") or self.stage_1_completion["ready_for_stage_2"]:
            progress["stage_1_progress"]["1.3_readiness_assessment"] = {
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