"""
Therapy System Wrapper for FastAPI
Handles proper imports and initialization for Docker environment
"""

import sys
import os

# Add project paths to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'src/core'))
sys.path.insert(0, os.path.join(project_root, 'src/agents'))
sys.path.insert(0, os.path.join(project_root, 'src/utils'))

# Now import the therapy system components
from src.core.session_state_manager import TRTSessionState
from src.utils.embedding_and_retrieval_setup import TRTRAGSystem
from src.utils.input_preprocessing import InputPreprocessor
from src.agents.ollama_llm_master_planning_agent import OllamaLLMMasterPlanningAgent
from src.agents.improved_ollama_dialogue_agent import ImprovedOllamaDialogueAgent
from src.utils.detailed_logger import get_detailed_logger

import time
from datetime import datetime

# Initialize detailed logger
logger = get_detailed_logger("TherapySystem")


class ImprovedOllamaTherapySystem:
    """
    Wrapper for the Improved Ollama TRT System
    Compatible with FastAPI and Docker environments
    """

    def __init__(self, ollama_url=None, model="llama3.1"):
        """Initialize the therapy system"""

        # Use environment variable or default
        if ollama_url is None:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        print(f"🚀 Initializing TRT System...")
        print(f"📡 Ollama URL: {ollama_url}")
        print(f"🤖 Model: {model}")

        # Initialize RAG system
        print("📚 Loading RAG system...")
        self.rag_system = TRTRAGSystem()

        # Get paths relative to project root
        faiss_path = os.path.join(project_root, "data/embeddings/trt_rag_index.faiss")
        metadata_path = os.path.join(project_root, "data/embeddings/trt_rag_metadata.json")

        try:
            self.rag_system.load_index(faiss_path, metadata_path)
            print("✅ RAG system loaded")
        except Exception as e:
            print(f"⚠️ RAG system not available: {e}")

        # Initialize agents
        print("🧠 Initializing Master Planning Agent...")
        self.master_agent = OllamaLLMMasterPlanningAgent(ollama_url=ollama_url, model=model)

        print("💬 Initializing Dialogue Agent...")
        self.dialogue_agent = ImprovedOllamaDialogueAgent(self.rag_system, ollama_url=ollama_url, model=model)

        # Initialize preprocessor
        self.preprocessor = InputPreprocessor()

        print("✅ TRT System Ready!")

    def create_session(self, session_id):
        """Create a new session state"""
        return TRTSessionState(session_id)

    def process_client_input(self, client_input: str, session_state: TRTSessionState = None) -> dict:
        """
        Process client input through the therapy system

        If session_state is None, creates a temporary one (for testing)
        """

        if session_state is None:
            session_state = TRTSessionState("temp_session")

        start_time = time.time()

        # Step 1: Preprocessing
        logger.log_preprocessing_start(client_input)
        preprocessing_result = self.preprocessor.preprocess_input(client_input)
        logger.log_preprocessing_result(preprocessing_result)

        # Step 2: Master Planning
        logger.log_navigation_start(session_state)
        navigation_output = self.master_agent.make_navigation_decision(client_input, session_state)
        logger.log_navigation_decision(navigation_output)

        # Track body questions
        body_question_decisions = [
            "body_awareness_inquiry",
            "guide_to_body",
            "body_location",
            "body_sensation"
        ]

        body_question_substates = [
            "2.1_seek",
            "1.2_problem_and_body"
        ]

        current_state = navigation_output.get("current_substate", "")
        if current_state not in ["3.1_assess_readiness", "3.2_alpha_sequence", "stage_1_complete"]:
            if (navigation_output.get("navigation_decision") in body_question_decisions or
                (navigation_output.get("current_substate") in body_question_substates and
                 "body" in navigation_output.get("navigation_decision", "").lower())):
                if session_state.last_client_provided_info not in ["body_location", "sensation_quality"]:
                    session_state.body_questions_asked += 1

        # Check MAX body question limit
        if session_state.body_questions_asked >= 3:
            current_sub = navigation_output.get("current_substate")
            if current_sub in ["2.1_seek", "1.2_problem_and_body", "2.2_location", "2.3_sensation"]:
                logger.log_state_transition(
                    from_state=current_sub,
                    to_state="3.1_assess_readiness",
                    trigger=f"Body question limit reached ({session_state.body_questions_asked}/3)"
                )
                session_state.current_substate = "3.1_assess_readiness"

                # Mark cycle 1 as complete when transitioning to readiness
                if session_state.body_enquiry_cycles == 0:
                    session_state.body_enquiry_cycles = 1
                    logger.info(f"✓ Body enquiry cycle 1 complete, entering readiness assessment")

                navigation_output["navigation_decision"] = "assess_readiness"
                navigation_output["current_substate"] = "3.1_assess_readiness"
                navigation_output["situation_type"] = "readiness_for_alpha"
                navigation_output["rag_query"] = "dr_q_ready"
                navigation_output["ready_for_next"] = True

        # Step 3: Dialogue Generation
        logger.log_dialogue_start(
            navigation_decision=navigation_output.get("navigation_decision", "unknown"),
            rag_examples_count=0  # Will be updated by dialogue agent
        )
        dialogue_output = self.dialogue_agent.generate_response(client_input, navigation_output, session_state)
        logger.log_dialogue_output(
            response=dialogue_output["therapeutic_response"],
            metadata={
                "technique_used": dialogue_output.get("technique_used"),
                "llm_confidence": dialogue_output.get("llm_confidence"),
                "fallback_used": dialogue_output.get("fallback_used")
            }
        )

        # Step 4: Update session
        session_state.add_exchange(
            client_input=client_input,
            therapist_response=dialogue_output["therapeutic_response"],
            navigation_output=navigation_output
        )
        logger.log_session_update(session_state)

        processing_time = time.time() - start_time
        logger.log_processing_summary(processing_time, session_state.session_id)

        # Return comprehensive result
        return {
            "therapist_response": dialogue_output["therapeutic_response"],
            "preprocessing": preprocessing_result,
            "navigation": navigation_output,
            "session_state": {
                "current_substate": session_state.current_substate,
                "body_question_count": session_state.body_questions_asked,
                "stage_1_completion": session_state.stage_1_completion
            },
            "processing_time": processing_time
        }
