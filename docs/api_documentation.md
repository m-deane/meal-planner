# FastAPI Core Structure Documentation

## Overview

The FastAPI core structure provides a production-ready REST API for the Gousto Recipe Meal Planner application. It includes configuration management, authentication, database integration, and comprehensive error handling.

## Architecture

```
src/api/
├── __init__.py           # Package initialization
├── config.py             # API configuration (extends base config)
├── dependencies.py       # Dependency injection utilities
└── main.py              # FastAPI application factory
```

## Files Created

### 1. `src/api/__init__.py`
Empty initialization file for the API package.

### 2. `src/api/config.py`
Extended configuration with API-specific settings:

**Key Features:**
- Extends base `Config` from `src/config.py`
- API server settings (host, port, debug)
- CORS configuration
- JWT authentication settings
- Rate limiting configuration
- Pagination defaults
- OpenAPI documentation settings

**Configuration Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_host` | "0.0.0.0" | API server host |
| `api_port` | 8000 | API server port |
| `api_debug` | False | Debug mode (auto-reload, detailed errors) |
| `cors_origins` | ["http://localhost:3000", ...] | Allowed CORS origins |
| `jwt_secret` | (warning shown) | JWT signing secret |
| `jwt_algorithm` | "HS256" | JWT algorithm |
| `jwt_expire_minutes` | 1440 (24h) | Token expiration |
| `pagination_default_limit` | 20 | Default page size |
| `pagination_max_limit` | 100 | Maximum page size |

**Environment Variables:**
All settings can be configured via environment variables:
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
JWT_SECRET=your-secret-key-here-minimum-32-chars
CORS_ORIGINS=["http://localhost:3000","https://myapp.com"]
```

### 3. `src/api/dependencies.py`
Dependency injection utilities for FastAPI endpoints:

**Database Dependency:**
```python
from src.api.dependencies import DatabaseSession

@app.get("/recipes")
def list_recipes(db: DatabaseSession):
    return db.query(Recipe).all()
```

**Authentication Dependencies:**
```python
from src.api.dependencies import CurrentUser, OptionalUser, AdminUser

# Required authentication
@app.get("/profile")
def get_profile(user: CurrentUser):
    return {"user_id": user["sub"]}

# Optional authentication
@app.get("/recipes")
def list_recipes(user: OptionalUser):
    if user:
        return get_personalized_recipes(user["sub"])
    return get_public_recipes()

# Admin-only endpoint
@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, admin: AdminUser):
    # Only admins can access
    pass
```

**Pagination Dependency:**
```python
from src.api.dependencies import PaginationParams

@app.get("/recipes")
def list_recipes(pagination: PaginationParams):
    skip, limit = pagination
    return db.query(Recipe).offset(skip).limit(limit).all()
```

**Available Functions:**
- `get_db()` - Database session generator
- `create_access_token(data, expires_delta)` - Create JWT token
- `decode_access_token(token)` - Decode and validate JWT
- `get_current_user(credentials)` - Required authentication
- `get_current_user_optional(credentials)` - Optional authentication
- `verify_admin_role(user)` - Admin role verification
- `get_pagination_params(skip, limit)` - Pagination validation

### 4. `src/api/main.py`
FastAPI application factory and configuration:

**Key Features:**
- Application factory pattern (`create_app()`)
- Lifespan management (startup/shutdown)
- CORS middleware
- Comprehensive exception handlers
- Health check endpoints
- OpenAPI documentation
- Router registration (placeholder)

**Health Check Endpoints:**

```bash
# Basic health check
GET /
Response: {
    "status": "healthy",
    "service": "Gousto Recipe Meal Planner API",
    "version": "1.0.0"
}

# Detailed health check with database
GET /health
Response: {
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0"
}
```

**Exception Handlers:**
- `RequestValidationError` - 422 with field-level errors
- `SQLAlchemyError` - 500 with database error details
- `Exception` - 500 catch-all handler

## Usage

### Starting the API Server

**Development Mode (with auto-reload):**
```bash
# Using the main module
python -m src.api.main

# Using uvicorn directly
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
# Using uvicorn with workers
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn with uvicorn workers
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Creating JWT Tokens

```python
from src.api.dependencies import create_access_token
from datetime import timedelta

# Default expiration (from config)
token = create_access_token({"sub": "user123", "role": "user"})

# Custom expiration
token = create_access_token(
    {"sub": "admin123", "role": "admin"},
    expires_delta=timedelta(hours=12)
)
```

### Using Authentication in Endpoints

```python
from fastapi import APIRouter
from src.api.dependencies import CurrentUser, DatabaseSession

router = APIRouter()

@router.get("/me")
def get_current_user_info(user: CurrentUser, db: DatabaseSession):
    """Get current authenticated user information."""
    user_id = user["sub"]
    # Use user_id to fetch from database
    return {"user_id": user_id, "role": user.get("role")}

