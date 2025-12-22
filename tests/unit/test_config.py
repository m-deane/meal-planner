"""
Unit tests for configuration module.
Tests environment variable loading and validation.
"""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config import Config


class TestConfig:
    """Test Config class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = Config()

        assert config.database_url == 'sqlite:///recipes.db'
        assert config.scraper_delay_seconds == 3.0
        assert config.scraper_max_retries == 3
        assert config.log_level == 'INFO'
        assert config.checkpoint_enabled is True

    def test_database_url_validation_sqlite(self):
        """Test valid SQLite database URL."""
        config = Config(database_url='sqlite:///test.db')

        assert config.database_url == 'sqlite:///test.db'
        assert config.is_sqlite is True
        assert config.is_postgresql is False

    def test_database_url_validation_postgresql(self):
        """Test valid PostgreSQL database URL."""
        config = Config(database_url='postgresql://user:pass@localhost/db')

        assert config.is_postgresql is True
        assert config.is_sqlite is False

    def test_database_url_validation_invalid(self):
        """Test invalid database URL raises error."""
        with pytest.raises(ValidationError):
            Config(database_url='invalid://url')

    def test_log_level_validation_valid(self):
        """Test valid log level."""
        config = Config(log_level='DEBUG')

        assert config.log_level == 'DEBUG'

    def test_log_level_validation_case_insensitive(self):
        """Test log level is case insensitive."""
        config = Config(log_level='debug')

        assert config.log_level == 'DEBUG'

    def test_log_level_validation_invalid(self):
        """Test invalid log level raises error."""
        with pytest.raises(ValidationError):
            Config(log_level='INVALID')

    def test_scraper_delay_validation_valid(self):
        """Test valid scraper delay."""
        config = Config(scraper_delay_seconds=2.5)

        assert config.scraper_delay_seconds == 2.5

    def test_scraper_delay_validation_min(self):
        """Test scraper delay minimum validation."""
        with pytest.raises(ValidationError):
            Config(scraper_delay_seconds=0.1)

    def test_scraper_delay_validation_max(self):
        """Test scraper delay maximum validation."""
        with pytest.raises(ValidationError):
            Config(scraper_delay_seconds=100.0)

    def test_scraper_max_retries_validation(self):
        """Test max retries validation."""
        config = Config(scraper_max_retries=5)

        assert config.scraper_max_retries == 5

    def test_database_pool_size_validation(self):
        """Test database pool size validation."""
        config = Config(database_pool_size=10)

        assert config.database_pool_size == 10

    def test_get_log_file_path(self):
        """Test getting log file path."""
        config = Config(log_file='logs/test.log')

        path = config.get_log_file_path()

        assert isinstance(path, Path)
        assert path.name == 'test.log'

    def test_get_log_file_path_none(self):
        """Test getting log file path when None."""
        config = Config(log_file=None)

        path = config.get_log_file_path()

        assert path is None

    def test_ensure_directories(self, tmp_path):
        """Test ensure directories creates paths."""
        log_file = tmp_path / 'logs' / 'test.log'
        checkpoint_file = tmp_path / 'checkpoints' / 'test.json'

        config = Config(
            log_file=str(log_file),
            checkpoint_file=str(checkpoint_file)
        )

        config.ensure_directories()

        assert log_file.parent.exists()
        assert checkpoint_file.parent.exists()

    def test_user_agents_list(self):
        """Test user agents configuration."""
        config = Config()

        assert isinstance(config.user_agents, list)
        assert len(config.user_agents) > 0

    def test_gousto_urls(self):
        """Test Gousto URL configuration."""
        config = Config()

        assert 'gousto.co.uk' in config.gousto_base_url
        assert 'sitemap' in config.gousto_sitemap_url
        assert 'robots.txt' in config.gousto_robots_url

    def test_validation_settings(self):
        """Test validation configuration."""
        config = Config(
            validation_strict=True,
            validation_require_ingredients=True,
            validation_require_instructions=True
        )

        assert config.validation_strict is True
        assert config.validation_require_ingredients is True
        assert config.validation_require_instructions is True

    def test_calories_validation_range(self):
        """Test calories validation range."""
        config = Config(
            validation_min_calories=50,
            validation_max_calories=3000
        )

        assert config.validation_min_calories == 50
        assert config.validation_max_calories == 3000

    def test_export_settings(self):
        """Test export configuration."""
        config = Config(
            export_include_inactive=True,
            export_pretty_json=False
        )

        assert config.export_include_inactive is True
        assert config.export_pretty_json is False

    def test_checkpoint_settings(self):
        """Test checkpoint configuration."""
        config = Config(
            checkpoint_enabled=True,
            checkpoint_interval=20,
            checkpoint_file='custom_checkpoint.json'
        )

        assert config.checkpoint_enabled is True
        assert config.checkpoint_interval == 20
        assert config.checkpoint_file == 'custom_checkpoint.json'
