"""
Unit tests for HTTP client module.
Tests rate limiting, retry logic, and robots.txt compliance.
"""

import time
from unittest.mock import Mock, patch, MagicMock

import pytest
import requests
from requests.exceptions import RequestException, HTTPError, Timeout

from src.utils.http_client import RateLimitedHTTPClient, create_http_client
from src.config import config


class TestRateLimitedHTTPClient:
    """Test HTTP client with rate limiting."""

    @pytest.fixture
    def client(self):
        """Create HTTP client instance."""
        with patch('src.utils.http_client.RobotFileParser'):
            client = RateLimitedHTTPClient()
            client.robot_parser = None
            yield client
            client.close()

    def test_initialization(self, client):
        """Test client initialization."""
        assert client.session is not None
        assert client.last_request_time == 0.0
        assert client.request_count == 0

    def test_create_session(self, client):
        """Test session creation with retry configuration."""
        session = client._create_session()

        assert isinstance(session, requests.Session)
        assert session.adapters['http://'] is not None
        assert session.adapters['https://'] is not None

    @patch('src.utils.http_client.RobotFileParser')
    def test_load_robots_txt_success(self, mock_parser_class):
        """Test successful robots.txt loading."""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        client = RateLimitedHTTPClient()

        assert client.robot_parser == mock_parser
        mock_parser.set_url.assert_called_once()
        mock_parser.read.assert_called_once()

    @patch('src.utils.http_client.RobotFileParser')
    def test_load_robots_txt_failure(self, mock_parser_class):
        """Test robots.txt loading failure."""
        mock_parser_class.side_effect = Exception("Network error")

        client = RateLimitedHTTPClient()

        assert client.robot_parser is None

    def test_can_fetch_no_robot_parser(self, client):
        """Test URL fetching allowed when no robot parser."""
        client.robot_parser = None

        assert client._can_fetch('https://example.com') is True

    def test_can_fetch_with_robot_parser(self, client):
        """Test URL fetching with robot parser."""
        client.robot_parser = Mock()
        client.robot_parser.can_fetch.return_value = True

        assert client._can_fetch('https://example.com') is True
        client.robot_parser.can_fetch.assert_called_once()

    def test_can_fetch_disallowed(self, client):
        """Test URL fetching when disallowed by robots.txt."""
        client.robot_parser = Mock()
        client.robot_parser.can_fetch.return_value = False

        assert client._can_fetch('https://example.com/admin') is False

    def test_get_user_agent(self, client):
        """Test user agent selection."""
        user_agent = client._get_user_agent()

        assert isinstance(user_agent, str)
        assert len(user_agent) > 0

    def test_get_user_agent_from_config(self, client, test_config):
        """Test user agent from config."""
        test_config.user_agents = ['TestAgent/1.0']

        user_agent = client._get_user_agent()

        assert user_agent == 'TestAgent/1.0'

    def test_get_user_agent_empty_config(self, client, test_config):
        """Test user agent with empty config."""
        test_config.user_agents = []

        user_agent = client._get_user_agent()

        assert 'RecipeScraper' in user_agent

    def test_enforce_rate_limit(self, client, test_config):
        """Test rate limiting enforcement."""
        test_config.scraper_delay_seconds = 0.2

        start_time = time.time()
        client.last_request_time = start_time
        client._enforce_rate_limit()
        elapsed = time.time() - start_time

        assert elapsed >= 0.2

    def test_enforce_rate_limit_no_delay_needed(self, client, test_config):
        """Test rate limiting when no delay needed."""
        test_config.scraper_delay_seconds = 0.1

        client.last_request_time = time.time() - 1.0

        start_time = time.time()
        client._enforce_rate_limit()
        elapsed = time.time() - start_time

        assert elapsed < 0.05

    def test_get_success(self, client):
        """Test successful GET request."""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'test content'
            mock_get.return_value = mock_response

            response = client.get('https://example.com')

            assert response == mock_response
            assert client.request_count == 1
            mock_get.assert_called_once()

    def test_get_with_custom_headers(self, client):
        """Test GET request with custom headers."""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'test content'
            mock_get.return_value = mock_response

            custom_headers = {'X-Custom': 'value'}
            client.get('https://example.com', headers=custom_headers)

            call_args = mock_get.call_args
            assert 'X-Custom' in call_args[1]['headers']
            assert 'User-Agent' in call_args[1]['headers']

    def test_get_with_timeout(self, client, test_config):
        """Test GET request with timeout."""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'test content'
            mock_get.return_value = mock_response

            client.get('https://example.com', timeout=10)

            call_args = mock_get.call_args
            assert call_args[1]['timeout'] == 10

    def test_get_raises_on_http_error(self, client):
        """Test GET request raises on HTTP error."""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = HTTPError()
            mock_get.return_value = mock_response

            with pytest.raises(HTTPError):
                client.get('https://example.com')

    def test_get_disallowed_by_robots(self, client):
        """Test GET request blocked by robots.txt."""
        client.robot_parser = Mock()
        client.robot_parser.can_fetch.return_value = False

        with pytest.raises(ValueError, match='disallowed by robots.txt'):
            client.get('https://example.com/admin')

    def test_get_with_retry_success_first_attempt(self, client):
        """Test get_with_retry succeeds on first attempt."""
        with patch.object(client, 'get') as mock_get:
            mock_response = Mock()
            mock_get.return_value = mock_response

            response = client.get_with_retry('https://example.com')

            assert response == mock_response
            mock_get.assert_called_once()

    def test_get_with_retry_success_after_failures(self, client):
        """Test get_with_retry succeeds after failures."""
        with patch.object(client, 'get') as mock_get:
            mock_response = Mock()
            mock_get.side_effect = [
                RequestException('Error 1'),
                RequestException('Error 2'),
                mock_response
            ]

            response = client.get_with_retry('https://example.com', max_attempts=3)

            assert response == mock_response
            assert mock_get.call_count == 3

    def test_get_with_retry_all_attempts_fail(self, client):
        """Test get_with_retry returns None when all attempts fail."""
        with patch.object(client, 'get') as mock_get:
            mock_get.side_effect = RequestException('Error')

            response = client.get_with_retry('https://example.com', max_attempts=2)

            assert response is None
            assert mock_get.call_count == 2

    def test_close(self, client):
        """Test client cleanup."""
        with patch.object(client.session, 'close') as mock_close:
            client.close()

            mock_close.assert_called_once()

    def test_context_manager(self):
        """Test client as context manager."""
        with patch('src.utils.http_client.RobotFileParser'):
            with RateLimitedHTTPClient() as client:
                assert client is not None
                assert client.session is not None


def test_create_http_client():
    """Test factory function creates client."""
    with patch('src.utils.http_client.RobotFileParser'):
        client = create_http_client()

        assert isinstance(client, RateLimitedHTTPClient)
        client.close()
