"""
Unit tests for CLI module.
Tests command-line interface commands.
"""

from unittest.mock import patch, Mock

import pytest
from click.testing import CliRunner

from src.cli import cli, discover, export, stats, clear_checkpoint


class TestCLI:
    """Test CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @patch('src.cli.create_gousto_scraper')
    @patch('src.cli.get_db_session')
    def test_discover_command(self, mock_get_session, mock_create_scraper, runner):
        """Test discover command."""
        mock_session = Mock()
        mock_get_session.return_value = iter([mock_session])

        mock_scraper = Mock()
        mock_scraper.discover_recipes.return_value = [
            'https://example.com/recipe1',
            'https://example.com/recipe2'
        ]
        mock_create_scraper.return_value = mock_scraper

        result = runner.invoke(discover)

        assert result.exit_code == 0
        assert 'Discovered 2 recipe URLs' in result.output


    @patch('src.cli.get_db_session')
    @patch('src.cli._export_json')
    def test_export_command_json(self, mock_export_json, mock_get_session, runner, tmp_path):
        """Test export command with JSON format."""
        mock_session = Mock()
        # Mock for path without limit
        mock_session.query.return_value.filter.return_value.all.return_value = []
        # Mock for path with limit
        mock_session.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        mock_get_session.return_value = iter([mock_session])

        output_file = tmp_path / 'recipes.json'

        result = runner.invoke(export, [
            '--format', 'json',
            '--output', str(output_file)
        ])

        assert result.exit_code == 0
        mock_export_json.assert_called_once()

    @patch('src.cli.get_db_session')
    @patch('src.cli._export_csv')
    def test_export_command_csv(self, mock_export_csv, mock_get_session, runner, tmp_path):
        """Test export command with CSV format."""
        mock_session = Mock()
        # Mock for path without limit
        mock_session.query.return_value.filter.return_value.all.return_value = []
        # Mock for path with limit
        mock_session.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        mock_get_session.return_value = iter([mock_session])

        output_file = tmp_path / 'recipes.csv'

        result = runner.invoke(export, [
            '--format', 'csv',
            '--output', str(output_file)
        ])

        assert result.exit_code == 0
        mock_export_csv.assert_called_once()

    @patch('src.cli.get_db_session')
    def test_stats_command(self, mock_get_session, runner):
        """Test stats command."""
        mock_session = Mock()
        mock_session.query.return_value.scalar.return_value = 10
        mock_session.query.return_value.filter.return_value.scalar.return_value = 8
        mock_get_session.return_value = iter([mock_session])

        result = runner.invoke(stats)

        assert result.exit_code == 0
        assert 'Database Statistics' in result.output

    @patch('src.cli.get_db_session')
    def test_stats_command_detailed(self, mock_get_session, runner):
        """Test stats command with detailed flag."""
        mock_session = Mock()
        # Basic counts
        mock_session.query.return_value.scalar.return_value = 10
        mock_session.query.return_value.filter.return_value.scalar.return_value = 8
        # Categories breakdown
        mock_session.query.return_value.join.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            ('Italian', 5),
            ('Indian', 3)
        ]
        # Nutrition join - returns integer for recipes_with_nutrition
        mock_session.query.return_value.join.return_value.scalar.return_value = 5
        mock_get_session.return_value = iter([mock_session])

        result = runner.invoke(stats, ['--detailed'])

        assert result.exit_code == 0
        assert 'Category Breakdown' in result.output


    @patch('src.cli.create_checkpoint_manager')
    def test_clear_checkpoint_command(self, mock_create_checkpoint, runner):
        """Test clear_checkpoint command."""
        mock_manager = Mock()
        mock_create_checkpoint.return_value = mock_manager

        result = runner.invoke(clear_checkpoint)

        assert result.exit_code == 0
        mock_manager.clear.assert_called_once()