@router.post("/recipes")
def create_recipe(recipe: RecipeCreate, user: CurrentUser, db: DatabaseSession):
    """Create a new recipe (authenticated users only)."""
    # user["sub"] contains the user ID
    new_recipe = Recipe(**recipe.dict(), created_by=user["sub"])
    db.add(new_recipe)
    db.commit()
    return new_recipe
```

### Making Authenticated Requests

```python
import requests

# Get a token (implement login endpoint first)
token = "your-jwt-token-here"

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/recipes", headers=headers)
```

## Testing

### Unit Tests

```bash
# Run all API tests
pytest tests/unit/test_api_core.py -v

# Run specific test class
pytest tests/unit/test_api_core.py::TestAPIConfig -v

# Run with coverage
pytest tests/unit/test_api_core.py --cov=src/api --cov-report=html
```

### Integration Tests

```bash
# Run integration tests
pytest tests/unit/test_api_core.py -v -m integration
```

### Manual Testing with Test Client

```python
from fastapi.testclient import TestClient
from src.api.main import create_app

app = create_app()
client = TestClient(app)

# Test endpoints
response = client.get("/")
assert response.status_code == 200

response = client.get("/health")
assert response.json()["status"] == "healthy"
```

## Next Steps: Implementing Routes

To add API routes, create router modules in `src/api/routes/`:

```python
# src/api/routes/recipes.py
from fastapi import APIRouter
from src.api.dependencies import DatabaseSession, CurrentUser, PaginationParams
from src.database.models import Recipe

router = APIRouter()

@router.get("/")
def list_recipes(
    db: DatabaseSession,
    pagination: PaginationParams,
    user: OptionalUser = None
):
    """List all recipes with pagination."""
    skip, limit = pagination
    query = db.query(Recipe).filter(Recipe.is_active == True)

    total = query.count()
    recipes = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "recipes": recipes
    }

@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, db: DatabaseSession):
    """Get a specific recipe by ID."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
```

Then register in `src/api/main.py`:

```python
from src.api.routes import recipes

def register_routers(app: FastAPI) -> None:
    app.include_router(
        recipes.router,
        prefix="/api/v1/recipes",
        tags=["recipes"]
    )
```

## Security Best Practices

1. **JWT Secret**: Always set a strong `JWT_SECRET` in production:
   ```bash
   # Generate a secure random key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **CORS Origins**: Restrict `CORS_ORIGINS` to your actual frontend domains:
   ```bash
   CORS_ORIGINS=["https://myapp.com","https://www.myapp.com"]
   ```

3. **HTTPS**: Always use HTTPS in production
4. **Rate Limiting**: Implement rate limiting for production
5. **Input Validation**: Use Pydantic models for all request/response data

## Troubleshooting

### Database Connection Issues

If health check shows "degraded":
```bash
# Initialize the database
python -m src.cli init-db

# Check database URL
python -c "from src.api.config import api_config; print(api_config.database_url)"
```

### JWT Token Issues

```python
# Verify token creation
from src.api.dependencies import create_access_token, decode_access_token

token = create_access_token({"sub": "test"})
print(f"Token: {token}")

decoded = decode_access_token(token)
print(f"Decoded: {decoded}")
```

### CORS Issues

If getting CORS errors, verify origins in config:
```python
from src.api.config import api_config
print(api_config.cors_origins)
```

## Performance Optimization

### Database Connection Pooling

For production, use PostgreSQL with connection pooling:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### Caching

Add caching for frequently accessed data:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_popular_recipes():
    # Cached for performance
    pass
```

### Background Tasks

Use FastAPI background tasks for non-blocking operations:
```python
from fastapi import BackgroundTasks

@router.post("/recipes")
def create_recipe(recipe: RecipeCreate, background_tasks: BackgroundTasks):
    # Add background task
    background_tasks.add_task(send_notification, recipe.id)
    return recipe
```

## Documentation

### Swagger UI
Visit `http://localhost:8000/docs` for interactive API documentation (when `API_DEBUG=true`)

### ReDoc
Visit `http://localhost:8000/redoc` for alternative documentation (when `API_DEBUG=true`)

### OpenAPI Schema
Get the OpenAPI schema at `http://localhost:8000/openapi.json`

## Dependencies Added

The following packages were added to `requirements.txt`:

```
# API Framework
fastapi==0.109.0
uvicorn[standard]==0.26.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
```

Install with:
```bash
pip install -r requirements.txt
```

## Summary

The FastAPI core structure provides:

- Production-ready API server
- JWT authentication system
- Database integration via dependency injection
- Comprehensive error handling
- CORS configuration
- Pagination support
- Health check endpoints
- OpenAPI documentation
- Extensible router system
- Type-safe configuration
- Comprehensive test coverage

All components integrate seamlessly with the existing SQLAlchemy models, database connection, and configuration system.
