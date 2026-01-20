"""
Rate limiting middleware for FastAPI.
Simple in-memory rate limiter with configurable requests per minute.
"""

import time
from collections import defaultdict, deque
from typing import Callable, DefaultDict, Deque, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.api.config import api_config
from src.utils.logger import get_logger

logger = get_logger("api.rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiting middleware.

    Tracks requests per client IP and enforces rate limits.
    Stores timestamps of requests in sliding window.

    Attributes:
        enabled: Whether rate limiting is enabled
        requests_per_minute: Maximum requests per minute per IP
        request_history: Deque of request timestamps per IP

    Example:
        app.add_middleware(RateLimitMiddleware)
    """

    def __init__(self, app: ASGIApp) -> None:
        """
        Initialize rate limiting middleware.

        Args:
            app: ASGI application
        """
        super().__init__(app)

        self.enabled = api_config.rate_limit_enabled
        self.requests_per_minute = api_config.rate_limit_per_minute

        # Store request timestamps per IP: {ip: deque([timestamp1, timestamp2, ...])}
        self.request_history: DefaultDict[str, Deque[float]] = defaultdict(deque)

        # Cleanup old entries periodically
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes

        if self.enabled:
            logger.info(
                f"Rate limiting enabled: {self.requests_per_minute} requests/minute"
            )
        else:
            logger.info("Rate limiting disabled")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and enforce rate limits.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response or rate limit error
        """
        # Skip rate limiting if disabled
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Cleanup old entries periodically
        self._periodic_cleanup()

        # Check rate limit
        is_allowed, retry_after = self._check_rate_limit(client_ip)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {client_ip}",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                    "limit": self.requests_per_minute
                }
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "status": "error",
                    "error_type": "rate_limit_error",
                    "limit": self.requests_per_minute,
                    "window": "1 minute",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after))
                }
            )

        # Record request
        self.request_history[client_ip].append(time.time())

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = self._get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.
        Checks X-Forwarded-For header first (for proxies).

        Args:
            request: Incoming request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (set by proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in chain
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"

    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limit.
        Uses sliding window algorithm.

        Args:
            client_ip: Client IP address

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - 60  # 1 minute window

        # Get request history for this IP
        requests = self.request_history[client_ip]

        # Remove requests outside the window
        while requests and requests[0] < window_start:
            requests.popleft()

        # Check if limit exceeded
        request_count = len(requests)

        if request_count >= self.requests_per_minute:
            # Calculate retry after (time until oldest request expires)
            retry_after = int(requests[0] + 60 - now) + 1
            return False, retry_after

        return True, 0

    def _get_remaining_requests(self, client_ip: str) -> int:
        """
        Get remaining requests for client in current window.

        Args:
            client_ip: Client IP address

        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - 60

        requests = self.request_history[client_ip]

        # Count requests in current window
        current_count = sum(1 for timestamp in requests if timestamp >= window_start)

        return max(0, self.requests_per_minute - current_count)

    def _periodic_cleanup(self) -> None:
        """
        Periodically clean up old request history entries.
        Removes IPs with no recent requests to prevent memory growth.
        """
        now = time.time()

        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now
        window_start = now - 60

        # Find IPs with no recent requests
        ips_to_remove = []
        for ip, requests in self.request_history.items():
            # Remove old timestamps
            while requests and requests[0] < window_start:
                requests.popleft()

            # Mark IP for removal if no recent requests
            if not requests:
                ips_to_remove.append(ip)

        # Remove empty entries
        for ip in ips_to_remove:
            del self.request_history[ip]

        if ips_to_remove:
            logger.debug(f"Cleaned up {len(ips_to_remove)} inactive IP entries")
