from typing import Any,Optional
class ResponseBuilder:
    @staticmethod
    def success(
        message:str,
        data:Optional[Any]=None
    ):
        return{
            "success":True,
            "message":message,
            "data":data
        }
    @staticmethod
    def error(
        message: str
    ):
        return{
            "success":False,
            "message":message
        }