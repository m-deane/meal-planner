# Test Suite Documentation

Comprehensive test suite for the Gousto Recipe Scraper with ≥80% code coverage.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── fixtures/                # Test data fixtures
│   ├── sample_recipe.json   # Complete recipe data example
│   ├── sample_sitemap.xml   # Sitemap XML for testing
│   └── sample_category_page.html
├── unit/                    # Unit tests (70% of test suite)
│   ├── test_data_normalizer.py
│   ├── test_data_validator.py
│   ├── test_http_client.py
│   ├── test_checkpoint.py
│   ├── test_logger.py
│   ├── test_config.py
│   ├── test_recipe_discoverer.py
│   ├── test_gousto_scraper.py
│   └── test_cli.py
└── integration/             # Integration tests (30% of test suite)
    └── test_full_workflow.py
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Run Specific Test Types
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific module
pytest tests/unit/test_data_normalizer.py

# Specific test
pytest tests/unit/test_data_normalizer.py::TestIngredientParser::test_parse_simple_ingredient
```

### Run with Markers
```bash
# Only fast tests
pytest -m "not slow"

# Only integration tests
pytest -m integration

# Skip network-dependent tests
pytest -m "not requires_network"
```

### Verbose Output
```bash
pytest -v  # Verbose
pytest -vv # Extra verbose
pytest -s  # Show print statements
```

## Test Coverage Requirements

- **Overall Target**: ≥80% line coverage
- **Critical Modules**: ≥90% coverage
  - `src/scrapers/gousto_scraper.py`
  - `src/scrapers/data_normalizer.py`
  - `src/validators/data_validator.py`

### Check Coverage
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing
```

## Test Categories

### Unit Tests

**Data Normalizer** (`test_data_normalizer.py`)
- Ingredient parsing (quantities, units, multipliers, optional ingredients)
- Instruction parsing (serving variants, time extraction)
- Nutrition normalization
- ISO duration parsing
- Servings parsing

**Data Validator** (`test_data_validator.py`)
- Required field validation
- Name validation (length, characters)
- Ingredient validation (negative quantities, missing names)
- Instruction validation (time constraints)
- Nutrition validation (calorie ranges, negative values)
- URL validation
- Strict mode behavior

**HTTP Client** (`test_http_client.py`)
- Rate limiting enforcement
- Retry logic with exponential backoff
- robots.txt compliance
- User-agent rotation
- Error handling
- Session management

**Checkpoint Manager** (`test_checkpoint.py`)
- Session creation and persistence
- URL tracking (pending, processed, failed)
- Auto-save functionality
- Progress statistics
- Checkpoint resumption

**Logger** (`test_logger.py`)
- Log level configuration
- File rotation
- Structured logging methods
- Progress tracking
- Recipe-specific logging

**Config** (`test_config.py`)
- Environment variable loading
- Validation constraints
- Default values
- Database URL validation
- Path resolution

**Recipe Discoverer** (`test_recipe_discoverer.py`)
- Sitemap parsing
- Sitemap index handling
- Category page crawling
- URL deduplication
- Recipe URL pattern matching

**Gousto Scraper** (`test_gousto_scraper.py`)
- Recipe scraping workflow
- Database integration
- Ingredient deduplication
- Category assignment
- Nutrition storage
- Error handling
- Validation integration

**CLI** (`test_cli.py`)
- Command execution
- Argument parsing
- Output formatting
- Error handling

### Integration Tests

**Full Workflow** (`test_full_workflow.py`)
- End-to-end scraping pipeline
- Discovery → Scrape → Normalize → Validate → Store
- Database relationships
- Transaction handling
- Error recovery

## Fixtures

### Database Fixtures
- `db_engine` - In-memory SQLite engine
- `db_session` - Fresh database session per test
- `populated_db_session` - Pre-populated with test data

### Mock Fixtures
- `mock_http_client` - Mock HTTP client
- `mock_recipe_scraper` - Mock recipe-scrapers instance

### Data Fixtures
- `sample_recipe_data` - Normalized recipe data
- `sample_raw_recipe` - Raw scraper output
- `sample_sitemap_xml` - Sitemap XML
- `sample_category_html` - Category page HTML
- `sample_robots_txt` - robots.txt content

