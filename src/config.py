"""
Configuration management for recipe scraper.
Supports environment variables, config files, and CLI arguments.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///recipes.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )
    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum overflow connections"
    )

    # Scraper Configuration
    scraper_delay_seconds: float = Field(
        default=3.0,
        ge=0.5,
        le=30.0,
        description="Delay between requests in seconds"
    )
    scraper_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts per request"
    )
    scraper_retry_backoff: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff multiplier"
    )
    scraper_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Request timeout in seconds"
    )
    scraper_batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of recipes to process in one batch"
    )
    scraper_max_recipes: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum number of recipes to scrape (None for unlimited)"
    )

    # User Agents
    user_agents: List[str] = Field(
        default=[
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ],
        description="List of user agents to rotate"
    )

    # Gousto-specific
    gousto_base_url: str = Field(
        default="https://www.gousto.co.uk",
        description="Base URL for Gousto website"
    )
    gousto_sitemap_url: str = Field(
        default="https://www.gousto.co.uk/sitemap.xml",
        description="Sitemap URL for recipe discovery"
    )
    gousto_robots_url: str = Field(
        default="https://www.gousto.co.uk/robots.txt",
        description="Robots.txt URL"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    log_file: Optional[str] = Field(
        default="logs/scraper.log",
        description="Log file path (None for console only)"
    )
    log_rotation: str = Field(
        default="10 MB",
        description="Log rotation size"
    )
    log_retention: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of backup log files to keep"
    )

    # Checkpoint Configuration
    checkpoint_enabled: bool = Field(
        default=True,
        description="Enable checkpoint/resume functionality"
    )
    checkpoint_interval: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Save checkpoint every N recipes"
    )
    checkpoint_file: str = Field(
        default=".scraper_checkpoint.json",
        description="Checkpoint file path"
    )

    # Data Validation
    validation_strict: bool = Field(
        default=False,
        description="Fail on validation errors vs. log warnings"
    )
    validation_require_ingredients: bool = Field(
        default=True,
        description="Require at least one ingredient"
    )
    validation_require_instructions: bool = Field(
        default=True,
        description="Require at least one instruction"
    )
    validation_min_calories: int = Field(
        default=0,
        ge=0,
        description="Minimum calorie value"
    )
    validation_max_calories: int = Field(
        default=5000,
        ge=100,
        description="Maximum calorie value"
    )

    # Export Configuration
    export_include_inactive: bool = Field(
        default=False,
        description="Include inactive recipes in exports"
    )
    export_pretty_json: bool = Field(
        default=True,
        description="Pretty-print JSON exports"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("sqlite://", "postgresql://", "postgresql+psycopg2://")):
            raise ValueError(
                "database_url must start with sqlite://, postgresql://, or postgresql+psycopg2://"
            )
        return v

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite:")

    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_url.startswith("postgresql")

    def get_log_file_path(self) -> Optional[Path]:
        """Get Path object for log file."""
        if self.log_file:
            return Path(self.log_file)
        return None

    def ensure_directories(self) -> None:
        """Create necessary directories."""
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

        if self.checkpoint_file:
            checkpoint_path = Path(self.checkpoint_file)
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = Config()
