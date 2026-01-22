"""
FastAPI application factory and configuration.
Main entry point for the Gousto Recipe Meal Planner API.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import api_config
from src.api.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    register_exception_handlers,
)
from src.database.connection import check_connection, get_engine
from src.utils.logger import get_logger

logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    logger.info("Starting API application...")
    logger.info(f"API Version: {api_config.api_version}")
    logger.info(f"Database: {api_config.database_url}")

    # Verify database connection
    engine = get_engine(api_config.database_url, echo=api_config.database_echo)

    if not check_connection(engine):
        logger.error("Failed to connect to database!")
        raise RuntimeError("Database connection failed")

    logger.info("Database connection verified")
    logger.info(f"API server ready at http://{api_config.api_host}:{api_config.api_port}")

    yield

    # Shutdown
    logger.info("Shutting down API application...")
    logger.info("Cleanup complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance

    Example:
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    app = FastAPI(
        title=api_config.api_title,
        description=api_config.api_description,
        version=api_config.api_version,
        docs_url=api_config.docs_url if api_config.api_debug else None,
        redoc_url=api_config.redoc_url if api_config.api_debug else None,
        openapi_url=api_config.openapi_url,
        lifespan=lifespan
    )

    # Configure middleware (order matters - CORS first, then rate limit, then logging)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config.cors_origins,
        allow_credentials=api_config.cors_allow_credentials,
        allow_methods=api_config.cors_allow_methods,
        allow_headers=api_config.cors_allow_headers,
    )

    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    # Add request/response logging middleware
    app.add_middleware(LoggingMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Register routers
    register_routers(app)

    # Health check endpoint
    @app.get("/", tags=["health"])
    async def root():
        """Root endpoint - API health check."""
        return {
            "status": "healthy",
            "service": api_config.api_title,
            "version": api_config.api_version,
            "docs": f"{api_config.docs_url}" if api_config.api_debug else None
        }

    @app.get("/health", tags=["health"])
    async def health_check():
        """Detailed health check with database connectivity."""
        from fastapi.responses import JSONResponse
        from fastapi import status

        try:
            db_healthy = check_connection()
            return {
                "status": "healthy" if db_healthy else "degraded",
                "database": "connected" if db_healthy else "disconnected",
                "version": api_config.api_version
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "error": str(e)
                }
            )

    return app


def register_routers(app: FastAPI) -> None:
    """
    Register all API routers.

    Args:
        app: FastAPI application instance

    Note:
        Router imports are placed here to avoid circular imports.
    """
    from src.api.routers import (
        recipes_router,
        categories_router,
        dietary_tags_router,
        allergens_router,
        meal_plans_router,
        shopping_lists_router,
        auth_router,
        users_router,
        cost_router,
        multi_week_router,
        safe_recipes_router,
        favorites_router,
    )

    # Register authentication and user routers first
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(favorites_router)

    # Register safe_recipes BEFORE recipes (route priority - /recipes/safe before /recipes/{id})
    app.include_router(safe_recipes_router)
    app.include_router(recipes_router)
    app.include_router(categories_router)
    app.include_router(dietary_tags_router)
    app.include_router(allergens_router)
    app.include_router(meal_plans_router)
    app.include_router(shopping_lists_router)
    app.include_router(cost_router)
    app.include_router(multi_week_router)

    logger.info("All routers registered successfully")


# Create the application instance
app = create_app()


if __name__ == "__main__":
    """
    Run the application with uvicorn when executed directly.
    For production, use: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    """
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=api_config.api_host,
        port=api_config.api_port,
        reload=api_config.api_debug,
        log_level=api_config.log_level.lower()
    )
