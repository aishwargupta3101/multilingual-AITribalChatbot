from fastapi import APIRouter
from backend.schemas.health import HealthResponse
from backend.services.health_service import HealthService
router = APIRouter(
    prefix="/health",
    tags=["Health"]
)
@router.get(
    "/",
    response_model=HealthResponse
)
async def health():
    return await HealthService.check()