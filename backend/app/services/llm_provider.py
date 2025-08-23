import asyncio, requests, json
from typing import AsyncGenerator
from ..config import settings
from ..logger import logger

OLLAMA_GEN_URL = f"{settings.OLLAMA_URL}/api/generate"
OLLAMA_EMBED_URL = f"{settings.OLLAMA_URL}/api/embeddings"

class OllamaProvider:
    def __init__(self, model: str = None):
        self.model = model or settings.OLLAMA_MODEL


    async def stream_generate(self, prompt: str, temperature: float = 0.2) -> AsyncGenerator[str, None]:
        """
        Streams tokens from Ollama via the /api/generate endpoint with stream=True.
        Yields strings (chunks).
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": True
        }
        # Use requests in a thread to avoid blocking; iterate response.iter_lines()
        loop = asyncio.get_event_loop()
        def req():
            return requests.post(OLLAMA_GEN_URL, json=payload, stream=True, timeout=120)
        resp = await loop.run_in_executor(None, req)
        if resp.status_code != 200:
            text = resp.text
            logger.error("Ollama error: %s", text)
            yield f"[MODEL_ERROR] {text}"
            return

        for raw in resp.iter_lines():
            if raw:
                try:
                    data = json.loads(raw.decode())
                except Exception:
                    # non-json line
                    continue
                # Ollama streaming shape can vary; adjust depending on version.
                if isinstance(data, dict):
                    if "response" in data:
                        yield data["response"]
                    elif data.get("done"):
                        break
            # yield control to event loop
            await asyncio.sleep(0)

    async def embed(self, text: str):
        payload = {"model": "nomic-embed-text", "prompt": text}
        resp = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json().get("embedding")
