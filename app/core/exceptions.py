"""
Global exception handlers for API error responses.
Provides consistent error responses across all endpoints.
"""

import logging
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, message: str, status_code: int = 400, detail: Any = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle APIError exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"API Error [Request ID: {request_id}]: {exc.message}",
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "detail": exc.detail,
            "request_id": request_id,
        },
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"Validation Error [Request ID: {request_id}]: {exc.error_count()} errors",
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation failed",
            "errors": [
                {
                    "field": ".".join(str(x) for x in err["loc"]),
                    "message": err["msg"],
                }
                for err in exc.errors()
            ],
            "request_id": request_id,
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"Unhandled Exception [Request ID: {request_id}]: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "request_id": request_id,
        },
    )
