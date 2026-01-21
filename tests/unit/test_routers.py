"""
Unit tests for FastAPI routers.
Tests all API endpoints for recipes, categories, meal plans, and shopping lists.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.database.models import Category, DietaryTag, Allergen


class TestRecipesRouter:
    """Test recipe endpoints."""

    @pytest.fixture
    def client(self, db_session):
        """Create test client with mocked database."""
        with patch("src.api.main.check_connection", return_value=True):
            app = create_app()

            def override_get_db():
                try:
                    yield db_session
                finally:
                    pass

            from src.api.dependencies import get_db
            app.dependency_overrides[get_db] = override_get_db

            with TestClient(app) as test_client:
                yield test_client

    def test_list_recipes_default(self, client):
        """Test listing recipes with default pagination."""
        with patch("src.api.routers.recipes.RecipeService") as mock_service:
            # Mock service response
            mock_service.return_value.get_recipes.return_value = {
                'recipes': [],
                'total': 0,
                'limit': 20,
                'offset': 0
            }

            response = client.get("/recipes")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data

    def test_list_recipes_with_filters(self, client):
        """Test listing recipes with filters."""
        with patch("src.api.routers.recipes.RecipeService") as mock_service:
            mock_service.return_value.get_recipes.return_value = {
                'recipes': [],
                'total': 0,
                'limit': 20,
                'offset': 0
            }

            response = client.get(
                "/recipes",
                params={
                    "category_slugs": ["italian", "pasta"],
                    "max_cooking_time": 30,
                    "min_protein": 20
                }
            )

            assert response.status_code == 200

    def test_search_recipes(self, client):
        """Test recipe search endpoint."""
        with patch("src.api.routers.recipes.RecipeService") as mock_service:
            mock_service.return_value.search_recipes.return_value = {
                'recipes': [],
                'query': 'pasta',
                'count': 0,
                'limit': 20,
                'offset': 0
            }

            response = client.get("/recipes/search", params={"q": "pasta"})

            assert response.status_code == 200
            data = response.json()
            assert "items" in data

    def test_get_recipe_by_id_success(self, client):
        """Test getting recipe by ID."""
        with patch("src.api.routers.recipes.RecipeService") as mock_service:
            mock_service.return_value.get_recipe_by_id.return_value = {
                'id': 1,
                'gousto_id': 'gousto-123',
                'slug': 'test-recipe',
                'name': 'Test Recipe',
                'description': 'Test description',
                'cooking_time_minutes': 30,
                'prep_time_minutes': 15,
                'total_time_minutes': 45,
                'difficulty': 'medium',
                'servings': 2,
                'source_url': 'https://example.com',
                'date_scraped': '2026-01-20T10:00:00',
                'last_updated': '2026-01-20T10:00:00',
                'is_active': True,
                'ingredients': [],
                'instructions': [],
                'categories': [],
                'dietary_tags': [],
                'allergens': [],
                'images': [],
                'nutritional_info': None
            }

            response = client.get("/recipes/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["name"] == "Test Recipe"

    def test_get_recipe_by_id_not_found(self, client):
        """Test getting non-existent recipe."""
        with patch("src.api.routers.recipes.RecipeService") as mock_service:
            mock_service.return_value.get_recipe_by_id.return_value = None

            response = client.get("/recipes/999")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_get_recipe_nutrition(self, client):
        """Test getting recipe nutrition."""
        with patch("src.api.routers.recipes.RecipeService") as mock_service:
            mock_service.return_value.get_recipe_nutrition.return_value = {
                'calories': 500,
                'protein_g': 30,
                'carbohydrates_g': 40,
                'fat_g': 20,
                'fiber_g': 5,
                'sugar_g': 10,
                'sodium_mg': 600
            }

            response = client.get("/recipes/1/nutrition")

            assert response.status_code == 200
            data = response.json()
            # Pydantic may return Decimal as string
            assert float(data["calories"]) == 500
            assert float(data["protein_g"]) == 30

    def test_get_recipe_ingredients(self, client):
        """Test getting recipe ingredients."""
        with patch("src.api.routers.recipes.RecipeService") as mock_service:
            mock_service.return_value.get_recipe_ingredients.return_value = [
                {
                    'name': 'Chicken Breast',
                    'quantity': 300,
                    'unit': 'g',
                    'unit_name': 'grams',
                    'preparation': 'diced',
                    'optional': False,
                    'display_order': 1
                }
            ]

            response = client.get("/recipes/1/ingredients")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "Chicken Breast"


class TestCategoriesRouter:
    """Test category endpoints."""

    @pytest.fixture
    def client(self, db_session):
        """Create test client with database."""
        with patch("src.api.main.check_connection", return_value=True):
            app = create_app()

            def override_get_db():
                try:
                    yield db_session
                finally:
                    pass

            from src.api.dependencies import get_db
            app.dependency_overrides[get_db] = override_get_db

            with TestClient(app) as test_client:
                yield test_client

    def test_list_categories(self, client, db_session):
        """Test listing all categories."""
        # Add test category
        category = Category(
            name="Italian",
            slug="italian",
            category_type="cuisine",
            description="Italian cuisine"
        )
        db_session.add(category)
        db_session.commit()

        response = client.get("/categories")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_dietary_tags(self, client, db_session):
        """Test listing dietary tags."""
        # Add test dietary tag
        tag = DietaryTag(
            name="Vegan",
            slug="vegan",
            description="Contains no animal products"
        )
        db_session.add(tag)
        db_session.commit()

        response = client.get("/dietary-tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_allergens(self, client, db_session):
        """Test listing allergens."""
        # Add test allergen
        allergen = Allergen(
            name="Dairy",
            description="Contains milk products"
        )
        db_session.add(allergen)
        db_session.commit()

        response = client.get("/allergens")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestMealPlansRouter:
    """Test meal plan endpoints."""

    @pytest.fixture
    def client(self, db_session):
        """Create test client."""
        with patch("src.api.main.check_connection", return_value=True):
            app = create_app()

            def override_get_db():
                try:
                    yield db_session
                finally:
                    pass

            from src.api.dependencies import get_db
            app.dependency_overrides[get_db] = override_get_db

            with TestClient(app) as test_client:
                yield test_client

    def test_generate_meal_plan(self, client):
        """Test basic meal plan generation."""
        with patch("src.api.routers.meal_plans.MealPlanService") as mock_service:
            mock_service.return_value.generate_meal_plan.return_value = {
                'plan': {},
                'weekly_totals': None,
                'weekly_averages': None,
                'metadata': {
                    'generated_at': '2026-01-20T10:00:00',
                    'total_days': 7,
                    'total_meals': 21
                }
            }

            response = client.post("/meal-plans/generate")

            assert response.status_code == 201
            data = response.json()
            assert "plan" in data
            assert "metadata" in data

    def test_generate_nutrition_meal_plan(self, client):
        """Test nutrition-based meal plan generation."""
        with patch("src.api.routers.meal_plans.MealPlanService") as mock_service:
            mock_service.return_value.generate_nutrition_meal_plan.return_value = {
                'plan': {},
                'weekly_totals': {'calories': 14000, 'protein_g': 840},
                'weekly_averages': {'calories': 2000, 'protein_g': 120},
                'metadata': {
                    'generated_at': '2026-01-20T10:00:00',
                    'total_days': 7
                }
            }

            response = client.post(
                "/meal-plans/generate-nutrition",
                params={
                    "min_protein_g": 25.0,
                    "max_carbs_g": 30.0
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert "weekly_totals" in data


class TestShoppingListsRouter:
    """Test shopping list endpoints."""

    @pytest.fixture
    def client(self, db_session):
        """Create test client."""
        with patch("src.api.main.check_connection", return_value=True):
            app = create_app()

            def override_get_db():
                try:
                    yield db_session
                finally:
                    pass

            from src.api.dependencies import get_db
            app.dependency_overrides[get_db] = override_get_db

            with TestClient(app) as test_client:
                yield test_client

    def test_generate_shopping_list(self, client):
        """Test shopping list generation from recipe IDs."""
        with patch("src.api.routers.shopping_lists.ShoppingListService") as mock_service:
            mock_service.return_value.generate_from_recipes.return_value = {
                'categories': [],
                'summary': {
                    'total_items': 0,
                    'total_categories': 0,
                    'recipes_count': 2
                },
                'recipe_ids': [1, 2]
            }

            response = client.post(
                "/shopping-lists/generate",
                json={
                    "recipe_ids": [1, 2],
                    "combine_similar": True
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert "categories" in data
            assert "summary" in data

    def test_generate_shopping_list_empty_recipes(self, client):
        """Test shopping list generation with empty recipe list."""
        response = client.post(
            "/shopping-lists/generate",
            json={
                "recipe_ids": [],
                "combine_similar": True
            }
        )

        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"].lower()

    def test_generate_compact_shopping_list(self, client):
        """Test compact shopping list generation."""
        with patch("src.api.routers.shopping_lists.ShoppingListService") as mock_service:
            mock_service.return_value.generate_compact_shopping_list.return_value = {
                'categories': {},
                'summary': {
                    'total_items': 0,
                    'total_categories': 0
                }
            }

            response = client.post(
                "/shopping-lists/generate-compact",
                json={"recipe_ids": [1, 2]}
            )

            assert response.status_code == 201
            data = response.json()
            assert "categories" in data
            assert "summary" in data
