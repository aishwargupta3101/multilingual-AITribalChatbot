from fastapi import Request
from fastapi.responses import JSONResponse
from backend.config.logger import logger
from backend.exceptions.base import TribalAIException

async  def tribal_exception_handler(
        request:Request,
        exc:TribalAIException
):
    logger.error(
        f"{exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )
async  def generic_exception_handler(
        request:Request,
        exc:Exception
):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error":"Internal Server Error",
            "message":str(exc)
        }

    )