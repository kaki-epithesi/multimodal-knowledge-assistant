from fastapi import APIRouter
from ..config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status": "ok", "version": settings.app_version}
