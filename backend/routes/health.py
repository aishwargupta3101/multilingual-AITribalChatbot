from fastapi import APIRouter, Depends
from backend.api.dependencies import get_health_service
from backend.services.health_service import HealthService
from backend.schemas.health import HealthResponse
import platform
import sys
router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get(
    "/",
    response_model=HealthResponse
)
async def health(
    health_service: HealthService = Depends(get_health_service)
):
    return await health_service.check()
@router.get("/system")
async def system_information():
    return{
        "python_version":sys.version,
        "platform":platform.system(),
        "platform_release":platform.release(),
    }
@router.get("/ready")
async def readiness():
    return{
        "ready":True,
        "message":"Backend is ready to accept request."
    }
@router.get("/live")
async def liveness():
    return{
        "alive": True
    }