### Utility Fixtures
- `temp_checkpoint_file` - Temporary checkpoint file
- `checkpoint_manager` - Configured checkpoint manager
- `test_config` - Test configuration overrides

## Writing New Tests

### Test Naming Convention
```python
# Class names: TestClassName
class TestDataNormalizer:
    pass

# Method names: test_should_do_something
def test_should_parse_ingredient_with_quantity():
    pass

# Use descriptive names
def test_parse_ingredient_with_multiplier():  # Good
def test_parser():  # Bad
```

### Test Structure (Arrange-Act-Assert)
```python
def test_parse_ingredient():
    # Arrange
    parser = IngredientParser()
    ingredient_str = "Tomato (250g)"

    # Act
    result = parser.parse(ingredient_str)

    # Assert
    assert result['name'] == 'Tomato'
    assert result['quantity'] == '250'
    assert result['unit'] == 'g'
```

### Using Fixtures
```python
def test_with_fixtures(db_session, sample_recipe_data):
    # Fixtures are injected automatically
    recipe = create_recipe_in_db(db_session, **sample_recipe_data)
    assert recipe.id is not None
```

### Mocking External Dependencies
```python
from unittest.mock import patch, Mock

def test_with_mock():
    with patch('src.module.external_function') as mock_func:
        mock_func.return_value = 'mocked value'

        result = function_under_test()

        assert result == 'mocked value'
        mock_func.assert_called_once()
```

## Continuous Integration

Tests run automatically on:
- Push to main branch
- Pull request creation
- Manual workflow dispatch

### CI Configuration
See `.github/workflows/test.yml` for CI pipeline configuration.

## Performance

### Test Execution Time
- Full suite: ~30 seconds
- Unit tests: ~15 seconds
- Integration tests: ~15 seconds

### Optimization Tips
- Use `pytest-xdist` for parallel execution: `pytest -n auto`
- Mark slow tests: `@pytest.mark.slow`
- Use session-scoped fixtures for expensive operations
- Mock external services (HTTP, database)

## Debugging Tests

### Run with PDB
```bash
pytest --pdb  # Drop into debugger on failure
pytest -x --pdb  # Stop at first failure
```

### Show Print Statements
```bash
pytest -s  # Show print() output
```

### Filter by Name
```bash
pytest -k "ingredient"  # Run tests with 'ingredient' in name
```

### Last Failed Tests
```bash
pytest --lf  # Re-run last failed tests
pytest --ff  # Run failed first, then others
```

## Test Data Management

### Adding New Fixtures
1. Create JSON file in `tests/fixtures/`
2. Add fixture function in `conftest.py`
3. Use `load_fixture` helper for dynamic loading

Example:
```python
# tests/fixtures/new_recipe.json
{"name": "New Recipe", ...}

# tests/conftest.py
@pytest.fixture
def new_recipe(load_fixture):
    return load_fixture('new_recipe.json')
```

## Code Quality

### Linting Tests
```bash
# Run black formatter
black tests/

# Run mypy type checking
mypy tests/
```

### Coverage Reports
- **HTML Report**: `htmlcov/index.html`
- **XML Report**: `coverage.xml` (for CI)
- **Terminal Report**: Inline during test run

## Troubleshooting

### Common Issues

**ImportError: No module named 'src'**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database locked errors**
- Use in-memory SQLite for tests (`:memory:`)
- Ensure proper session cleanup in fixtures

**Flaky tests**
- Add proper teardown in fixtures
- Avoid time-dependent assertions
- Use `freezegun` for time-based tests

**Coverage not including files**
- Check `pytest.ini` coverage configuration
- Ensure files are in `src/` directory
- Verify `__init__.py` files exist

## Best Practices

1. **One assertion per test** (when possible)
2. **Test edge cases** (empty inputs, None, extremes)
3. **Use descriptive names** (test name should describe behavior)
4. **Keep tests isolated** (no dependencies between tests)
5. **Mock external services** (HTTP, file I/O)
6. **Test error conditions** (exceptions, validation failures)
7. **Use fixtures** (avoid code duplication)
8. **Keep tests fast** (mock slow operations)

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure ≥80% coverage for new code
3. Add docstrings to test classes/methods
4. Update this README if adding new test categories
5. Run full test suite before committing

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
