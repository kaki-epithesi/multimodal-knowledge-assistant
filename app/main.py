from fastapi import FastAPI
from app.routes import ingestion
from app.db import init_db

app = FastAPI(title="Multimodal Knowledge Assistant - v0.2")

init_db()

app.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])