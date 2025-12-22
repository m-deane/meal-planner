"""
HTTP client with rate limiting, retries, and user-agent rotation.
Handles robots.txt compliance and session management.
"""

import random
import time
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

from src.config import config
from src.utils.logger import get_logger

logger = get_logger("http_client")


class RateLimitedHTTPClient:
    """HTTP client with built-in rate limiting and retry logic."""

    def __init__(self):
        """Initialize HTTP client with session and retry configuration."""
        self.session = self._create_session()
        self.robot_parser = self._load_robots_txt()
        self.last_request_time = 0.0
        self.request_count = 0

    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry configuration.

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=config.scraper_max_retries,
            backoff_factor=config.scraper_retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _load_robots_txt(self) -> Optional[RobotFileParser]:
        """
        Load and parse robots.txt file.

        Returns:
            RobotFileParser instance or None if unavailable
        """
        try:
            parser = RobotFileParser()
            parser.set_url(config.gousto_robots_url)
            parser.read()
            logger.info(f"Loaded robots.txt from {config.gousto_robots_url}")
            return parser
        except Exception as e:
            logger.warning(
                f"Failed to load robots.txt: {e}. Proceeding with caution."
            )
            return None

    def _can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed, False otherwise
        """
        if not self.robot_parser:
            return True

        user_agent = config.user_agents[0] if config.user_agents else "*"
        return self.robot_parser.can_fetch(user_agent, url)

    def _get_user_agent(self) -> str:
        """
        Get random user agent from configured list.

        Returns:
            User agent string
        """
        if not config.user_agents:
            return "Mozilla/5.0 (compatible; RecipeScraper/1.0)"
        return random.choice(config.user_agents)

    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < config.scraper_delay_seconds:
            sleep_time = config.scraper_delay_seconds - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

    def get(
        self,
        url: str,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform GET request with rate limiting and retries.

        Args:
            url: URL to fetch
            headers: Optional custom headers
            timeout: Request timeout in seconds
            **kwargs: Additional arguments for requests.get

        Returns:
            Response object

        Raises:
            RequestException: If request fails after all retries
            ValueError: If URL is disallowed by robots.txt
        """
        if not self._can_fetch(url):
            raise ValueError(f"URL disallowed by robots.txt: {url}")

        self._enforce_rate_limit()

        if headers is None:
            headers = {}

        headers["User-Agent"] = self._get_user_agent()

        timeout = timeout or config.scraper_timeout_seconds

        try:
            logger.debug(f"GET {url}")
            response = self.session.get(
                url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()

            self.last_request_time = time.time()
            self.request_count += 1

            logger.debug(
                f"Response: {response.status_code} | "
                f"Size: {len(response.content)} bytes"
            )

            return response

        except RequestException as e:
            logger.error(f"Request failed: {url} | Error: {e}")
            raise

    def get_with_retry(
        self,
        url: str,
        max_attempts: Optional[int] = None,
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Perform GET request with manual retry logic.

        Args:
            url: URL to fetch
            max_attempts: Maximum retry attempts (uses config if None)
            **kwargs: Additional arguments for get()

        Returns:
            Response object or None if all retries failed
        """
        max_attempts = max_attempts or config.scraper_max_retries
        last_exception = None

        for attempt in range(1, max_attempts + 1):
            try:
                return self.get(url, **kwargs)

            except RequestException as e:
                last_exception = e
                if attempt < max_attempts:
                    backoff_time = config.scraper_retry_backoff ** attempt
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {url}. "
                        f"Retrying in {backoff_time:.1f}s"
                    )
                    time.sleep(backoff_time)
                else:
                    logger.error(
                        f"All {max_attempts} attempts failed for {url}: {e}"
                    )

        return None

    def close(self) -> None:
        """Close HTTP session."""
        self.session.close()
        logger.info(
            f"HTTP client closed. Total requests: {self.request_count}"
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_http_client() -> RateLimitedHTTPClient:
    """
    Factory function to create HTTP client.

    Returns:
        Configured RateLimitedHTTPClient instance
    """
    return RateLimitedHTTPClient()
