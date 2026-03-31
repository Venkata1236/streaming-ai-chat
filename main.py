from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest, ChatResponse, HealthResponse
from core.streaming_chain import stream_response, run_response
from core.memory import (
    get_turn_count,
    get_history_as_list,
    clear_session,
    get_all_sessions
)
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────
app = FastAPI(
    title="Streaming AI Chat API",
    description="Real-time token streaming AI Chat — FastAPI + LangChain",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Streaming AI Chat API is running!",
        "docs": "/docs",
        "endpoints": [
            "GET  /health",
            "POST /chat        ← full response at once",
            "POST /stream      ← token-by-token streaming",
            "GET  /session/{id}",
            "DELETE /session/{id}"
        ]
    }


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="healthy",
        active_sessions=len(get_all_sessions())
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Non-streaming endpoint — returns full response at once.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        response = run_response(
            session_id=request.session_id,
            message=request.message,
            system_prompt=request.system_prompt
        )
        return ChatResponse(
            session_id=request.session_id,
            message=request.message,
            response=response,
            turn_count=get_turn_count(request.session_id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
def stream(request: ChatRequest):
    """
    Streaming endpoint — yields tokens one by one via SSE.

    Response format (Server-Sent Events):
    data: {"token": "Hello"}
    data: {"token": " world"}
    data: {"token": "!"}
    data: {"done": true, "turn_count": 1}
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    def generate():
        try:
            for token in stream_response(
                session_id=request.session_id,
                message=request.message,
                system_prompt=request.system_prompt
            ):
                # SSE format: data: {json}\n\n
                data = json.dumps({"token": token})
                yield f"data: {data}\n\n"

            # Send done signal with turn count
            done_data = json.dumps({
                "done": True,
                "turn_count": get_turn_count(request.session_id)
            })
            yield f"data: {done_data}\n\n"

        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/session/{session_id}")
def get_session(session_id: str):
    return {
        "session_id": session_id,
        "turn_count": get_turn_count(session_id),
        "history": get_history_as_list(session_id)
    }


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    existed = clear_session(session_id)
    return {
        "session_id": session_id,
        "message": "Cleared" if existed else "Not found"
    }


@app.get("/sessions")
def list_sessions():
    sessions = get_all_sessions()
    return {
        "active_sessions": len(sessions),
        "session_ids": sessions
    }