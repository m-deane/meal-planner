"""
Unit tests for recipe discoverer module.
Tests URL discovery from sitemaps and category pages.
"""

from unittest.mock import Mock, patch

import pytest

from src.scrapers.recipe_discoverer import RecipeDiscoverer, create_recipe_discoverer


class TestRecipeDiscoverer:
    """Test RecipeDiscoverer class."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def discoverer(self, http_client):
        """Create recipe discoverer instance."""
        return RecipeDiscoverer(http_client)

    def test_initialization(self, discoverer, http_client):
        """Test discoverer initialization."""
        assert discoverer.http_client == http_client
        assert isinstance(discoverer.discovered_urls, set)
        assert len(discoverer.discovered_urls) == 0

    def test_is_recipe_url_valid(self, discoverer):
        """Test recipe URL validation."""
        valid_urls = [
            'https://www.gousto.co.uk/cookbook/recipes/chicken-tikka',
            'https://www.gousto.co.uk/cookbook/chicken/chicken-curry',
            'https://www.gousto.co.uk/cookbook/beef/beef-stir-fry'
        ]

        for url in valid_urls:
            assert discoverer._is_recipe_url(url) is True

    def test_is_recipe_url_invalid(self, discoverer):
        """Test recipe URL validation for invalid URLs."""
        invalid_urls = [
            'https://www.gousto.co.uk/',
            'https://www.gousto.co.uk/cookbook/categories/italian',
            'https://www.gousto.co.uk/cookbook/category/indian',
            'https://www.gousto.co.uk/cookbook/tags/quick',
            'https://www.gousto.co.uk/about'
        ]

        for url in invalid_urls:
            assert discoverer._is_recipe_url(url) is False

    def test_discover_from_sitemap(self, discoverer, http_client, sample_sitemap_xml):
        """Test discovering URLs from sitemap."""
        mock_response = Mock()
        mock_response.content = sample_sitemap_xml.encode('utf-8')
        http_client.get.return_value = mock_response

        urls = discoverer.discover_from_sitemap()

        assert len(urls) == 3
        assert 'https://www.gousto.co.uk/cookbook/recipes/chicken-pasta' in urls
        assert 'https://www.gousto.co.uk/cookbook/recipes/beef-stir-fry' in urls
        assert 'https://www.gousto.co.uk/cookbook/recipes/vegan-curry' in urls

    def test_discover_from_sitemap_filters_non_recipes(self, discoverer, http_client, sample_sitemap_xml):
        """Test sitemap discovery filters out non-recipe URLs."""
        mock_response = Mock()
        mock_response.content = sample_sitemap_xml.encode('utf-8')
        http_client.get.return_value = mock_response

        urls = discoverer.discover_from_sitemap()

        assert 'https://www.gousto.co.uk/cookbook/categories/vegetarian' not in urls

    def test_discover_from_sitemap_error(self, discoverer, http_client):
        """Test sitemap discovery handles errors."""
        http_client.get.side_effect = Exception('Network error')

        with pytest.raises(Exception):
            discoverer.discover_from_sitemap()

    def test_discover_from_sitemap_index(self, discoverer, http_client, sample_sitemap_index_xml, sample_sitemap_xml):
        """Test discovering URLs from sitemap index."""
        mock_index_response = Mock()
        mock_index_response.content = sample_sitemap_index_xml.encode('utf-8')

        mock_sub_response = Mock()
        mock_sub_response.content = sample_sitemap_xml.encode('utf-8')

        http_client.get.side_effect = [mock_index_response, mock_sub_response, mock_sub_response]

        urls = discoverer.discover_from_sitemap_index()

        assert len(urls) > 0
        assert http_client.get.call_count >= 2

    def test_discover_from_sitemap_index_not_index(self, discoverer, http_client, sample_sitemap_xml):
        """Test sitemap index when sitemap is not an index."""
        mock_response = Mock()
        mock_response.content = sample_sitemap_xml.encode('utf-8')
        http_client.get.return_value = mock_response

        urls = discoverer.discover_from_sitemap_index()

        assert len(urls) > 0

    def test_discover_from_categories(self, discoverer, http_client, sample_category_html):
        """Test discovering URLs from category pages."""
        mock_response = Mock()
        mock_response.text = sample_category_html
        http_client.get.return_value = mock_response

        category_urls = ['https://www.gousto.co.uk/cookbook/chicken']
        urls = discoverer.discover_from_categories(category_urls)

        assert len(urls) > 0
        http_client.get.assert_called()

    def test_discover_from_categories_error(self, discoverer, http_client):
        """Test category discovery handles errors gracefully."""
        http_client.get.side_effect = Exception('Network error')

        category_urls = ['https://www.gousto.co.uk/cookbook/chicken']
        urls = discoverer.discover_from_categories(category_urls)

        assert len(urls) == 0

    def test_extract_recipe_urls_from_html(self, discoverer, sample_category_html):
        """Test extracting recipe URLs from HTML."""
        base_url = 'https://www.gousto.co.uk/cookbook/chicken'

        urls = discoverer._extract_recipe_urls_from_html(sample_category_html, base_url)

        assert len(urls) > 0
        assert all('cookbook' in url for url in urls)

    def test_extract_recipe_urls_from_html_resolves_relative(self, discoverer):
        """Test HTML extraction resolves relative URLs."""
        html = '<a href="/cookbook/recipes/test">Recipe</a>'
        base_url = 'https://www.gousto.co.uk'

        urls = discoverer._extract_recipe_urls_from_html(html, base_url)

        assert len(urls) > 0
        assert urls[0].startswith('https://')

    def test_get_category_urls(self, discoverer):
        """Test getting list of category URLs."""
        urls = discoverer.get_category_urls()

        assert len(urls) > 0
        assert all('cookbook' in url for url in urls)
        assert any('chicken' in url for url in urls)
        assert any('vegetarian' in url for url in urls)

    def test_discover_all_sitemap_only(self, discoverer, http_client, sample_sitemap_xml):
        """Test discovering all URLs using sitemap only."""
        mock_response = Mock()
        mock_response.content = sample_sitemap_xml.encode('utf-8')
        http_client.get.return_value = mock_response

        urls = discoverer.discover_all(use_sitemap=True, use_categories=False)

        assert len(urls) > 0
        assert len(discoverer.discovered_urls) > 0

    def test_discover_all_categories_only(self, discoverer, http_client, sample_category_html):
        """Test discovering all URLs using categories only."""
        mock_response = Mock()
        mock_response.text = sample_category_html
        http_client.get.return_value = mock_response

        urls = discoverer.discover_all(use_sitemap=False, use_categories=True)

        assert len(urls) > 0

    def test_discover_all_both_methods(self, discoverer, http_client, sample_sitemap_xml, sample_category_html):
        """Test discovering URLs using both methods."""
        mock_sitemap = Mock()
        mock_sitemap.content = sample_sitemap_xml.encode('utf-8')

        mock_category = Mock()
        mock_category.text = sample_category_html

        http_client.get.side_effect = [mock_sitemap, mock_category, mock_category, mock_category]

        urls = discoverer.discover_all(use_sitemap=True, use_categories=True)

        assert len(urls) > 0

    def test_discover_all_deduplicates(self, discoverer, http_client, sample_sitemap_xml):
        """Test discovering all URLs deduplicates results."""
        mock_response = Mock()
        mock_response.content = sample_sitemap_xml.encode('utf-8')
        mock_response.text = '<a href="/cookbook/recipes/chicken-pasta">Recipe</a>'

        http_client.get.return_value = mock_response

        urls = discoverer.discover_all(use_sitemap=True, use_categories=True)

        assert len(urls) == len(set(urls))

    def test_discover_all_handles_errors(self, discoverer, http_client):
        """Test discover all handles errors gracefully."""
        http_client.get.side_effect = Exception('Network error')

        urls = discoverer.discover_all(use_sitemap=True, use_categories=True)

        assert isinstance(urls, list)


def test_create_recipe_discoverer():
    """Test factory function creates discoverer."""
    http_client = Mock()
    discoverer = create_recipe_discoverer(http_client)

    assert isinstance(discoverer, RecipeDiscoverer)
    assert discoverer.http_client == http_client
