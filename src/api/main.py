"""
FastAPI Application for TRT AI Therapist
Provides REST API endpoints for agentic workflow integration
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os
import uuid
from typing import Dict

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.api.models import (
    SessionCreateRequest, SessionCreateResponse,
    ClientInputRequest, TherapistResponse,
    SessionStatusResponse, HealthCheckResponse, ErrorResponse,
    PreprocessingResult, NavigationDecision, SessionProgress,
    EmotionalState, SafetyChecks
)
from src.api.therapy_system_wrapper import ImprovedOllamaTherapySystem
from src.utils.redis_session_manager import RedisSessionManager

# ============================================================
# FASTAPI APP INITIALIZATION
# ============================================================

app = FastAPI(
    title="TRT AI Therapist API",
    description="Trauma Resiliency Training (TRT) Stage 1 System - Dr. Q's Methodology",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REDIS SESSION STORAGE
# ============================================================

# Initialize Redis Session Manager
try:
    redis_manager = RedisSessionManager()
    print("✅ Redis session manager initialized")
except Exception as e:
    print(f"⚠️ Redis connection failed, using in-memory fallback: {e}")
    redis_manager = None

# In-memory fallback (only used if Redis fails)
active_sessions: Dict[str, Dict] = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_session(session_id: str):
    """Retrieve session or raise 404"""
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    return active_sessions[session_id]


def create_session_id() -> str:
    """Generate unique session ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"session_{timestamp}_{unique_id}"


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Verifies that all system components are operational
    """
    try:
        # Check Ollama connection
        import requests
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        ollama_status = "connected" if ollama_response.status_code == 200 else "disconnected"
    except Exception:
        ollama_status = "disconnected"

    # Check if RAG embeddings exist
    embeddings_path = "/app/data/embeddings/trt_rag_index.faiss"
    rag_status = "ready" if os.path.exists(embeddings_path) else "not_found"

    # Check if CSV state machine exists
    csv_path = "/app/config/STAGE1_COMPLETE.csv"
    state_machine_status = "loaded" if os.path.exists(csv_path) else "not_found"

    # Check Redis connection
    if redis_manager:
        redis_health = redis_manager.health_check()
        redis_status = redis_health.get("status", "unhealthy")
    else:
        redis_status = "not_configured"

    overall_status = "healthy" if all([
        ollama_status == "connected",
        rag_status == "ready",
        state_machine_status == "loaded",
        redis_status == "healthy"
    ]) else "unhealthy"

    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(),
        services={
            "ollama": ollama_status,
            "rag": rag_status,
            "state_machine": state_machine_status,
            "redis": redis_status
        }
    )


@app.post("/api/v1/session/create", response_model=SessionCreateResponse, tags=["Session"])
async def create_session(request: SessionCreateRequest):
    """
    Create a new therapy session

    You can either:
    - Provide a custom session_id in the request (for integration with external systems)
    - Leave it blank to auto-generate a unique session ID

    Returns:
        SessionCreateResponse: Session ID and initialization info
    """
    try:
        # Use provided session_id or generate a new one
        if request.session_id:
            session_id = request.session_id

            # Check if session ID already exists
            if session_id in active_sessions:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Session ID '{session_id}' already exists. Please use a different ID or omit it for auto-generation."
                )
        else:
            # Auto-generate session ID
            session_id = create_session_id()

        # Initialize therapy system for this session
        therapy_system = ImprovedOllamaTherapySystem()
        session_state = therapy_system.create_session(session_id)

        # Store session data
        active_sessions[session_id] = {
            "session_id": session_id,
            "client_id": request.client_id,
            "metadata": request.metadata,
            "therapy_system": therapy_system,
            "session_state": session_state,
            "created_at": datetime.now(),
            "last_interaction": datetime.now(),
            "turn_count": 0,
            "status": "active"
        }

        return SessionCreateResponse(
            session_id=session_id,
            created_at=datetime.now(),
            status="active",
            message="Session created successfully. Ready to begin therapy."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@app.post("/api/v1/input", response_model=TherapistResponse, tags=["Session"])
async def process_input_with_session(request: ClientInputRequest):
    """
    Process client input and generate therapist response

    **Session ID in request body** - First call creates session + processes input, subsequent calls use existing session

    Args:
        request: Client input request containing session_id and user_input

    Returns:
        TherapistResponse: Complete response with preprocessing, navigation, and progress
    """
    try:
        session_id = request.session_id

        # Check if session exists (Redis or fallback)
        session_exists = False
        if redis_manager:
            session_exists = redis_manager.session_exists(session_id)
        else:
            session_exists = session_id in active_sessions

        # Create session if it doesn't exist (first call)
        if not session_exists:
            # Initialize therapy system for this new session
            therapy_system = ImprovedOllamaTherapySystem()
            session_state = therapy_system.create_session(session_id)

            # Save to Redis or fallback to memory
            if redis_manager:
                redis_manager.save_session_state(session_id, session_state)
                redis_manager.save_session_metadata(session_id, {"created_via": "input_endpoint"})
            else:
                active_sessions[session_id] = {
                    "session_id": session_id,
                    "client_id": None,
                    "metadata": {"created_via": "input_endpoint"},
                    "therapy_system": therapy_system,
                    "session_state": session_state,
                    "created_at": datetime.now(),
                    "last_interaction": datetime.now(),
                    "turn_count": 0,
                    "status": "active"
                }
        else:
            # Load existing session
            if redis_manager:
                session_data = redis_manager.load_session_state(session_id)
                therapy_system = ImprovedOllamaTherapySystem()
                session_state = therapy_system.create_session(session_id)
                # Restore state
                session_state.current_stage = session_data["current_stage"]
                session_state.current_substate = session_data["current_substate"]
                session_state.body_questions_asked = session_data["body_questions_asked"]
                session_state.stage_1_completion = session_data["stage_1_completion"]
            else:
                session = active_sessions[session_id]
                therapy_system = session["therapy_system"]
                session_state = session["session_state"]

        # Process client input through therapy system
        result = therapy_system.process_client_input(request.user_input, session_state)

        # Save updated state
        if redis_manager:
            redis_manager.save_session_state(session_id, session_state)
            redis_manager.add_conversation_exchange(session_id, {
                "client_input": request.user_input,
                "therapist_response": result["therapist_response"],
                "navigation_decision": result["navigation"].get("navigation_decision"),
                "current_substate": session_state.current_substate
            })
        else:
            # Update in-memory session
            session = active_sessions[session_id]
            session["last_interaction"] = datetime.now()
            session["turn_count"] += 1

        # Convert result to response model
        response = TherapistResponse(
            therapist_response=result["therapist_response"],
            preprocessing=PreprocessingResult(
                original_input=result["preprocessing"]["original_input"],
                cleaned_input=result["preprocessing"]["cleaned_input"],
                corrected_input=result["preprocessing"]["corrected_input"],
                emotional_state=EmotionalState(**result["preprocessing"]["emotional_state"]),
                input_category=result["preprocessing"]["input_category"],
                spelling_corrections=result["preprocessing"]["spelling_corrections"],
                safety_checks=SafetyChecks(
                    self_harm_detected=result["preprocessing"]["self_harm_detected"],
                    thinking_mode_detected=result["preprocessing"]["thinking_mode_detected"],
                    past_tense_detected=result["preprocessing"]["past_tense_detected"],
                    i_dont_know_detected=result["preprocessing"]["i_dont_know_detected"]
                )
            ),
            navigation=NavigationDecision(
                decision=result["navigation"].get("navigation_decision", "unknown"),
                next_state=result["navigation"].get("current_substate"),
                rag_query=result["navigation"].get("rag_query"),
                reasoning=result["navigation"].get("reasoning")
            ),
            session_progress=SessionProgress(
                current_substate=result["session_state"]["current_substate"],
                body_question_count=result["session_state"]["body_question_count"],
                completion_criteria={
                    k: v for k, v in result["session_state"]["stage_1_completion"].items()
                    if isinstance(v, bool)
                }
            ),
            timestamp=datetime.now()
        )

        # Check if session is complete
        if result["session_state"]["stage_1_completion"].get("ready_for_stage_2", False):
            session["status"] = "completed"

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process input: {str(e)}"
        )


@app.post("/api/v1/session/{session_id}/input", response_model=TherapistResponse, tags=["Session"])
async def process_input_path_based(session_id: str, request: ClientInputRequest):
    """
    Process client input and generate therapist response

    **Auto-creates session if it doesn't exist** - Just provide your session_id and start talking!

    Args:
        session_id: Unique session identifier (will be created if doesn't exist)
        request: Client input request

    Returns:
        TherapistResponse: Complete response with preprocessing, navigation, and progress
    """
    try:
        # Auto-create session if it doesn't exist
        if session_id not in active_sessions:
            # Initialize therapy system for this new session
            therapy_system = ImprovedOllamaTherapySystem()
            session_state = therapy_system.create_session(session_id)

            # Store session data
            active_sessions[session_id] = {
                "session_id": session_id,
                "client_id": None,  # Not needed in simplified flow
                "metadata": {"auto_created": True},
                "therapy_system": therapy_system,
                "session_state": session_state,
                "created_at": datetime.now(),
                "last_interaction": datetime.now(),
                "turn_count": 0,
                "status": "active"
            }

        # Retrieve session
        session = active_sessions[session_id]
        therapy_system = session["therapy_system"]
        session_state = session["session_state"]

        # Process client input through therapy system
        result = therapy_system.process_client_input(request.user_input, session_state)

        # Update session metadata
        session["last_interaction"] = datetime.now()
        session["turn_count"] += 1

        # Convert result to response model
        response = TherapistResponse(
            therapist_response=result["therapist_response"],
            preprocessing=PreprocessingResult(
                original_input=result["preprocessing"]["original_input"],
                cleaned_input=result["preprocessing"]["cleaned_input"],
                corrected_input=result["preprocessing"]["corrected_input"],
                emotional_state=EmotionalState(**result["preprocessing"]["emotional_state"]),
                input_category=result["preprocessing"]["input_category"],
                spelling_corrections=result["preprocessing"]["spelling_corrections"],
                safety_checks=SafetyChecks(
                    self_harm_detected=result["preprocessing"]["self_harm_detected"],
                    thinking_mode_detected=result["preprocessing"]["thinking_mode_detected"],
                    past_tense_detected=result["preprocessing"]["past_tense_detected"],
                    i_dont_know_detected=result["preprocessing"]["i_dont_know_detected"]
                )
            ),
            navigation=NavigationDecision(
                decision=result["navigation"].get("navigation_decision", "unknown"),
                next_state=result["navigation"].get("current_substate"),
                rag_query=result["navigation"].get("rag_query"),
                reasoning=result["navigation"].get("reasoning")
            ),
            session_progress=SessionProgress(
                current_substate=result["session_state"]["current_substate"],
                body_question_count=result["session_state"]["body_question_count"],
                completion_criteria={
                    k: v for k, v in result["session_state"]["stage_1_completion"].items()
                    if isinstance(v, bool)
                }
            ),
            timestamp=datetime.now()
        )

        # Check if session is complete
        if result["session_state"]["stage_1_completion"].get("ready_for_stage_2", False):
            session["status"] = "completed"

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process input: {str(e)}"
        )


@app.get("/api/v1/session/{session_id}/status", response_model=SessionStatusResponse, tags=["Session"])
async def get_session_status(session_id: str):
    """
    Get current session status and progress

    Args:
        session_id: Unique session identifier

    Returns:
        SessionStatusResponse: Session status and completion criteria
    """
    try:
        # Retrieve session
        session = get_session(session_id)
        session_state = session["session_state"]

        return SessionStatusResponse(
            session_id=session_id,
            status=session["status"],
            current_substate=session_state.current_substate,
            body_question_count=session_state.body_questions_asked,
            completion_criteria={
                k: v for k, v in session_state.stage_1_completion.items()
                if isinstance(v, bool)
            },
            turn_count=session["turn_count"],
            created_at=session["created_at"],
            last_interaction=session["last_interaction"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}"
        )


@app.delete("/api/v1/session/{session_id}", tags=["Session"])
async def delete_session(session_id: str):
    """
    Delete a session and free resources

    Args:
        session_id: Unique session identifier

    Returns:
        Success message
    """
    try:
        # Retrieve and delete session
        session = get_session(session_id)
        del active_sessions[session_id]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"Session '{session_id}' deleted successfully",
                "timestamp": datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@app.get("/api/v1/sessions", tags=["Session"])
async def list_sessions():
    """
    List all active sessions

    Returns:
        List of active session IDs with metadata
    """
    try:
        sessions_list = []

        if redis_manager:
            # Get from Redis
            session_ids = redis_manager.list_active_sessions(limit=100)
            for session_id in session_ids:
                session_data = redis_manager.load_session_state(session_id)
                if session_data:
                    sessions_list.append({
                        "session_id": session_id,
                        "current_substate": session_data.get("current_substate"),
                        "last_interaction": session_data.get("last_interaction"),
                        "storage": "redis"
                    })
        else:
            # Get from memory
            for session_id, session_data in active_sessions.items():
                sessions_list.append({
                    "session_id": session_id,
                    "client_id": session_data.get("client_id"),
                    "status": session_data["status"],
                    "created_at": session_data["created_at"].isoformat(),
                    "last_interaction": session_data["last_interaction"].isoformat(),
                    "turn_count": session_data["turn_count"],
                    "storage": "memory"
                })

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "total_sessions": len(sessions_list),
                "sessions": sessions_list,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    print("🚀 TRT AI Therapist API starting...")
    print(f"📝 API Documentation: http://localhost:8000/docs")
    print(f"📋 ReDoc: http://localhost:8000/redoc")
    print(f"🩺 Health Check: http://localhost:8000/health")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    print("🛑 TRT AI Therapist API shutting down...")
    # Clean up sessions
    active_sessions.clear()


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
