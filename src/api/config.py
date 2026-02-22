"""
API-specific configuration extending the base application config.
"""

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from src.config import Config as BaseConfig


class APIConfig(BaseConfig):
    """Extended configuration with API-specific settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Server Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host"
    )
    api_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API server port"
    )
    api_debug: bool = Field(
        default=False,
        description="Enable debug mode (auto-reload, detailed errors)"
    )
    api_title: str = Field(
        default="Gousto Recipe Meal Planner API",
        description="API title for OpenAPI docs"
    )
    api_description: str = Field(
        default="RESTful API for recipe discovery, meal planning, and shopping list generation",
        description="API description"
    )
    api_version: str = Field(
        default="1.0.0",
        description="API version"
    )

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
            "http://localhost:3100",
            "http://127.0.0.1:3100",
            "http://localhost:8100",
            "http://127.0.0.1:8100",
            "http://localhost:3200",
            "http://127.0.0.1:3200",
            "http://localhost:8200",
            "http://127.0.0.1:8200",
        ],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description="Allowed HTTP methods for CORS"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed headers for CORS"
    )

    # JWT Authentication Configuration
    jwt_secret: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    jwt_expire_minutes: int = Field(
        default=1440,  # 24 hours
        ge=5,
        le=43200,  # 30 days
        description="JWT token expiration time in minutes"
    )
    jwt_refresh_expire_minutes: int = Field(
        default=10080,  # 7 days
        ge=60,
        le=525600,  # 1 year
        description="JWT refresh token expiration in minutes"
    )

    # API Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        le=10000,
        description="Maximum requests per minute per IP"
    )
    rate_limit_per_hour: int = Field(
        default=1000,
        ge=1,
        le=100000,
        description="Maximum requests per hour per IP"
    )

    # API Pagination
    pagination_default_limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Default number of items per page"
    )
    pagination_max_limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum items per page"
    )

    # OpenAPI Documentation
    docs_url: str = Field(
        default="/docs",
        description="Swagger UI documentation path"
    )
    redoc_url: str = Field(
        default="/redoc",
        description="ReDoc documentation path"
    )
    openapi_url: str = Field(
        default="/openapi.json",
        description="OpenAPI schema path"
    )

    # API Features
    enable_meal_planner: bool = Field(
        default=True,
        description="Enable meal planning endpoints"
    )
    enable_shopping_list: bool = Field(
        default=True,
        description="Enable shopping list endpoints"
    )
    enable_recipe_search: bool = Field(
        default=True,
        description="Enable recipe search endpoints"
    )

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret is set in production."""
        if v == "your-secret-key-change-this-in-production":
            import warnings
            warnings.warn(
                "Using default JWT secret! Change this in production via JWT_SECRET environment variable.",
                UserWarning
            )
        if len(v) < 32:
            raise ValueError("jwt_secret must be at least 32 characters long")
        return v

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm."""
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in valid_algorithms:
            raise ValueError(f"jwt_algorithm must be one of {valid_algorithms}")
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins format."""
        for origin in v:
            if origin != "*" and not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid CORS origin format: {origin}")
        return v


# Global API configuration instance
api_config = APIConfig()
