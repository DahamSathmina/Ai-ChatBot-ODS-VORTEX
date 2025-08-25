import os
import json
from typing import AsyncGenerator, List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemma3:270m")  # or "llama3.2:1b" for llama-tiny

app = FastAPI(title="ODS Vortex Chat Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok", "ollama_url": OLLAMA_URL, "default_model": DEFAULT_MODEL}

async def ollama_stream_chat(messages: List[Dict[str, Any]], model: str) -> AsyncGenerator[str, None]:
    payload = {"model": model, "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as r:
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        # sometimes the stream may include lines like "data: {...}"
                        if line.startswith("data:"):
                            try:
                                data = json.loads(line.split("data:",1)[1].strip())
                            except Exception:
                                continue
                        else:
                            continue
                    # Ollama emits partial tokens in message.content
                    if "message" in data and data["message"].get("content"):
                        yield data["message"]["content"]
                    if data.get("done"):
                        break
        except httpx.RequestError as e:
            yield f"\n[Backend Error] Could not reach Ollama at {OLLAMA_URL}: {e}"

@app.post("/api/chat/stream")
async def chat_stream(req: Request):
    body = await req.json()
    messages = body.get("messages")
    model = body.get("model") or DEFAULT_MODEL
    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be a list of {role, content}")
    async def generator():
        async for chunk in ollama_stream_chat(messages, model):
            # raw text streaming for a simple ReadableStream on the client
            yield chunk
    return StreamingResponse(generator(), media_type="text/plain")

@app.post("/api/models")
async def list_models():
    # proxy to Ollama so the UI can show locally available models
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{OLLAMA_URL}/api/tags")
        return JSONResponse(r.json())
