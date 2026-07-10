import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request,call_next):
        start = time.perf_counter()
        response =await call_next(request)
        total= time.perf_counter()-start
        response.headers["X-Process-Time"]=f"{total:.4f}"
        return response