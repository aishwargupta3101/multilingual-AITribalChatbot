from fastapi import HTTPException
class TribalAIException(HTTPException):
    def __init__(
            self,
            status_code:int,
            error:str,
            message:str
        ):

            super().__init__(
                status_code=status_code,
                detail={
                    "success":False,
                    "error":error,
                    "message":message
                }
            )