# FastAPI Quick Reference Guide

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and set:
# - JWT_SECRET (minimum 32 characters)
# - DATABASE_URL (if not using default SQLite)
# - CORS_ORIGINS (your frontend URL)
```

### 3. Initialize Database
```bash
python -m src.cli init-db
```

### 4. Start API Server
```bash
# Development mode (auto-reload)
uvicorn src.api.main:app --reload

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## Common Patterns

### Creating an Endpoint

```python
# src/api/routes/recipes.py
from fastapi import APIRouter, HTTPException, status
from src.api.dependencies import DatabaseSession, CurrentUser, PaginationParams
from src.database.models import Recipe

router = APIRouter()

@router.get("/")
def list_recipes(
    db: DatabaseSession,
    pagination: PaginationParams
):
    """List all active recipes with pagination."""
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found"
        )

    return recipe

@router.post("/")
def create_recipe(
    recipe_data: RecipeCreate,  # Define in schemas
    db: DatabaseSession,
    user: CurrentUser
):
    """Create a new recipe (authenticated users only)."""
    recipe = Recipe(**recipe_data.dict())
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return recipe

@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: DatabaseSession,
    admin: AdminUser  # Admin only
):
    """Delete a recipe (admin only)."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()

    return {"message": "Recipe deleted successfully"}
```

### Register Router

```python
# src/api/main.py
from src.api.routes import recipes

def register_routers(app: FastAPI) -> None:
    app.include_router(
        recipes.router,
        prefix="/api/v1/recipes",
        tags=["recipes"]
    )
```

### Creating Pydantic Schemas

```python
# src/api/schemas/recipe.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RecipeBase(BaseModel):
    """Base recipe schema."""
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    cooking_time_minutes: Optional[int] = Field(None, ge=0)
    servings: int = Field(default=2, ge=1)

class RecipeCreate(RecipeBase):
    """Schema for creating a recipe."""
    gousto_id: str
    slug: str
    source_url: str

class RecipeUpdate(BaseModel):
    """Schema for updating a recipe."""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    cooking_time_minutes: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None

class RecipeResponse(RecipeBase):
    """Schema for recipe responses."""
    id: int
    gousto_id: str
    slug: str
    source_url: str
    is_active: bool
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True  # Pydantic v2
```

### Using Dependencies

```python
from src.api.dependencies import (
    DatabaseSession,      # Database session
    CurrentUser,          # Required auth (returns user dict)
    OptionalUser,         # Optional auth (returns user dict or None)
    AdminUser,            # Admin only (returns user dict)
    PaginationParams,     # Validated pagination (skip, limit)
)

@router.get("/profile")
def get_profile(user: CurrentUser, db: DatabaseSession):
    """Get current user profile."""
    user_id = user["sub"]
    role = user.get("role", "user")
    return {"user_id": user_id, "role": role}

@router.get("/public-or-private")
def conditional_endpoint(user: OptionalUser):
    """Endpoint that works with or without auth."""
    if user:
        return {"message": f"Hello {user['sub']}!"}
    return {"message": "Hello guest!"}

@router.delete("/admin-only")
def admin_endpoint(admin: AdminUser):
    """Admin-only endpoint."""
    return {"message": f"Admin {admin['sub']} has access"}
```

### Creating JWT Tokens

```python
from src.api.dependencies import create_access_token
from datetime import timedelta

# Default expiration (from config: 24 hours)
token = create_access_token({"sub": "user123", "role": "user"})

# Custom expiration
token = create_access_token(
    {"sub": "admin@example.com", "role": "admin"},
    expires_delta=timedelta(hours=12)
)

# Return in login response
return {
    "access_token": token,
    "token_type": "bearer",
    "expires_in": 86400  # seconds
}
```

### Making Authenticated Requests

```python
# Python requests
import requests

token = "your-jwt-token-here"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "http://localhost:8000/api/v1/recipes",
    headers=headers
)

# cURL
curl -H "Authorization: Bearer YOUR-TOKEN" \
     http://localhost:8000/api/v1/recipes

# JavaScript fetch
fetch('http://localhost:8000/api/v1/recipes', {
    headers: {
        'Authorization': 'Bearer YOUR-TOKEN',
        'Content-Type': 'application/json'
    }
})
```

### Error Handling

```python
from fastapi import HTTPException, status

# 400 Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input parameters"
)

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient permissions"
)

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

# 422 Unprocessable Entity (automatic for validation errors)
# Pydantic handles this automatically

# 500 Internal Server Error (automatic for unhandled exceptions)
# Handled by global exception handler
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    """Send email in background."""
    # Email sending logic
    pass

@router.post("/recipes")
def create_recipe(
    recipe: RecipeCreate,
    background_tasks: BackgroundTasks
):
    """Create recipe and send notification."""
    # Create recipe
    new_recipe = Recipe(**recipe.dict())
    db.add(new_recipe)
    db.commit()

    # Schedule background task
    background_tasks.add_task(
        send_email,
        "admin@example.com",
        f"New recipe created: {new_recipe.name}"
    )

    return new_recipe
```

### Query Parameters

```python
from typing import Optional

@router.get("/recipes")
def search_recipes(
    q: Optional[str] = None,           # Optional search query
    category: Optional[str] = None,    # Optional filter
    min_time: int = 0,                 # Default value
    max_time: int = 120,
    skip: int = 0,
    limit: int = 20
):
    """Search recipes with filters."""
    query = db.query(Recipe)

    if q:
        query = query.filter(Recipe.name.contains(q))

    if category:
        query = query.join(Recipe.categories).filter(
            Category.slug == category
        )

    query = query.filter(
        Recipe.cooking_time_minutes >= min_time,
        Recipe.cooking_time_minutes <= max_time
    )

    return query.offset(skip).limit(limit).all()

# Usage:
# GET /recipes?q=chicken&category=quick&min_time=10&max_time=30&skip=0&limit=20
```

