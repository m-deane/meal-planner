# Gousto Recipe Website Technical Research

**Research Date:** 2025-12-20
**Target Website:** https://www.gousto.co.uk/cookbook/recipes
**Analysis Method:** Browser automation (Playwright) + Schema.org analysis

---

## Executive Summary

Gousto recipe pages implement **schema.org Recipe microdata in JSON-LD format**, making them suitable for structured data extraction. The website is a **React-based JavaScript application** requiring browser automation (Playwright/Selenium) for content rendering. Recipe data is embedded in `<script type="application/ld+json">` tags in a standardized format.

**Key Findings:**
- JSON-LD schema.org Recipe microdata: **CONFIRMED**
- JavaScript rendering required: **YES** (React application)
- Browser automation necessary: **Playwright or Selenium**
- Recipe discovery challenge: Limited pagination/navigation on list page
- Existing scraper support: **recipe-scrapers library** (Python)

---

## 1. JSON-LD Schema Availability

### Confirmation: PRESENT

Each recipe page contains exactly **one JSON-LD script tag** with comprehensive Recipe schema.

**Sample from:** `https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice`

```json
{
  "@context": "http://schema.org/",
  "@type": "Recipe",
  "name": "Butter Chicken With Coriander Rice",
  "author": {
    "@type": "Organization",
    "@id": "https://www.gousto.co.uk/",
    "name": "Gousto",
    "url": "https://gousto.co.uk/cookbook/butter-chicken-with-coriander-rice"
  },
  "image": "https://production-media.gousto.co.uk/cms/mood-image/890_Butter-Chicken-With-Coriander-Rice--1873-1611139093994.jpg",
  "description": "Butter chicken or 'murgh makhani' is a curry house favourite...",
  "recipeYield": "2 or 4 servings",
  "recipeIngredient": [...],
  "recipeInstructions": [...],
  "nutrition": {...},
  "aggregateRating": {...},
  "recipeCategory": "Indian",
  "recipeCuisine": "Indian",
  "totalTime": "PT35M"
}
```

---

## 2. Data Fields Available

### Complete Field Inventory

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `@context` | String | Schema.org context | "http://schema.org/" |
| `@type` | String | Schema type | "Recipe" |
| `name` | String | Recipe title | "Butter Chicken With Coriander Rice" |
| `author` | Object | Organization details | `{"@type": "Organization", "name": "Gousto"}` |
| `image` | String (URL) | High-res recipe image | CDN URL (production-media.gousto.co.uk) |
| `description` | String | Recipe description | Full text description |
| `recipeYield` | String | Servings | "2 or 4 servings" |
| `recipeIngredient` | Array[String] | Ingredients list | See ingredient format below |
| `recipeInstructions` | Array[String] | Step-by-step instructions | Multi-line text per step |
| `nutrition` | Object | Nutritional information | NutritionInformation schema |
| `aggregateRating` | Object | User ratings | AggregateRating schema |
| `recipeCategory` | String | Category | "Indian" |
| `recipeCuisine` | String | Cuisine type | "Indian" |
| `totalTime` | String (ISO 8601) | Total cook time | "PT35M" (35 minutes) |

### Ingredient Format Notes

Ingredients include quantity and unit in parentheses, with serving multipliers:

```json
"recipeIngredient": [
  "Cornish clotted cream (40g)",
  "Chicken breast strips (250g)",
  "Ground coriander (2tsp) x0",   // x0 indicates optional/alternative serving
  "Garlic clove x2",
  "Brown onion"
]
```

**Known Issue:** Some ingredients show duplicate quantities (e.g., "1 1 tbsp cornflour") due to Gousto's multi-serving format - see [recipe-scrapers issue #1156](https://github.com/hhursev/recipe-scrapers/issues/1156).

### Nutrition Information Schema

```json
"nutrition": {
  "@type": "NutritionInformation",
  "calories": "565 calories",
  "carbohydrateContent": "67.12",
  "fatContent": "17.70",
  "fiberContent": "4.83",
  "proteinContent": "34.68",
  "sugarContent": "5.63",
  "sodiumContent": "289.06"
}
```

