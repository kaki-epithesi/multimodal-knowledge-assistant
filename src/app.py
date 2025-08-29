from fastapi import FastAPI
from .config import settings
from .routes.health import router as health_router

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Routers
app.include_router(health_router)

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Server running", "version": settings.app_version}
