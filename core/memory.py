from langchain_community.chat_message_histories import ChatMessageHistory

# Global session store — session_id → ChatMessageHistory
_session_store: dict = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    """Returns existing or new ChatMessageHistory for session."""
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]


def clear_session(session_id: str) -> bool:
    if session_id in _session_store:
        del _session_store[session_id]
        return True
    return False


def get_all_sessions() -> list:
    return list(_session_store.keys())


def get_turn_count(session_id: str) -> int:
    if session_id not in _session_store:
        return 0
    return len(_session_store[session_id].messages) // 2


def get_history_as_list(session_id: str) -> list:
    if session_id not in _session_store:
        return []
    result = []
    for msg in _session_store[session_id].messages:
        result.append({
            "role": "user" if msg.type == "human" else "assistant",
            "content": msg.content
        })
    return result