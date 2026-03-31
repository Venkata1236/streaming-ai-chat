import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from core.memory import get_session_history
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPT = """You are a helpful, friendly AI assistant.
You provide clear and concise answers.
You remember conversation history and can refer back to previous messages."""


def get_api_key():
    try:
        import streamlit as st
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def create_streaming_chain(system_prompt: str = None):
    """
    Creates a LangChain chain with streaming=True.
    Returns RunnableWithMessageHistory.
    """
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.7,
        streaming=True,              # ← KEY: enables token-by-token streaming
        openai_api_key=get_api_key()
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt or DEFAULT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    return chain_with_history


def stream_response(session_id: str, message: str, system_prompt: str = None):
    """
    Generator that yields tokens one by one.
    Used by FastAPI StreamingResponse.
    """
    chain = create_streaming_chain(system_prompt)
    config = {"configurable": {"session_id": session_id}}

    for chunk in chain.stream({"input": message}, config=config):
        token = chunk.content
        if token:
            yield token


def run_response(session_id: str, message: str, system_prompt: str = None) -> str:
    """
    Non-streaming version — returns full response.
    Used by CLI and non-streaming endpoint.
    """
    chain = create_streaming_chain(system_prompt)
    config = {"configurable": {"session_id": session_id}}
    response = chain.invoke({"input": message}, config=config)
    return response.content