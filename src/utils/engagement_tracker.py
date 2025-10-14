"""
Engagement Tracking System
Monitors client engagement and triggers appropriate interventions:
1. Confirmation detection ("Yes," "Okay," "It makes sense")
2. Silence/disengagement monitoring
3. Non-responsive intervention triggers
4. Human handoff for complete disengagement
"""

from typing import Dict, List, Optional
from datetime import datetime


class EngagementTracker:
    """Tracks client engagement throughout therapeutic session"""

    def __init__(self):
        # Engagement indicators
        self.minimal_engagement_phrases = [
            "yes", "yeah", "yep", "ok", "okay", "sure", "right",
            "that's right", "makes sense", "i understand", "got it",
            "uh huh", "mm hmm", "exactly", "absolutely", "correct"
        ]

        self.confusion_indicators = [
            "i don't know", "not sure", "don't understand",
            "what do you mean", "confused", "huh", "what",
            "i don't get it", "can you explain"
        ]

        self.disengagement_indicators = [
            "...", ".", "k", "whatever", "fine", "idk"
        ]

        # Tracking state
        self.engagement_history = []
        self.consecutive_minimal_responses = 0
        self.consecutive_non_responses = 0
        self.total_turns = 0
        self.confusion_count = 0
        self.last_intervention_turn = 0

    def assess_engagement(self, client_input: str, turn_number: int) -> Dict:
        """
        Assess client engagement level from their input
        Returns engagement assessment with recommendations
        """
        self.total_turns = turn_number

        if not client_input or not client_input.strip():
            # Empty/silence
            return self._handle_silence(turn_number)

        input_lower = client_input.lower().strip()
        word_count = len(client_input.split())

        # Determine engagement type
        engagement_type = self._classify_engagement(input_lower, word_count)

        # Update tracking
        self._update_engagement_tracking(engagement_type, turn_number)

        # Get intervention recommendation
        intervention = self._determine_intervention(engagement_type, turn_number)

        assessment = {
            "engagement_type": engagement_type,
            "engagement_level": self._calculate_engagement_level(engagement_type, word_count),
            "word_count": word_count,
            "intervention_needed": intervention["needed"],
            "intervention_type": intervention["type"],
            "intervention_message": intervention["message"],
            "handoff_recommended": self._should_recommend_handoff(),
            "turn_number": turn_number
        }

        # Log assessment
        self.engagement_history.append({
            "turn": turn_number,
            "timestamp": datetime.now().isoformat(),
            "engagement_type": engagement_type,
            "assessment": assessment
        })

        return assessment

    def _classify_engagement(self, input_lower: str, word_count: int) -> str:
        """Classify type of engagement"""

        # Check for confusion
        if any(phrase in input_lower for phrase in self.confusion_indicators):
            return "confused"

        # Check for disengagement
        if any(phrase == input_lower for phrase in self.disengagement_indicators):
            return "disengaged"

        # Check for minimal engagement
        if any(input_lower.startswith(phrase) for phrase in self.minimal_engagement_phrases):
            if word_count <= 3:
                return "minimal_confirmation"
            else:
                return "confirmation_with_content"

        # Check for substantial engagement
        if word_count >= 10:
            return "engaged"
        elif word_count >= 5:
            return "moderate"
        else:
            return "minimal"

    def _calculate_engagement_level(self, engagement_type: str, word_count: int) -> str:
        """Calculate overall engagement level (high/medium/low/critical)"""

        if engagement_type in ["engaged", "confirmation_with_content"]:
            return "high"
        elif engagement_type in ["moderate", "minimal_confirmation"]:
            return "medium"
        elif engagement_type in ["minimal", "confused"]:
            return "low"
        else:  # disengaged
            return "critical"

    def _update_engagement_tracking(self, engagement_type: str, turn_number: int):
        """Update internal tracking counters"""

        # Reset or increment minimal response counter
        if engagement_type in ["minimal_confirmation", "minimal"]:
            self.consecutive_minimal_responses += 1
        else:
            self.consecutive_minimal_responses = 0

        # Track confusion
        if engagement_type == "confused":
            self.confusion_count += 1

        # Track non-responses (silence would be handled separately)
        if engagement_type == "disengaged":
            self.consecutive_non_responses += 1
        else:
            self.consecutive_non_responses = 0

    def _handle_silence(self, turn_number: int) -> Dict:
        """Handle empty/silent response"""

        self.consecutive_non_responses += 1

        # Determine severity
        if self.consecutive_non_responses >= 3:
            intervention_type = "critical_silence"
            message = "I notice you've been quiet. What's happening for you right now? Are you okay to continue?"
            handoff = True
        elif self.consecutive_non_responses >= 2:
            intervention_type = "repeated_silence"
            message = "You've gone quiet. What's happening right now?"
            handoff = False
        else:
            intervention_type = "initial_silence"
            message = "What's happening now?"
            handoff = False

        assessment = {
            "engagement_type": "silence",
            "engagement_level": "critical" if self.consecutive_non_responses >= 3 else "low",
            "word_count": 0,
            "intervention_needed": True,
            "intervention_type": intervention_type,
            "intervention_message": message,
            "handoff_recommended": handoff,
            "turn_number": turn_number
        }

        self.engagement_history.append({
            "turn": turn_number,
            "timestamp": datetime.now().isoformat(),
            "engagement_type": "silence",
            "assessment": assessment
        })

        return assessment

    def _determine_intervention(self, engagement_type: str, turn_number: int) -> Dict:
        """Determine if intervention is needed and what type"""

        # Avoid intervening too frequently
        turns_since_last_intervention = turn_number - self.last_intervention_turn

        # Critical: Disengagement
        if engagement_type == "disengaged":
            if self.consecutive_non_responses >= 2:
                self.last_intervention_turn = turn_number
                return {
                    "needed": True,
                    "type": "disengagement_check",
                    "message": "I'm noticing you might be pulling back. What's happening for you right now? Do you need a break?"
                }

        # High priority: Confusion
        if engagement_type == "confused":
            self.last_intervention_turn = turn_number
            return {
                "needed": True,
                "type": "clarification",
                "message": "Let me ask that differently. What are you noticing in your body right now?"
            }

        # Monitor: Too many minimal responses
        if self.consecutive_minimal_responses >= 4 and turns_since_last_intervention >= 3:
            self.last_intervention_turn = turn_number
            return {
                "needed": True,
                "type": "engagement_check",
                "message": "Are you with me? Does that make sense to you?"
            }

        # No intervention needed
        return {
            "needed": False,
            "type": "none",
            "message": None
        }

    def _should_recommend_handoff(self) -> bool:
        """Determine if human handoff should be recommended"""

        # Critical disengagement
        if self.consecutive_non_responses >= 3:
            return True

        # Extended confusion
        if self.confusion_count >= 5:
            return True

        # Sustained low engagement over many turns
        if len(self.engagement_history) >= 10:
            recent_engagement = self.engagement_history[-10:]
            low_engagement_count = sum(
                1 for entry in recent_engagement
                if entry["assessment"]["engagement_level"] in ["low", "critical"]
            )
            if low_engagement_count >= 7:  # 7 out of 10 turns low engagement
                return True

        return False

    def get_engagement_summary(self) -> Dict:
        """Get summary of engagement throughout session"""

        if not self.engagement_history:
            return {
                "total_turns": 0,
                "engagement_levels": {},
                "confusion_instances": 0,
                "overall_engagement": "unknown"
            }

        # Calculate engagement distribution
        engagement_levels = {"high": 0, "medium": 0, "low": 0, "critical": 0}
        for entry in self.engagement_history:
            level = entry["assessment"]["engagement_level"]
            engagement_levels[level] = engagement_levels.get(level, 0) + 1

        # Determine overall engagement
        total = len(self.engagement_history)
        if engagement_levels["high"] / total > 0.6:
            overall = "high"
        elif (engagement_levels["high"] + engagement_levels["medium"]) / total > 0.6:
            overall = "moderate"
        elif engagement_levels["critical"] > 0:
            overall = "critical"
        else:
            overall = "low"

        return {
            "total_turns": total,
            "engagement_levels": engagement_levels,
            "confusion_instances": self.confusion_count,
            "consecutive_minimal_responses": self.consecutive_minimal_responses,
            "consecutive_non_responses": self.consecutive_non_responses,
            "overall_engagement": overall,
            "handoff_recommended": self._should_recommend_handoff()
        }

    def reset(self):
        """Reset tracker for new session"""
        self.engagement_history = []
        self.consecutive_minimal_responses = 0
        self.consecutive_non_responses = 0
        self.total_turns = 0
        self.confusion_count = 0
        self.last_intervention_turn = 0


