"""
Middleware for adding request ID tracking to all requests.
Useful for distributed tracing and debugging.
"""

import logging
import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to each request for tracing.
    If no X-Request-ID header is provided, one is generated.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER)

        if not request_id:
            request_id = str(uuid.uuid4())

        # Store request ID in request state for use in handlers
        request.state.request_id = request_id

        # Create response with request ID
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id

        return response
