import json, asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..services.llm_provider import OllamaProvider
from ..services.vectorstore import FaissStore
from ..services.embeddings import get_embedding
from ..config import settings
from ..logger import logger

router = APIRouter()
provider = OllamaProvider()
store = FaissStore(dim=settings.EMBEDDING_DIM, path="/data/faiss")

async def build_prompt(user_text: str, top_k: int = 4):
    # embed & retrieve context
    emb = get_embedding(user_text)
    hits = store.search(emb, top_k=top_k)
    context_parts = []
    for idx, score in hits:
        context_parts.append(store.get_text(idx))
    context = "\n\n".join(context_parts)
    system = "You are ODS Vortex — a concise assistant. Use the provided context when relevant.\n\n"
    prompt = f"{system}CONTEXT:\n{context}\n\nUser: {user_text}\nAssistant:"
    return prompt

@router.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            # Expect a JSON payload { "type":"message", "text": "...", "session": "..." }
            try:
                payload = json.loads(raw)
                text = payload.get("text") or ""
            except Exception:
                text = raw

            prompt = await build_prompt(text)
            # Stream tokens and forward to client as delta messages
            async for chunk in provider.stream_generate(prompt):
                msg = {"type":"delta","content":chunk}
                await ws.send_text(json.dumps(msg))
            await ws.send_text(json.dumps({"type":"done"}))
    except WebSocketDisconnect:
        logger.info("client disconnected")
    except Exception as e:
        logger.exception("ws error")
        await ws.close()
