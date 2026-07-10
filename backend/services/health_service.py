from backend.utils.response import ResponseBuilder
class HealthService:

    async def check(self):
        return ResponseBuilder.success(
            message="Backend Healthy",
            data={
                "status":"healthy",
                "version":"1.0.0"
            }
        )