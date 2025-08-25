# Next‑Level AI Chatbot (Free‑tier Cloud + Local)

A full‑stack starter you can extend:
- **Backend:** FastAPI (Python) with pluggable providers (Groq, Gemini, Ollama)
- **Frontend:** React + Vite + Tailwind with streaming UI and settings
- **Streaming:** SSE-compatible from Groq and Ollama
- **Config:** .env (server) + localStorage (client) headers override

## Run it

1) **Server**
```bash
cd server
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell
# or: source .venv/bin/activate                    # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Fill GROQ_API_KEY / GEMINI_API_KEY if you have them
uvicorn app:app --reload --port 8000
```

2) **Client**
```bash
cd client
npm i
npm run dev
```

Open http://localhost:5173

## Notes

- Groq uses an OpenAI-compatible endpoint. For streaming, the backend re-streams as `text/event-stream`.
- Gemini here is non‑streaming to keep the starter simple. You can add streaming later via the `streamGenerateContent` endpoint.
- Ollama is optional for local testing.
