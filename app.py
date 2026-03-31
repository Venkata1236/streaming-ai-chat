import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")


def print_separator():
    print("\n" + "=" * 60 + "\n")


def print_welcome():
    print_separator()
    print("⚡  STREAMING AI CHAT — CLI MODE")
    print("    Powered by FastAPI + LangChain Streaming")
    print_separator()
    print("Commands:")
    print("  'quit'  → Exit")
    print("  'reset' → New session")
    print_separator()


def stream_from_api(session_id: str, message: str):
    """
    Calls /stream endpoint and prints tokens as they arrive.
    """
    print("\n⚡ AI: ", end="", flush=True)

    response = requests.post(
        f"{API_URL}/stream",
        json={"session_id": session_id, "message": message},
        stream=True,
        timeout=60
    )

    turn_count = 0
    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if "token" in data:
                    print(data["token"], end="", flush=True)
                elif "done" in data:
                    turn_count = data.get("turn_count", 0)
                elif "error" in data:
                    print(f"\n❌ Error: {data['error']}")

    print(f"\n\n[Turn {turn_count}]")


def run_cli():
    print_welcome()

    # Check API health
    try:
        health = requests.get(f"{API_URL}/health", timeout=3)
        if health.status_code == 200:
            print(f"✅ Connected to API at {API_URL}\n")
        else:
            print(f"❌ API returned {health.status_code}")
            sys.exit(1)
    except Exception:
        print(f"❌ Cannot connect to API at {API_URL}")
        print("Start FastAPI first: uvicorn main:app --reload --port 8000")
        sys.exit(1)

    import uuid
    session_id = str(uuid.uuid4())[:8]
    print(f"Session ID: {session_id}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("👋 Goodbye!")
            break

        if user_input.lower() == "reset":
            requests.delete(f"{API_URL}/session/{session_id}")
            session_id = str(uuid.uuid4())[:8]
            print(f"✅ New session: {session_id}\n")
            continue

        try:
            stream_from_api(session_id, user_input)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    run_cli()