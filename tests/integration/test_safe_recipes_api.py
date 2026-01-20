"""
Integration tests for safe recipes API endpoints.
Tests allergen filtering and warnings functionality.
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from src.database.models import Recipe, Allergen, UserAllergen, RecipeAllergen
from tests.conftest import create_test_recipe, create_test_user


@pytest.mark.integration
class TestSafeRecipesAPI:
    """Integration tests for safe recipes endpoints."""

    @pytest.fixture
    def allergen_peanuts(self, db_session):
        """Create peanuts allergen."""
        allergen = Allergen(id=1, name="Peanuts")
        db_session.add(allergen)
        db_session.commit()
        return allergen

    @pytest.fixture
    def allergen_dairy(self, db_session):
        """Create dairy allergen."""
        allergen = Allergen(id=2, name="Dairy")
        db_session.add(allergen)
        db_session.commit()
        return allergen

    @pytest.fixture
    def recipe_with_peanuts(self, db_session, allergen_peanuts):
        """Create recipe containing peanuts."""
        recipe = create_test_recipe(db_session, name="Peanut Butter Cookies")
        recipe_allergen = RecipeAllergen(recipe_id=recipe.id, allergen_id=allergen_peanuts.id)
        db_session.add(recipe_allergen)
        db_session.commit()
        return recipe

    @pytest.fixture
    def safe_recipe(self, db_session):
        """Create recipe without allergens."""
        return create_test_recipe(db_session, name="Vegetable Stir Fry", slug="vegetable-stir-fry")

    @pytest.fixture
    def user_with_peanut_allergy(self, db_session, test_user, allergen_peanuts):
        """Create user with peanut allergy."""
        user_allergen = UserAllergen(
            user_id=test_user.id,
            allergen_id=allergen_peanuts.id,
            severity="severe"
        )
        db_session.add(user_allergen)
        db_session.commit()
        return test_user

    def test_get_safe_recipes_unauthenticated(self, client):
        """Test getting safe recipes without authentication."""
        # Execute
        response = client.get("/api/v1/recipes/safe")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_safe_recipes_no_allergens(self, client, auth_headers, db_session, safe_recipe):
        """Test getting safe recipes when user has no allergen profile."""
        # Execute
        response = client.get("/api/v1/recipes/safe", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'items' in data

    def test_get_safe_recipes_excludes_allergens(
        self,
        client,
        auth_headers,
        db_session,
        user_with_peanut_allergy,
        recipe_with_peanuts,
        safe_recipe
    ):
        """Test that safe recipes excludes recipes with user's allergens."""
        # Execute
        response = client.get("/api/v1/recipes/safe", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should only include safe recipe, not the one with peanuts
        recipe_names = [item['name'] for item in data['items']]
        assert "Vegetable Stir Fry" in recipe_names
        assert "Peanut Butter Cookies" not in recipe_names

    def test_get_safe_recipes_with_filters(
        self,
        client,
        auth_headers,
        db_session,
        user_with_peanut_allergy,
        safe_recipe
    ):
        """Test safe recipes with additional filters."""
        # Execute
        response = client.get(
            "/api/v1/recipes/safe?max_cooking_time=30&difficulty=easy",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'items' in data

    def test_get_safe_recipes_pagination(
        self,
        client,
        auth_headers,
        db_session,
        user_with_peanut_allergy
    ):
        """Test safe recipes pagination."""
        # Setup - create multiple safe recipes
        for i in range(5):
            create_test_recipe(db_session, name=f"Safe Recipe {i}", slug=f"safe-recipe-{i}")

        # Execute
        response = client.get(
            "/api/v1/recipes/safe?page=1&page_size=2",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['items']) <= 2
        assert data['page'] == 1

    def test_get_allergen_warnings_no_allergens(
        self,
        client,
        auth_headers,
        db_session,
        safe_recipe
    ):
        """Test allergen warnings for recipe without allergens."""
        # Execute
        response = client.get(
            f"/api/v1/recipes/{safe_recipe.id}/allergen-warnings",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['recipe_id'] == safe_recipe.id
        assert data['is_safe'] is True
        assert len(data['warnings']) == 0

    def test_get_allergen_warnings_with_severe_allergen(
        self,
        client,
        auth_headers,
        db_session,
        user_with_peanut_allergy,
        recipe_with_peanuts
    ):
        """Test allergen warnings for recipe with user's severe allergen."""
        # Execute
        response = client.get(
            f"/api/v1/recipes/{recipe_with_peanuts.id}/allergen-warnings",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['recipe_id'] == recipe_with_peanuts.id
        assert data['is_safe'] is False
        assert len(data['warnings']) > 0

        # Check warning details
        warning = data['warnings'][0]
        assert warning['allergen_name'] == "Peanuts"
        assert warning['severity'] == "severe"
        assert "SEVERE" in warning['message']

    def test_get_allergen_warnings_recipe_not_found(self, client, auth_headers):
        """Test allergen warnings for non-existent recipe."""
        # Execute
        response = client.get(
            "/api/v1/recipes/99999/allergen-warnings",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_allergen_warnings_unauthenticated(self, client, db_session, safe_recipe):
        """Test allergen warnings without authentication."""
        # Execute
        response = client.get(f"/api/v1/recipes/{safe_recipe.id}/allergen-warnings")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_allergen_substitutions(
        self,
        client,
        auth_headers,
        db_session,
        user_with_peanut_allergy,
        recipe_with_peanuts
    ):
        """Test getting allergen substitutions for a recipe."""
        # Execute
        response = client.get(
            f"/api/v1/recipes/{recipe_with_peanuts.id}/allergen-substitutions",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # If substitutions are found, verify structure
        if len(data) > 0:
            substitution = data[0]
            assert 'original_ingredient' in substitution
            assert 'allergen' in substitution
            assert 'substitutes' in substitution
            assert isinstance(substitution['substitutes'], list)

    def test_get_allergen_substitutions_safe_recipe(
        self,
        client,
        auth_headers,
        db_session,
        user_with_peanut_allergy,
        safe_recipe
    ):
        """Test getting substitutions for recipe without user's allergens."""
        # Execute
        response = client.get(
            f"/api/v1/recipes/{safe_recipe.id}/allergen-substitutions",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should be empty since recipe doesn't contain user's allergens
        assert len(data) == 0

    def test_get_allergen_substitutions_recipe_not_found(self, client, auth_headers):
        """Test substitutions for non-existent recipe."""
        # Execute
        response = client.get(
            "/api/v1/recipes/99999/allergen-substitutions",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_safe_recipes_with_trace_ok_severity(
        self,
        client,
        auth_headers,
        db_session,
        test_user,
        allergen_dairy,
        safe_recipe
    ):
        """Test that recipes with trace_ok allergen are included in safe recipes."""
        # Setup - create user allergen with trace_ok severity
        user_allergen = UserAllergen(
            user_id=test_user.id,
            allergen_id=allergen_dairy.id,
            severity="trace_ok"
        )
        db_session.add(user_allergen)

        # Create recipe with dairy
        dairy_recipe = create_test_recipe(db_session, name="Cheese Pizza", slug="cheese-pizza")
        recipe_allergen = RecipeAllergen(recipe_id=dairy_recipe.id, allergen_id=allergen_dairy.id)
        db_session.add(recipe_allergen)
        db_session.commit()

        # Execute
        response = client.get("/api/v1/recipes/safe", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # With trace_ok, the dairy recipe should be included
        recipe_names = [item['name'] for item in data['items']]
        assert "Cheese Pizza" in recipe_names

    def test_safe_recipes_multiple_allergens(
        self,
        client,
        auth_headers,
        db_session,
        test_user,
        allergen_peanuts,
        allergen_dairy
    ):
        """Test safe recipes filtering with multiple user allergens."""
        # Setup - add multiple allergens to user
        ua1 = UserAllergen(user_id=test_user.id, allergen_id=allergen_peanuts.id, severity="severe")
        ua2 = UserAllergen(user_id=test_user.id, allergen_id=allergen_dairy.id, severity="avoid")
        db_session.add_all([ua1, ua2])

        # Create recipes with different allergens
        safe_recipe = create_test_recipe(db_session, name="Safe Recipe", slug="safe-recipe")

        peanut_recipe = create_test_recipe(db_session, name="Peanut Recipe", slug="peanut-recipe")
        db_session.add(RecipeAllergen(recipe_id=peanut_recipe.id, allergen_id=allergen_peanuts.id))

        dairy_recipe = create_test_recipe(db_session, name="Dairy Recipe", slug="dairy-recipe")
        db_session.add(RecipeAllergen(recipe_id=dairy_recipe.id, allergen_id=allergen_dairy.id))

        db_session.commit()

        # Execute
        response = client.get("/api/v1/recipes/safe", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        recipe_names = [item['name'] for item in data['items']]
        assert "Safe Recipe" in recipe_names
        assert "Peanut Recipe" not in recipe_names
        assert "Dairy Recipe" not in recipe_names
