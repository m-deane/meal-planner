# Gousto Recipe Scraper

Production-ready web scraper for extracting recipe data from Gousto.co.uk with comprehensive data normalization, validation, and database storage.

## Features

- **Automated Recipe Discovery**: Discovers recipe URLs from sitemaps and category pages
- **Robust Scraping**: Uses the battle-tested `recipe-scrapers` library with built-in Gousto support
- **Rate Limiting**: Configurable delays and exponential backoff to respect server resources
- **Data Normalization**: Parses ingredients, instructions, and nutrition into structured format
- **Schema Validation**: Validates against schema.org Recipe spec before storage
- **Checkpoint/Resume**: Resume interrupted scraping sessions automatically
- **Database Integration**: Stores normalized data in SQLite or PostgreSQL
- **CLI Interface**: User-friendly command-line tools for all operations
- **Comprehensive Logging**: Structured logging with rotation and progress tracking

## Installation

### 1. Clone Repository and Install Dependencies

```bash
cd /Users/matthewdeane/Documents/Data\ Science/python/_projects/__utils-recipes

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Initialize Database

```bash
python -m src.cli init-db
```

## Quick Start

### Discover Recipe URLs

```bash
# Discover all recipe URLs from sitemap and categories
python -m src.cli discover
```

### Scrape Recipes

```bash
# Scrape first 10 recipes
python -m src.cli scrape --limit 10

# Scrape with custom rate limit (5 seconds between requests)
python -m src.cli scrape --limit 50 --delay 5

# Resume from checkpoint after interruption
python -m src.cli scrape --resume

# Scrape specific URLs from file
echo "https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice" > urls.txt
python -m src.cli scrape --urls-file urls.txt
```

### Export Data

```bash
# Export to JSON
python -m src.cli export --format json --output data/recipes.json

# Export to CSV
python -m src.cli export --format csv --output data/recipes.csv --limit 100

# Include inactive recipes
python -m src.cli export --format json --output data/all_recipes.json --include-inactive
```

### View Statistics

```bash
# Basic statistics
python -m src.cli stats

# Detailed statistics with breakdowns
python -m src.cli stats --detailed
```

## CLI Commands

### `discover`
Discover recipe URLs from sitemap and category pages.

**Options:**
- `--save-to-db`: Save discovered URLs to database

**Example:**
```bash
python -m src.cli discover --save-to-db
```

### `scrape`
Scrape recipes from Gousto.

**Options:**
- `--limit INTEGER`: Maximum number of recipes to scrape
- `--delay FLOAT`: Delay between requests in seconds
- `--resume`: Resume from last checkpoint
- `--urls-file PATH`: File containing URLs to scrape (one per line)

**Examples:**
```bash
python -m src.cli scrape --limit 100 --delay 3
python -m src.cli scrape --resume
python -m src.cli scrape --urls-file my_urls.txt
```

### `export`
Export recipes to JSON or CSV.

**Options:**
- `--format [json|csv]`: Export format (required)
- `--output PATH`: Output file path (required)
- `--include-inactive`: Include inactive recipes
- `--limit INTEGER`: Maximum number of recipes to export

**Examples:**
```bash
python -m src.cli export --format json --output recipes.json
python -m src.cli export --format csv --output recipes.csv --limit 50
```

### `stats`
Show database statistics.

**Options:**
- `--detailed`: Show detailed statistics with breakdowns

**Example:**
```bash
python -m src.cli stats --detailed
```

### `init-db`
Initialize database schema.

**Example:**
```bash
python -m src.cli init-db
```

### `clear-checkpoint`
Clear checkpoint file to start fresh scraping session.

**Example:**
```bash
python -m src.cli clear-checkpoint
```

## Configuration

All configuration is managed through environment variables in `.env` file or the `src/config.py` module.

### Key Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///recipes.db` | Database connection URL |
| `SCRAPER_DELAY_SECONDS` | `3.0` | Delay between requests |
| `SCRAPER_MAX_RETRIES` | `3` | Maximum retry attempts |
| `SCRAPER_TIMEOUT_SECONDS` | `30` | Request timeout |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | `logs/scraper.log` | Log file path |
| `CHECKPOINT_ENABLED` | `true` | Enable checkpoint/resume |
| `CHECKPOINT_INTERVAL` | `10` | Save checkpoint every N recipes |
| `VALIDATION_STRICT` | `false` | Fail on validation warnings |

See `.env.example` for complete configuration options.

## Architecture

```
src/
├── cli.py                          # Command-line interface
├── config.py                       # Configuration management
├── scrapers/
│   ├── gousto_scraper.py          # Main scraper orchestration
│   ├── recipe_discoverer.py       # URL discovery from sitemap/categories
│   └── data_normalizer.py         # Data normalization and parsing
├── validators/
│   └── data_validator.py          # Schema.org validation
├── utils/
│   ├── logger.py                  # Structured logging
│   ├── http_client.py             # Rate-limited HTTP client
│   └── checkpoint.py              # Resume functionality
└── database/                       # Database models and queries
    ├── models.py                  # SQLAlchemy ORM models
    ├── connection.py              # Database connection
    └── queries.py                 # Common queries
```

## Data Flow

1. **Discovery**: `RecipeDiscoverer` extracts URLs from sitemap.xml and category pages
2. **Scraping**: `GoustoScraper` uses `recipe-scrapers` library to extract JSON-LD data
3. **Normalization**: `DataNormalizer` parses ingredients, instructions, and nutrition
4. **Validation**: `RecipeValidator` validates against schema.org Recipe spec
5. **Storage**: Normalized data saved to database via SQLAlchemy ORM
6. **Checkpoint**: Progress tracked for resume capability

## Database Schema

The scraper uses a comprehensive relational schema:

