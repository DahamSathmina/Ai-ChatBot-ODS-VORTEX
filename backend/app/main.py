from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import ws, uploads, admin
from .config import settings

app = FastAPI(title="ODS Chat Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws.router, prefix="/v1")
app.include_router(uploads.router, prefix="/v1")
app.include_router(admin.router, prefix="/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}
