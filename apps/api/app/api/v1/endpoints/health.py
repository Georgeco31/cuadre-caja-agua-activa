from fastapi import APIRouter

from app.core.config import get_settings


router = APIRouter()


@router.get("/health")
def read_health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.api_service_name,
    }
