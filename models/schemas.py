from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Request body for POST /chat and POST /stream"""
    session_id: str
    message: str
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    """Response body for POST /chat (non-streaming)"""
    session_id: str
    message: str
    response: str
    turn_count: int


class HealthResponse(BaseModel):
    """Response body for GET /health"""
    status: str
    active_sessions: int