from .llm_provider import OllamaProvider

provider = OllamaProvider()

def get_embedding(text: str):
    emb = provider.embed(text)
    return emb
