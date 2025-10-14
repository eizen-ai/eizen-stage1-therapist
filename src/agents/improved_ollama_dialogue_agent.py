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
from embedding_and_retrieval_setup import TRTRAGSystem
from session_state_manager import TRTSessionState
from no_harm_framework import NoHarmFramework
from language_techniques import LanguageTechniques
from engagement_tracker import EngagementTracker
from vision_language_templates import VisionLanguageTemplates
from psycho_education import PsychoEducation
from alpha_sequence import AlphaSequence
import logging

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

                return {
                    "therapeutic_response": "Okay. I'm going to guide you through a brief process. Are you ready?",
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

                # Update session state to 3.2
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
                return {
                    "therapeutic_response": "It's very simple, just a few minutes. I'll guide you through it. Ready to try?",
                    "technique_used": "alpha_permission_reassurance",
                    "examples_used": 0,
                    "rag_similarity_scores": [],
                    "navigation_reasoning": "Client hesitant - reassuring and re-asking permission",
                    "llm_confidence": 0.9,
                    "llm_reasoning": "Reassuring hesitant client about alpha process",
                    "fallback_used": False
                }

        # PRIORITY 8: Check for active alpha sequence checkpoints
        if self.alpha_sequence.sequence_active:
            return self._handle_alpha_sequence_checkpoint(client_input, session_state)

        # PRIORITY 9: Check for goal clarification (use rule-based for consistency)
        if navigation_output.get('navigation_decision') == 'clarify_goal':
            return self._generate_goal_clarification_response(client_input)

        # PRIORITY 9: Check for vision building (use rule-based for consistency)
        if navigation_output.get('navigation_decision') == 'build_vision':
            return self._generate_vision_building_response(session_state)

        # Get RAG examples
        rag_examples = self.rag_system.get_few_shot_examples(
            navigation_output,
            client_input,
            max_examples=3
        )

        # Check if we should affirm and move forward
        if self._should_affirm_and_proceed(client_input, session_state, navigation_output):
            return self._generate_affirmation_response(client_input, session_state, navigation_output)

        # Check if client is confused - clarify
        if session_state.last_client_provided_info == "confusion":
            return self._generate_clarification_response(client_input, navigation_output, session_state)

        # Generate main therapeutic response
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

    def _generate_affirmation_response(self, client_input: str, session_state: TRTSessionState, navigation_output: dict) -> dict:
        """Generate affirmation + next logical question (like Dr. Q)"""

        client_lower = client_input.lower()

        # FIRST: Check for emotion and acknowledge it (Dr. Q method)
        emotion_acknowledgment = self._detect_and_acknowledge_emotion(client_input)

        # Use Dr. Q's natural affirmations - vary them
        affirmations = ["That's right.", "Yeah.", "Got it.", "Okay."]
        import random
        affirmation = random.choice(affirmations)

        # Determine next question based on what was just provided
        if session_state.last_client_provided_info == "body_location":
            # They gave location, now ask about sensation quality (only if not already asked)
            # ACCEPT ANY LOCATION - even vague
            candidate_q = "What kind of sensation is it? Is it an ache? Tight? Sharp? Heavy?"
            if not session_state.body_sensation_described and not session_state.was_question_asked_recently(candidate_q):
                next_question = candidate_q
            else:
                # Body location already provided, move forward
                next_question = "How are you feeling NOW?"

        elif session_state.last_client_provided_info == "sensation_quality":
            # They described sensation, now ask about present moment (Dr. Q style) - BUT ONLY ONCE!
            # Simple and direct: "How are you feeling NOW?" (not "that NOW")
            candidate_q = "How are you feeling NOW?"
            # Check if we've EVER asked about present moment (not just recently)
            if not session_state.stage_1_completion.get("present_moment_focus", False) and "feeling now" not in str(session_state.questions_asked_set).lower():
                next_question = candidate_q
            else:
                # Already asked about present moment OR already established, move to problem exploration
                if not session_state.stage_1_completion.get("problem_identified"):
                    next_question = "What's been making it hard?"
                else:
                    next_question = "Tell me more about that."

        elif session_state.last_client_provided_info == "affirmation":
            # They affirmed, move to next stage topic based on completion status
            completion = session_state.stage_1_completion

            # CRITICAL: Check if they just affirmed "You're feeling that right now" or "How are you feeling that NOW"
            if session_state.last_question_asked and ("feeling that right now" in session_state.last_question_asked or
                                                       "feeling that now" in session_state.last_question_asked.lower()):
                # They confirmed present moment, mark it complete
                session_state.stage_1_completion["present_moment_focus"] = True
                completion = session_state.stage_1_completion  # Update reference

            # Priority order for what to ask next (Dr. Q's actual flow)
            if not completion["goal_stated"]:
                next_question = "What do you want our time to focus on today?"
            elif not completion["vision_accepted"]:
                # Vision should be built by rule, but if we're here, ask confirming question
                next_question = "Does that make sense to you?"
            elif not completion.get("psycho_education_provided", False):
                # After vision accepted, move toward psycho-education (handled by priority system)
                next_question = "Tell me more about that."
            elif not completion["body_awareness_present"]:
                # After psycho-education, ask about problem
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
                        next_question = "Tell me more about that."
            else:
                # All criteria met - move toward readiness
                next_question = "What haven't I understood? Is there more I should know?"
        else:
            next_question = "Tell me more about that."

        # Build response: emotion acknowledgment (if any) + affirmation + next question
        if emotion_acknowledgment:
            # Emotion detected: use emotion acknowledgment instead of generic affirmation
            response = f"{emotion_acknowledgment}{next_question}"
        else:
            # No emotion: use standard affirmation
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

        # Dr. Q is gentle but direct when redirecting from thinking to feeling
        response = "Yeah, I hear you thinking about it. Rather than thinking, what are you FEELING right now? Where do you feel that?"

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

        # Dr. Q acknowledges the past but brings to present
        response = "Got it. That was then. Right now, in this moment, what are you FEELING? What's happening in your body?"

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

            # Extract emotion/problem if mentioned
            emotions = {
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
                "gloomy": "gloomy",
                "down": "down",
                "lonely": "lonely",
                "hopeless": "hopeless",
                "miserable": "miserable",
                "unhappy": "unhappy"
            }

            mentioned_emotion = None
            for emotion_word, emotion_label in emotions.items():
                if emotion_word in client_lower:
                    mentioned_emotion = emotion_label
                    self.logger.info(f"[GOAL_CLARIFICATION] ✅ Detected emotion: '{emotion_word}' → '{emotion_label}'")
                    break

            if mentioned_emotion:
                # Check if emotion is positive or negative
                positive_emotions = ["good", "great", "better", "okay", "fine", "calm", "peaceful", "happy"]
                is_positive = any(pos in client_lower for pos in positive_emotions)

                if is_positive:
                    # Positive emotion: acknowledge in present, add enthusiasm
                    response = f"You're feeling {mentioned_emotion}, that's great! What do we want our time to focus on today?"
                else:
                    # Negative emotion: acknowledge in PAST TENSE (Dr. Q: put stress/problems in past)
                    response = f"So you've been feeling {mentioned_emotion}. What would we like to get out of our session today?"

                self.logger.info(f"[GOAL_CLARIFICATION] 💬 Generated with emotion acknowledgment ({'positive' if is_positive else 'negative'}): '{response}'")
            else:
                # No emotion detected, use standard opening - SIMPLE like Dr. Q
                response = "What do we want our time to focus on today?"
                self.logger.info(f"[GOAL_CLARIFICATION] 💬 No emotion detected, standard response: '{response}'")
        else:
            # No client input provided (shouldn't happen, but fallback)
            response = "So what do you want our time to focus on today? What do we want to get better for you?"

        return {
            "therapeutic_response": response,
            "technique_used": "goal_clarification",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Clarifying therapeutic goal (Dr. Q style with acknowledgment)",
            "llm_confidence": 0.95,
            "llm_reasoning": "Rule-based goal clarification with natural conversation and emotion acknowledgment",
            "fallback_used": False
        }

    def _generate_vision_building_response(self, session_state: TRTSessionState) -> dict:
        """Generate vision building response (rule-based for consistency)"""

        # Extract goal from session state - handle both dict and direct access
        try:
            if isinstance(session_state.stage_1_completion, dict):
                goal_content = session_state.stage_1_completion.get("goal_content", "")
            else:
                goal_content = getattr(session_state.stage_1_completion, "goal_content", "")
        except:
            goal_content = ""

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

        # Find what they want
        desired_state = "calm"  # Default
        for key, value in goal_mappings.items():
            if key in goal_lower:
                desired_state = value
                break

        # Build vision response like Dr. Q - more natural, conversational
        response = f"Got it. So you want to feel {desired_state}. I'm seeing you who's {desired_state}, at ease, lighter. Does that make sense to you?"

        return {
            "therapeutic_response": response,
            "technique_used": "vision_building",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": "Building future vision from stated goal (Dr. Q style)",
            "llm_confidence": 0.95,
            "llm_reasoning": "Rule-based vision building with natural conversation",
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
                return result.get('response', '')
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

        prompt = f"""You are Dr. Q, a master TRT therapist. Generate ONE short therapeutic response (1-2 sentences max).

CLIENT JUST SAID: "{client_input}"

CURRENT STAGE: {current_substate}
CURRENT SITUATION: {situation}
GOAL ALREADY STATED: {goal_already_stated}
GOAL CONTENT: {goal if goal else "Not yet stated"}

DR. Q EXAMPLES - STUDY THESE CAREFULLY AND MATCH HIS EXACT STYLE:
{rag_examples_text}

CRITICAL INSTRUCTION:
The examples above show Dr. Q's ACTUAL responses from real sessions.
ADAPT his exact phrasing, warmth, and simplicity.
Use similar sentence structures and word choices.
Match his natural, conversational tone.
DO NOT add clinical language or formal phrasing.

DR. Q'S NATURAL STYLE - BE CONVERSATIONAL:
- Use warm acknowledgments: "Yeah", "Got it", "That's right", "Okay"
- Sound natural, not clinical: "So before we get started..." not "State your goal"
- Ask multiple variations when exploring: "What do you want our time to focus on? What do we want to get better for you? How do you want to be when we're done?"
- Use "you know", "right" for rapport (but don't overdo it)

DR. Q'S RULES (CRITICAL - FOLLOW EXACTLY):

1. NEVER ASK SAME QUESTION TWICE
   - If client gave body location → ask about sensation type
   - If client described sensation → ask if feeling it now
   - Move forward, don't repeat

2. BODY AWARENESS SEQUENCE (Dr. Q's approach):
   - First ask: "Where do you feel that in your body?"
   - Then ask: "What kind of sensation? Ache? Tight? Heavy?"
   - ACCEPT VAGUE ANSWERS: "smooth", "nice", "pressure" are all GOOD
   - Goal is ENGAGEMENT in sensing, NOT precision
   - After they answer, say "That's right" and ask "How are you feeling NOW?"
   - DON'T repeat sensation questions - move forward!

3. ACCEPT ANSWERS WARMLY
   - If client answered, say "That's right" or "Yeah" or "Got it"
   - Then ask NEXT question, not same question

4. CRITICAL: NEVER ASK ABOUT GOAL WHEN ALREADY STATED
   - If GOAL ALREADY STATED = True, NEVER EVER ask "what do you want our time to focus on"
   - FORBIDDEN PHRASES when goal already stated:
     * "what do you want our time to focus on"
     * "what do we want to get better"
     * "So before we get started"
   - If in Stage 1.2, you're doing problem/body exploration - stay there!

5. BUILD VISION CONVERSATIONALLY (STAGE 1.1 ONLY)
   - Acknowledge: "Got it."
   - Summarize: "So you want to feel [their goal]."
   - Paint picture: "I'm seeing you who's peaceful, calm, grounded."
   - Check: "Does that make sense to you?"

6. BODY QUESTIONS LIMIT: {body_q_count}/3
   - If body_q_count >= 3: DON'T ask more body questions
   - Accept what they said and move on

7. CRITICAL: IF IN STATE 3.1 (ALPHA READINESS) - NO MORE BODY QUESTIONS!
   - State 3.1 means body exploration is DONE
   - Ask ONLY: "What haven't I understood? Is there more I should know?"
   - DO NOT ask about body location, sensation, or present moment
   - If client ready for alpha ("yes", "ready"), proceed to alpha sequence

8. BE CONCISE AND NATURAL
   - 1-2 sentences max (like Dr. Q)
   - Sound like a real conversation, not a script
   - Warm, present, attentive

RESPONSE GUIDELINES BY DECISION:

clarify_goal (STAGE 1.1 ONLY):
→ "What do we want our time to focus on today?"

build_vision (STAGE 1.1 ONLY):
→ "Got it. So you want to feel [goal]. I'm seeing you who's [desired state], at ease, lighter. Does that make sense to you?"

body_awareness_inquiry (STAGE 1.2):
→ Step 1: "Where do you feel that in your body?"
→ Step 2 (after location): "What kind of sensation? Ache? Tight? Heavy?"
→ Step 3 (after sensation - ACCEPT vague!): "That's right. How are you feeling NOW?"

explore_problem (STAGE 1.2):
→ "So what's been making it hard for you?"
→ After they mention problem: "Where do you feel that in your body?"

present_moment_focus:
→ "How are you feeling NOW?"

STAGE 1.2 FLOW (when goal already stated):
→ Client mentions problem → Ask: "Where do you feel that in your body?"
→ Client gives location → Ask: "What kind of sensation? Ache? Tight?"
→ Client describes sensation (ACCEPT vague!) → Ask: "How are you feeling NOW?"
→ NEVER ask about goal again!

Generate response (1-2 sentences, conversational Dr. Q style):"""

        return prompt

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
                        # Get the quoted response
                        response = parts[1]
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

    def _handle_alpha_sequence_checkpoint(self, client_input: str, session_state: TRTSessionState) -> dict:
        """Handle alpha sequence checkpoint response"""

        # Process checkpoint
        result = self.alpha_sequence.process_checkpoint_response(client_input)

        return {
            "therapeutic_response": result.get('response', ''),
            "technique_used": "alpha_sequence_checkpoint",
            "examples_used": 0,
            "rag_similarity_scores": [],
            "navigation_reasoning": f"Alpha sequence: {result.get('action', 'processing')}",
            "llm_confidence": 0.95,
            "llm_reasoning": f"Alpha sequence step {self.alpha_sequence.current_step.name}",
            "fallback_used": False,
            "checkpoint_question": result.get('checkpoint_question', '')
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
