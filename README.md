# ⚡ Streaming AI Chat

> Real-time token-by-token streaming — FastAPI + LangChain + SSE + Streamlit

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)

---

## 📌 What Is This?

A real-time streaming AI chat. Tokens stream one by one from OpenAI → FastAPI → Streamlit — exactly like ChatGPT. Built using FastAPI StreamingResponse, Server-Sent Events (SSE), LangChain streaming=True, and Streamlit's st.write_stream().

---

## 🗺️ Simple Flow
```
User sends message
        ↓
Streamlit calls POST /stream
        ↓
FastAPI starts StreamingResponse
        ↓
LangChain streams tokens (streaming=True)
        ↓
Each token → SSE → Streamlit
        ↓
st.write_stream() displays tokens as they arrive
```

---

## 📁 Project Structure
```
streaming_ai_chat/
├── main.py                     ← FastAPI — /chat + /stream endpoints
├── streamlit_app.py            ← Streamlit — st.write_stream display
├── app.py                      ← CLI streaming client
├── core/
│   ├── __init__.py
│   ├── streaming_chain.py      ← LangChain streaming=True chain
│   └── memory.py               ← Per-session memory
├── models/
│   ├── __init__.py
│   └── schemas.py              ← Pydantic schemas
├── .env
├── requirements.txt
└── README.md
```

---

## 🔗 API Endpoints

| Method | Endpoint | Type | Description |
|---|---|---|---|
| GET | `/health` | Normal | Health check |
| POST | `/chat` | Normal | Full response at once |
| POST | `/stream` | SSE | Token-by-token streaming |
| GET | `/session/{id}` | Normal | Get history |
| DELETE | `/session/{id}` | Normal | Clear session |

---

## 🧠 Key Concepts

| Concept | What It Does |
|---|---|
| `streaming=True` | ChatOpenAI yields tokens one by one |
| `StreamingResponse` | FastAPI streams chunks to client |
| `Server-Sent Events` | HTTP protocol for real-time server push |
| `st.write_stream()` | Streamlit displays tokens as generator yields |
| `iter_lines()` | requests reads SSE lines as they arrive |

---

## ⚙️ Local Setup
```bash
pip install -r requirements.txt
```

Add `.env`:
```
OPENAI_API_KEY=your_key_here
```

Add `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your_key_here"
API_URL = "http://localhost:8000"
```

Run:
```bash
# Terminal 1
uvicorn main:app --reload --port 8000

# Terminal 2
python -m streamlit run streamlit_app.py

# Terminal (CLI)
python app.py
```

---

## 📦 Tech Stack

- **FastAPI** — StreamingResponse + SSE endpoint
- **LangChain** — streaming=True + RunnableWithMessageHistory
- **OpenAI** — GPT-4o-mini token streaming
- **Streamlit** — st.write_stream() for live display

---

## 👤 Author

**Venkata Reddy Bommavaram**
- 📧 bommavaramvenkat2003@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/venkatareddy1203)
- 🐙 [GitHub](https://github.com/venkata1236)