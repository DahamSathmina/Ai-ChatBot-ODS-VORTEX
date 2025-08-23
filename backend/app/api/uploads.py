from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.embeddings import get_embedding
from ..services.vectorstore import FaissStore
from ..config import settings

router = APIRouter()
store = FaissStore(dim=settings.EMBEDDING_DIM, path="/data/faiss")

@router.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    # naive text extraction: assume plain text, otherwise integrate textract/pdfminer
    text = content.decode(errors="ignore")
    emb = get_embedding(text)
    if not emb:
        raise HTTPException(500, "embedding failed")
    store.add(text, emb)
    return {"status":"indexed"}
