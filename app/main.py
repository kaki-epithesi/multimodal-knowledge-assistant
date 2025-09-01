from fastapi import FastAPI
from app.routes import ingestion, qa
from app.db import init_db

app = FastAPI(title="Multimodal Knowledge Assistant - v0.3")

init_db()

app.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])
app.include_router(qa.router, tags=["qa"])

@app.get("/health")
def health():
    return {"status": "ok"}