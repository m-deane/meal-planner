"""
Unit tests for logger module.
Tests structured logging with rotation support.
"""

import logging
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from src.utils.logger import ScraperLogger, get_logger


class TestScraperLogger:
    """Test ScraperLogger class."""

    def test_initialization_console_only(self):
        """Test logger initialization with console only."""
        logger = ScraperLogger(name='test', log_file=None, console_output=True)

        assert logger.logger.name == 'test'
        assert len(logger.logger.handlers) > 0

    def test_initialization_with_file(self, tmp_path):
        """Test logger initialization with file handler."""
        log_file = tmp_path / "test.log"

        logger = ScraperLogger(name='test', log_file=log_file, console_output=False)

        assert logger.logger.name == 'test'
        assert log_file.parent.exists()

    def test_parse_size_megabytes(self):
        """Test parsing megabytes size string."""
        result = ScraperLogger._parse_size('10 MB')

        assert result == 10 * 1024 * 1024

    def test_parse_size_kilobytes(self):
        """Test parsing kilobytes size string."""
        result = ScraperLogger._parse_size('500 KB')

        assert result == 500 * 1024

    def test_parse_size_gigabytes(self):
        """Test parsing gigabytes size string."""
        result = ScraperLogger._parse_size('1 GB')

        assert result == 1024 * 1024 * 1024

    def test_parse_size_invalid(self):
        """Test parsing invalid size string."""
        result = ScraperLogger._parse_size('invalid')

        assert result == 10 * 1024 * 1024

    def test_debug_logging(self, tmp_path):
        """Test debug level logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger.logger, 'debug') as mock_debug:
            logger.debug('Test message')
            mock_debug.assert_called_once()

    def test_info_logging(self, tmp_path):
        """Test info level logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger.logger, 'info') as mock_info:
            logger.info('Test message')
            mock_info.assert_called_once()

    def test_warning_logging(self, tmp_path):
        """Test warning level logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger.logger, 'warning') as mock_warning:
            logger.warning('Test message')
            mock_warning.assert_called_once()

    def test_error_logging(self, tmp_path):
        """Test error level logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger.logger, 'error') as mock_error:
            logger.error('Test message', exc_info=False)
            mock_error.assert_called_once()

    def test_critical_logging(self, tmp_path):
        """Test critical level logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger.logger, 'critical') as mock_critical:
            logger.critical('Test message', exc_info=False)
            mock_critical.assert_called_once()

    def test_scraping_progress(self, tmp_path):
        """Test scraping progress logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger, 'info') as mock_info:
            logger.scraping_progress(
                current=50,
                total=100,
                success=45,
                failed=5
            )

            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert '50/100' in call_args
            assert '50.0%' in call_args

    def test_recipe_scraped(self, tmp_path):
        """Test recipe scraped logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger, 'info') as mock_info:
            logger.recipe_scraped(
                recipe_name='Test Recipe',
                recipe_url='https://example.com',
                ingredients_count=5,
                instructions_count=3
            )

            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert 'Test Recipe' in call_args

    def test_recipe_error(self, tmp_path):
        """Test recipe error logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger, 'error') as mock_error:
            logger.recipe_error(
                recipe_url='https://example.com',
                error_type='NetworkError',
                error_message='Connection failed'
            )

            mock_error.assert_called_once()

    def test_validation_error(self, tmp_path):
        """Test validation error logging."""
        log_file = tmp_path / "test.log"
        logger = ScraperLogger(name='test', log_file=log_file)

        with patch.object(logger, 'warning') as mock_warning:
            logger.validation_error(
                recipe_name='Test Recipe',
                field='name',
                error_message='Name too short'
            )

            mock_warning.assert_called_once()


def test_get_logger(test_config):
    """Test get_logger factory function."""
    logger = get_logger('test_logger')

    assert isinstance(logger, ScraperLogger)
    assert logger.logger.name == 'test_logger'
