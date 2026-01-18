"""Authentication middleware for JWT token validation.

Note: Phase 3 uses FastAPI Depends() pattern from api/deps.py for JWT verification.
This file is provided for middleware-based auth if needed in future.

For current implementation, see src/api/deps.py:verify_jwt_token()
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT authentication middleware (currently unused - using Depends pattern).

    Phase 3 uses dependency injection via api/deps.py:verify_jwt_token()
    for per-endpoint authentication rather than global middleware.

    This middleware is provided for reference if global JWT validation is needed.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and validate JWT token.

        Currently bypassed - authentication handled by FastAPI Depends().

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        # Authentication is handled per-endpoint via Depends()
        # See src/api/deps.py:verify_jwt_token()
        response = await call_next(request)
        return response
