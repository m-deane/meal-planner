"""
Integration tests for user preferences router endpoints.
Tests preference management, allergen profiles, and dietary tags.
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.main import app
from src.api.dependencies import get_db
from src.api.services.user_service import UserService
from src.database.models import Allergen, DietaryTag


class TestUsersRouter:
    """Test suite for user preferences and profile endpoints."""

    @pytest.fixture
    def client(self, db_session: Session) -> TestClient:
        """Create test client with database override."""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def test_user(self, db_session: Session) -> dict:
        """Create a test user."""
        user = UserService.create_user(
            db=db_session,
            email="usertest@example.com",
            username="usertest",
            password="TestPass123"
        )

        return {"user": user, "username": "usertest", "password": "TestPass123"}

    @pytest.fixture
    def auth_headers(self, client: TestClient, test_user: dict) -> dict:
        """Get authentication headers."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )

        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def allergens(self, db_session: Session) -> list[Allergen]:
        """Create test allergens."""
        allergen_names = ["Peanuts", "Shellfish", "Dairy", "Gluten", "Eggs"]
        allergens = []

        for name in allergen_names:
            allergen = Allergen(name=name, description=f"{name} allergy")
            db_session.add(allergen)
            allergens.append(allergen)

        db_session.commit()

        for allergen in allergens:
            db_session.refresh(allergen)

        return allergens

    @pytest.fixture
    def dietary_tags(self, db_session: Session) -> list[DietaryTag]:
        """Create test dietary tags."""
        tag_data = [
            ("Vegan", "vegan", "No animal products"),
            ("Vegetarian", "vegetarian", "No meat"),
            ("Keto", "keto", "Low carb"),
            ("Paleo", "paleo", "Primal diet")
        ]
        tags = []

        for name, slug, desc in tag_data:
            tag = DietaryTag(name=name, slug=slug, description=desc)
            db_session.add(tag)
            tags.append(tag)

        db_session.commit()

        for tag in tags:
            db_session.refresh(tag)

        return tags

    # ========================================================================
    # PREFERENCE ENDPOINTS
    # ========================================================================

    def test_get_preferences(self, client: TestClient, auth_headers: dict):
        """Test getting user preferences."""
        response = client.get("/users/me/preferences", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "user_id" in data
        assert data["default_servings"] == 2
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_preferences_no_auth(self, client: TestClient):
        """Test getting preferences without authentication."""
        response = client.get("/users/me/preferences")

        assert response.status_code == 401

    def test_update_preferences(self, client: TestClient, auth_headers: dict):
        """Test updating user preferences."""
        response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={
                "default_servings": 4,
                "calorie_target": 2000,
                "protein_target_g": 150,
                "carb_limit_g": 200,
                "fat_limit_g": 70
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["default_servings"] == 4
        assert data["calorie_target"] == 2000
        assert float(data["protein_target_g"]) == 150.0
        assert float(data["carb_limit_g"]) == 200.0
        assert float(data["fat_limit_g"]) == 70.0

    def test_update_preferences_partial(self, client: TestClient, auth_headers: dict):
        """Test partial update of preferences."""
        response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={"default_servings": 6}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["default_servings"] == 6

    def test_update_preferences_invalid_values(self, client: TestClient, auth_headers: dict):
        """Test update fails with invalid values."""
        response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={"default_servings": -1}
        )

        assert response.status_code == 422

    def test_update_preferences_no_auth(self, client: TestClient):
        """Test updating preferences without authentication."""
        response = client.put(
            "/users/me/preferences",
            json={"default_servings": 4}
        )

        assert response.status_code == 401

    # ========================================================================
    # ALLERGEN PROFILE ENDPOINTS
    # ========================================================================

    def test_get_allergens_empty(self, client: TestClient, auth_headers: dict):
        """Test getting allergens when user has none."""
        response = client.get("/users/me/allergens", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["allergens"] == []
        assert data["count"] == 0

    def test_add_single_allergen(
        self, client: TestClient, auth_headers: dict, allergens: list[Allergen]
    ):
        """Test adding a single allergen."""
        response = client.post(
            "/users/me/allergens",
            headers=auth_headers,
            json={
                "allergen_id": allergens[0].id,
                "severity": "severe"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["allergen_id"] == allergens[0].id
        assert data["severity"] == "severe"
        assert "allergen" in data
        assert data["allergen"]["name"] == "Peanuts"

    def test_add_allergen_invalid_severity(
        self, client: TestClient, auth_headers: dict, allergens: list[Allergen]
    ):
        """Test adding allergen with invalid severity."""
        response = client.post(
            "/users/me/allergens",
            headers=auth_headers,
            json={
                "allergen_id": allergens[0].id,
                "severity": "invalid"
            }
        )

        assert response.status_code == 422

    def test_add_allergen_nonexistent(self, client: TestClient, auth_headers: dict):
        """Test adding non-existent allergen."""
        response = client.post(
            "/users/me/allergens",
            headers=auth_headers,
            json={
                "allergen_id": 99999,
                "severity": "severe"
            }
        )

        assert response.status_code == 400

    def test_update_allergen_severity(
        self, client: TestClient, auth_headers: dict, allergens: list[Allergen]
    ):
        """Test updating allergen severity."""
        # Add allergen
        client.post(
            "/users/me/allergens",
            headers=auth_headers,
            json={"allergen_id": allergens[0].id, "severity": "avoid"}
        )

        # Update severity
        response = client.post(
            "/users/me/allergens",
            headers=auth_headers,
            json={"allergen_id": allergens[0].id, "severity": "trace_ok"}
        )

        assert response.status_code == 201
        assert response.json()["severity"] == "trace_ok"

        # Verify only one entry exists
        get_response = client.get("/users/me/allergens", headers=auth_headers)
        assert len(get_response.json()["allergens"]) == 1

    def test_bulk_update_allergens(
        self, client: TestClient, auth_headers: dict, allergens: list[Allergen]
    ):
        """Test bulk updating allergen profile."""
        response = client.put(
            "/users/me/allergens",
            headers=auth_headers,
            json={
                "allergens": [
                    {"allergen_id": allergens[0].id, "severity": "severe"},
                    {"allergen_id": allergens[1].id, "severity": "avoid"},
                    {"allergen_id": allergens[2].id, "severity": "trace_ok"}
                ]
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 3
        assert len(data["allergens"]) == 3

        severities = {a["allergen_id"]: a["severity"] for a in data["allergens"]}
        assert severities[allergens[0].id] == "severe"
        assert severities[allergens[1].id] == "avoid"
        assert severities[allergens[2].id] == "trace_ok"

    def test_bulk_update_replaces_existing(
        self, client: TestClient, auth_headers: dict, allergens: list[Allergen]
    ):
        """Test bulk update replaces existing allergens."""
        # Add initial allergens
        client.put(
            "/users/me/allergens",
            headers=auth_headers,
            json={
                "allergens": [
                    {"allergen_id": allergens[0].id, "severity": "severe"},
                    {"allergen_id": allergens[1].id, "severity": "avoid"}
                ]
            }
        )

        # Replace with new set
        response = client.put(
            "/users/me/allergens",
            headers=auth_headers,
            json={
                "allergens": [
                    {"allergen_id": allergens[2].id, "severity": "trace_ok"}
                ]
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert data["allergens"][0]["allergen_id"] == allergens[2].id

    def test_remove_allergen(
        self, client: TestClient, auth_headers: dict, allergens: list[Allergen]
    ):
        """Test removing an allergen."""
        # Add allergen
        client.post(
            "/users/me/allergens",
            headers=auth_headers,
            json={"allergen_id": allergens[0].id, "severity": "severe"}
        )

        # Remove it
        response = client.delete(
            f"/users/me/allergens/{allergens[0].id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get("/users/me/allergens", headers=auth_headers)
        assert get_response.json()["count"] == 0

    def test_remove_allergen_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test removing non-existent allergen."""
        response = client.delete(
            "/users/me/allergens/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_allergens_no_auth(self, client: TestClient, allergens: list[Allergen]):
        """Test allergen endpoints without authentication."""
        # GET
        assert client.get("/users/me/allergens").status_code == 401

        # POST
        assert client.post(
            "/users/me/allergens",
            json={"allergen_id": allergens[0].id, "severity": "severe"}
        ).status_code == 401

        # PUT
        assert client.put(
            "/users/me/allergens",
            json={"allergens": []}
        ).status_code == 401

        # DELETE
        assert client.delete(
            f"/users/me/allergens/{allergens[0].id}"
        ).status_code == 401

    # ========================================================================
    # DIETARY TAGS ENDPOINTS
    # ========================================================================

    def test_get_dietary_tags_empty(self, client: TestClient, auth_headers: dict):
        """Test getting dietary tags when user has none."""
        response = client.get("/users/me/dietary-tags", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["dietary_tags"] == []
        assert data["count"] == 0

    def test_set_dietary_tags(
        self, client: TestClient, auth_headers: dict, dietary_tags: list[DietaryTag]
    ):
        """Test setting dietary tags."""
        response = client.put(
            "/users/me/dietary-tags",
            headers=auth_headers,
            json={
                "dietary_tag_ids": [dietary_tags[0].id, dietary_tags[2].id]
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 2
        tag_ids = [tag["id"] for tag in data["dietary_tags"]]
        assert dietary_tags[0].id in tag_ids
        assert dietary_tags[2].id in tag_ids

    def test_set_dietary_tags_replaces_existing(
        self, client: TestClient, auth_headers: dict, dietary_tags: list[DietaryTag]
    ):
        """Test setting tags replaces existing ones."""
        # Set initial tags
        client.put(
            "/users/me/dietary-tags",
            headers=auth_headers,
            json={"dietary_tag_ids": [dietary_tags[0].id, dietary_tags[1].id]}
        )

        # Replace with new tags
        response = client.put(
            "/users/me/dietary-tags",
            headers=auth_headers,
            json={"dietary_tag_ids": [dietary_tags[2].id]}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert data["dietary_tags"][0]["id"] == dietary_tags[2].id

    def test_set_dietary_tags_empty_list(
        self, client: TestClient, auth_headers: dict, dietary_tags: list[DietaryTag]
    ):
        """Test setting empty dietary tags list."""
        # Add some tags first
        client.put(
            "/users/me/dietary-tags",
            headers=auth_headers,
            json={"dietary_tag_ids": [dietary_tags[0].id]}
        )

        # Clear tags
        response = client.put(
            "/users/me/dietary-tags",
            headers=auth_headers,
            json={"dietary_tag_ids": []}
        )

        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_dietary_tags_no_auth(self, client: TestClient):
        """Test dietary tag endpoints without authentication."""
        # GET
        assert client.get("/users/me/dietary-tags").status_code == 401

        # PUT
        assert client.put(
            "/users/me/dietary-tags",
            json={"dietary_tag_ids": [1, 2]}
        ).status_code == 401

    # ========================================================================
    # COMBINED WORKFLOW TESTS
    # ========================================================================

    def test_complete_user_profile_setup(
        self,
        client: TestClient,
        auth_headers: dict,
        allergens: list[Allergen],
        dietary_tags: list[DietaryTag]
    ):
        """Test complete user profile setup workflow."""
        # 1. Update preferences
        prefs_response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={
                "default_servings": 4,
                "calorie_target": 2000,
                "protein_target_g": 150
            }
        )
        assert prefs_response.status_code == 200

        # 2. Set allergens
        allergen_response = client.put(
            "/users/me/allergens",
            headers=auth_headers,
            json={
                "allergens": [
                    {"allergen_id": allergens[0].id, "severity": "severe"},
                    {"allergen_id": allergens[2].id, "severity": "avoid"}
                ]
            }
        )
        assert allergen_response.status_code == 200
        assert allergen_response.json()["count"] == 2

        # 3. Set dietary tags
        tags_response = client.put(
            "/users/me/dietary-tags",
            headers=auth_headers,
            json={"dietary_tag_ids": [dietary_tags[0].id, dietary_tags[1].id]}
        )
        assert tags_response.status_code == 200
        assert tags_response.json()["count"] == 2

        # 4. Verify all settings
        get_prefs = client.get("/users/me/preferences", headers=auth_headers)
        assert get_prefs.json()["default_servings"] == 4

        get_allergens = client.get("/users/me/allergens", headers=auth_headers)
        assert get_allergens.json()["count"] == 2

        get_tags = client.get("/users/me/dietary-tags", headers=auth_headers)
        assert get_tags.json()["count"] == 2
