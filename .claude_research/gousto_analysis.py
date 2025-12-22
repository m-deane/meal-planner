"""
Gousto Recipe Website Analysis Script
Extracts JSON-LD schema.org data from a sample Gousto recipe page
"""

import json
import re
from playwright.sync_api import sync_playwright

def analyze_gousto_recipe(url):
    """
    Analyze a Gousto recipe page to extract:
    1. JSON-LD schema.org Recipe microdata
    2. Page structure
    3. Navigation/pagination elements
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Fetching: {url}")
        page.goto(url, wait_until='networkidle')

        # Extract all JSON-LD scripts
        json_ld_scripts = page.query_selector_all('script[type="application/ld+json"]')

        print(f"\nFound {len(json_ld_scripts)} JSON-LD script tags\n")

        json_ld_data = []
        for idx, script in enumerate(json_ld_scripts):
            content = script.inner_text()
            try:
                data = json.loads(content)
                json_ld_data.append(data)
                print(f"=== JSON-LD Block {idx + 1} ===")
                print(json.dumps(data, indent=2))
                print("\n")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON-LD block {idx + 1}: {e}")

        # Look for recipe-specific schema
        recipe_schema = None
        for data in json_ld_data:
            if isinstance(data, dict):
                if data.get('@type') == 'Recipe':
                    recipe_schema = data
                    break
                # Handle graph structure
                elif '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'Recipe':
                            recipe_schema = item
                            break

        if recipe_schema:
            print("\n=== RECIPE SCHEMA FOUND ===")
            print(json.dumps(recipe_schema, indent=2))

            # Document available fields
            print("\n=== AVAILABLE FIELDS ===")
            for key in sorted(recipe_schema.keys()):
                print(f"  - {key}")
        else:
            print("\n!!! NO RECIPE SCHEMA FOUND !!!")

        # Check page title and meta
        title = page.title()
        print(f"\n=== PAGE METADATA ===")
        print(f"Title: {title}")

        # Look for pagination or recipe list elements
        print(f"\n=== PAGE STRUCTURE ANALYSIS ===")

        # Check for recipe cards/links
        recipe_links = page.query_selector_all('a[href*="/cookbook/"]')
        print(f"Recipe links found: {len(recipe_links)}")

        # Sample a few URLs
        if recipe_links:
            print("Sample recipe URLs:")
            for i, link in enumerate(recipe_links[:5]):
                href = link.get_attribute('href')
                print(f"  {i+1}. {href}")

        # Check for pagination
        pagination_selectors = [
            'nav[aria-label*="pagination"]',
            '.pagination',
            'button[aria-label*="next"]',
            'a[aria-label*="next page"]',
            '[data-testid*="pagination"]'
        ]

        for selector in pagination_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"\nPagination found with selector: {selector} ({len(elements)} elements)")

        # Check for infinite scroll indicators
        scroll_indicators = page.query_selector_all('[data-testid*="load"], [class*="load-more"]')
        if scroll_indicators:
            print(f"\nInfinite scroll indicators: {len(scroll_indicators)}")

        # Get the full HTML to analyze structure
        html = page.content()

        # Check if content is server-rendered or client-rendered
        initial_html_length = len(html)
        print(f"\nHTML content length: {initial_html_length} characters")

        # Look for Next.js or React indicators
        if '__NEXT_DATA__' in html:
            print("Detected: Next.js application")
            # Extract Next.js data
            next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>'
            match = re.search(next_data_pattern, html, re.DOTALL)
            if match:
                try:
                    next_data = json.loads(match.group(1))
                    print("\n=== NEXT.JS DATA STRUCTURE ===")
                    print(json.dumps({k: type(v).__name__ for k, v in next_data.items()}, indent=2))
                except:
                    pass

        if 'react' in html.lower() or '_reactroot' in html.lower():
            print("Detected: React application")

        browser.close()

        return {
            'json_ld_data': json_ld_data,
            'recipe_schema': recipe_schema,
            'title': title,
            'recipe_links_count': len(recipe_links)
        }

def analyze_recipe_list_page(url):
    """
    Analyze the recipe list page to understand navigation and pagination
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"\n{'='*80}")
        print(f"ANALYZING RECIPE LIST PAGE")
        print(f"{'='*80}\n")
        print(f"URL: {url}\n")

        page.goto(url, wait_until='networkidle')

        # Count recipe cards
        recipe_selectors = [
            'a[href*="/cookbook/recipes/"]',
            'a[href*="/cookbook/"][href*="recipes"]',
            '[data-testid*="recipe"]',
            '.recipe-card',
            'article'
        ]

        print("=== RECIPE DISCOVERY ===")
        all_recipe_urls = set()

        for selector in recipe_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"\n{selector}: {len(elements)} elements found")
                for elem in elements[:3]:
                    href = elem.get_attribute('href')
                    if href and '/cookbook/' in href:
                        all_recipe_urls.add(href)
                        print(f"  Sample: {href}")

        print(f"\nUnique recipe URLs discovered: {len(all_recipe_urls)}")

        # Check for total count display
        text_content = page.inner_text('body')
        count_patterns = [
            r'(\d+)\s+recipes',
            r'(\d+)\s+results',
            r'Showing\s+\d+\s+of\s+(\d+)',
            r'(\d+)\s+of\s+(\d+)',
        ]

        print("\n=== TOTAL COUNT DETECTION ===")
        for pattern in count_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                print(f"Pattern '{pattern}' found: {matches[:3]}")

        # Check for API calls in network
        print("\n=== NETWORK ANALYSIS ===")
        print("Monitoring network requests for API endpoints...")

        api_requests = []

        def handle_request(request):
            url = request.url
            if any(keyword in url.lower() for keyword in ['api', 'graphql', 'recipe', 'query']):
                api_requests.append({
                    'url': url,
                    'method': request.method,
                    'resource_type': request.resource_type
                })

        page.on('request', handle_request)

        # Scroll to trigger lazy loading
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(2000)

        if api_requests:
            print(f"\nFound {len(api_requests)} API requests:")
            for req in api_requests[:10]:
                print(f"  {req['method']} {req['url'][:100]}...")
        else:
            print("No obvious API requests detected")

        browser.close()

        return {
            'total_urls_found': len(all_recipe_urls),
            'sample_urls': list(all_recipe_urls)[:10],
            'api_requests': api_requests[:10]
        }

if __name__ == '__main__':
    # Analyze a specific recipe page
    recipe_url = 'https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice'
    recipe_data = analyze_gousto_recipe(recipe_url)

    # Analyze the recipe list page
    list_url = 'https://www.gousto.co.uk/cookbook/recipes'
    list_data = analyze_recipe_list_page(list_url)

    # Save results
    results = {
        'recipe_page_analysis': recipe_data,
        'list_page_analysis': list_data
    }

    with open('/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/.claude_research/gousto_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n" + "="*80)
    print("Analysis complete. Results saved to gousto_analysis_results.json")
    print("="*80)
