"""
Unit tests for FavoritesService.
Tests favorite recipe management operations.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi import HTTPException

from src.api.services.favorites_service import FavoritesService
from src.database.models import FavoriteRecipe, Recipe, User, Image


class TestFavoritesService:
    """Test suite for FavoritesService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_db):
        """Create FavoritesService instance."""
        return FavoritesService(mock_db)

    @pytest.fixture
    def sample_recipe(self):
        """Create sample recipe for testing."""
        recipe = Mock(spec=Recipe)
        recipe.id = 1
        recipe.slug = "test-recipe"
        recipe.name = "Test Recipe"
        recipe.description = "A test recipe"
        recipe.cooking_time_minutes = 30
        recipe.difficulty = "easy"
        recipe.images = []
        return recipe

    @pytest.fixture
    def sample_favorite(self, sample_recipe):
        """Create sample favorite for testing."""
        favorite = Mock(spec=FavoriteRecipe)
        favorite.id = 1
        favorite.user_id = 1
        favorite.recipe_id = 1
        favorite.notes = "Love this recipe!"
        favorite.created_at = datetime(2026, 1, 15)
        favorite.recipe = sample_recipe
        return favorite

    def test_get_user_favorites_success(self, service, mock_db, sample_favorite):
        """Test getting user's favorites successfully."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_favorite]

        # Execute
        result = service.get_user_favorites(user_id=1, skip=0, limit=20)

        # Assert
        assert len(result) == 1
        assert result[0]['id'] == 1
        assert result[0]['recipe']['name'] == "Test Recipe"
        assert result[0]['notes'] == "Love this recipe!"

    def test_add_favorite_success(self, service, mock_db, sample_recipe):
        """Test adding a recipe to favorites successfully."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [sample_recipe, None]  # Recipe exists, not favorited

        new_favorite = Mock(spec=FavoriteRecipe)
        new_favorite.id = 1
        new_favorite.user_id = 1
        new_favorite.recipe_id = 1
        new_favorite.notes = "Great recipe!"
        new_favorite.created_at = datetime.utcnow()
        new_favorite.recipe = sample_recipe

        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 1))

        # Execute
        with patch.object(FavoriteRecipe, '__init__', return_value=None):
            with patch('src.api.services.favorites_service.FavoriteRecipe', return_value=new_favorite):
                result = service.add_favorite(user_id=1, recipe_id=1, notes="Great recipe!")

        # Assert
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_add_favorite_recipe_not_found(self, service, mock_db):
        """Test adding favorite when recipe doesn't exist."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.add_favorite(user_id=1, recipe_id=999, notes="Test")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    def test_add_favorite_already_exists(self, service, mock_db, sample_recipe, sample_favorite):
        """Test adding favorite when recipe is already favorited."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [sample_recipe, sample_favorite]

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.add_favorite(user_id=1, recipe_id=1, notes="Test")

        assert exc_info.value.status_code == 409
        assert "already in favorites" in exc_info.value.detail

    def test_remove_favorite_success(self, service, mock_db, sample_favorite):
        """Test removing a favorite successfully."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_favorite

        # Execute
        result = service.remove_favorite(user_id=1, recipe_id=1)

        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(sample_favorite)
        mock_db.commit.assert_called_once()

    def test_remove_favorite_not_found(self, service, mock_db):
        """Test removing favorite when it doesn't exist."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.remove_favorite(user_id=1, recipe_id=1)

        assert exc_info.value.status_code == 404
        assert "not found in favorites" in exc_info.value.detail

    def test_update_favorite_notes_success(self, service, mock_db, sample_favorite):
        """Test updating favorite notes successfully."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_favorite

        # Execute
        result = service.update_favorite_notes(user_id=1, recipe_id=1, notes="Updated notes")

        # Assert
        assert sample_favorite.notes == "Updated notes"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_favorite_notes_not_found(self, service, mock_db):
        """Test updating notes when favorite doesn't exist."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.update_favorite_notes(user_id=1, recipe_id=1, notes="Test")

        assert exc_info.value.status_code == 404

    def test_is_favorite_true(self, service, mock_db, sample_favorite):
        """Test checking if recipe is favorited (True case)."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_favorite

        # Execute
        is_fav, data = service.is_favorite(user_id=1, recipe_id=1)

        # Assert
        assert is_fav is True
        assert data is not None
        assert data['notes'] == "Love this recipe!"

    def test_is_favorite_false(self, service, mock_db):
        """Test checking if recipe is favorited (False case)."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Execute
        is_fav, data = service.is_favorite(user_id=1, recipe_id=1)

        # Assert
        assert is_fav is False
        assert data is None

    def test_get_favorite_count(self, service, mock_db):
        """Test getting count of user's favorites."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        # Execute
        result = service.get_favorite_count(user_id=1)

        # Assert
        assert result == 5

    def test_serialize_favorite_with_image(self, service, sample_favorite):
        """Test serializing favorite with recipe image."""
        # Setup
        image = Mock(spec=Image)
        image.url = "https://example.com/image.jpg"
        image.image_type = "hero"
        sample_favorite.recipe.images = [image]

        # Execute
        result = service._serialize_favorite(sample_favorite)

        # Assert
        assert result['recipe']['image_url'] == "https://example.com/image.jpg"
        assert result['recipe']['name'] == "Test Recipe"

    def test_serialize_favorite_without_image(self, service, sample_favorite):
        """Test serializing favorite without recipe image."""
        # Execute
        result = service._serialize_favorite(sample_favorite)

        # Assert
        assert result['recipe']['image_url'] is None
        assert result['recipe']['name'] == "Test Recipe"