Units: Grams unless otherwise specified (calories specified in string).

### Rating Information Schema

```json
"aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": 4.5,
  "reviewCount": 77163
}
```

---

## 3. Recipe URL Patterns

### Individual Recipe URLs

**Primary Pattern:**
```
https://www.gousto.co.uk/cookbook/{category}/{recipe-slug}
```

**Examples:**
- `https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice`
- `https://www.gousto.co.uk/cookbook/chicken-recipes/southern-fried-chicken-with-homemade-gravy`
- `https://www.gousto.co.uk/cookbook/pork-recipes/creamy-pork-tagliatelle`

**Alternative Pattern (newer URLs):**
```
https://www.gousto.co.uk/cookbook/recipes/{recipe-slug}
```

**Examples:**
- `https://www.gousto.co.uk/cookbook/recipes/summery-roast-chicken-salad`
- `https://www.gousto.co.uk/cookbook/recipes/korean-fried-chicken-with-yang-nyum-sauce`
- `https://www.gousto.co.uk/cookbook/recipes/one-pot-creamy-chicken-breast-vegetable-fricassee`

### Category Pages

```
https://www.gousto.co.uk/cookbook/{category}
```

**Examples:**
- `/cookbook/chicken-recipes`
- `/cookbook/plant-based-recipes`
- `/cookbook/low-calorie-recipes`
- `/cookbook/lighter`

---

## 4. Pagination/Navigation Analysis

### Challenge: Limited Recipe Discovery

**Observations from `/cookbook/recipes` page:**
- Only **5-6 unique recipe URLs** discovered in initial page load
- 189 total links to `/cookbook/` paths (mostly category/navigation links)
- **No obvious pagination controls detected**
- **No infinite scroll indicators found**
- **No API endpoints discovered** in network traffic

### Potential Discovery Strategies

1. **Category-based crawling**
   - Enumerate all category pages
   - Extract recipe links from each category
   - Risk: Incomplete coverage if recipes aren't categorized

2. **Sitemap analysis**
   - Check for XML sitemap at `/sitemap.xml`
   - May contain complete recipe URL list

3. **Search/filter functionality**
   - Investigate if search results expose more recipes
   - Check network traffic for API calls

4. **Historical crawling**
   - Use existing recipe-scrapers test data
   - Community-maintained URL lists

5. **Menu/weekly recipes endpoint**
   - `https://www.gousto.co.uk/menu` shows weekly rotation
   - May have JSON API for menu data

### Recommendation

**Start with sitemap analysis**, then supplement with category crawling. The lack of pagination suggests Gousto may rotate recipes through their weekly menu system rather than maintaining a static archive.

---

## 5. JavaScript Rendering Requirements

### Confirmed: Browser Automation Required

**Evidence:**
1. Initial HTTP request returns only: `"You need to enable JavaScript to run this app"`
2. Page is React-based single-page application (SPA)
3. Recipe data loaded client-side after JavaScript execution
4. HTML content length: 100,702 characters (after rendering)

### Recommended Tools

1. **Playwright** (preferred)
   - Modern, fast, well-maintained
   - Native TypeScript support
   - Python bindings available
   - Headless Chrome/Firefox/WebKit

2. **Selenium** (alternative)
   - More mature ecosystem
   - Wider community support
   - Larger resource footprint

3. **Existing Library: recipe-scrapers**
   - Python library with Gousto support
   - Uses schema.org extraction (HTML parsing)
   - May not require full browser if schema is in initial HTML

### Implementation Note

The recipe-scrapers library (Python) already implements Gousto scraping using schema.org extraction. Test whether the JSON-LD is present in initial HTML or requires JavaScript execution.

**Test command:**
```python
from recipe_scrapers import scrape_me

scraper = scrape_me('https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice')
print(scraper.to_json())
```

---

## 6. Sample Data Structure

### Complete Recipe Object (Real Example)