### Path Parameters

```python
@router.get("/recipes/{recipe_id}/ingredients/{ingredient_id}")
def get_recipe_ingredient(
    recipe_id: int,
    ingredient_id: int,
    db: DatabaseSession
):
    """Get specific ingredient from recipe."""
    ingredient = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id,
        RecipeIngredient.ingredient_id == ingredient_id
    ).first()

    if not ingredient:
        raise HTTPException(status_code=404, detail="Not found")

    return ingredient
```

### Request Body

```python
from pydantic import BaseModel

class MealPlanRequest(BaseModel):
    """Request schema for meal plan generation."""
    days: int = Field(default=7, ge=1, le=30)
    min_protein_score: float = Field(default=40.0, ge=0, le=100)
    max_carb_score: float = Field(default=40.0, ge=0, le=100)
    include_breakfast: bool = True
    include_lunch: bool = True
    include_dinner: bool = True

@router.post("/meal-plans")
def generate_meal_plan(
    request: MealPlanRequest,
    db: DatabaseSession,
    user: CurrentUser
):
    """Generate a meal plan based on criteria."""
    from src.meal_planner.planner import MealPlanner

    planner = MealPlanner(db)
    meal_plan = planner.generate_weekly_meal_plan(
        min_protein_score=request.min_protein_score,
        max_carb_score=request.max_carb_score,
        include_breakfast=request.include_breakfast,
        include_lunch=request.include_lunch,
        include_dinner=request.include_dinner
    )

    return meal_plan
```

## Configuration

### Environment Variables

```bash
# Server
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/recipes.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost:5432/meals

# JWT
JWT_SECRET=your-super-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["http://localhost:3000","https://myapp.com"]

# Pagination
PAGINATION_DEFAULT_LIMIT=20
PAGINATION_MAX_LIMIT=100
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run API tests only
pytest tests/unit/test_api_core.py -v

# Run with coverage
pytest --cov=src/api --cov-report=html

# Run specific test
pytest tests/unit/test_api_core.py::TestAPIConfig::test_api_config_defaults -v
```

### Manual Testing with Test Client

```python
# test_my_endpoint.py
from fastapi.testclient import TestClient
from src.api.main import create_app

app = create_app()
client = TestClient(app)

def test_get_recipes():
    response = client.get("/api/v1/recipes")
    assert response.status_code == 200
    data = response.json()
    assert "recipes" in data

def test_authenticated_endpoint():
    # Create token
    from src.api.dependencies import create_access_token
    token = create_access_token({"sub": "user123", "role": "user"})

    # Make request
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/profile", headers=headers)

    assert response.status_code == 200
```

### Run Demo

```bash
python examples/api_demo.py
```

## Troubleshooting

### Database Connection Error

```bash
# Initialize database
python -m src.cli init-db

# Check database URL
python -c "from src.api.config import api_config; print(api_config.database_url)"
```

### JWT Token Errors

```python
# Generate a secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in .env
JWT_SECRET=your-generated-secret-here
```

### CORS Errors

```bash
# Add your frontend URL to .env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Import Errors

```bash
# Install dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH=/home/user/meal-planner:$PYTHONPATH
```

## Production Checklist

- [ ] Set strong `JWT_SECRET` (32+ characters)
- [ ] Configure production database (PostgreSQL)
- [ ] Set `API_DEBUG=false`
- [ ] Restrict `CORS_ORIGINS` to actual domains
- [ ] Set up HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up logging and monitoring
- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Set up reverse proxy (nginx)
- [ ] Configure environment-specific settings
- [ ] Set up database backups
- [ ] Implement health checks
- [ ] Set up CI/CD pipeline

## Production Deployment

```bash
# Using Gunicorn with Uvicorn workers
gunicorn src.api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -

# Using Docker
docker build -t meal-planner-api .
docker run -p 8000:8000 \
    -e JWT_SECRET=your-secret \
    -e DATABASE_URL=postgresql://... \
    meal-planner-api

# Using systemd
[Unit]
Description=Meal Planner API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/meal-planner
Environment="PATH=/opt/meal-planner/venv/bin"
ExecStart=/opt/meal-planner/venv/bin/gunicorn src.api.main:app -c gunicorn.conf.py

[Install]
WantedBy=multi-user.target
```

## Useful Commands

```bash
# Start server
uvicorn src.api.main:app --reload

# Run tests
pytest tests/unit/test_api_core.py -v

# Check test coverage
pytest --cov=src/api

# Format code
black src/api

# Type checking
mypy src/api

# Generate OpenAPI schema
python -c "from src.api.main import create_app; import json; app=create_app(); print(json.dumps(app.openapi(), indent=2))" > openapi.json

# Test endpoint with curl
curl -X GET http://localhost:8000/health

# Test with authentication
TOKEN=$(python -c "from src.api.dependencies import create_access_token; print(create_access_token({'sub': 'test'}))")
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/profile
```

## Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- Pydantic Docs: https://docs.pydantic.dev
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- JWT.io: https://jwt.io
- Project Docs: `/home/user/meal-planner/docs/api_documentation.md`
- Examples: `/home/user/meal-planner/examples/api_demo.py`
