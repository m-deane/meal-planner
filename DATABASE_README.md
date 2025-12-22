# Recipe Database Schema - Gousto Recipe Scraper

A production-ready, normalized PostgreSQL/SQLite database schema for storing and querying recipe data from Gousto.

## Features

- Normalized 3NF+ schema eliminating data duplication
- Support for both SQLite (dev) and PostgreSQL (prod)
- Complete SQLAlchemy ORM with type hints
- Strategic indexing for query performance
- Pre-seeded reference data (units, allergens, dietary tags)
- Advanced filtering and search capabilities
- Comprehensive documentation and examples
- 100+ sample queries
- Full test suite

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env to configure database type and connection
```

### 3. Initialize Database

```python
from src.database import init_database

# SQLite (development)
engine = init_database(
    database_url='sqlite:///data/recipes.db',
    seed_data=True
)

# PostgreSQL (production)
engine = init_database(
    database_url='postgresql://user:password@localhost/recipes',
    seed_data=True
)
```

### 4. Basic Usage

```python
from src.database import get_session, RecipeQuery

session = get_session()
query = RecipeQuery(session)

# Search recipes
results = query.search_by_name('chicken')

# Filter by criteria
vegan_quick = query.filter_recipes(
    dietary_tags=['vegan'],
    max_cooking_time=30
)

# Get high-protein recipes
high_protein = query.get_high_protein_recipes(min_protein=30)
```

## Project Structure

```
.
├── src/database/              # Database module
│   ├── schema.sql            # DDL statements (471 lines)
│   ├── models.py             # SQLAlchemy ORM models (479 lines)
│   ├── connection.py         # Connection management (227 lines)
│   ├── queries.py            # Query helpers (347 lines)
│   ├── seed.py               # Reference data (174 lines)
│   ├── example_usage.py      # Usage examples (339 lines)
│   └── README.md             # Module documentation
│
├── docs/                      # Documentation
│   ├── DATABASE_SCHEMA.md    # Complete schema docs (578 lines)
│   ├── SAMPLE_QUERIES.md     # 100+ query examples (662 lines)
│   ├── INDEX_STRATEGY.md     # Index optimization (462 lines)
│   └── QUICK_REFERENCE.md    # Quick reference guide (393 lines)
│
├── tests/                     # Test suite
│   └── test_database.py      # Unit tests (549 lines)
│
├── migrations/                # Database migrations
│   └── 001_initial_schema.sql
│
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── verify_database.py        # Verification script
└── DATABASE_README.md        # This file
```

## Database Schema Overview

### Core Tables

- **recipes** - Main recipe entity with metadata
- **categories** - Cuisine types, meal types, occasions
- **ingredients** - Normalized ingredient master list
- **units** - Measurement units (g, ml, cups, etc.)
- **allergens** - Allergen master list
- **dietary_tags** - Dietary classifications (vegan, keto, etc.)
- **nutritional_info** - Per-serving nutritional data
- **cooking_instructions** - Step-by-step ordered instructions
- **images** - Recipe photos and media

### Relationship Tables (Many-to-Many)

- **recipe_categories** - Recipes ↔ Categories
- **recipe_ingredients** - Recipes ↔ Ingredients (with quantities)
- **recipe_allergens** - Recipes ↔ Allergens
- **recipe_dietary_tags** - Recipes ↔ Dietary Tags

### Audit Tables

- **scraping_history** - Track scraping operations
- **schema_version** - Migration tracking

## Code Statistics

| Component | Lines of Code |
|-----------|--------------|
| SQL Schema | 471 |
| Python Models | 479 |
| Connection Management | 227 |
| Query Helpers | 347 |
| Seed Data | 174 |
| Example Usage | 339 |
| Unit Tests | 549 |
| **Total Code** | **2,586** |
| Documentation | 3,117 |
| **Grand Total** | **5,203** |

## Documentation

| Document | Description |
|----------|-------------|
| [Database Schema](docs/DATABASE_SCHEMA.md) | Complete schema documentation with ER diagram |
| [Sample Queries](docs/SAMPLE_QUERIES.md) | 100+ SQL and ORM query examples |
| [Index Strategy](docs/INDEX_STRATEGY.md) | Index design and optimization guide |
| [Quick Reference](docs/QUICK_REFERENCE.md) | Quick lookup guide for common operations |
| [Module README](src/database/README.md) | Database module API reference |
| [Implementation Summary](DATABASE_IMPLEMENTATION_SUMMARY.md) | Complete implementation overview |

## Testing

### Run Verification

```bash
python verify_database.py
```

### Run Unit Tests

```bash
pytest tests/test_database.py -v
```

## Validation Checklist

- [x] Normalized schema (3NF+)
- [x] Appropriate indexes for common queries
- [x] Foreign key relationships with cascading
- [x] SQLite and PostgreSQL compatibility
- [x] Migration-friendly with version tracking
- [x] Complete SQL DDL statements
- [x] ER diagram description
- [x] Index strategy documentation
- [x] Sample queries (100+)
- [x] Python SQLAlchemy models
- [x] Connection management utilities
- [x] Query helper API
- [x] Comprehensive tests
- [x] Example usage code
- [x] Production deployment guide
