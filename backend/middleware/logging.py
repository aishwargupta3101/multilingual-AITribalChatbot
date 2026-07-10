from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from backend.config.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request, call_next):
        logger.info(
            f"{request.method}{request.url.path}"
        )
        response = await call_next(request)
        logger.info(
            f"Status Code :{ response.status_code}"
        )
        return response
