"""
Structured logging with rotation support.
Provides different log levels and separate logs for scraping vs system errors.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from src.config import config


class ScraperLogger:
    """Centralized logging configuration."""

    def __init__(
        self,
        name: str = "scraper",
        log_file: Optional[Path] = None,
        console_output: bool = True
    ):
        """
        Initialize logger with rotation and formatting.

        Args:
            name: Logger name
            log_file: Path to log file (None for console only)
            console_output: Enable console output
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.log_level))
        self.logger.handlers.clear()

        formatter = logging.Formatter(config.log_format)

        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, config.log_level))
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)

            max_bytes = self._parse_size(config.log_rotation)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=config.log_retention,
                encoding="utf-8"
            )
            file_handler.setLevel(getattr(logging, config.log_level))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    @staticmethod
    def _parse_size(size_str: str) -> int:
        """
        Parse size string to bytes.

        Args:
            size_str: Size string like '10 MB', '1 GB', '500 KB'

        Returns:
            Size in bytes
        """
        size_str = size_str.strip().upper()
        units = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 ** 2,
            'GB': 1024 ** 3,
        }

        parts = size_str.split()
        if len(parts) != 2:
            return 10 * 1024 * 1024

        try:
            value = float(parts[0])
            unit = parts[1]
            return int(value * units.get(unit, 1024 ** 2))
        except (ValueError, KeyError):
            return 10 * 1024 * 1024

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)

    def scraping_progress(
        self,
        current: int,
        total: int,
        success: int,
        failed: int,
        message: str = ""
    ) -> None:
        """
        Log scraping progress metrics.

        Args:
            current: Current item number
            total: Total items to process
            success: Number of successful scrapes
            failed: Number of failed scrapes
            message: Additional message
        """
        percentage = (current / total * 100) if total > 0 else 0
        success_rate = (success / current * 100) if current > 0 else 0

        progress_msg = (
            f"Progress: {current}/{total} ({percentage:.1f}%) | "
            f"Success: {success} ({success_rate:.1f}%) | "
            f"Failed: {failed}"
        )

        if message:
            progress_msg += f" | {message}"

        self.info(progress_msg)

    def recipe_scraped(
        self,
        recipe_name: str,
        recipe_url: str,
        ingredients_count: int,
        instructions_count: int
    ) -> None:
        """
        Log successful recipe scrape.

        Args:
            recipe_name: Recipe name
            recipe_url: Recipe URL
            ingredients_count: Number of ingredients extracted
            instructions_count: Number of instructions extracted
        """
        self.info(
            f"Scraped: {recipe_name} | "
            f"Ingredients: {ingredients_count} | "
            f"Instructions: {instructions_count} | "
            f"URL: {recipe_url}"
        )

    def recipe_error(
        self,
        recipe_url: str,
        error_type: str,
        error_message: str
    ) -> None:
        """
        Log recipe scraping error.

        Args:
            recipe_url: Recipe URL
            error_type: Type of error
            error_message: Error message
        """
        self.error(
            f"Failed to scrape: {recipe_url} | "
            f"Error: {error_type} | "
            f"Message: {error_message}"
        )

    def validation_error(
        self,
        recipe_name: str,
        field: str,
        error_message: str
    ) -> None:
        """
        Log data validation error.

        Args:
            recipe_name: Recipe name
            field: Field that failed validation
            error_message: Validation error message
        """
        self.warning(
            f"Validation error: {recipe_name} | "
            f"Field: {field} | "
            f"Error: {error_message}"
        )


def get_logger(name: str = "scraper") -> ScraperLogger:
    """
    Get configured logger instance.

    Args:
        name: Logger name

    Returns:
        Configured ScraperLogger instance
    """
    config.ensure_directories()
    log_file = config.get_log_file_path()
    return ScraperLogger(name=name, log_file=log_file)