```json
{
  "@context": "http://schema.org/",
  "@type": "Recipe",
  "name": "Butter Chicken With Coriander Rice",
  "author": {
    "@type": "Organization",
    "@id": "https://www.gousto.co.uk/",
    "name": "Gousto",
    "url": "https://gousto.co.uk/cookbook/butter-chicken-with-coriander-rice"
  },
  "image": "https://production-media.gousto.co.uk/cms/mood-image/890_Butter-Chicken-With-Coriander-Rice--1873-1611139093994.jpg",
  "description": "Butter chicken or 'murgh makhani' is a curry house favourite. To make your own, you'll simmer chicken breast in a mild tomato sauce swirled with clotted cream. Serve with coriander rice to the side. Add both naan and salted caramel chocolate pot to save 20% on your side and dessert.",
  "recipeYield": "2 or 4 servings",
  "recipeIngredient": [
    "Cornish clotted cream (40g)",
    "Chicken breast strips (250g)",
    "Tomato paste (32g)",
    "Ground turmeric (1tsp)",
    "Ground coriander (1tsp)",
    "Garlic clove x2",
    "Fresh root ginger (15g)",
    "Garam masala (1tbsp)",
    "Coriander (10g)",
    "Brown onion",
    "White long grain rice (130g)",
    "Chicken stock mix (5.5g)"
  ],
  "recipeInstructions": [
    "Take your chicken out of the fridge, open the packet and let it air\nAdd your white long grain rice to a pot with a lid with 225ml [300ml] [450ml] cold water and bring to the boil over a high heat\nOnce boiling, reduce the heat to very low and cook, covered, for 12-15 min or until all the water has absorbed and the rice is cooked\nOnce done, remove from the heat and set aside (lid on) to steam until serving",
    "Cut your chicken into large, bite-sized pieces\nCombine the chopped chicken with your ground coriander, 1/2 tsp per person garam masala (save the rest for later!) and a generous pinch of salt in a large bowl – this is your coated chicken",
    "Heat a large, wide-based pan (preferably non-stick with a matching lid) with a drizzle of vegetable oil over a high heat\nOnce hot, add the coated chicken and cook for 5-6 min, turning occasionally until the chicken is browned\nOnce done, transfer the browned chicken to a plate (reserve the pan for later!)",
    "Boil half a kettle\nPeel and finely dice your brown onion[s]\nReturn the reserved pan to a medium heat with 1 tbsp [1 1/2 tbsp] [2 tbsp] butter\nOnce the butter has melted, add the diced onion with a pinch of salt and cook for 5 min or until softened and starting to caramelise",
    "Peel (scrape the skin off with a teaspoon) and finely chop (or grate) your ginger\nPeel and finely chop (or grate) your garlic\nOnce softened, add the chopped ginger, chopped garlic, your ground turmeric, tomato paste and the remaining garam masala to the pan and cook for 1 min or until fragrant\nAdd your chicken stock mix, then add 250ml [325ml] [450ml] boiled water",
    "Return the browned chicken to the pan, increase the heat to medium-high and cook, covered, for 5-6 min or until the sauce has thickened to a curry-like consistency and the chicken is cooked through (no pink meat!)\nMeanwhile, chop most of your coriander finely, including the stalks (save a few leaves for garnish!)\nFluff the cooked rice with a fork, stir through the chopped coriander and season with salt – this is your coriander rice",
    "Once the chicken is cooked, remove the pan from the heat and stir in your clotted cream – this is your butter chicken",
    "Serve the butter chicken over the coriander rice\nGarnish with the reserved coriander leaves\nEnjoy!"
  ],
  "nutrition": {
    "@type": "NutritionInformation",
    "calories": "565 calories",
    "carbohydrateContent": "67.12",
    "fatContent": "17.70",
    "fiberContent": "4.83",
    "proteinContent": "34.68",
    "sugarContent": "5.63",
    "sodiumContent": "289.06"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.5,
    "reviewCount": 77163
  },
  "recipeCategory": "Indian",
  "recipeCuisine": "Indian",
  "totalTime": "PT35M"
}
```

---

## 7. Technical Implementation Recommendations

### Architecture Decision: Use Existing Library vs. Custom

