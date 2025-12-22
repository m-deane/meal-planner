# Gousto Recipe Website Research - Executive Summary

**Date:** 2025-12-20
**Researcher:** Technical Researcher Agent
**Target:** https://www.gousto.co.uk/cookbook/recipes

---

## Quick Answers

### 1. JSON-LD Schema Availability
**CONFIRMED** - Schema.org Recipe microdata present in `<script type="application/ld+json">` tags

### 2. JavaScript Rendering Required
**YES** - React-based SPA requiring Playwright/Selenium for content rendering

### 3. Recommended Approach
**Use recipe-scrapers Python library** - Already implements Gousto support with JSON-LD extraction

### 4. Recipe Discovery Challenge
**LIMITED** - No obvious pagination; requires sitemap analysis or category crawling

---

## Essential Technical Details

### Data Available (JSON-LD Fields)

```json
{
  "name": "Recipe Title",
  "description": "Recipe description",
  "image": "High-res CDN URL",
  "recipeIngredient": ["Ingredient 1", "Ingredient 2"],
  "recipeInstructions": ["Step 1", "Step 2"],
  "nutrition": {
    "calories": "565 calories",
    "carbohydrateContent": "67.12",
    "fatContent": "17.70",
    "proteinContent": "34.68"
  },
  "aggregateRating": {
    "ratingValue": 4.5,
    "reviewCount": 77163
  },
  "recipeCategory": "Indian",
  "recipeCuisine": "Indian",
  "totalTime": "PT35M",
  "recipeYield": "2 or 4 servings"
}
```

### URL Patterns

```
Primary: https://www.gousto.co.uk/cookbook/{category}/{recipe-slug}
Alternative: https://www.gousto.co.uk/cookbook/recipes/{recipe-slug}
```

### Known Data Quality Issues

1. Ingredient quantities include serving multipliers: `"Chicken breast strips (250g)"` or `"x0"` for alternatives
2. Duplicate quantities: `"1 1 tbsp cornflour"` (Gousto displays this way)
3. Instructions contain newlines and serving variations in brackets: `[2 servings] [4 servings]`

---

## Implementation Quick Start

### Option 1: Use Existing Library (Recommended)

```bash
pip install recipe-scrapers
```

```python
from recipe_scrapers import scrape_me

url = 'https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice'
scraper = scrape_me(url)
recipe_data = scraper.to_json()
print(recipe_data)
```

**Pros:** Battle-tested, maintained, handles edge cases
**Cons:** Limited to library's extraction logic

### Option 2: Custom Playwright Scraper

```python
from playwright.sync_api import sync_playwright
import json

def scrape_gousto(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')

        script = page.query_selector('script[type="application/ld+json"]')
        if script:
            data = json.loads(script.inner_text())
            browser.close()
            return data
```

**Pros:** Full control, can extract additional data
**Cons:** More maintenance, slower execution

---

## Recipe Discovery Strategy

### Priority 1: Check Sitemap
```
https://www.gousto.co.uk/sitemap.xml
```

### Priority 2: Category Crawling
- Enumerate categories from `/cookbook/recipes`
- Visit each category page
- Extract recipe links

### Priority 3: Menu API Investigation
- Monitor network traffic on `https://www.gousto.co.uk/menu`
- Look for GraphQL/REST endpoints
- Weekly rotation of ~150 recipes

---

## Critical Issues to Handle

### Issue 1: Ingredient Format Requires Parsing

```
"Cornish clotted cream (40g)"          → Parse quantity + unit
"Chicken breast strips (250g)"         → Parse quantity + unit
"Ground coriander (2tsp) x0"           → Handle serving modifiers
"Garlic clove x2"                      → Handle multipliers
"Brown onion"                          → No quantity specified
```

**Solution:** Post-process ingredients to extract quantities, units, and names

### Issue 2: Multi-Serving Instructions

```
"Add 225ml [300ml] [450ml] cold water..."
```

Brackets indicate quantities for different serving sizes.

**Solution:** Parse bracket notation or preserve for user selection

### Issue 3: Limited Recipe Discovery

Only 5-6 recipes discovered on main list page.

**Solution:** Use sitemap + category crawling approach

---

## Community Resources

### Active Libraries
- **recipe-scrapers** (Python): https://github.com/hhursev/recipe-scrapers
  - Supports Gousto + 500 other sites
  - Uses JSON-LD extraction
  - Last updated: 2024

### Historical Issues
- [Issue #376](https://github.com/hhursev/recipe-scrapers/issues/376): HTML scraper broke in 2022 (fixed by migrating to JSON-LD)
- [Issue #1156](https://github.com/hhursev/recipe-scrapers/issues/1156): Ingredient parsing issues (closed as NOT_PLANNED)
- [Issue #140](https://github.com/hhursev/recipe-scrapers/issues/140): Initial Gousto scraper implementation

---

## Next Steps

1. **Test recipe-scrapers library** (5 min)
2. **Analyze sitemap.xml** (10 min)
3. **Enumerate categories** (30 min)
4. **Implement URL discovery** (2-4 hours)
5. **Build data cleaning pipeline** (4-8 hours)

---

## Sample Recipe Data

**URL Tested:** https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice

**Recipe Name:** Butter Chicken With Coriander Rice
**Category:** Indian
**Total Time:** 35 minutes
**Servings:** 2 or 4
**Rating:** 4.5/5 (77,163 reviews)
**Calories:** 565 per serving

**Ingredients (19 items):** Clotted cream, chicken breast, spices, rice, vegetables
**Instructions (8 steps):** Detailed step-by-step with serving variations
**Nutrition:** Complete macros (carbs, fat, protein, fiber, sugar, sodium)
**Image:** High-resolution (production-media.gousto.co.uk CDN)

---

## Files Generated

1. **gousto_analysis.py** - Playwright-based analysis script
2. **gousto_analysis_results.json** - Raw analysis data
3. **gousto_technical_research.md** - Comprehensive technical documentation (this file)
4. **gousto_research_output.json** - Structured JSON research output
5. **GOUSTO_RESEARCH_SUMMARY.md** - This quick reference

**Location:** `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/.claude_research/`

---

## Conclusion

Gousto recipes are **scrapable via JSON-LD schema.org** data embedded in recipe pages. The **recipe-scrapers library** provides the fastest implementation path. The primary challenge is **recipe URL discovery** due to limited pagination, which requires sitemap analysis or category crawling.

**Estimated Implementation Time:**
- Using recipe-scrapers: 1-2 days (including URL discovery)
- Custom implementation: 3-5 days (including data cleaning)

**Recommended Stack:**
- Python 3.11+
- recipe-scrapers library
- Playwright (for URL discovery)
- FastAPI (for data API)
- PostgreSQL/SQLite (for storage)

---

**Research Complete**
