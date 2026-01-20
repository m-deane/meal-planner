"""
Middleware package for FastAPI application.
Contains error handling, logging, and rate limiting middleware.
"""

from src.api.middleware.error_handler import (
    APIException,
    register_exception_handlers,
)
from src.api.middleware.logging import LoggingMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware

__all__ = [
    "APIException",
    "register_exception_handlers",
    "LoggingMiddleware",
    "RateLimitMiddleware",
]