#### Option A: Use `recipe-scrapers` Library (Recommended)

**Pros:**
- Battle-tested Gousto scraper already implemented
- Handles schema.org extraction
- Fixed known ingredient parsing issues (as of 2022)
- Community-maintained and updated
- Supports 500+ recipe sites

**Cons:**
- Limited to library's scraping approach
- May not extract all custom fields
- Dependency on external library

**Implementation:**
```python
from recipe_scrapers import scrape_me

scraper = scrape_me('https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice')
recipe_data = scraper.to_json()
```

**GitHub:** https://github.com/hhursev/recipe-scrapers

#### Option B: Custom Playwright Scraper

**Pros:**
- Full control over extraction logic
- Can extract additional data not in schema
- Can monitor network requests for API endpoints
- Flexible for website changes

**Cons:**
- More development effort
- Maintenance burden
- Browser overhead (slower, more resources)

**Implementation:**
```python
from playwright.sync_api import sync_playwright
import json

def scrape_gousto(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')

        # Extract JSON-LD
        script = page.query_selector('script[type="application/ld+json"]')
        if script:
            data = json.loads(script.inner_text())
            return data

        browser.close()
```

### Recipe URL Discovery Strategy

1. **Check for sitemap:**
   ```python
   import requests
   response = requests.get('https://www.gousto.co.uk/sitemap.xml')
   # Parse XML for recipe URLs
   ```

2. **Category enumeration:**
   - Scrape category list from main cookbook page
   - Visit each category page
   - Extract recipe links from category pages

3. **Weekly menu API investigation:**
   - Monitor network traffic on `/menu` page
   - Look for GraphQL or REST API endpoints
   - May contain JSON with recipe IDs/URLs

4. **Fallback: Community URL lists**
   - Check recipe-scrapers test data
   - GitHub repositories with Gousto recipe collections

### Data Quality Considerations

1. **Ingredient parsing:**
   - Handle "x0" serving modifiers
   - Parse quantities and units from parentheses
   - Deal with duplicate quantity issues (e.g., "1 1 tbsp")

2. **Instruction formatting:**
   - Instructions contain newlines for sub-steps
   - May want to split into finer-grained steps
   - Handle serving size variations in brackets [2 servings] [4 servings]

3. **Image handling:**
   - CDN URLs are high-resolution (production-media.gousto.co.uk)
   - Consider downloading and hosting locally
   - Check for multiple image sizes/formats

4. **Rating reliability:**
   - Review counts are very high (77,163 in sample)
   - May include all-time historical data
   - Consider freshness of ratings

---

## 8. Known Issues and Limitations

### Issue 1: Ingredient Quantity Duplication

