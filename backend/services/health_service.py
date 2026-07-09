from backend.schemas.health import HealthResponse

class HealthService:
    @staticmethod
    async def check():
        return HealthResponse(
            status="healthy",
            version="1.0.0"
        )
