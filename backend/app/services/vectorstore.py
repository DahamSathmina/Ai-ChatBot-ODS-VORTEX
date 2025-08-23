import faiss, numpy as np, os, pickle
from typing import List, Tuple
from .llm_provider import OllamaProvider
from ..config import settings

class FaissStore:
    def __init__(self, dim: int = None, path: str = "/data/faiss.index"):
        self.dim = dim or settings.EMBEDDING_DIM
        self.index = faiss.IndexFlatIP(self.dim)  # cosine via normalized vectors
        self.texts: List[str] = []
        self.path = path
        # load if exists
        if os.path.exists(self.path):
            self._load()

    def add(self, text: str, vector: List[float]):
        v = np.array([vector], dtype='float32')
        # normalize for IP-cosine
        faiss.normalize_L2(v)
        self.index.add(v)
        self.texts.append(text)
        self._save()

    def search(self, vector: List[float], top_k: int = 4) -> List[Tuple[int, float]]:
        q = np.array([vector], dtype='float32')
        faiss.normalize_L2(q)
        D, I = self.index.search(q, top_k)
        results = []
        for score, idx in zip(D[0].tolist(), I[0].tolist()):
            if idx == -1: continue
            results.append((idx, float(score)))
        return results

    def get_text(self, idx: int) -> str:
        return self.texts[idx]

    def _save(self):
        faiss.write_index(self.index, self.path + ".index")
        with open(self.path + ".meta", "wb") as f:
            pickle.dump(self.texts, f)

    def _load(self):
        try:
            self.index = faiss.read_index(self.path + ".index")
            with open(self.path + ".meta", "rb") as f:
                self.texts = pickle.load(f)
        except Exception:
            pass
