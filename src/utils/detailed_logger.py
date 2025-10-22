"""
Detailed Logging Utility for TRT AI Therapist
Provides structured, color-coded logging for Docker environments
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
import sys

class DetailedLogger:
    """
    Centralized logger with structured output for tracking:
    - API endpoint inputs/outputs
    - Decision-making flow
    - Agent reasoning
    - Processing steps
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []

        # Create console handler with detailed formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Detailed format with timestamp, level, and component
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False

    def log_endpoint_input(self, endpoint: str, session_id: str, user_input: str, request_data: Dict = None):
        """Log API endpoint input"""
        self.logger.info("=" * 100)
        self.logger.info(f"📥 ENDPOINT INPUT: {endpoint}")
        self.logger.info("=" * 100)
        self.logger.info(f"Session ID: {session_id}")
        self.logger.info(f"User Input: '{user_input}'")
        if request_data:
            self.logger.info(f"Additional Data: {json.dumps(request_data, indent=2)}")
        self.logger.info("-" * 100)

    def log_endpoint_output(self, endpoint: str, session_id: str, response: str, metadata: Dict = None):
        """Log API endpoint output"""
        self.logger.info("-" * 100)
        self.logger.info(f"📤 ENDPOINT OUTPUT: {endpoint}")
        self.logger.info(f"Session ID: {session_id}")
        self.logger.info(f"Therapist Response: '{response}'")
        if metadata:
            self.logger.info(f"Metadata: {json.dumps(metadata, indent=2)}")
        self.logger.info("=" * 100)
        self.logger.info("")  # Empty line for readability

    def log_preprocessing_start(self, user_input: str):
        """Log preprocessing start"""
        self.logger.info("🔄 STEP 1: INPUT PREPROCESSING")
        self.logger.info(f"   Original Input: '{user_input}'")

    def log_preprocessing_result(self, result: Dict):
        """Log preprocessing results"""
        self.logger.info(f"   ✓ Cleaned Input: '{result.get('cleaned_input', '')}'")
        self.logger.info(f"   ✓ Corrected Input: '{result.get('corrected_input', '')}'")
        self.logger.info(f"   ✓ Emotional State: {result.get('emotional_state', {})}")
        self.logger.info(f"   ✓ Input Category: {result.get('input_category', 'unknown')}")

        # Log safety checks
        if result.get('self_harm_detected', {}).get('detected'):
            self.logger.warning(f"   ⚠️  SELF-HARM DETECTED: {result['self_harm_detected']}")
        if result.get('thinking_mode_detected', {}).get('detected'):
            self.logger.info(f"   💭 Thinking Mode Detected: {result['thinking_mode_detected']}")
        if result.get('past_tense_detected', {}).get('detected'):
            self.logger.info(f"   ⏮️  Past Tense Detected: {result['past_tense_detected']}")

    def log_navigation_start(self, session_state: Any):
        """Log navigation decision start"""
        self.logger.info("")
        self.logger.info("🧭 STEP 2: NAVIGATION DECISION (Master Planning Agent)")
        self.logger.info(f"   Current Stage: {session_state.current_stage}")
        self.logger.info(f"   Current Substate: {session_state.current_substate}")
        self.logger.info(f"   Completion Status:")
        for key, value in session_state.stage_1_completion.items():
            if isinstance(value, bool):
                status = "✓" if value else "✗"
                self.logger.info(f"      {status} {key}: {value}")

    def log_navigation_decision(self, navigation_output: Dict):
        """Log navigation decision results"""
        self.logger.info(f"   📍 Navigation Decision: {navigation_output.get('navigation_decision', 'unknown')}")
        self.logger.info(f"   📊 Situation Type: {navigation_output.get('situation_type', 'unknown')}")
        self.logger.info(f"   🎯 RAG Query: {navigation_output.get('rag_query', 'none')}")
        self.logger.info(f"   💡 Reasoning: {navigation_output.get('reasoning', 'No reasoning provided')}")

        if navigation_output.get('rule_override'):
            self.logger.info(f"   ⚡ RULE OVERRIDE Applied")
        if navigation_output.get('llm_reasoning'):
            self.logger.info(f"   🤖 LLM Reasoning Used (Confidence: {navigation_output.get('llm_confidence', 'N/A')})")

    def log_dialogue_start(self, navigation_decision: str, rag_examples_count: int = 0):
        """Log dialogue generation start"""
        self.logger.info("")
        self.logger.info("💬 STEP 3: DIALOGUE GENERATION (Dialogue Agent)")
        self.logger.info(f"   Decision to Implement: {navigation_decision}")
        if rag_examples_count > 0:
            self.logger.info(f"   📚 RAG Examples Retrieved: {rag_examples_count}")

    def log_dialogue_decision_point(self, decision_type: str, reasoning: str):
        """Log dialogue agent decision points"""
        self.logger.info(f"   🔀 Decision Point: {decision_type}")
        self.logger.info(f"      Reasoning: {reasoning}")

    def log_dialogue_technique(self, technique: str, details: str = None):
        """Log therapeutic technique used"""
        self.logger.info(f"   🎭 Technique Used: {technique}")
        if details:
            self.logger.info(f"      Details: {details}")

    def log_dialogue_output(self, response: str, metadata: Dict = None):
        """Log dialogue generation output"""
        self.logger.info(f"   ✓ Generated Response: '{response}'")
        if metadata:
            if metadata.get('llm_confidence'):
                self.logger.info(f"   ✓ LLM Confidence: {metadata['llm_confidence']}")
            if metadata.get('fallback_used'):
                self.logger.warning(f"   ⚠️  Fallback Response Used")

    def log_session_update(self, session_state: Any):
        """Log session state update"""
        self.logger.info("")
        self.logger.info("💾 STEP 4: SESSION STATE UPDATE")
        self.logger.info(f"   Updated Substate: {session_state.current_substate}")
        self.logger.info(f"   Body Questions Asked: {session_state.body_questions_asked}")
        self.logger.info(f"   Conversation Turns: {len(session_state.conversation_history)}")

    def log_processing_summary(self, processing_time: float, session_id: str):
        """Log overall processing summary"""
        self.logger.info("")
        self.logger.info("⏱️  PROCESSING SUMMARY")
        self.logger.info(f"   Session ID: {session_id}")
        self.logger.info(f"   Total Processing Time: {processing_time:.3f}s")
        self.logger.info("")

    def log_error(self, component: str, error: Exception, context: Dict = None):
        """Log error with context"""
        self.logger.error("=" * 100)
        self.logger.error(f"❌ ERROR in {component}")
        self.logger.error(f"Error Type: {type(error).__name__}")
        self.logger.error(f"Error Message: {str(error)}")
        if context:
            self.logger.error(f"Context: {json.dumps(context, indent=2, default=str)}")
        self.logger.error("=" * 100)

    def log_rule_based_decision(self, rule_name: str, condition: str, action: str):
        """Log rule-based decision"""
        self.logger.info(f"   📏 RULE APPLIED: {rule_name}")
        self.logger.info(f"      Condition: {condition}")
        self.logger.info(f"      Action: {action}")

    def log_llm_call(self, prompt_type: str, model: str, prompt_preview: str = None):
        """Log LLM API call"""
        self.logger.info(f"   🤖 LLM Call: {prompt_type}")
        self.logger.info(f"      Model: {model}")
        if prompt_preview:
            preview = prompt_preview[:200] + "..." if len(prompt_preview) > 200 else prompt_preview
            self.logger.info(f"      Prompt Preview: {preview}")

    def log_llm_response(self, response_preview: str, confidence: float = None):
        """Log LLM response"""
        preview = response_preview[:200] + "..." if len(response_preview) > 200 else response_preview
        self.logger.info(f"   ✓ LLM Response Preview: {preview}")
        if confidence:
            self.logger.info(f"   ✓ Confidence: {confidence}")

    def log_rag_retrieval(self, query: str, num_results: int, top_scores: list = None):
        """Log RAG retrieval"""
        self.logger.info(f"   📚 RAG Retrieval")
        self.logger.info(f"      Query: {query}")
        self.logger.info(f"      Results Found: {num_results}")
        if top_scores:
            self.logger.info(f"      Top Similarity Scores: {top_scores}")

    def log_state_transition(self, from_state: str, to_state: str, trigger: str):
        """Log state transition"""
        self.logger.info(f"   🔄 State Transition: {from_state} → {to_state}")
        self.logger.info(f"      Trigger: {trigger}")

    def info(self, message: str):
        """Standard info log"""
        self.logger.info(message)

    def warning(self, message: str):
        """Standard warning log"""
        self.logger.warning(message)

    def error(self, message: str):
        """Standard error log"""
        self.logger.error(message)

    def debug(self, message: str):
        """Standard debug log"""
        self.logger.debug(message)


def get_detailed_logger(name: str) -> DetailedLogger:
    """Get or create a detailed logger instance"""
    return DetailedLogger(name)