**Source:** [recipe-scrapers issue #1156](https://github.com/hhursev/recipe-scrapers/issues/1156)

**Description:** Ingredients sometimes show duplicate quantities (e.g., "1 1 tbsp cornflour")

**Cause:** Gousto's multi-serving format includes serving multipliers

**Status:** Closed as NOT_PLANNED (reflects actual website display)

**Workaround:** Post-process ingredients to normalize quantities

### Issue 2: Limited Recipe Discovery

**Description:** Recipe list page doesn't expose all recipes via pagination

**Impact:** Cannot easily discover all available recipes

**Workaround:** Use sitemap or category crawling

### Issue 3: Scraper Breakage in 2022

**Source:** [recipe-scrapers issue #376](https://github.com/hhursev/recipe-scrapers/issues/376)

**Description:** HTML-based scraper broke when Gousto implemented JavaScript detection

**Resolution:** Migrated to schema.org JSON-LD extraction (PR #390)

**Lesson:** JSON-LD extraction is more resilient than HTML parsing

---

## 9. Total Recipe Count

**Status:** NOT DISCOVERABLE from analyzed pages

**Observations:**
- No recipe count displayed on list pages
- No pagination showing "X of Y recipes"
- No API responses containing total count

**Discovery Method:** Requires full sitemap or category crawling

**Estimate Based on Analysis:**
- Multiple categories with dozens of recipes each
- Weekly menu rotation of ~150 recipes mentioned on site
- Likely hundreds to low thousands of recipes in total archive

---

## 10. Research Artifacts

### Files Generated

1. `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/.claude_research/gousto_analysis.py`
   - Playwright-based analysis script
   - Extracts JSON-LD and analyzes page structure

2. `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/.claude_research/gousto_analysis_results.json`
   - Raw analysis results
   - Sample recipe schema and metadata

3. `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/.claude_research/gousto_technical_research.md`
   - This document

### Test URLs Used

- Recipe page: `https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice`
- List page: `https://www.gousto.co.uk/cookbook/recipes`

---

## 11. Next Steps for Implementation

### Immediate Actions

1. **Test recipe-scrapers library:**
   ```bash
   pip install recipe-scrapers
   python -c "from recipe_scrapers import scrape_me; print(scrape_me('https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice').to_json())"
   ```

2. **Analyze sitemap:**
   - Check `https://www.gousto.co.uk/sitemap.xml`
   - Check `https://www.gousto.co.uk/robots.txt` for sitemap references

3. **Enumerate categories:**
   - Scrape category list from `/cookbook/recipes`
   - Document all category URLs

4. **Investigate menu API:**
   - Load `https://www.gousto.co.uk/menu` with network monitoring
   - Look for GraphQL/REST endpoints
   - Document API structure if found

### Development Priorities

1. **URL discovery system** (highest priority)
2. **Recipe scraper** (use recipe-scrapers library)
3. **Data cleaning pipeline** (ingredient normalization)
4. **Storage/database** (recipe data persistence)
5. **Update monitoring** (detect new/changed recipes)

---

## 12. References and Sources

### Primary Sources

- Gousto Cookbook: https://www.gousto.co.uk/cookbook/recipes
- Sample Recipe: https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice

### Technical Documentation

- Schema.org Recipe: https://schema.org/Recipe
- Google Recipe Schema: https://developers.google.com/search/docs/appearance/structured-data/recipe
- JSON-LD Format: https://json-ld.org/

### Community Resources

- recipe-scrapers library: https://github.com/hhursev/recipe-scrapers
- Issue #376 (scraper broken): https://github.com/hhursev/recipe-scrapers/issues/376
- Issue #1156 (ingredient parsing): https://github.com/hhursev/recipe-scrapers/issues/1156
- Issue #140 (initial implementation): https://github.com/hhursev/recipe-scrapers/issues/140

### Related Projects

- gousto-recipes-api (Laravel): https://github.com/miwels/gousto-recipes-api
- gousto-meal-planner: https://github.com/VFjr/gousto-meal-planner

---

## Appendix A: Schema.org Recipe Fields

### Standard Fields Used by Gousto

- `@context`: Schema.org context URL
- `@type`: "Recipe"
- `name`: Recipe name
- `author`: Organization object
- `image`: Image URL
- `description`: Text description
- `recipeYield`: Serving count
- `recipeIngredient`: Array of ingredient strings
- `recipeInstructions`: Array of instruction strings
- `nutrition`: NutritionInformation object
- `aggregateRating`: AggregateRating object
- `recipeCategory`: Category string
- `recipeCuisine`: Cuisine type string
- `totalTime`: ISO 8601 duration

### Standard Fields NOT Used by Gousto

- `prepTime`: Preparation time (only totalTime provided)
- `cookTime`: Cooking time (only totalTime provided)
- `keywords`: Recipe keywords/tags
- `recipeVideo`: Video instructions
- `suitableForDiet`: Dietary restrictions
- `recipeIngredient` as structured objects (uses strings instead)

---

## Appendix B: Sample Network Request Analysis

**No API endpoints discovered during analysis of:**
- `/cookbook/recipes` (main list page)
- Individual recipe pages

**Observations:**
- React application likely bundles data with initial page load
- No GraphQL endpoint detected
- No REST API calls observed for recipe data
- May use server-side rendering for SEO with JSON-LD

**Recommendation:** Monitor network traffic on `/menu` page for potential API endpoints related to weekly recipe selection.

---

**End of Research Document**
