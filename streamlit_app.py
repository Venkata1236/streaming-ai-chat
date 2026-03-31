import streamlit as st
import requests
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
def get_api_url():
    try:
        return st.secrets["API_URL"]
    except Exception:
        return os.getenv("API_URL", "http://localhost:8000")

API_URL = get_api_url()


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def check_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200, r.json()
    except Exception:
        return False, {}


def stream_tokens(session_id: str, message: str, system_prompt: str):
    """
    Generator that yields tokens from /stream endpoint.
    Used by st.write_stream() for real-time display.
    """
    response = requests.post(
        f"{API_URL}/stream",
        json={
            "session_id": session_id,
            "message": message,
            "system_prompt": system_prompt
        },
        stream=True,
        timeout=60
    )

    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "token" in data:
                        yield data["token"]
                    elif "done" in data:
                        st.session_state.turn_count = data.get("turn_count", 0)
                    elif "error" in data:
                        yield f"\n❌ Error: {data['error']}"
                except Exception:
                    pass


st.set_page_config(
    page_title="Streaming AI Chat",
    page_icon="⚡",
    layout="centered"
)


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.title("⚡ Streaming AI Chat")
    st.markdown("---")

    st.markdown("### 🔑 Session")
    st.code(st.session_state.session_id)
    st.caption("Each session has separate memory")

    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Turn Count", st.session_state.turn_count)

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        height=100
    )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Session", use_container_width=True):
            try:
                requests.delete(
                    f"{API_URL}/session/{st.session_state.session_id}",
                    timeout=3
                )
            except Exception:
                pass
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.chat_history = []
            st.session_state.turn_count = 0
            st.rerun()

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            try:
                requests.delete(
                    f"{API_URL}/session/{st.session_state.session_id}",
                    timeout=3
                )
            except Exception:
                pass
            st.session_state.chat_history = []
            st.session_state.turn_count = 0
            st.rerun()

    st.markdown("---")

    # API Status
    st.markdown("### 🔌 API Status")
    is_healthy, health_data = check_health()
    if is_healthy:
        st.success("✅ API Online")
        st.caption(f"Active sessions: {health_data.get('active_sessions', 0)}")
    else:
        st.error("❌ API Offline")
        st.caption(f"Cannot reach: {API_URL}")
        if "localhost" in API_URL:
            st.code("uvicorn main:app --reload --port 8000")

    st.markdown("---")
    st.caption(
        "Tokens stream in real-time via SSE. "
        "FastAPI → LangChain → OpenAI → token by token."
    )


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
st.title("⚡ Streaming AI Chat")
st.caption(
    f"Session: `{st.session_state.session_id}` — "
    "Responses stream token-by-token like ChatGPT."
)

# API status banner
is_healthy, _ = check_health()
if is_healthy:
    st.success(f"🔗 Connected to FastAPI at `{API_URL}`")
else:
    st.error(
        f"❌ Cannot connect to FastAPI at `{API_URL}`\n\n"
        "Make sure FastAPI is running."
    )

st.markdown("---")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(message["content"])

# Chat input
user_input = st.chat_input(
    "Type your message — response streams token by token...",
    disabled=not is_healthy
)

if user_input:
    # Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Stream AI response
    with st.chat_message("assistant", avatar="⚡"):
        try:
            # st.write_stream — displays tokens as they arrive
            full_response = st.write_stream(
                stream_tokens(
                    st.session_state.session_id,
                    user_input,
                    system_prompt
                )
            )

            # Save to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except requests.exceptions.ConnectionError:
            st.error(
                f"❌ Cannot connect to FastAPI at `{API_URL}`\n\n"
                "Make sure FastAPI is running."
            )
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    st.rerun()