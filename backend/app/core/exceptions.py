"""
TransitSense AI: Custom Domain Exceptions & Error Handlers
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class TransitSenseException(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class RouteNotFoundException(TransitSenseException):
    def __init__(self, route_id: str):
        super().__init__(
            code="ROUTE_NOT_FOUND",
            message=f"Bus route '{route_id}' does not exist in the Delhi transit network.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"route_id": route_id}
        )


class StopNotFoundException(TransitSenseException):
    def __init__(self, stop_id: str):
        super().__init__(
            code="STOP_NOT_FOUND",
            message=f"Transit stop '{stop_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"stop_id": stop_id}
        )


class JourneyPlanningException(TransitSenseException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="JOURNEY_PLANNING_FAILED",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ModelInferenceException(TransitSenseException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="MODEL_INFERENCE_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


async def transitsense_exception_handler(request: Request, exc: TransitSenseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "details": {}
            }
        }
    )
