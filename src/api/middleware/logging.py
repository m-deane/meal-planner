"""
Request/Response logging middleware for FastAPI.
Logs HTTP requests, responses, and timing information.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.utils.logger import get_logger

logger = get_logger("api.requests")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Tracks:
    - Request method and path
    - Request ID (generated or from header)
    - Response status code
    - Request duration
    - Client IP address

    Example:
        app.add_middleware(LoggingMiddleware)
    """

    def __init__(self, app: ASGIApp) -> None:
        """
        Initialize logging middleware.

        Args:
            app: ASGI application
        """
        super().__init__(app)
        logger.info("Request logging middleware initialized")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response from the application
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store request ID in request state for access in routes
        request.state.request_id = request_id

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Log incoming request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )

        # Start timer
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log response
            log_level = self._get_log_level(response.status_code)
            log_message = (
                f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {duration_ms}ms"
            )

            getattr(logger, log_level)(
                log_message,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": client_ip
                }
            )

            return response

        except Exception as exc:
            # Calculate duration even on error
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"Error: {type(exc).__name__} - Duration: {duration_ms}ms",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "client_ip": client_ip,
                    "exception_type": type(exc).__name__
                }
            )

            # Re-raise exception to be handled by exception handlers
            raise

    @staticmethod
    def _get_log_level(status_code: int) -> str:
        """
        Determine appropriate log level based on status code.

        Args:
            status_code: HTTP status code

        Returns:
            Log level name (info, warning, error)
        """
        if status_code < 400:
            return "info"
        elif status_code < 500:
            return "warning"
        else:
            return "error"
