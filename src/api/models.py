"""
Pydantic Models for TRT FastAPI
Request and Response schemas for all endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


# ============================================================
# REQUEST MODELS
# ============================================================

class SessionCreateRequest(BaseModel):
    """Request to create a new therapy session"""
    session_id: Optional[str] = Field(None, description="Optional custom session ID (if not provided, one will be auto-generated)")
    client_id: Optional[str] = Field(None, description="Optional client identifier for tracking")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional session metadata")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "custom_session_001",
                "client_id": "client_123",
                "metadata": {
                    "platform": "web",
                    "version": "1.0"
                }
            }
        }


class ClientInputRequest(BaseModel):
    """Request to process client input in a session"""
    session_id: str = Field(..., description="Unique session identifier", min_length=1)
    user_input: str = Field(..., description="Client's text input", min_length=1)

    class Config:
        schema_extra = {
            "example": {
                "session_id": "user_1234",
                "user_input": "I'm feeling really stressed and overwhelmed"
            }
        }


# ============================================================
# RESPONSE MODELS
# ============================================================

class SessionCreateResponse(BaseModel):
    """Response after creating a new session"""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    status: str = Field(..., description="Session status")
    message: str = Field(..., description="Welcome message")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_20251014_123456",
                "created_at": "2025-10-14T12:34:56",
                "status": "active",
                "message": "Session created successfully. Ready to begin therapy."
            }
        }


class EmotionalState(BaseModel):
    """Emotional state detection from input"""
    categories: Dict[str, List[str]] = Field(default_factory=dict, description="Detected emotion categories")
    intensity: int = Field(0, description="Emotional intensity (0-3)")
    primary_emotion: str = Field("neutral_unclear", description="Primary emotional category")


class SafetyChecks(BaseModel):
    """Safety check results"""
    self_harm_detected: Dict[str, Any] = Field(default_factory=dict, description="Self-harm detection results")
    thinking_mode_detected: Dict[str, Any] = Field(default_factory=dict, description="Thinking mode detection")
    past_tense_detected: Dict[str, Any] = Field(default_factory=dict, description="Past tense detection")
    i_dont_know_detected: Dict[str, Any] = Field(default_factory=dict, description="Uncertainty detection")


class PreprocessingResult(BaseModel):
    """Input preprocessing results"""
    original_input: str = Field(..., description="Original user input")
    cleaned_input: str = Field(..., description="Cleaned input text")
    corrected_input: str = Field(..., description="Spelling-corrected input")
    emotional_state: EmotionalState = Field(..., description="Detected emotional state")
    input_category: str = Field(..., description="Input category")
    spelling_corrections: List[tuple] = Field(default_factory=list, description="Applied spelling corrections")
    safety_checks: SafetyChecks = Field(..., description="Safety check results")


class NavigationDecision(BaseModel):
    """Master planning agent navigation decision"""
    decision: str = Field(..., description="Navigation decision")
    next_state: Optional[str] = Field(None, description="Next state to transition to")
    rag_query: Optional[str] = Field(None, description="RAG query for dialogue agent")
    reasoning: Optional[str] = Field(None, description="Reasoning behind decision")


class SessionProgress(BaseModel):
    """Session progress tracking"""
    current_substate: str = Field(..., description="Current TRT substate")
    body_question_count: int = Field(0, description="Number of body questions asked")
    completion_criteria: Dict[str, bool] = Field(default_factory=dict, description="Stage 1 completion criteria")


class TherapistResponse(BaseModel):
    """Complete therapist response"""
    therapist_response: str = Field(..., description="Therapist's response text")
    preprocessing: PreprocessingResult = Field(..., description="Input preprocessing results")
    navigation: NavigationDecision = Field(..., description="Navigation decision")
    session_progress: SessionProgress = Field(..., description="Session progress")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        schema_extra = {
            "example": {
                "therapist_response": "I hear you're feeling stressed and overwhelmed. What would we like to get out of our session today?",
                "preprocessing": {
                    "original_input": "I'm feeling really stressed",
                    "cleaned_input": "i am feeling really stressed",
                    "corrected_input": "i am feeling really stressed",
                    "emotional_state": {
                        "categories": {"negative_moderate": ["stressed"]},
                        "intensity": 2,
                        "primary_emotion": "moderate_distress"
                    },
                    "input_category": "feeling_statement",
                    "spelling_corrections": [],
                    "safety_checks": {
                        "self_harm_detected": {"detected": False},
                        "thinking_mode_detected": {"detected": False},
                        "past_tense_detected": {"detected": False},
                        "i_dont_know_detected": {"detected": False}
                    }
                },
                "navigation": {
                    "decision": "continue",
                    "next_state": "1.1_goal_and_vision",
                    "rag_query": "client feeling stressed, ask about session goal"
                },
                "session_progress": {
                    "current_substate": "1.1_goal_and_vision",
                    "body_question_count": 0,
                    "completion_criteria": {
                        "goal_established": False,
                        "vision_created": False
                    }
                },
                "timestamp": "2025-10-14T12:35:00"
            }
        }


class SessionStatusResponse(BaseModel):
    """Session status information"""
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Session status (active/completed)")
    current_substate: str = Field(..., description="Current TRT substate")
    body_question_count: int = Field(..., description="Body questions asked")
    completion_criteria: Dict[str, bool] = Field(..., description="Stage 1 completion criteria")
    turn_count: int = Field(..., description="Number of conversation turns")
    created_at: datetime = Field(..., description="Session creation time")
    last_interaction: datetime = Field(..., description="Last interaction time")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_20251014_123456",
                "status": "active",
                "current_substate": "1.2_problem_and_body",
                "body_question_count": 1,
                "completion_criteria": {
                    "goal_established": True,
                    "vision_created": True,
                    "problem_identified": True,
                    "body_awareness_present": False
                },
                "turn_count": 5,
                "created_at": "2025-10-14T12:34:56",
                "last_interaction": "2025-10-14T12:38:23"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    services: Dict[str, str] = Field(..., description="Service component statuses")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-14T12:34:56",
                "services": {
                    "ollama": "connected",
                    "rag": "ready",
                    "state_machine": "loaded"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

    class Config:
        schema_extra = {
            "example": {
                "error": "SessionNotFound",
                "message": "Session with ID 'session_123' not found",
                "details": {
                    "session_id": "session_123"
                },
                "timestamp": "2025-10-14T12:34:56"
            }
        }
