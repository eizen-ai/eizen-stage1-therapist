"""
Improved Ollama Dialogue Agent - Following Dr. Q's methodology
Key improvements:
1. Give examples for sensations (ache, tight, sharp, etc.)
2. Accept answers and move forward (don't repeat questions)
3. Affirm client responses ("That's right", "Yeah")
4. Use "How do you know?" technique
5. Build vision with summarization
6. Limit body questions to 2-3 max
"""

import json
import requests
from src.utils.embedding_and_retrieval_setup import TRTRAGSystem
from src.core.session_state_manager import TRTSessionState
from src.utils.no_harm_framework import NoHarmFramework
from src.utils.language_techniques import LanguageTechniques
from src.utils.engagement_tracker import EngagementTracker
from src.utils.vision_language_templates import VisionLanguageTemplates
from src.utils.psycho_education import PsychoEducation
from src.core.alpha_sequence import AlphaSequence
from src.utils.prompt_loader import get_prompt_loader
from src.utils.detailed_logger import get_detailed_logger
import logging

# Initialize detailed logger
detailed_logger = get_detailed_logger("DialogueAgent")

class ImprovedOllamaDialogueAgent:
    """Improved Ollama Dialogue Agent following Dr. Q's real methodology"""

    def __init__(self, rag_system: TRTRAGSystem, ollama_url="http://localhost:11434", model="llama3.1"):
        self.rag_system = rag_system
        self.ollama_url = ollama_url
        self.model = model
        self.api_endpoint = f"{ollama_url}/api/generate"

        # Initialize no-harm framework
        self.no_harm_framework = NoHarmFramework()

        # Initialize new Dr. Q enhancement modules
        self.language_techniques = LanguageTechniques()
        self.engagement_tracker = EngagementTracker()
        self.vision_templates = VisionLanguageTemplates()
        self.psycho_education = PsychoEducation()
        self.alpha_sequence = AlphaSequence()

        # Initialize prompt loader
        self.prompt_loader = get_prompt_loader()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"✅ Improved Ollama Dialogue Agent initialized: {ollama_url} (model: {model})")
        self.logger.info(f"✅ Dr. Q Enhancement Modules loaded: Language Techniques, Engagement Tracking, Vision Templates, Psycho-Education, Alpha Sequence")

    def generate_response(self, client_input: str, navigation_output: dict,
                         session_state: TRTSessionState) -> dict:
        """Generate therapeutic response using improved methodology"""

        # Track engagement
        turn_number = len(session_state.conversation_history) + 1
        engagement_assessment = self.engagement_tracker.assess_engagement(client_input, turn_number)

        # PRIORITY 1: Check for self-harm/crisis (HIGHEST PRIORITY)
        if navigation_output.get('self_harm_detected', {}).get('detected', False):
            detailed_logger.log_dialogue_decision_point(
                decision_type="PRIORITY 1: Self-Harm Detection",
                reasoning="Self-harm detected - using no-harm framework response"
            )
            return self.no_harm_framework.generate_no_harm_response(
                client_input,
                navigation_output['self_harm_detected'],
                {'session_state': session_state, 'navigation': navigation_output}
            )

        # PRIORITY 2: Check for past tense redirect (BEFORE thinking mode)
        if navigation_output.get('past_tense_detected', {}).get('detected', False):
            response = self._generate_past_redirect_response(client_input)
            # Apply language techniques
            response['therapeutic_response'] = self.language_techniques.prepare_response_language(
                response['therapeutic_response']
            )
            return response

        # PRIORITY 3: Check for thinking mode redirect
        if navigation_output.get('thinking_mode_detected', {}).get('detected', False):
            response = self._generate_thinking_redirect_response(client_input)
            response['therapeutic_response'] = self.language_techniques.prepare_response_language(
                response['therapeutic_response']
            )
            return response

        # PRIORITY 4: Check for "I don't know" → offer vision language
        if navigation_output.get('i_dont_know_detected', {}).get('detected', False):
            return self._handle_i_dont_know(navigation_output['i_dont_know_detected'], session_state)

        # PRIORITY 5: Check engagement and intervene if needed
        if engagement_assessment['intervention_needed']:
            return self._generate_engagement_intervention(engagement_assessment, session_state)

        # PRIORITY 6: Check for psycho-education trigger
        if self.psycho_education.should_provide_education(session_state):
            return self._generate_psycho_education_response(session_state)

        # PRIORITY 7: Check for alpha sequence trigger (state 3.1 → 3.1.5 → 3.2)
        if navigation_output.get('current_substate') == '3.1_assess_readiness':
            # Check if client finished answering readiness questions
            client_lower = client_input.lower().strip()
            readiness_phrases = ["nothing", "no", "all good", "that's it", "i'm good", "nope", "nothing more"]

            if any(phrase in client_lower for phrase in readiness_phrases):
                # Client says nothing more to share → Ask permission for alpha
                self.logger.info("📋 Client readiness confirmed - asking permission for alpha sequence")

                # Update to permission stage
                session_state.current_substate = "3.1.5_alpha_permission"

                # Load alpha permission from config
                response = self.prompt_loader.get_redirect('alpha_permission')

                return {
                    "therapeutic_response": response,
                    "technique_used": "alpha_permission_request",
                    "examples_used": 0,
                    "rag_similarity_scores": [],
                    "navigation_reasoning": "Readiness confirmed - requesting permission for alpha",
                    "llm_confidence": 0.95,
                    "llm_reasoning": "Asking permission before starting alpha sequence",
                    "fallback_used": False,
                    "alpha_permission_requested": True
                }

        # PRIORITY 7.5: Check for alpha permission confirmation (state 3.1.5 → 3.2)
        if navigation_output.get('current_substate') == '3.1.5_alpha_permission':
            # Check if client gave permission
            client_lower = client_input.lower().strip()
            permission_phrases = ["yes", "ready", "okay", "sure", "yeah", "yep", "ok", "go ahead"]

            if any(phrase in client_lower for phrase in permission_phrases):
                # Client gave permission! Start alpha sequence
                self.logger.info("🚀 Permission granted - starting alpha sequence!")
                alpha_start = self.alpha_sequence.start_sequence()

                # CRITICAL: Mark alpha as started in session state so core system doesn't restart it
                session_state.alpha_started = True
                session_state.current_substate = "3.2_alpha_sequence"

                # Return alpha start instruction
                response_text = f"{alpha_start['instruction']} {alpha_start['checkpoint_question']}"

                return {
                    "therapeutic_response": response_text,
                    "technique_used": "alpha_sequence_start",
                    "examples_used": 0,
                    "rag_similarity_scores": [],
                    "navigation_reasoning": "Permission granted - started alpha sequence",
                    "llm_confidence": 0.95,
                    "llm_reasoning": "Client gave permission - initiated alpha sequence",
                    "fallback_used": False,
                    "alpha_sequence_started": True
                }
            else:
                # Client hesitant or unclear - reassure and re-ask
                response = self.prompt_loader.get_redirect('alpha_permission_reassurance')

                return {
                    "therapeutic_response": response,
                    "technique_used": "alpha_permission_reassurance",
                    "examples_used": 0,
                    "rag_similarity_scores": [],
                    "navigation_reasoning": "Client hesitant - reassuring and re-asking permission",
                    "llm_confidence": 0.9,
                    "llm_reasoning": "Reassuring hesitant client about alpha process",
                    "fallback_used": False
                }

        # PRIORITY 8: Check for stage_1_complete (session conclusion)
        # CRITICAL: Also check session_state directly in case state was updated by dialogue agent
        if (navigation_output.get('current_substate') == 'stage_1_complete' or
            session_state.current_substate == 'stage_1_complete' or
            session_state.alpha_complete):
            return self._generate_session_conclusion_response(client_input, session_state)

        # PRIORITY 9: Check for active alpha sequence checkpoints
        if self.alpha_sequence.sequence_active:
            return self._handle_alpha_sequence_checkpoint(client_input, session_state)

        # PRIORITY 9: Check for goal clarification (use rule-based for consistency)
        if navigation_output.get('navigation_decision') == 'clarify_goal':
            self.logger.info("📋 BYPASSING RAG: Using rule-based goal clarification")
            return self._generate_goal_clarification_response(client_input)

        # PRIORITY 9: Check for vision building (use rule-based for consistency)
        if navigation_output.get('navigation_decision') == 'build_vision':
            self.logger.info("📋 BYPASSING RAG: Using rule-based vision building")
            return self._generate_vision_building_response(session_state, client_input)

        # PRIORITY 10: Check for explore_problem when problem NOT yet identified (state 1.2 entry)
        # BUT: Only ask about problem if we haven't asked before AND user hasn't already provided problem info
        if (navigation_output.get('navigation_decision') == 'explore_problem' and
            not session_state.stage_1_completion.get('problem_identified', False) and
            navigation_output.get('current_substate') == '1.2_problem_and_body'):

            # CRITICAL: Check if user ALREADY provided problem information in their current input
            # If they did, DON'T ask "what's making it hard" - move directly to body/emotion inquiry
            client_lower = client_input.lower()
            problem_indicators = ["stress", "stressed", "anxiety", "anxious", "worry", "worried",
                                "pressure", "overwhelmed", "frustrated", "angry", "sad", "depressed",
                                "scared", "afraid", "nervous", "upset", "difficult", "hard", "problem",
                                "issue", "trouble", "concern", "bully", "bullied"]

            user_already_provided_problem = any(indicator in client_lower for indicator in problem_indicators)

            if user_already_provided_problem:
                self.logger.info("📋 User ALREADY provided problem info - skipping problem question, moving to emotion/body inquiry")
                # User already mentioned problem - don't ask "what's making it hard" again
                # Instead, this will fall through to the RAG+LLM generation which will detect
                # the problem and ask about emotion/body location
            else:
                # Check if we've already asked about the problem
                # CRITICAL: Scan last 6+ turns to catch repetitions that are further apart
                problem_question_asked = False
                if len(session_state.conversation_history) > 0:
                    # Check last 6 turns, or all history if less than 6 turns
                    scan_range = min(6, len(session_state.conversation_history))
                    for exchange in session_state.conversation_history[-scan_range:]:
                        therapist_response = exchange.get('therapist_response', '').lower()
                        problem_phrases = ["what's been making it hard", "what's been making it difficult",
                                         "what's been getting in the way"]
                        if any(phrase in therapist_response for phrase in problem_phrases):
                            problem_question_asked = True
                            self.logger.info(f"📋 Problem question already asked in last {scan_range} turns - skipping")
                            break

                # Only ask if we haven't asked before
                if not problem_question_asked:
                    self.logger.info("📋 BYPASSING RAG: Asking about problem (state 1.2 entry, first time)")
                    return self._generate_problem_inquiry_response(session_state)

        # PRIORITY 11: Check for assess_readiness in state 3.1 (with NEW problem detection)
        if (navigation_output.get('navigation_decision') == 'assess_readiness' and
            navigation_output.get('current_substate') == '3.1_assess_readiness'):
            self.logger.info("📋 BYPASSING RAG: Assessing readiness for alpha (state 3.1)")
            return self._generate_readiness_assessment_response(session_state, client_input)

        # Get RAG examples
        self.logger.info(f"🎯 USING RAG for decision: {navigation_output.get('navigation_decision')}")
        rag_examples = self.rag_system.get_few_shot_examples(
            navigation_output,
            client_input,
            max_examples=3
        )
        self.logger.info(f"📚 RAG returned {len(rag_examples)} examples for LLM prompting")

        # HYBRID APPROACH: Decide when to use RAG+LLM vs Rules
        decision = navigation_output.get('navigation_decision', '')
        current_substate = navigation_output.get('current_substate', '')
        body_q_count = session_state.body_questions_asked

        # ESCAPE CONDITIONS - Prevent loops and ensure progress
        # EXCEPTION: Don't escape if we're in body enquiry cycle 2
        in_cycle_2 = navigation_output.get('in_cycle_2', False)

        should_escape_body = (
            body_q_count >= 5 or  # Hit body question limit
            (current_substate == '3.1_assess_readiness' and not in_cycle_2) or  # Moved to readiness (unless cycle 2)
            current_substate == '3.2_alpha_sequence' or  # In alpha sequence
            self.alpha_sequence.sequence_active  # Alpha is active
        )

        # Check if we should affirm and move forward (rule-based)
        if self._should_affirm_and_proceed(client_input, session_state, navigation_output):
            # EXCEPTION: Use RAG for body exploration follow-ups (if not escaping)
            if (decision in ['body_symptoms_exploration', 'explore_problem', 'pattern_inquiry'] and
                len(rag_examples) > 0 and
                not should_escape_body):
                self.logger.info(f"🎯 HYBRID: Using RAG+LLM for {decision} (not rule-based affirmation)")
                llm_response = self._generate_llm_therapeutic_response(
                    client_input, navigation_output, rag_examples, session_state
                )
                # Count all body-related exploration toward limit (not just specific types)
                # This includes explore_problem when in body exploration context
                if current_substate == '1.2_problem_and_body':
                    session_state.body_questions_asked += 1
                    self.logger.info(f"📊 Body question count: {session_state.body_questions_asked}/5")
            elif should_escape_body:
                # Escape body loop - move forward without more body questions
                self.logger.info(f"⚠️ ESCAPE: Body exploration limit reached (count={body_q_count}), progressing naturally")

                # Varied body awareness questions (not "How are you feeling NOW?" - that's for present moment)
                import random
                body_awareness_questions = [
                    "What sensations or changes do you notice in your body?",
                    "What are you noticing in your body right now?",
                    "What's happening in your body at this moment?",
                    "What do you feel in your body right now?"
                ]

                return {
                    "therapeutic_response": f"Got it. {random.choice(body_awareness_questions)}",
                    "technique_used": "escape_body_loop",
                    "examples_used": 0,
                    "rag_similarity_scores": [],
                    "navigation_reasoning": f"Escaped body questions (count {body_q_count}), moving to present moment",
                    "llm_confidence": 0.9,
                    "llm_reasoning": "Loop prevention - asking about present moment to progress",
                    "fallback_used": False
                }
            else:
                # Use rule-based affirmation (standard flow)
                self.logger.info(f"📋 BYPASSING LLM: Using rule-based affirmation (RAG examples retrieved but not used)")
                return self._generate_affirmation_response(client_input, session_state, navigation_output)

        # Check if client is confused - clarify
        elif session_state.last_client_provided_info == "confusion":
            self.logger.info("📋 BYPASSING LLM: Using rule-based clarification (RAG examples retrieved but not used)")
            return self._generate_clarification_response(client_input, navigation_output, session_state)

        # Use RAG+LLM for exploratory scenarios (if not escaping)
        elif (decision in ['body_symptoms_exploration', 'explore_problem', 'pattern_inquiry', 'general_inquiry'] and
              len(rag_examples) > 0 and
              not should_escape_body):
            self.logger.info(f"🤖 GENERATING LLM RESPONSE with {len(rag_examples)} RAG examples for {decision}")
            llm_response = self._generate_llm_therapeutic_response(
                client_input, navigation_output, rag_examples, session_state
            )
            # Count all body-related exploration toward limit when in body exploration substate
            if current_substate == '1.2_problem_and_body':
                session_state.body_questions_asked += 1
                self.logger.info(f"📊 Body question count: {session_state.body_questions_asked}/5")

        # Escape condition met - move forward with simple affirmation
        elif should_escape_body:
            self.logger.info(f"⚠️ ESCAPE: Body exploration complete (count={body_q_count}, state={current_substate}), moving forward")
            return {
                "therapeutic_response": "Tell me more about that.",
                "technique_used": "escape_body_loop",
                "examples_used": 0,
                "rag_similarity_scores": [],
                "navigation_reasoning": f"Escaped body questions (count {body_q_count}), progressing naturally",
                "llm_confidence": 0.85,
                "llm_reasoning": "Loop prevention - moving forward",
                "fallback_used": False
            }

        # Default: Generate LLM response with RAG
        else:
            self.logger.info(f"🤖 GENERATING LLM RESPONSE with {len(rag_examples)} RAG examples (default path)")
            llm_response = self._generate_llm_therapeutic_response(
                client_input, navigation_output, rag_examples, session_state
            )

        return {
            "therapeutic_response": llm_response["response"],
            "technique_used": navigation_output["rag_query"],
            "examples_used": len(rag_examples),
            "rag_similarity_scores": [ex["similarity_score"] for ex in rag_examples],
            "navigation_reasoning": navigation_output["reasoning"],
            "llm_confidence": llm_response.get("confidence", 0.8),
            "llm_reasoning": llm_response.get("reasoning", ""),
            "fallback_used": llm_response.get("fallback_used", False)
        }

    def _should_affirm_and_proceed(self, client_input: str, session_state: TRTSessionState, navigation_output: dict) -> bool:
        """Check if we should just affirm and move forward (like Dr. Q does)"""

        # If client just provided body location (and hasn't been asked about sensation yet)
        if session_state.last_client_provided_info == "body_location":
            return True

        # If client just provided sensation quality (and hasn't been asked about present moment yet)
        if session_state.last_client_provided_info == "sensation_quality":
            return True

        # If client affirmed ("yes", "that's right"), acknowledge and proceed
        if session_state.last_client_provided_info == "affirmation":
            return True

        return False

    def _detect_and_acknowledge_emotion(self, client_input: str) -> str:
        """Detect emotion in client input and generate appropriate acknowledgment"""

        client_lower = client_input.lower().strip()

        # Define emotion categories
        positive_emotions = {
            "good": "good",
            "great": "great",
            "better": "better",
            "okay": "okay",
            "fine": "fine",
            "calm": "calm",
            "peaceful": "peaceful",
            "happy": "happy",
            "relaxed": "relaxed",
            "lighter": "lighter",
            "easier": "easier",
            "relieved": "relieved"
        }

        negative_emotions = {
            "overwhelmed": "overwhelmed",
            "stressed": "stressed",
            "anxious": "anxious",
            "depressed": "down",
            "sad": "sad",
            "angry": "angry",
            "frustrated": "frustrated",
            "annoyed": "annoyed",
            "irritated": "irritated",
            "upset": "upset",
            "worried": "worried",
            "scared": "scared",
            "afraid": "afraid",
            "nervous": "nervous",
            "lost": "lost",
            "stuck": "stuck",
            "confused": "confused",
            "tired": "tired",
            "exhausted": "exhausted",
            "drained": "drained",
            "bad": "bad",
            "not good": "not good",
            "terrible": "terrible",
            "awful": "awful",
            "hard": "hard",
            "difficult": "difficult",
            "heavy": "heavy",
            "gloomy": "gloomy",
            "down": "down",
            "lonely": "lonely",
            "hopeless": "hopeless",
            "miserable": "miserable",
            "unhappy": "unhappy",
            "depressing": "depressing"
        }

        # Check for emotions
        detected_emotion = None
        is_positive = False

        # Check positive emotions first (more specific)
        for emotion_word, emotion_label in positive_emotions.items():
            if emotion_word in client_lower:
                detected_emotion = emotion_label
                is_positive = True
                break

        # If no positive emotion, check negative
        if not detected_emotion:
            for emotion_word, emotion_label in negative_emotions.items():
                if emotion_word in client_lower:
                    detected_emotion = emotion_label
                    is_positive = False
                    break

        # Generate acknowledgment
        if detected_emotion:
            if is_positive:
                # Positive: acknowledge in PRESENT tense with enthusiasm
                return f"You're feeling {detected_emotion}, that's great! "
            else:
                # Negative: acknowledge in PAST tense (Dr. Q method)
                return f"So you've been feeling {detected_emotion}. "

        return ""  # No emotion detected

    def _detect_pattern_language(self, client_input: str) -> dict:
        """Detect if client is describing a recurring pattern (for 'How do you know?' technique)"""

        client_lower = client_input.lower()

        # Pattern indicators that suggest recurring experiences
        pattern_words = ["always", "often", "usually", "constantly", "every time", "whenever",
                        "keep", "keeps", "repeatedly", "again and again", "all the time",
                        "never", "struggle", "struggling", "finding difficulty"]

        # Emotional/relational patterns
        pattern_phrases = ["feel like", "feeling like", "i am disappointing", "not able to",
                          "can't seem to", "having trouble", "difficulty with"]

        # Check for pattern indicators
        has_pattern_word = any(word in client_lower for word in pattern_words)
        has_pattern_phrase = any(phrase in client_lower for phrase in pattern_phrases)

        if has_pattern_word or has_pattern_phrase:
            # Extract what they're describing (for use in "How do you know?" question)
            # Try to identify the emotion or situation they mentioned
            emotion_words = ["disappointing", "anxious", "stressed", "worried", "frustrated",
                           "angry", "sad", "overwhelmed", "upset", "afraid", "scared"]

            detected_emotion = None
            for emotion in emotion_words:
                if emotion in client_lower:
                    detected_emotion = emotion
                    break

            return {
                "detected": True,
                "emotion_or_pattern": detected_emotion or "that",
                "full_input": client_input
            }

        return {"detected": False}

    def _generate_affirmation_response(self, client_input: str, session_state: TRTSessionState, navigation_output: dict) -> dict:
        """Generate affirmation + optional reflection/validation + next logical question (like Dr. Q)"""

        client_lower = client_input.lower()

        # FIRST: Detect if client mentioned a pattern (for "How do you know?" technique)
        pattern_detected = self._detect_pattern_language(client_input)

        # SECOND: Check for emotion and acknowledge it (Dr. Q method)
        emotion_acknowledgment = self._detect_and_acknowledge_emotion(client_input)

        # Use Dr. Q's natural affirmations - vary them
        affirmations = ["That's right.", "Yeah.", "Got it.", "Okay."]
        import random
        affirmation = random.choice(affirmations)

        # CHECK: Should we use "How do you know?" technique for pattern exploration?
        # Only use if: pattern detected, in problem/body exploration state, and haven't used it yet
        use_how_do_you_know = False
        current_substate = navigation_output.get('current_substate', '')

        if (pattern_detected.get('detected', False) and
            current_substate == '1.2_problem_and_body' and
            not getattr(session_state, 'how_do_you_know_asked', False) and
            len(client_input.split()) > 8 and  # Substantial input
            random.random() < 0.3):  # 30% chance for variety

            use_how_do_you_know = True
            session_state.how_do_you_know_asked = True  # Mark as used for this session

        # NEW: Add reflection/validation if client provided substantial information (>5 words)
        # This makes conversation more elaborative like Dr. Q
        add_reflection = len(client_input.split()) > 5 and random.random() < 0.4  # 40% chance for variety

        # NEW #5: Detect when client is providing LONG elaboration (>20 words)
        # Dr. Q encourages elaboration without asking immediate questions
        client_is_elaborating = len(client_input.split()) > 20
        encourage_more_elaboration = client_is_elaborating and random.random() < 0.4  # 40% chance

        # Generate reflection text if needed (Dr. Q style - summarize what they said)
        reflection_text = ""
        if add_reflection:
            # Extract key content from client input for reflection
            # Dr. Q often reflects back the essence: "So that [situation] has [impact]"
            reflection_templates = [
                f"So {client_input.lower()}.",
                f"I hear that {client_input.lower()}.",
                "Right, I understand."
            ]
            # Use first template if input is long enough, otherwise generic
            if len(client_input.split()) > 8:
                reflection_text = reflection_templates[0]
            else:
                reflection_text = random.choice(reflection_templates[1:])

        # Determine next question based on what was just provided
        if session_state.last_client_provided_info == "emotion":
            # They gave emotion, now ask where they feel it in body
            emotion = session_state.stage_1_completion.get("emotion_content", "that")
            next_question = f"Where do you feel that {emotion} in your body?"

        elif session_state.last_client_provided_info == "body_location":
            # Check if they mentioned sensation words (hurt, pain, ache, etc.)
            sensation_indicators = ["hurt", "hurting", "pain", "painful", "ache", "aching",
                                   "tight", "tightness", "pressure", "heavy", "sharp", "dull"]
            client_mentioned_sensation = any(word in client_input.lower() for word in sensation_indicators)

            # If they mentioned sensation AND haven't explored quality yet, ask about type
            if (client_mentioned_sensation and
                not session_state.body_sensation_described and
                not session_state.anything_else_asked):
                # Ask about sensation quality
                import random
                sensation_quality_questions = [
                    "What kind of sensation?",
                    "What kind of hurt is it? Achy? Stabbing?",
                    "What does that feel like? Is it an ache? Pressure?",
                    "What kind of sensation is that? Tight? Pressure?"
                ]
                next_question = random.choice(sensation_quality_questions)
            # Otherwise, gracefully check if there's more (don't force details)
            elif not session_state.anything_else_asked:
                # Ask if there's more to share (graceful exploration)
                import random
                what_else_variations = [
                    "What else comes to mind?",
                    "What else are you noticing?",
                    "So tell me more about what's going on for you",
                    "What else would be useful for me to know?"
                ]
                next_question = random.choice(what_else_variations)
            else:
                # Already asked "What else?" - move to present moment grounding
                next_question = "How are you feeling NOW?"

        elif session_state.last_client_provided_info == "sensation_quality":
            # They described sensation, check if we've asked "What else?" yet
            if not session_state.anything_else_asked:
                # First ask if there's more to share
                import random
                what_else_questions = [
                    "What else?",
                    "What else comes to mind?",
                    "What else would be useful for me to know?",
                    "What else are you noticing?"
                ]
                next_question = random.choice(what_else_questions)
            else:
                # Already asked "What else?", now move to present moment
                candidate_q = "How are you feeling NOW?"
                # Check if we've EVER asked about present moment (not just recently)
                if not session_state.stage_1_completion.get("present_moment_focus", False) and "feeling now" not in str(session_state.questions_asked_set).lower():
                    next_question = candidate_q
                else:
                    # Already asked about present moment OR already established
                    # Check if we're ready to move to readiness assessment
                    if not session_state.stage_1_completion.get("problem_identified"):
                        next_question = "What's been making it hard?"
                    else:
                        # Problem identified + present moment focus → move to readiness
                        next_question = "What haven't I understood? Is there more I should know?"

        elif session_state.last_client_provided_info == "nothing_more":
            # Client said "nothing" or "that's it" (likely after "What else?" question)
            # Move to present moment
            next_question = "How are you feeling NOW?"

        elif session_state.last_client_provided_info == "affirmation":
            # They affirmed, move to next stage topic based on completion status
            completion = session_state.stage_1_completion

            # CRITICAL: Check if they just affirmed "You're feeling that right now" or "How are you feeling that NOW"
            if session_state.last_question_asked and ("feeling that right now" in session_state.last_question_asked or
                                                       "feeling that now" in session_state.last_question_asked.lower()):
                # They confirmed present moment, mark it complete
                session_state.stage_1_completion["present_moment_focus"] = True
                completion = session_state.stage_1_completion  # Update reference

            # CRITICAL: Check if client just elaborated on a problem (in their affirmation response)
            # If they mentioned problem words, we should shift to emotion inquiry, NOT ask "what's making it hard" again
            problem_mentioned_in_response = any(word in client_input.lower() for word in [
                "beat", "bully", "bullied", "insult", "hurt", "abuse", "problem", "difficult",
                "stress", "pressure", "worry", "anxiety", "scared", "afraid"
            ])

            # Priority order for what to ask next (Dr. Q's actual flow)
            if not completion["goal_stated"]:
                next_question = "What do you want our time to focus on today?"
            elif not completion["vision_accepted"]:
                # Vision should be built by rule, but if we're here, ask confirming question
                next_question = "Does that make sense to you?"
            elif not completion.get("psycho_education_provided", False):
                # After vision accepted, psycho-education will be provided by PRIORITY 6
                # If we're in affirmation logic and psycho-education not yet provided,
                # this shouldn't happen - but if it does, move to problem inquiry
                next_question = "So what's been making it hard for you?"
            elif not completion["body_awareness_present"]:
                # Check if problem was just mentioned - if so, shift to emotion/body inquiry
                if problem_mentioned_in_response:
                    # Client just described problem - shift to present emotion/feeling inquiry
                    import random
                    emotion_inquiry_questions = [
                        "And as you describe that, what do you feel? What do you notice inside?",
                        "As you talk about that now, what are you feeling? What do you notice?",
                        "And when you say that, what are you feeling right now?",
                        "What do you feel as you describe that? What's happening inside?"
                    ]
                    next_question = random.choice(emotion_inquiry_questions)
                else:
                    # Problem not mentioned recently - ask about problem
                    next_question = "So what's been making it hard for you?"
            elif not completion["present_moment_focus"]:
                # Dr. Q's ACTUAL style: Simple and direct - BUT ONLY ASK ONCE!
                # "How are you feeling NOW?" (not "that NOW")
                candidate_q = "How are you feeling NOW?"
                # Check if we've EVER asked this (not just recently)
                if "feeling now" not in str(session_state.questions_asked_set).lower():
                    next_question = candidate_q
                else:
                    # Already asked about present moment, mark as complete and move on
                    session_state.stage_1_completion["present_moment_focus"] = True
                    if not completion["problem_identified"]:
                        next_question = "What's been making it hard?"
                    else:
                        # Problem identified + present moment focus → move to readiness
                        next_question = "What haven't I understood? Is there more I should know?"
            else:
                # All criteria met - move toward readiness
                next_question = "What haven't I understood? Is there more I should know?"
        else:
            next_question = "Tell me more about that."

        # OVERRIDE #1: If we should use "How do you know?" technique, replace next_question
        if use_how_do_you_know:
            emotion_or_pattern = pattern_detected.get('emotion_or_pattern', 'that')
            # Dr. Q's style: "How do you know when [pattern]? What is it that's happening in that moment?"
            how_do_you_know_questions = [
                f"How do you know when you feel {emotion_or_pattern}? What is it that's happening in that moment?",
                f"How do you know when that feeling starts? What's happening in that moment?",
                f"What is it that triggers {emotion_or_pattern} for you? How do you know when it's coming?",
                f"How do you recognize when {emotion_or_pattern} is happening? What's going on in that moment?"
            ]
            next_question = random.choice(how_do_you_know_questions)
            self.logger.info(f"💡 Using 'How do you know?' technique for pattern exploration")

        # OVERRIDE #2: If client is elaborating (>20 words), encourage more instead of asking question
        # Dr. Q's style: "So keep going", "Tell me more", or just reflection
        if encourage_more_elaboration and not use_how_do_you_know:  # Don't override "How do you know?"
            encouragement_phrases = [
                "So keep going.",
                "Tell me more about that.",
                "Yeah, go on.",
                "Right.",  # Just affirmation, client continues
                ""  # Sometimes just reflection, no question
            ]
            next_question = random.choice(encouragement_phrases)
            self.logger.info(f"💬 Encouraging elaboration instead of asking next question (client provided {len(client_input.split())} words)")

        # Build response: emotion acknowledgment (if any) + affirmation + reflection (if any) + next question
        if emotion_acknowledgment:
            # Emotion detected: use emotion acknowledgment instead of generic affirmation
            if reflection_text:
                # Insert reflection between acknowledgment and question for elaboration
                response = f"{emotion_acknowledgment}{reflection_text} {next_question}"
            else:
                response = f"{emotion_acknowledgment}{next_question}"
        else:
            # No emotion: use standard affirmation with optional reflection
            if reflection_text:
                # Insert reflection between affirmation and question for elaboration
                response = f"{affirmation} {reflection_text} {next_question}"
            else:
                response = f"{affirmation} {next_question}"

        return {
            "therapeutic_response": response,
            "technique_used": "affirmation_and_proceed",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Affirmed client answer and moved forward (Dr. Q style)" + (" with emotion acknowledgment" if emotion_acknowledgment else ""),
            "llm_confidence": 0.9,
            "llm_reasoning": "Dr. Q style: affirm and proceed with natural language",
            "fallback_used": False
        }

    def _generate_clarification_response(self, client_input: str, navigation_output: dict, session_state: TRTSessionState) -> dict:
        """Generate clarification when client is confused"""

        client_lower = client_input.lower()

        # If asking about "sensations" - give examples like Dr. Q
        if "sensation" in client_lower or "feel like" in client_lower or "mean by" in client_lower:
            response = "Let me clarify - when I ask about sensations, I mean things like: Is it an ache? Is it tight or pressure? Sharp or dull? Heavy or weighted? What kind of physical feeling is it?"

        # If asking about body location - give examples (Dr. Q method)
        elif "where" in client_lower or "don't know where" in client_lower or "not sure where" in client_lower:
            response = "It could be anywhere - your head, chest, stomach, shoulders, feet. Whatever comes to mind first, that's it. Where do you notice it?"

        else:
            response = "Let me ask it a different way. What are you noticing in your body right now?"

        return {
            "therapeutic_response": response,
            "technique_used": "clarification",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Clarified confused client with examples",
            "llm_confidence": 0.9,
            "llm_reasoning": "Provided concrete examples",
            "fallback_used": False
        }

    def _generate_thinking_redirect_response(self, client_input: str) -> dict:
        """Redirect from thinking mode to feeling mode (Dr. Q style)"""

        # Load redirect response from config
        response = self.prompt_loader.get_redirect('thinking_mode')

        return {
            "therapeutic_response": response,
            "technique_used": "thinking_mode_redirect",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Redirected from thinking to feeling (Dr. Q style)",
            "llm_confidence": 0.95,
            "llm_reasoning": "THINK priority state activated with natural language",
            "fallback_used": False
        }

    def _generate_past_redirect_response(self, client_input: str) -> dict:
        """Redirect from past tense to present moment (Dr. Q style)"""

        # Load redirect response from config
        response = self.prompt_loader.get_redirect('past_tense')

        return {
            "therapeutic_response": response,
            "technique_used": "past_tense_redirect",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Redirected from past to present (Dr. Q style)",
            "llm_confidence": 0.95,
            "llm_reasoning": "PAST priority state activated with natural language",
            "fallback_used": False
        }

    def _generate_goal_clarification_response(self, client_input: str = "", navigation_output: dict = None) -> dict:
        """Generate goal clarification response (rule-based, Dr. Q style)"""

        # Dr. Q's natural conversational style - warm, multiple questions, building rapport
        # If client mentioned a feeling/problem, acknowledge it first
        if client_input:
            client_lower = client_input.lower()
            self.logger.debug(f"[GOAL_CLARIFICATION] Processing input: '{client_input}'")

            # Check if client said "I don't know" - offer menu of options (Dr. Q style)
            if any(phrase in client_lower for phrase in ["i don't know", "i dont know", "not sure", "don't know"]):
                # Use vision language templates to offer menu
                vision_response = self.vision_templates.get_vision_response(context="goal")
                return {
                    "therapeutic_response": vision_response['full_response'],
                    "technique_used": "goal_clarification_with_menu",
                    "examples_used": 0,
                    "rag_similarity_scores": [],
                    "navigation_reasoning": "Client doesn't know goal - offering menu of options (Dr. Q style)",
                    "llm_confidence": 0.95,
                    "llm_reasoning": "Offered vision language menu for uncertain client",
                    "fallback_used": False
                }

            # Use LLM to detect emotion and intensity
            emotion_analysis = self._detect_emotion_with_llm(client_input)

            # Varied follow-up questions (Dr. Q style - natural variety)
            import random
            goal_questions = [
                "What do we want our time to focus on today?",
                "What would you like to get out of our session today?",
                "What do we want to get better for you?",
                "What would you like to focus on today?",
                "What do you want our time together to accomplish?"
            ]

            if emotion_analysis:
                emotional_state = emotion_analysis.get("emotional_state", "neutral")
                acknowledgment = emotion_analysis.get("acknowledgment", "")

                # Pick a varied question
                question = random.choice(goal_questions)
                response = f"{acknowledgment} {question}"

                self.logger.info(f"[GOAL_CLARIFICATION] 💬 LLM emotion detection: {emotional_state} → '{response}'")
            else:
                # LLM failed, use generic acknowledgment with variety
                generic_acknowledgments = [
                    "I hear you.",
                    "Okay, I hear that.",
                    "I understand."
                ]
                ack = random.choice(generic_acknowledgments)
                question = random.choice(goal_questions)
                response = f"{ack} {question}"
                self.logger.info(f"[GOAL_CLARIFICATION] 💬 LLM detection failed, using fallback: '{response}'")
        else:
            # No client input provided (shouldn't happen, but fallback)
            response = "So what do you want our time to focus on today? What do we want to get better for you?"

        return {
            "therapeutic_response": response,
            "technique_used": "goal_clarification",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Clarifying therapeutic goal (Dr. Q style with LLM emotion acknowledgment)",
            "llm_confidence": 0.95,
            "llm_reasoning": "LLM-based emotion detection with varied follow-up questions",
            "fallback_used": False
        }

    def _detect_emotion_with_llm(self, client_input: str) -> dict:
        """Use LLM to detect emotion and generate appropriate acknowledgment"""

        # Load prompt template from config
        prompt_template = self.prompt_loader.get_prompt('dialogue_agent', 'emotion_detection')
        prompt = prompt_template.format(client_input=client_input)

        try:
            # Call Ollama
            llm_response = self._call_ollama(prompt)
            self.logger.debug(f"[EMOTION_DETECTION] LLM raw response: {llm_response}")

            # Parse JSON from response
            # Clean response - extract JSON if wrapped in text
            cleaned = llm_response.strip()

            # Find JSON object
            start_idx = cleaned.find('{')
            end_idx = cleaned.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = cleaned[start_idx:end_idx+1]
                emotion_data = json.loads(json_str)
                self.logger.info(f"[EMOTION_DETECTION] ✅ Detected: {emotion_data.get('emotional_state')} ({emotion_data.get('intensity')})")
                return emotion_data
            else:
                self.logger.warning(f"[EMOTION_DETECTION] ⚠️ No JSON found in response")
                return None

        except Exception as e:
            self.logger.error(f"[EMOTION_DETECTION] ❌ LLM emotion detection failed: {e}")
            return None

    def _generate_problem_inquiry_response(self, session_state: TRTSessionState) -> dict:
        """Generate initial problem inquiry (state 1.2 entry) - rule-based"""

        # Extract goal from session state
        goal_content = session_state.stage_1_completion.get("goal_content", "")

        # Extract desired state from goal
        goal_lower = goal_content.lower() if goal_content else ""

        # Common goal states to reference
        goal_states = {
            "peace": "peaceful",
            "peaceful": "peaceful",
            "calm": "calm",
            "better": "better",
            "happy": "happy",
            "grounded": "grounded",
            "relaxed": "relaxed"
        }

        # Find what they want
        desired_state = None
        for key, value in goal_states.items():
            if key in goal_lower:
                desired_state = value
                break

        # Varied problem inquiry questions (Dr. Q style)
        import random
        if desired_state:
            # Reference their goal
            problem_questions = [
                f"So what's been making it hard for you to feel {desired_state}?",
                f"What's been getting in the way of you feeling {desired_state}?",
                f"What's been making it difficult for you?"
            ]
        else:
            # Generic problem inquiry
            problem_questions = [
                "So what's been making it hard for you?",
                "What's been making it difficult?",
                "What's been getting in the way?"
            ]

        response = random.choice(problem_questions)

        return {
            "therapeutic_response": response,
            "technique_used": "problem_inquiry_initial",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Initial problem inquiry (state 1.2 entry) - Dr. Q style",
            "llm_confidence": 0.95,
            "llm_reasoning": "Rule-based problem inquiry with goal reference",
            "fallback_used": False
        }

    def _generate_readiness_assessment_response(self, session_state: TRTSessionState, client_input: str = "") -> dict:
        """Generate readiness assessment for alpha (state 3.1) - with NEW problem detection"""

        # CRITICAL: Check if client is providing NEW problem/emotion
        # If yes, start a NEW body enquiry cycle instead of just asking "what else?"
        client_lower = client_input.lower().strip() if client_input else ""

        # Detect NEW problems/stressors/emotions mentioned
        stressor_words = [
            "work", "job", "boss", "deadline", "pressure", "stress", "overwhelm",
            "family", "parent", "spouse", "partner", "child", "sibling", "argument",
            "relationship", "friend", "conflict", "fight",
            "money", "financial", "debt", "bills",
            "health", "pain", "sick", "illness",
            "school", "study", "exam", "grade",
            "bully", "bullied", "bullying"  # ADDED: bullying as stressor
        ]

        emotion_words = [
            "anxious", "anxiety", "worry", "worried", "nervous",
            "sad", "sadness", "depressed", "down", "unhappy",
            "angry", "anger", "mad", "frustrated", "irritated", "annoyed",
            "hurt", "pain", "ache", "suffering",
            "scared", "fear", "afraid", "terrified",
            "lonely", "alone", "isolated",
            "guilty", "shame", "ashamed",
            "overwhelmed", "exhausted", "tired", "drained",
            "hate", "hatred"  # ADDED: hate as strong emotion
        ]

        # Check if client is mentioning a NEW stressor or emotion
        new_stressor_detected = any(word in client_lower for word in stressor_words)
        new_emotion_detected = any(word in client_lower for word in emotion_words)

        # Also check for phrases indicating new information (not "nothing")
        has_new_information = (
            len(client_lower.split()) > 3 and  # More than just "no" or "nothing"
            "nothing" not in client_lower and
            "no" != client_lower.strip() and
            "nope" not in client_lower and
            "all good" not in client_lower
        )

        # If NEW problem/emotion detected, start NEW body enquiry cycle
        # BUT only if we haven't reached MAX 2 cycles
        if (new_stressor_detected or new_emotion_detected) and has_new_information and session_state.body_enquiry_cycles < 2:
            # Extract the emotion or problem mentioned
            detected_emotion = None
            detected_problem = None

            for emotion in emotion_words:
                if emotion in client_lower:
                    detected_emotion = emotion
                    break

            for stressor in stressor_words:
                if stressor in client_lower:
                    detected_problem = stressor
                    break

            # Construct body location question (Dr. Q style with options)
            if detected_emotion:
                response = f"Where do you feel that {detected_emotion} in your body? Chest? Head? Shoulders?"
                reasoning = f"NEW emotion detected: {detected_emotion} - starting body enquiry cycle 2"
            elif detected_problem:
                response = f"Where do you feel that in your body? Is it in your chest, head, shoulders, stomach?"
                reasoning = f"NEW problem detected: {detected_problem} - starting body enquiry cycle 2"
            else:
                response = "Where do you feel that in your body? Chest, head, shoulders?"
                reasoning = "NEW information provided - starting body enquiry cycle 2"

            self.logger.info(f"🔄 READINESS PHASE: Detected new problem/emotion - starting NEW body enquiry cycle")
            self.logger.info(f"   Detected emotion: {detected_emotion}, problem: {detected_problem}")

            # Mark that we're starting a second body enquiry cycle
            # Reset last_client_provided_info to track new cycle
            session_state.last_client_provided_info = "new_problem_mentioned"

            # Increment body enquiry cycle counter if we haven't reached max
            # We're in readiness (after cycle 1), so this is cycle 2
            if session_state.body_enquiry_cycles < 2:
                session_state.body_enquiry_cycles = 2  # Mark as cycle 2
                self.logger.info(f"   Starting cycle {session_state.body_enquiry_cycles}/2")

            return {
                "therapeutic_response": response,
                "technique_used": "body_enquiry_cycle_2",
                "examples_used": 0,
                "rag_similarity_scores": [],
                "navigation_reasoning": reasoning,
                "llm_confidence": 0.95,
                "llm_reasoning": "New problem detected during readiness - starting second body enquiry cycle",
                "fallback_used": False,
                "new_cycle_started": True
            }

        # Otherwise, continue with regular readiness questions
        import random
        readiness_questions = [
            "What haven't I understood? Is there more I should know?",
            "What else should I know? Anything I'm missing?",
            "Is there anything else I should understand?",
            "What haven't we covered? Anything more?"
        ]

        response = random.choice(readiness_questions)

        return {
            "therapeutic_response": response,
            "technique_used": "readiness_assessment",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Assessing readiness for alpha sequence (state 3.1) - Dr. Q style",
            "llm_confidence": 0.95,
            "llm_reasoning": "Rule-based readiness assessment, NO body questions",
            "fallback_used": False
        }

    def _generate_vision_building_response(self, session_state: TRTSessionState, client_input: str = "") -> dict:
        """Generate vision building response (rule-based for consistency)"""

        # Extract goal from session state - handle both dict and direct access
        try:
            if isinstance(session_state.stage_1_completion, dict):
                goal_content = session_state.stage_1_completion.get("goal_content", "")
            else:
                goal_content = getattr(session_state.stage_1_completion, "goal_content", "")
        except:
            goal_content = ""

        # CRITICAL FIX: Check if current input contains a goal clarification
        # When user says "calm", "peaceful", "at peace" etc., use THAT as the goal instead
        client_lower = client_input.lower() if client_input else ""

        # Common goal keywords that might appear in current input
        goal_keywords = {
            "peace": "peaceful",
            "peaceful": "peaceful",
            "calm": "calm",
            "happy": "happy",
            "grounded": "grounded",
            "relaxed": "relaxed",
            "free": "free",
            "strong": "strong",
            "confident": "confident",
            "at ease": "at ease",
            "lighter": "lighter",
            "centered": "centered"
        }

        # Check if user just provided a clear goal in their input
        clarified_goal = None
        for keyword, state in goal_keywords.items():
            if keyword in client_lower:
                clarified_goal = state
                # Update session state with the clarified goal
                if isinstance(session_state.stage_1_completion, dict):
                    session_state.stage_1_completion["goal_content"] = f"want to be {state}"
                self.logger.info(f"[VISION_BUILDING] ✅ User clarified goal to: '{state}' - updating session state")
                break

        # Extract key words from goal
        goal_lower = goal_content.lower() if goal_content else ""

        # Common goal states
        goal_mappings = {
            "peace": "peaceful",
            "peaceful": "peaceful",
            "calm": "calm",
            "better": "lighter and more at ease",
            "happy": "happy",
            "grounded": "grounded",
            "relaxed": "relaxed",
            "free": "free",
            "strong": "strong"
        }

        # Vague goals that need clarification (Dr. Q style - offer options)
        vague_goals = ["good", "better", "fine", "okay", "alright", "well", "normal"]

        # Check if goal is vague - BUT ONLY if user didn't just clarify it!
        # If user just said "calm" or "peaceful", we should build vision, not ask for clarification again
        is_vague = any(vague in goal_lower for vague in vague_goals) and not clarified_goal

        if is_vague:
            # Offer Dr. Q's vision options
            import random
            clarification_responses = [
                "What does 'good' mean to you? Is it calm? Peaceful? Confident? More grounded?",
                "When you say 'good', what does that look like? Calm? At ease? Lighter? More relaxed?",
                "Help me understand 'good' - is it peaceful? Calm? Confident? Free?"
            ]
            response = random.choice(clarification_responses)

            self.logger.info(f"[VISION_BUILDING] 💬 Vague goal detected ('{goal_content}'), asking for clarification")

            return {
                "therapeutic_response": response,
                "technique_used": "vision_clarification",
                "examples_used": 0,
                "rag_similarity_scores": [],
                "navigation_reasoning": "Goal is vague - asking for clarification with options (Dr. Q style)",
                "llm_confidence": 0.95,
                "llm_reasoning": "Clarifying vague goal before building vision",
                "fallback_used": False
            }

        # Find what they want - prioritize clarified goal from current input
        desired_state = clarified_goal  # Use clarified goal if available

        if not desired_state:
            # Fall back to checking stored goal_content
            for key, value in goal_mappings.items():
                if key in goal_lower:
                    desired_state = value
                    break

        # If still no specific state found, use generic
        if not desired_state:
            desired_state = "at ease"

        # Log vision building
        if clarified_goal:
            self.logger.info(f"[VISION_BUILDING] ✅ Building vision with clarified goal: '{desired_state}'")
        else:
            self.logger.info(f"[VISION_BUILDING] 💬 Building vision with stored goal: '{desired_state}'")

        # Build ELABORATE vision response like Dr. Q - 4-5 sentences with multiple descriptors
        import random

        # Dr. Q style: Acknowledge goal, expand on multiple aspects, paint detailed picture, confirm
        vision_templates = [
            f"Got it. So you want to be {desired_state}. I'm seeing you who's {desired_state}, where you're not carrying all that weight, right? You're lighter, more at ease, more grounded in yourself. Not so caught up in the worry or the stress. More emotionally present, right here in the moment. Does that make sense to you?",

            f"Okay. You want to be {desired_state}. So I see you {desired_state}, calm, centered in yourself. Not so much in your head, not so much caught up in all the overthinking. More grounded, more okay in you. Lighter, right? Not carrying all that heaviness. Does that resonate with you?",

            f"I hear you. You want to be {desired_state}. So we want to get you to where you're {desired_state}, at ease, lighter. Not so much in that stressed state, not so much triggered by what's happening around you. More emotionally present, more grounded. Like you're okay in yourself. Does that feel right to you?",

            f"Yeah. So you want to be {desired_state}. I'm seeing you who's {desired_state}, calm, at ease in yourself. Where you're not so caught up in all the pressure or the stress. You're lighter, more grounded, more present. Not so much in your head worrying about things. Does that make sense?"
        ]

        response = random.choice(vision_templates)

        return {
            "therapeutic_response": response,
            "technique_used": "vision_building",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Building future vision from stated goal (Dr. Q style)",
            "llm_confidence": 0.95,
            "llm_reasoning": "Rule-based vision building with varied phrasing and 'be' instead of 'feel'",
            "fallback_used": False
        }

    def _generate_llm_therapeutic_response(self, client_input: str, navigation_output: dict,
                                         rag_examples: list, session_state: TRTSessionState) -> dict:
        """Generate response using Ollama LLM with improved prompting"""

        prompt = self._construct_improved_dialogue_prompt(
            client_input, navigation_output, rag_examples, session_state
        )

        try:
            # Call Ollama
            llm_response = self._call_ollama(prompt)

            # Parse response
            parsed_response = self._parse_dialogue_response(llm_response)

            return parsed_response

        except Exception as e:
            self.logger.error(f"Ollama dialogue generation failed: {e}")
            # Fallback
            return self._fallback_response_generation(
                client_input, navigation_output, rag_examples, session_state
            )

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        try:
            detailed_logger.log_llm_call(
                prompt_type="Dialogue Generation",
                model=self.model,
                prompt_preview=prompt[:300]
            )

            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower for more consistent responses
                        "num_predict": 200   # Shorter responses like Dr. Q
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '')
                detailed_logger.log_llm_response(llm_response[:200])
                return llm_response
            else:
                raise Exception(f"Ollama returned status {response.status_code}: {response.text}")

        except Exception as e:
            self.logger.error(f"Ollama call failed: {e}")
            raise

    def _construct_improved_dialogue_prompt(self, client_input: str, navigation_output: dict,
                                 rag_examples: list, session_state: TRTSessionState) -> str:
        """Construct improved dialogue prompt following Dr. Q methodology"""

        decision = navigation_output["navigation_decision"]
        situation = navigation_output["situation_type"]
        substate = navigation_output["current_substate"]

        # CRITICAL: Detect what client JUST provided
        last_info_provided = session_state.last_client_provided_info
        body_location_provided = session_state.body_location_provided
        body_sensation_described = session_state.body_sensation_described

        # STATE-BASED PROMPTS: Use focused prompts for body exploration
        # These are laser-focused and prevent LLM from losing context

        # NEW: Get emotion tracking info
        emotion_identified = session_state.stage_1_completion.get("emotion_identified", False)
        emotion_provided = session_state.emotion_provided

        # BODY EXPLORATION STATE 0: Client mentioned problem BUT emotion NOT yet identified
        # This is the FIRST step - ask about emotion before asking about body
        if (substate == "1.2_problem_and_body" and
            decision in ["explore_problem", "body_symptoms_exploration"] and
            not emotion_identified and
            not emotion_provided):
            # Check if client just mentioned a problem/situation
            problem_indicators = ["school", "friends", "bully", "work", "stress", "pressure",
                                "deadline", "relationship", "family", "difficult", "hard",
                                "problem", "issue", "trouble", "worry", "concern"]
            client_mentioned_situation = any(word in client_input.lower() for word in problem_indicators)

            if client_mentioned_situation:
                return self._construct_emotion_inquiry_prompt(client_input, session_state, rag_examples)

        # BODY EXPLORATION STATE 1: Client provided emotion BUT body location NOT yet given
        # Ask where they feel that emotion in their body
        elif (substate == "1.2_problem_and_body" and
              last_info_provided == "emotion" and
              not body_location_provided):
            return self._construct_emotion_to_body_prompt(client_input, session_state, rag_examples)

        # BODY EXPLORATION STATE 2: Client just provided body location
        # Check if they mentioned sensation words - if so, we can explore quality
        elif last_info_provided == "body_location":
            # Check if client mentioned sensation words in their response (hurt, pain, ache, tight, etc.)
            sensation_indicators = ["hurt", "hurting", "pain", "painful", "ache", "aching",
                                   "tight", "tightness", "pressure", "heavy", "sharp", "dull"]
            client_mentioned_sensation = any(word in client_input.lower() for word in sensation_indicators)

            # If they mentioned sensation words AND we haven't explored quality yet, ask about type
            if (client_mentioned_sensation and
                not body_sensation_described and
                not session_state.anything_else_asked):
                # Ask about sensation quality ("what kind of hurt - achy, stabbing?")
                return self._construct_sensation_quality_prompt(client_input, session_state, rag_examples)
            # Otherwise, gracefully check if there's more (don't force details)
            elif not session_state.anything_else_asked:
                return self._construct_what_else_prompt(client_input, session_state, rag_examples)
            else:
                # Already asked "What else?" - move to present moment grounding
                return self._construct_present_moment_prompt(client_input, session_state, rag_examples)

        # BODY EXPLORATION STATE 3: Client provided more info after "What else?"
        elif last_info_provided == "sensation_quality" and session_state.anything_else_asked:
            # They described sensation after we asked "What else?" - move to present moment
            return self._construct_present_moment_prompt(client_input, session_state, rag_examples)

        # BODY EXPLORATION STATE 4: Asking initial body location (fallback if emotion already known)
        elif decision == "body_awareness_inquiry" and not body_location_provided:
            return self._construct_initial_body_location_prompt(client_input, session_state)

        # For all other cases, use general prompt
        else:
            return self._construct_general_dialogue_prompt(
                client_input, navigation_output, rag_examples, session_state
            )

    def _construct_emotion_inquiry_prompt(self, client_input: str, session_state: TRTSessionState, rag_examples: list) -> str:
        """Focused prompt when client mentioned a problem/situation but emotion not yet identified"""

        # Format RAG examples if available
        rag_examples_text = ""
        if rag_examples and len(rag_examples) > 0:
            rag_examples_text = "Dr. Q's examples:\n"
            for i, example in enumerate(rag_examples[:2], 1):
                doctor_response = example.get('doctor_example', '')
                if doctor_response:
                    rag_examples_text += f"{i}. \"{doctor_response}\"\n"

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'emotion_inquiry')
        return template.format(
            client_input=client_input,
            rag_examples=rag_examples_text
        )

    def _construct_emotion_to_body_prompt(self, client_input: str, session_state: TRTSessionState, rag_examples: list) -> str:
        """Focused prompt when client just provided emotion - now ask where in body"""

        # Extract the emotion/problem they mentioned - use the tracked one for accuracy
        emotion_content = session_state.most_recent_emotion_or_problem or session_state.stage_1_completion.get("emotion_content", "that")

        # Format RAG examples if available
        rag_examples_text = ""
        if rag_examples and len(rag_examples) > 0:
            rag_examples_text = "Dr. Q's examples:\n"
            for i, example in enumerate(rag_examples[:2], 1):
                doctor_response = example.get('doctor_example', '')
                if doctor_response:
                    rag_examples_text += f"{i}. \"{doctor_response}\"\n"

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'emotion_to_body')
        return template.format(
            emotion_content=emotion_content,
            client_input=client_input,
            rag_examples=rag_examples_text
        )

    def _construct_what_else_prompt(self, client_input: str, session_state: TRTSessionState, rag_examples: list) -> str:
        """Gracefully ask what else after body location - don't force details"""

        # Format RAG examples if available
        rag_examples_text = ""
        if rag_examples and len(rag_examples) > 0:
            rag_examples_text = "Dr. Q's examples:\n"
            for i, example in enumerate(rag_examples[:2], 1):
                doctor_response = example.get('doctor_example', '')
                if doctor_response:
                    rag_examples_text += f"{i}. \"{doctor_response}\"\n"

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'what_else_inquiry')
        return template.format(
            client_input=client_input,
            rag_examples=rag_examples_text
        )

    def _construct_sensation_quality_prompt(self, client_input: str, session_state: TRTSessionState, rag_examples: list) -> str:
        """Ask about sensation quality when client mentioned sensation words like hurt, pain, ache"""

        # Extract body part from client input for more specific questioning
        client_lower = client_input.lower()
        body_parts = ["chest", "head", "forehead", "shoulders", "shoulder", "neck", "stomach",
                     "leg", "arm", "back", "feet", "foot", "hands", "hand", "throat", "belly"]

        detected_body_part = "that area"  # Default
        for part in body_parts:
            if part in client_lower:
                detected_body_part = f"your {part}"
                break

        # Format RAG examples if available
        rag_examples_text = ""
        if rag_examples and len(rag_examples) > 0:
            rag_examples_text = "Dr. Q's examples:\n"
            for i, example in enumerate(rag_examples[:2], 1):
                doctor_response = example.get('doctor_example', '')
                if doctor_response:
                    rag_examples_text += f"{i}. \"{doctor_response}\"\n"

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'sensation_quality')
        return template.format(
            client_input=client_input,
            rag_examples=rag_examples_text,
            body_part=detected_body_part
        )

    def _construct_present_moment_prompt(self, client_input: str, session_state: TRTSessionState, rag_examples: list) -> str:
        """Simple present moment grounding after exploration"""

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'present_moment')
        return template.format(client_input=client_input)

    def _construct_body_location_followup_prompt(self, client_input: str, session_state: TRTSessionState, rag_examples: list) -> str:
        """Focused prompt when client just provided body location"""

        # Format RAG examples if available
        rag_examples_text = ""
        if rag_examples and len(rag_examples) > 0:
            rag_examples_text = "Dr. Q's examples:\n"
            for i, example in enumerate(rag_examples[:2], 1):
                doctor_response = example.get('doctor_example', '')
                if doctor_response:
                    rag_examples_text += f"{i}. \"{doctor_response}\"\n"

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'body_location_followup')
        return template.format(
            client_input=client_input,
            rag_examples=rag_examples_text
        )

    def _construct_sensation_followup_prompt(self, client_input: str, session_state: TRTSessionState, rag_examples: list) -> str:
        """Focused prompt when client just provided sensation"""

        # Check if we've already asked "What else?"
        anything_else_asked = session_state.anything_else_asked

        if not anything_else_asked:
            # First time after sensation - ask if there's more to share
            template = self.prompt_loader.get_prompt('dialogue_agent', 'sensation_followup')
            return template.format(client_input=client_input)
        else:
            # Already asked "What else?" - now move to present moment
            template = self.prompt_loader.get_prompt('dialogue_agent', 'sensation_to_present')
            return template.format(client_input=client_input)

    def _construct_problem_to_body_prompt(self, client_input: str, session_state: TRTSessionState) -> str:
        """Focused prompt when client mentioned a problem - shift to body IMMEDIATELY"""

        # Extract the problem/stress mentioned by client
        problem_words = ["stress", "anxiety", "worry", "fear", "overwhelmed", "frustrated",
                        "angry", "sad", "depressed", "problem", "issue", "difficulty"]

        detected_problem = "that"
        client_lower = client_input.lower()
        for word in problem_words:
            if word in client_lower:
                detected_problem = word
                break

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'problem_to_body')
        return template.format(
            client_input=client_input,
            detected_problem=detected_problem
        )

    def _construct_initial_body_location_prompt(self, client_input: str, session_state: TRTSessionState) -> str:
        """Focused prompt for initial body location question"""

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'initial_body_location')
        return template.format(client_input=client_input)

    def _construct_general_dialogue_prompt(self, client_input: str, navigation_output: dict,
                                 rag_examples: list, session_state: TRTSessionState) -> str:
        """General dialogue prompt for non-body-exploration scenarios"""

        decision = navigation_output["navigation_decision"]
        situation = navigation_output["situation_type"]
        substate = navigation_output["current_substate"]

        # Format RAG examples
        rag_examples_text = ""
        for i, example in enumerate(rag_examples, 1):
            rag_examples_text += f"Example {i}: Dr. Q: \"{example.get('doctor_example', 'N/A')}\"\n"

        # Get goal if stated
        goal = session_state.stage_1_completion.get("goal_content", "")

        # Check body question count
        body_q_count = session_state.body_questions_asked

        # Get current stage info
        current_substate = navigation_output.get("current_substate", "")
        goal_already_stated = session_state.stage_1_completion.get("goal_stated", False)

        # CRITICAL: Detect what client JUST provided
        last_info_provided = session_state.last_client_provided_info
        body_location_provided = session_state.body_location_provided
        body_sensation_described = session_state.body_sensation_described

        # Check if problem question was already asked
        # CRITICAL: Scan last 6+ turns to catch repetitions that are further apart
        problem_question_already_asked = False
        if len(session_state.conversation_history) > 0:
            # Check last 6 turns, or all history if less than 6 turns
            scan_range = min(6, len(session_state.conversation_history))
            for exchange in session_state.conversation_history[-scan_range:]:
                therapist_response = exchange.get('therapist_response', '').lower()
                if any(phrase in therapist_response for phrase in ["what's been making it hard", "what's been making it difficult", "what's been getting in the way"]):
                    problem_question_already_asked = True
                    break

        # Load template from config
        template = self.prompt_loader.get_prompt('dialogue_agent', 'general_therapeutic')
        return template.format(
            client_input=client_input,
            current_substate=current_substate,
            situation=situation,
            goal_already_stated=goal_already_stated,
            goal=goal if goal else "Not yet stated",
            problem_question_already_asked=problem_question_already_asked,
            last_info_provided=last_info_provided,
            body_location_provided=body_location_provided,
            body_sensation_described=body_sensation_described,
            rag_examples=rag_examples_text,
            body_q_count=body_q_count
        )

    def _parse_dialogue_response(self, llm_response: str) -> dict:
        """Parse Ollama response and remove LLM artifacts"""

        # Clean up response
        response = llm_response.strip()

        # Remove any JSON formatting if present
        if response.startswith('{'):
            try:
                parsed = json.loads(response)
                response = parsed.get('response', response)
            except:
                pass

        # Remove common prefixes
        prefixes_to_remove = ["THERAPIST:", "Dr. Q:", "Response:", "Generate response:", "Here is a short therapeutic response:"]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        # CRITICAL: Remove LLM reasoning artifacts (like "Since the client said..." or "Here's a short...")
        artifact_patterns = [
            "Here's a short therapeutic response:",
            "Here is a short therapeutic response:",
            "Here's a therapeutic response:",
            "Here is a therapeutic response:",
            "Here are some examples:",
            "Here's an example:",
            "Here is an example:",
            "Choose one that fits",
            "Generate a natural",
            "Generate response",
            "Since the client",
            "Since they",
            "Given that",
            "Because the",
            "I'll respond with:",
            "I will say:",
            "My response is:",
            "I'll ask:",
            "I'm going to",
            "I would say:",
            "I should respond:"
        ]

        for pattern in artifact_patterns:
            if pattern.lower() in response.lower():
                # Remove the artifact and everything before it
                idx = response.lower().find(pattern.lower())
                if idx != -1:
                    # Remove pattern and everything before it
                    response = response[idx + len(pattern):].strip()
                    # Clean up leading punctuation
                    response = response.lstrip(':"\'').strip()

                # Also try to extract quoted response if present
                if '"' in response:
                    # Extract text between quotes
                    parts = response.split('"')
                    if len(parts) >= 3:
                        # Get the first quoted response (ignore multiple examples)
                        response = parts[1]
                        break

        # ADDITIONAL CLEANING: If response contains bullet points or multiple examples, take only the first one
        if response.startswith('*') or '\n*' in response or '* "' in response:
            # Extract first bullet point
            lines = response.split('\n')
            for line in lines:
                clean_line = line.strip().lstrip('*').strip()
                if clean_line and len(clean_line) > 10:  # Ignore very short lines
                    # Extract quoted text if present
                    if '"' in clean_line:
                        parts = clean_line.split('"')
                        if len(parts) >= 3:
                            response = parts[1]
                            break
                    else:
                        response = clean_line
                        break

        # Remove extra quotes
        response = response.strip('"').strip("'").strip()

        # Remove line breaks and extra spaces
        response = ' '.join(response.split())

        return {
            "response": response,
            "reasoning": "Generated using improved Dr. Q methodology",
            "confidence": 0.8,
            "technique_focus": "dr_q_style",
            "fallback_used": False
        }

    def _fallback_response_generation(self, client_input: str, navigation_output: dict,
                                    rag_examples: list, session_state: TRTSessionState) -> dict:
        """Fallback rule-based responses following Dr. Q style"""

        decision = navigation_output["navigation_decision"]
        client_lower = client_input.lower()

        # Check what client just provided
        answer_type = session_state.last_client_provided_info

        # If they gave body info, affirm and ask next (Dr. Q style)
        if answer_type == "body_location":
            response = "Got it. What kind of sensation is it? Is it an ache? Tight? Sharp?"
        elif answer_type == "sensation_quality":
            response = "Yeah. You're feeling that right now, aren't you?"
        else:
            # Standard fallback by decision type (Dr. Q style)
            fallback_responses = {
                "clarify_goal": "So before we get started, what do you want our time to focus on today? What do we want to get better for you?",
                "build_vision": "Got it. So you want to feel peaceful. I'm seeing you who's calm, grounded, at ease. Does that make sense to you?",
                "explore_problem": "What's been making it hard for you?",
                "body_awareness_inquiry": "Where do you feel that in your body?",
                "body_symptoms_exploration": "What kind of sensation is it? Is it an ache? Tight? Heavy?",
                "pattern_inquiry": "How do you know when that feeling starts? What's happening in that moment?",
                "assess_readiness": "What haven't I understood? Is there more I should know?",
                "general_inquiry": "Tell me more about that."
            }

            response = fallback_responses.get(decision, "Tell me more about that.")

        return {
            "response": response,
            "reasoning": f"Fallback for {decision}",
            "confidence": 0.7,
            "technique_focus": decision,
            "fallback_used": True
        }

    def _handle_i_dont_know(self, i_dont_know_detection: dict, session_state: TRTSessionState) -> dict:
        """Handle 'I don't know' responses with vision language"""

        context = i_dont_know_detection.get('context', 'general')

        # Generate vision language response
        vision_response = self.vision_templates.get_vision_response(context)

        return {
            "therapeutic_response": vision_response['full_response'],
            "technique_used": "i_dont_know_vision_language",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": f"Client said 'I don't know' in {context} context - offered vision language",
            "llm_confidence": 0.9,
            "llm_reasoning": "Auto-offered universal positive outcomes",
            "fallback_used": False
        }

    def _generate_engagement_intervention(self, engagement_assessment: dict, session_state: TRTSessionState) -> dict:
        """Generate intervention response for engagement issues"""

        return {
            "therapeutic_response": engagement_assessment['intervention_message'],
            "technique_used": engagement_assessment['intervention_type'],
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": f"Engagement intervention: {engagement_assessment['engagement_type']}",
            "llm_confidence": 0.95,
            "llm_reasoning": "Engagement tracker triggered intervention",
            "fallback_used": False,
            "handoff_recommended": engagement_assessment.get('handoff_recommended', False)
        }

    def _generate_psycho_education_response(self, session_state: TRTSessionState) -> dict:
        """Generate psycho-education (zebra-lion) response"""

        # Provide concise version by default
        education = self.psycho_education.provide_education(version="concise", session_state=session_state)

        # Mark as provided
        self.psycho_education.mark_education_provided(session_state)
        session_state.stage_1_completion["psycho_education_provided"] = True

        return {
            "therapeutic_response": education['psycho_education'],
            "technique_used": "psycho_education_zebra_lion",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Providing brain mechanism explanation before problem inquiry",
            "llm_confidence": 0.95,
            "llm_reasoning": "Psycho-education: Zebra-lion brain explanation",
            "fallback_used": False
        }

    def _generate_session_conclusion_response(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Generate graceful session conclusion (Stage 1 complete)"""

        client_lower = client_input.lower()

        # Check if we've already given the session conclusion
        if session_state.session_conclusion_given:
            # Client is continuing to talk after session conclusion
            # Give a brief acknowledgment and gently end
            brief_acknowledgments = [
                "Thank you for sharing. We'll continue next time.",
                "I appreciate that. Let's pick this up in our next session.",
                "I hear you. We can explore that further next time.",
                "Thank you. Looking forward to our next session."
            ]

            import random
            response = random.choice(brief_acknowledgments)

            return {
                "therapeutic_response": response,
                "technique_used": "post_conclusion_acknowledgment",
                "examples_used": 0,
                "rag_similarity_scores": [],
                "navigation_reasoning": "Session already concluded - brief acknowledgment for continued conversation",
                "llm_confidence": 0.95,
                "llm_reasoning": "Gracefully acknowledging post-session conversation",
                "fallback_used": False,
                "session_complete": True
            }

        # First time giving conclusion - acknowledge what client said
        acknowledgments = {
            "peaceful": "I'm glad you're feeling peaceful.",
            "calm": "That's wonderful that you're feeling calm.",
            "better": "I'm glad you're feeling better.",
            "good": "I'm pleased to hear you're feeling good.",
            "relaxed": "That's great that you're feeling relaxed."
        }

        # Find acknowledgment
        acknowledgment = "I hear you."
        for feeling, ack in acknowledgments.items():
            if feeling in client_lower:
                acknowledgment = ack
                break

        # Graceful conclusion
        response = f"{acknowledgment} That was a great session. I'll be looking forward to our next session."

        # Mark conclusion as given
        session_state.session_conclusion_given = True

        return {
            "therapeutic_response": response,
            "technique_used": "session_conclusion",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Stage 1 complete - concluding session gracefully",
            "llm_confidence": 0.95,
            "llm_reasoning": "Session concluded with acknowledgment and future-oriented close",
            "fallback_used": False,
            "session_complete": True
        }

    def _handle_alpha_sequence_checkpoint(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Handle alpha sequence checkpoint response"""

        # Process checkpoint
        result = self.alpha_sequence.process_checkpoint_response(client_input)

        # Build response text
        therapist_response = result.get('response', '')

        # Add checkpoint question if provided
        if result.get('checkpoint_question'):
            therapist_response += f" {result.get('checkpoint_question')}"

        # Check if sequence is complete
        if result.get('action') == 'sequence_complete':
            # Mark alpha as complete in session state
            session_state.alpha_complete = True
            session_state.current_substate = "stage_1_complete"
            self.alpha_sequence.sequence_active = False
            self.logger.info("✅ Alpha sequence completed - Stage 1 complete!")

        return {
            "therapeutic_response": therapist_response,
            "technique_used": "alpha_sequence_checkpoint",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": f"Alpha sequence: {result.get('action', 'processing')}",
            "llm_confidence": 0.95,
            "llm_reasoning": f"Alpha sequence step {self.alpha_sequence.current_step.name}",
            "fallback_used": False,
            "alpha_complete": result.get('action') == 'sequence_complete'
        }

    def get_system_status(self) -> dict:
        """System status"""
        return {
            "ollama_url": self.ollama_url,
            "model": self.model,
            "mode": "improved_ollama",
            "enhancements": {
                "language_techniques": True,
                "engagement_tracking": True,
                "vision_templates": True,
                "psycho_education": True,
                "alpha_sequence": True
            },
            "engagement_summary": self.engagement_tracker.get_engagement_summary(),
            "alpha_sequence_status": self.alpha_sequence.get_sequence_summary() if self.alpha_sequence.sequence_active else None
        }
