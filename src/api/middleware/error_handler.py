"""
Global exception handlers for FastAPI application.
Handles custom exceptions, validation errors, and database errors.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import (
    DatabaseError,
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)

from src.api.config import api_config
from src.utils.logger import get_logger

logger = get_logger("api.error_handler")


class APIException(Exception):
    """
    Custom API exception with status code and detail.

    Attributes:
        status_code: HTTP status code
        detail: Error message detail
        headers: Optional HTTP headers

    Example:
        raise APIException(
            status_code=404,
            detail="Recipe not found",
            headers={"X-Error": "not-found"}
        )
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Initialize API exception.

        Args:
            status_code: HTTP status code
            detail: Error message
            headers: Optional HTTP headers
        """
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(detail)


def format_error_response(
    detail: str,
    errors: Optional[list] = None,
    error_type: Optional[str] = None,
    debug_info: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Format error response consistently.

    Args:
        detail: Main error message
        errors: List of specific errors
        error_type: Type of error
        debug_info: Debug information (only in debug mode)

    Returns:
        Formatted error response dictionary
    """
    response = {
        "detail": detail,
        "status": "error"
    }

    if errors:
        response["errors"] = errors

    if error_type:
        response["error_type"] = error_type

    if debug_info and api_config.api_debug:
        response["debug"] = debug_info

    return response


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers for the application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        """
        Handle custom API exceptions.

        Args:
            request: Incoming request
            exc: API exception

        Returns:
            JSON response with error details
        """
        logger.warning(
            f"API exception: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(
                detail=exc.detail,
                error_type="api_error"
            ),
            headers=exc.headers
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle request validation errors with detailed field information.

        Args:
            request: Incoming request
            exc: Validation error

        Returns:
            JSON response with validation error details
        """
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_type = error["type"]

            errors.append({
                "field": field,
                "message": message,
                "type": error_type
            })

        logger.warning(
            f"Validation error on {request.method} {request.url.path}",
            extra={
                "errors": errors,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=format_error_response(
                detail="Validation error",
                errors=errors,
                error_type="validation_error"
            )
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors.

        Args:
            request: Incoming request
            exc: Pydantic validation error

        Returns:
            JSON response with validation error details
        """
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]

            errors.append({
                "field": field,
                "message": message,
                "type": error["type"]
            })

        logger.warning(
            f"Pydantic validation error on {request.method} {request.url.path}",
            extra={
                "errors": errors,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=format_error_response(
                detail="Data validation error",
                errors=errors,
                error_type="validation_error"
            )
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: IntegrityError
    ) -> JSONResponse:
        """
        Handle database integrity constraint violations.

        Args:
            request: Incoming request
            exc: Integrity error

        Returns:
            JSON response with integrity error details
        """
        logger.error(
            f"Database integrity error: {exc}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )

        detail = "Database constraint violation"
        if api_config.api_debug:
            detail = f"{detail}: {str(exc.orig)}"

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_error_response(
                detail=detail,
                error_type="integrity_error",
                debug_info=str(exc) if api_config.api_debug else None
            )
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(
        request: Request,
        exc: OperationalError
    ) -> JSONResponse:
        """
        Handle database operational errors (connection issues, etc.).

        Args:
            request: Incoming request
            exc: Operational error

        Returns:
            JSON response with operational error details
        """
        logger.error(
            f"Database operational error: {exc}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=format_error_response(
                detail="Database temporarily unavailable",
                error_type="database_error",
                debug_info=str(exc) if api_config.api_debug else None
            )
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(
        request: Request,
        exc: DatabaseError
    ) -> JSONResponse:
        """
        Handle general database errors.

        Args:
            request: Incoming request
            exc: Database error

        Returns:
            JSON response with database error details
        """
        logger.error(
            f"Database error: {exc}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response(
                detail="Database error occurred",
                error_type="database_error",
                debug_info=str(exc) if api_config.api_debug else None
            )
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """
        Handle all other SQLAlchemy errors.

        Args:
            request: Incoming request
            exc: SQLAlchemy error

        Returns:
            JSON response with database error details
        """
        logger.error(
            f"SQLAlchemy error: {exc}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response(
                detail="Database error occurred",
                error_type="database_error",
                debug_info=str(exc) if api_config.api_debug else None
            )
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Handle all other unhandled exceptions.

        Args:
            request: Incoming request
            exc: Unhandled exception

        Returns:
            JSON response with generic error message
        """
        logger.error(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__
            }
        )

        detail = "Internal server error"
        if api_config.api_debug:
            detail = f"{detail}: {str(exc)}"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response(
                detail=detail,
                error_type="internal_error",
                debug_info={
                    "exception_type": type(exc).__name__,
                    "message": str(exc)
                } if api_config.api_debug else None
            )
        )

    logger.info("Exception handlers registered")
