from fastapi import FastAPI
from app.routes import ingestion, qa
from app.routes.summaries import router as summaries_router
from app.db import init_db

app = FastAPI(title="Multimodal Knowledge Assistant")

init_db()

app.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])
app.include_router(qa.router, tags=["qa"])
app.include_router(summaries_router, prefix="/summaries", tags=["summaries"])


@app.get("/health")
def health():
    return {"status": "ok"}