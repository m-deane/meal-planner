"""
Recipe URL discovery from sitemaps and category pages.
Handles URL extraction from Gousto's sitemap.xml and category crawling.
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Set
from urllib.parse import urljoin, urlparse

from src.config import config
from src.utils.http_client import RateLimitedHTTPClient
from src.utils.logger import get_logger

logger = get_logger("recipe_discoverer")


class RecipeDiscoverer:
    """Discovers recipe URLs from sitemap and category pages."""

    def __init__(self, http_client: RateLimitedHTTPClient):
        """
        Initialize recipe discoverer.

        Args:
            http_client: HTTP client for making requests
        """
        self.http_client = http_client
        self.discovered_urls: Set[str] = set()

    def discover_from_sitemap(self) -> List[str]:
        """
        Discover recipe URLs from sitemap.xml.

        Returns:
            List of recipe URLs

        Raises:
            Exception: If sitemap cannot be fetched or parsed
        """
        logger.info(f"Fetching sitemap: {config.gousto_sitemap_url}")

        try:
            response = self.http_client.get(config.gousto_sitemap_url)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            urls = []
            for url_element in root.findall('.//ns:url', namespace):
                loc = url_element.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    url = loc.text.strip()
                    if self._is_recipe_url(url):
                        urls.append(url)
                        self.discovered_urls.add(url)

            logger.info(f"Discovered {len(urls)} recipe URLs from sitemap")
            return urls

        except ET.ParseError as e:
            logger.error(f"Failed to parse sitemap XML: {e}", exc_info=True)
            raise

        except Exception as e:
            logger.error(f"Failed to fetch sitemap: {e}", exc_info=True)
            raise

    def discover_from_sitemap_index(self) -> List[str]:
        """
        Discover recipe URLs from sitemap index (if sitemap.xml is an index).

        Returns:
            List of recipe URLs from all sub-sitemaps
        """
        logger.info("Checking if sitemap is an index")

        try:
            response = self.http_client.get(config.gousto_sitemap_url)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            sitemap_urls = []
            for sitemap in root.findall('.//ns:sitemap', namespace):
                loc = sitemap.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    sitemap_urls.append(loc.text.strip())

            if not sitemap_urls:
                logger.debug("Sitemap is not an index, treating as regular sitemap")
                return self.discover_from_sitemap()

            logger.info(f"Found {len(sitemap_urls)} sub-sitemaps")

            all_urls = []
            for sitemap_url in sitemap_urls:
                logger.info(f"Processing sub-sitemap: {sitemap_url}")
                try:
                    response = self.http_client.get(sitemap_url)
                    response.raise_for_status()

                    sub_root = ET.fromstring(response.content)

                    for url_element in sub_root.findall('.//ns:url', namespace):
                        loc = url_element.find('ns:loc', namespace)
                        if loc is not None and loc.text:
                            url = loc.text.strip()
                            if self._is_recipe_url(url):
                                all_urls.append(url)
                                self.discovered_urls.add(url)

                except Exception as e:
                    logger.error(f"Failed to process sub-sitemap {sitemap_url}: {e}")

            logger.info(f"Discovered {len(all_urls)} recipe URLs from sitemap index")
            return all_urls

        except Exception as e:
            logger.error(f"Failed to process sitemap index: {e}", exc_info=True)
            return []

    def discover_from_categories(self, category_urls: List[str]) -> List[str]:
        """
        Discover recipe URLs by crawling category pages.

        Args:
            category_urls: List of category page URLs to crawl

        Returns:
            List of discovered recipe URLs
        """
        logger.info(f"Discovering recipes from {len(category_urls)} categories")

        all_urls = []

        for category_url in category_urls:
            try:
                logger.info(f"Crawling category: {category_url}")
                response = self.http_client.get(category_url)
                response.raise_for_status()

                urls = self._extract_recipe_urls_from_html(
                    response.text,
                    base_url=category_url
                )

                new_urls = [url for url in urls if url not in self.discovered_urls]
                all_urls.extend(new_urls)
                self.discovered_urls.update(new_urls)

                logger.info(f"Found {len(new_urls)} new recipe URLs in {category_url}")

            except Exception as e:
                logger.error(f"Failed to crawl category {category_url}: {e}")

        logger.info(f"Discovered {len(all_urls)} recipe URLs from categories")
        return all_urls

    def _is_recipe_url(self, url: str) -> bool:
        """
        Check if URL is a recipe page.

        Args:
            url: URL to check

        Returns:
            True if URL is a recipe page
        """
        url_lower = url.lower()

        recipe_patterns = [
            r'/cookbook/[^/]+/[^/]+$',
            r'/cookbook/recipes/[^/]+$',
        ]

        for pattern in recipe_patterns:
            if re.search(pattern, url_lower):
                exclude_patterns = [
                    r'/category/',
                    r'/categories/',
                    r'/tag/',
                    r'/tags/',
                    r'/page/',
                ]

                for exclude in exclude_patterns:
                    if exclude in url_lower:
                        return False

                return True

        return False

    def _extract_recipe_urls_from_html(
        self,
        html: str,
        base_url: str
    ) -> List[str]:
        """
        Extract recipe URLs from HTML content.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of recipe URLs
        """
        url_pattern = re.compile(
            r'href=["\']([^"\']*/(cookbook/[^"\']+))["\']',
            re.IGNORECASE
        )

        matches = url_pattern.findall(html)
        urls = []

        for match in matches:
            url = match[0]

            if not url.startswith('http'):
                url = urljoin(base_url, url)

            if self._is_recipe_url(url):
                urls.append(url)

        return list(set(urls))

    def get_category_urls(self) -> List[str]:
        """
        Get list of known category URLs.

        Returns:
            List of category URLs
        """
        categories = [
            'chicken-recipes',
            'beef-recipes',
            'pork-recipes',
            'fish-recipes',
            'vegetarian-recipes',
            'vegan-recipes',
            'pasta-recipes',
            'rice-recipes',
            'curry-recipes',
            'italian-recipes',
            'indian-recipes',
            'chinese-recipes',
            'mexican-recipes',
            'thai-recipes',
            'quick-recipes',
            'healthy-recipes',
            'low-calorie-recipes',
            'lighter',
        ]

        return [
            f"{config.gousto_base_url}/cookbook/{cat}"
            for cat in categories
        ]

    def discover_all(
        self,
        use_sitemap: bool = True,
        use_categories: bool = True
    ) -> List[str]:
        """
        Discover all recipe URLs using multiple methods.

        Args:
            use_sitemap: Use sitemap for discovery
            use_categories: Use category crawling for discovery

        Returns:
            List of all discovered recipe URLs
        """
        logger.info("Starting comprehensive recipe URL discovery")

        all_urls = []

        if use_sitemap:
            try:
                sitemap_urls = self.discover_from_sitemap_index()
                all_urls.extend(sitemap_urls)
                logger.info(f"Sitemap discovery: {len(sitemap_urls)} URLs")
            except Exception as e:
                logger.error(f"Sitemap discovery failed: {e}")

        if use_categories:
            try:
                category_urls = self.get_category_urls()
                category_discovered = self.discover_from_categories(category_urls)
                all_urls.extend(category_discovered)
                logger.info(f"Category discovery: {len(category_discovered)} URLs")
            except Exception as e:
                logger.error(f"Category discovery failed: {e}")

        unique_urls = list(self.discovered_urls)

        logger.info(f"Total unique recipe URLs discovered: {len(unique_urls)}")

        return unique_urls


def create_recipe_discoverer(
    http_client: RateLimitedHTTPClient
) -> RecipeDiscoverer:
    """
    Factory function to create recipe discoverer.

    Args:
        http_client: HTTP client instance

    Returns:
        RecipeDiscoverer instance
    """
    return RecipeDiscoverer(http_client)
