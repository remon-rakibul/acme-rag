from fastapi import FastAPI
from app.routers import ingest, retrieve, generate

app = FastAPI(
    title="Healthcare Knowledge Assistant API",
    description="RAG-powered assistant for retrieving medical guidelines and research summaries in English and Japanese",
    version="1.0.0"
)

app.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
app.include_router(retrieve.router, prefix="/retrieve", tags=["retrieval"])
app.include_router(generate.router, prefix="/generate", tags=["generation"])


@app.get("/")
async def root():
    return {
        "message": "Healthcare Knowledge Assistant API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