- **recipes**: Core recipe data (name, description, times, servings)
- **ingredients**: Normalized ingredient master list
- **recipe_ingredients**: Recipe-ingredient associations with quantities
- **cooking_instructions**: Step-by-step instructions
- **nutritional_info**: Nutritional data per serving
- **categories**: Recipe categories (cuisine, meal type)
- **allergens**: Allergen information
- **dietary_tags**: Dietary classifications (vegan, vegetarian, etc.)
- **images**: Recipe images
- **scraping_history**: Audit trail of scraping operations

See `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/src/database/models.py` for complete schema.

## Data Normalization

### Ingredient Parsing

Handles Gousto's complex ingredient format:

```python
# Input: "Chicken breast strips (250g)"
# Output: {
#   'name': 'Chicken breast strips',
#   'quantity': '250',
#   'unit': 'g',
#   'preparation': None,
#   'is_optional': False
# }

# Input: "Garlic clove x2"
# Output: {
#   'name': 'Garlic clove',
#   'quantity': '2',
#   'unit': 'whole',
#   'preparation': None,
#   'is_optional': False
# }

# Input: "Ground coriander (2tsp) x0"
# Output: {
#   'name': 'Ground coriander',
#   'quantity': '2',
#   'unit': 'tsp',
#   'preparation': None,
#   'is_optional': True
# }
```

### Instruction Parsing

Extracts structured data from cooking instructions:

- Removes serving size variants in brackets `[2 servings] [4 servings]`
- Extracts time estimates ("cook for 5-6 minutes")
- Cleans whitespace and newlines
- Preserves original text for reference

### Nutrition Normalization

Converts various formats to standardized Decimal values:

- Parses "565 calories" to `Decimal('565')`
- Handles grams, milligrams, and percentages
- Validates ranges (0-5000 calories by default)

## Error Handling

The scraper implements comprehensive error handling:

1. **Network Errors**: Automatic retry with exponential backoff
2. **Parsing Errors**: Logged with full context, scraping continues
3. **Validation Errors**: Configurable strict mode (fail vs. warn)
4. **Database Errors**: Transaction rollback with detailed logging
5. **Checkpoint Recovery**: Resume from last successful point

## Logging

Structured logging with multiple levels:

```
2024-12-20 14:30:15 - scraper - INFO - Starting recipe discovery
2024-12-20 14:30:18 - scraper - INFO - Discovered 847 recipe URLs
2024-12-20 14:30:20 - scraper - INFO - [1/100] Scraping: https://...
2024-12-20 14:30:23 - scraper - INFO - Scraped: Butter Chicken | Ingredients: 12 | Instructions: 8
2024-12-20 14:30:25 - scraper - INFO - Progress: 10/100 (10.0%) | Success: 9 (90.0%) | Failed: 1
```

Logs are written to:
- Console (stdout) for real-time monitoring
- Log file with rotation (default: `logs/scraper.log`, 10MB max, 10 backups)

## Rate Limiting & Robots.txt

The scraper respects website resources:

- **Rate Limiting**: 3-second delay between requests (configurable)
- **Robots.txt**: Automatically checks and respects disallow rules
- **User-Agent Rotation**: Rotates through multiple user agents
- **Exponential Backoff**: Retries with increasing delays (2x, 4x, 8x)
- **Request Timeout**: 30-second timeout (configurable)

## Testing

Run tests (to be implemented by test-engineer):

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Issue: "No checkpoint found"

**Solution**: Start fresh scraping session without `--resume` flag.

```bash
python -m src.cli clear-checkpoint
python -m src.cli scrape --limit 10
```

### Issue: "Database locked" (SQLite)

**Solution**: Close other connections or use PostgreSQL for concurrent access.

```bash
# Switch to PostgreSQL in .env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/recipes
```

### Issue: "Rate limit errors"

**Solution**: Increase delay between requests.

```bash
python -m src.cli scrape --delay 5  # 5 seconds between requests
```

### Issue: "Validation errors"

**Solution**: Check validation settings in `.env`.

```bash
# Disable strict validation
VALIDATION_STRICT=false

# Allow recipes without nutrition data
VALIDATION_REQUIRE_INGREDIENTS=true
VALIDATION_REQUIRE_INSTRUCTIONS=true
```

## Performance

Estimated scraping times:

- **10 recipes**: ~45 seconds (with 3s delay)
- **100 recipes**: ~7 minutes
- **1000 recipes**: ~70 minutes

Database write performance:
- SQLite: ~50-100 recipes/min (single-threaded)
- PostgreSQL: ~100-200 recipes/min (concurrent writes)

## Limitations

1. **JavaScript Rendering**: recipe-scrapers library may not handle all JS-heavy pages
2. **Pagination**: Limited recipe discovery without comprehensive sitemap
3. **Ingredient Parsing**: Some complex formats may not parse perfectly
4. **Rate Limits**: Aggressive scraping may trigger IP blocks (use delays!)

## Future Enhancements

- Parallel scraping with asyncio
- Image downloading and local storage
- Duplicate detection based on recipe similarity
- Incremental updates (detect changed recipes)
- API endpoint for recipe access
- Web dashboard for monitoring

## License

This is a utility project for personal recipe collection. Respect Gousto's terms of service and robots.txt when scraping.

## Support

For issues or questions:
1. Check logs in `logs/scraper.log`
2. Review configuration in `.env`
3. Enable debug logging: `LOG_LEVEL=DEBUG`

## File Locations

- **Source Code**: `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/src/`
- **Database**: `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/recipes.db` (SQLite)
- **Logs**: `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/logs/`
- **Checkpoints**: `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/.scraper_checkpoint.json`
- **Configuration**: `/Users/matthewdeane/Documents/Data Science/python/_projects/__utils-recipes/.env`
