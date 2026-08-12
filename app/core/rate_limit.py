"""
Shared rate-limiter instance for the application.

Usage in route handlers:

    from app.core.rate_limit import limiter

    @router.post("/endpoint")
    @limiter.limit("10/minute")
    def my_endpoint(request: Request):
        ...
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
