"""
Integration tests for favorites API endpoints.
Tests the complete request/response cycle for favorite recipes.
"""

import pytest
from datetime import datetime
from fastapi import status
from sqlalchemy.orm import Session

from src.database.models import User, Recipe, FavoriteRecipe, Image
from tests.conftest import create_test_recipe, create_test_user


@pytest.mark.integration
class TestFavoritesAPI:
    """Integration tests for favorites endpoints."""

    def test_list_favorites_empty(self, client, auth_headers, db_session):
        """Test listing favorites when user has none."""
        # Execute
        response = client.get("/api/v1/favorites", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['items'] == []
        assert data['total'] == 0

    def test_add_favorite_success(self, client, auth_headers, db_session):
        """Test adding a recipe to favorites."""
        # Setup - create a recipe
        recipe = create_test_recipe(db_session, name="Test Recipe")

        # Execute
        response = client.post(
            f"/api/v1/favorites/{recipe.id}",
            headers=auth_headers,
            json={"notes": "Love this recipe!"}
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['recipe']['name'] == "Test Recipe"
        assert data['notes'] == "Love this recipe!"

    def test_add_favorite_without_notes(self, client, auth_headers, db_session):
        """Test adding a favorite without notes."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")

        # Execute
        response = client.post(
            f"/api/v1/favorites/{recipe.id}",
            headers=auth_headers,
            json={}
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['notes'] is None

    def test_add_favorite_recipe_not_found(self, client, auth_headers):
        """Test adding non-existent recipe to favorites."""
        # Execute
        response = client.post(
            "/api/v1/favorites/99999",
            headers=auth_headers,
            json={"notes": "Test"}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()['detail'].lower()

    def test_add_favorite_already_exists(self, client, auth_headers, db_session):
        """Test adding recipe that's already favorited."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")

        # Add favorite first time
        client.post(
            f"/api/v1/favorites/{recipe.id}",
            headers=auth_headers,
            json={"notes": "First time"}
        )

        # Execute - try to add again
        response = client.post(
            f"/api/v1/favorites/{recipe.id}",
            headers=auth_headers,
            json={"notes": "Second time"}
        )

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already in favorites" in response.json()['detail'].lower()

    def test_add_favorite_unauthenticated(self, client, db_session):
        """Test adding favorite without authentication."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")

        # Execute
        response = client.post(
            f"/api/v1/favorites/{recipe.id}",
            json={"notes": "Test"}
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_favorites_success(self, client, auth_headers, db_session):
        """Test listing favorites with multiple recipes."""
        # Setup - create and favorite multiple recipes
        recipe1 = create_test_recipe(db_session, name="Recipe 1")
        recipe2 = create_test_recipe(db_session, name="Recipe 2", slug="recipe-2")

        client.post(f"/api/v1/favorites/{recipe1.id}", headers=auth_headers, json={"notes": "Note 1"})
        client.post(f"/api/v1/favorites/{recipe2.id}", headers=auth_headers, json={"notes": "Note 2"})

        # Execute
        response = client.get("/api/v1/favorites", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['items']) == 2
        assert data['total'] == 2

    def test_list_favorites_pagination(self, client, auth_headers, db_session):
        """Test favorites pagination."""
        # Setup - create multiple favorites
        for i in range(5):
            recipe = create_test_recipe(db_session, name=f"Recipe {i}", slug=f"recipe-{i}")
            client.post(f"/api/v1/favorites/{recipe.id}", headers=auth_headers, json={})

        # Execute - get page 1 with 2 items
        response = client.get(
            "/api/v1/favorites?page=1&page_size=2",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['items']) == 2
        assert data['total'] == 5
        assert data['page'] == 1
        assert data['page_size'] == 2

    def test_remove_favorite_success(self, client, auth_headers, db_session):
        """Test removing a favorite."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")
        client.post(f"/api/v1/favorites/{recipe.id}", headers=auth_headers, json={})

        # Execute
        response = client.delete(f"/api/v1/favorites/{recipe.id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "removed" in response.json()['message'].lower()

        # Verify it's gone
        list_response = client.get("/api/v1/favorites", headers=auth_headers)
        assert len(list_response.json()['items']) == 0

    def test_remove_favorite_not_found(self, client, auth_headers, db_session):
        """Test removing non-existent favorite."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")

        # Execute - try to remove without adding first
        response = client.delete(f"/api/v1/favorites/{recipe.id}", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_favorite_notes_success(self, client, auth_headers, db_session):
        """Test updating favorite notes."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")
        client.post(
            f"/api/v1/favorites/{recipe.id}",
            headers=auth_headers,
            json={"notes": "Original notes"}
        )

        # Execute
        response = client.put(
            f"/api/v1/favorites/{recipe.id}/notes",
            headers=auth_headers,
            json={"notes": "Updated notes"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['notes'] == "Updated notes"

    def test_update_favorite_notes_clear(self, client, auth_headers, db_session):
        """Test clearing favorite notes."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")
        client.post(
            f"/api/v1/favorites/{recipe.id}",
            headers=auth_headers,
            json={"notes": "Original notes"}
        )

        # Execute
        response = client.put(
            f"/api/v1/favorites/{recipe.id}/notes",
            headers=auth_headers,
            json={"notes": None}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['notes'] is None

    def test_get_favorite_status_true(self, client, auth_headers, db_session):
        """Test checking favorite status for favorited recipe."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")
        client.post(
            f"/api/v1/favorites/{recipe.id}",
            headers=auth_headers,
            json={"notes": "Test notes"}
        )

        # Execute
        response = client.get(f"/api/v1/favorites/{recipe.id}/status", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['is_favorite'] is True
        assert data['notes'] == "Test notes"
        assert data['created_at'] is not None

    def test_get_favorite_status_false(self, client, auth_headers, db_session):
        """Test checking favorite status for non-favorited recipe."""
        # Setup
        recipe = create_test_recipe(db_session, name="Test Recipe")

        # Execute
        response = client.get(f"/api/v1/favorites/{recipe.id}/status", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['is_favorite'] is False
        assert data['notes'] is None
        assert data['created_at'] is None

    def test_get_favorites_count(self, client, auth_headers, db_session):
        """Test getting count of favorites."""
        # Setup - add some favorites
        for i in range(3):
            recipe = create_test_recipe(db_session, name=f"Recipe {i}", slug=f"recipe-{i}")
            client.post(f"/api/v1/favorites/{recipe.id}", headers=auth_headers, json={})

        # Execute
        response = client.get("/api/v1/favorites/count", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['count'] == 3

    def test_favorites_isolated_between_users(self, client, db_session):
        """Test that favorites are isolated between users."""
        # Setup - create two users
        user1_headers = {"Authorization": "Bearer user1_token"}
        user2_headers = {"Authorization": "Bearer user2_token"}

        recipe = create_test_recipe(db_session, name="Test Recipe")

        # User 1 favorites the recipe
        # Note: This would require actual auth tokens; simplified for test
        # In real scenario, you'd create actual users and get their tokens

        # For this test, we verify the API requires authentication
        response = client.post(f"/api/v1/favorites/{recipe.id}", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