# Example usage and testing
if __name__ == "__main__":
    tracker = EngagementTracker()

    print("=" * 80)
    print("ENGAGEMENT TRACKER TEST")
    print("=" * 80)

    # Simulate session
    test_inputs = [
        ("I'm feeling really anxious about work", 1),
        ("My chest feels tight", 2),
        ("Yeah", 3),
        ("Okay", 4),
        ("I don't know what you mean", 5),
        ("", 6),  # Silence
        ("", 7),  # More silence
        ("I'm trying to understand what I feel in my body when the anxiety starts", 8),
        ("Yes, that makes sense", 9),
        ("k", 10)  # Disengaged
    ]

    for client_input, turn in test_inputs:
        print(f"\nTurn {turn}: Client: \"{client_input}\"")
        assessment = tracker.assess_engagement(client_input, turn)
        print(f"  Engagement Type: {assessment['engagement_type']}")
        print(f"  Engagement Level: {assessment['engagement_level']}")
        print(f"  Word Count: {assessment['word_count']}")

        if assessment['intervention_needed']:
            print(f"  ⚠️ INTERVENTION: {assessment['intervention_type']}")
            print(f"  Message: \"{assessment['intervention_message']}\"")

        if assessment['handoff_recommended']:
            print(f"  🚨 HANDOFF RECOMMENDED")

    # Summary
    print("\n" + "=" * 80)
    print("SESSION SUMMARY")
    print("=" * 80)
    summary = tracker.get_engagement_summary()
    print(f"Total Turns: {summary['total_turns']}")
    print(f"Engagement Distribution: {summary['engagement_levels']}")
    print(f"Overall Engagement: {summary['overall_engagement']}")
    print(f"Confusion Instances: {summary['confusion_instances']}")
    print(f"Handoff Recommended: {summary['handoff_recommended']}")
