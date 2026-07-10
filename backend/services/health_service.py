from backend.config.settings import settings
from backend.schemas.health import (
    HealthResponse,
    ComponentStatus,
)
class HealthService:
    async def check(self) -> HealthResponse:
        return HealthResponse(
            application=settings.APP_NAME,
            version=settings.APP_VERSION,
            backend=ComponentStatus(
                status="Healthy",
                message="Backend is running"
            ),
            mongodb=ComponentStatus(
                status="Pending",
                message="MongoDB integration not completed"
            ),
            vector_db=ComponentStatus(
                status="Pending",
                message="FAISS integration not completed"
            ),
            llama=ComponentStatus(
                status="Pending",
                message="Llama 3 not loaded"
            ),
            nemo=ComponentStatus(
                status="Pending",
                message="NVIDIA NeMo not loaded"
            ),
            translation=ComponentStatus(
                status="Pending",
                message="Meta SeamlessM4T not loaded"
            )
        )