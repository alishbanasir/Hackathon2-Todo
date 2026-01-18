"""Rate limiting middleware for API endpoints.

Implements token bucket algorithm to limit requests per user.
"""

import time
from collections import defaultdict
from typing import Callable, Dict
from uuid import UUID

import structlog
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class TokenBucket:
    """Token bucket for rate limiting.

    Implements leaky bucket algorithm with token refill.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.

        Args:
            capacity: Maximum number of tokens (requests)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens.

        Args:
            tokens: Number of tokens to consume (default 1)

        Returns:
            True if tokens consumed, False if insufficient tokens
        """
        # Refill tokens based on time elapsed
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity, self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now

        # Try to consume tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_wait_time(self) -> float:
        """Get time to wait before next request.

        Returns:
            Seconds to wait for token refill
        """
        if self.tokens >= 1:
            return 0.0
        return (1 - self.tokens) / self.refill_rate


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm.

    Limits: 60 requests per minute per user (T107)
    """

    def __init__(self, app, requests_per_minute: int = 60):
        """Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Max requests per user per minute (default 60)
        """
        super().__init__(app)
        self.buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=requests_per_minute,
                refill_rate=requests_per_minute / 60.0,  # tokens per second
            )
        )
        self.requests_per_minute = requests_per_minute

    def _get_user_key(self, request: Request) -> str:
        """Extract user identifier from request.

        Args:
            request: FastAPI request object

        Returns:
            User identifier (user_id from JWT or IP address)
        """
        # Try to get user_id from JWT token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # For rate limiting, we use the token itself as the key
            # In production, decode JWT to get user_id
            return f"token:{token[:20]}"  # Use first 20 chars as identifier

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response from endpoint or 429 rate limit error

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get user identifier
        user_key = self._get_user_key(request)

        # Get or create token bucket for user
        bucket = self.buckets[user_key]

        # Try to consume a token
        if not bucket.consume():
            # Rate limit exceeded
            wait_time = bucket.get_wait_time()

            logger.warning(
                "rate_limit_exceeded",
                user_key=user_key,
                path=request.url.path,
                wait_time=round(wait_time, 2),
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Please try again in {int(wait_time)} seconds.",
                    "retry_after": int(wait_time) + 1,
                    "limit": self.requests_per_minute,
                    "window": "60 seconds",
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + bucket.get_wait_time())
        )

        return response

    def cleanup_old_buckets(self, max_age: int = 3600):
        """Clean up inactive buckets (optional housekeeping).

        Args:
            max_age: Remove buckets older than this many seconds (default 1 hour)
        """
        now = time.time()
        to_remove = []

        for key, bucket in self.buckets.items():
            # If bucket hasn't been used recently and is full, remove it
            if (
                now - bucket.last_refill > max_age
                and bucket.tokens >= bucket.capacity
            ):
                to_remove.append(key)

        for key in to_remove:
            del self.buckets[key]

        if to_remove:
            logger.info(
                "rate_limiter_cleanup", removed_buckets=len(to_remove)
            )
