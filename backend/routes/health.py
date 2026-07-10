from fastapi import APIRouter, Depends
from backend.api.dependencies import get_health_service
from backend.services.health_service import HealthService

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)
@router.get("/")
async def health(
    health_service: HealthService = Depends(get_health_service)
):
    return await health_service.check()