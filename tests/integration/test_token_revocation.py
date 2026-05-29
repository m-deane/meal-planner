"""
Integration tests for token revocation and account-status enforcement
(logout, password change, expired tokens, deactivated accounts).
"""

from datetime import timedelta

from fastapi.testclient import TestClient

from src.api.dependencies import create_access_token


class TestTokenRevocation:
    def test_logout_revokes_token(self, client: TestClient, test_user, auth_headers):
        # Token works before logout.
        assert client.get("/auth/me", headers=auth_headers).status_code == 200

        # Log out (revokes via token_version bump).
        assert client.post("/auth/logout", headers=auth_headers).status_code == 200

        # The same token is now rejected.
        assert client.get("/auth/me", headers=auth_headers).status_code == 401

    def test_password_change_revokes_old_tokens(self, client: TestClient, test_user, auth_headers):
        resp = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={"current_password": test_user.password, "new_password": "NewPass456"},
        )
        assert resp.status_code == 200
        # Old token no longer valid after password change.
        assert client.get("/auth/me", headers=auth_headers).status_code == 401

    def test_refresh_issues_working_token(self, client: TestClient, test_user, auth_headers):
        resp = client.post("/auth/refresh", headers=auth_headers)
        assert resp.status_code == 200
        new_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {new_token}"}
        assert client.get("/auth/me", headers=headers).status_code == 200

    def test_verify_endpoint(self, client: TestClient, test_user, auth_headers):
        resp = client.get("/auth/verify", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == test_user.username

    def test_expired_token_rejected(self, client: TestClient, test_user):
        expired = create_access_token(
            {"sub": str(test_user.id), "ver": 0},
            expires_delta=timedelta(seconds=-1),
        )
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
        assert resp.status_code == 401

    def test_deactivated_account_rejected(self, client: TestClient, test_user, auth_headers, db_session):
        from src.database.models import User
        user = db_session.query(User).filter(User.id == test_user.id).first()
        user.is_active = False
        db_session.commit()

        assert client.get("/auth/me", headers=auth_headers).status_code == 401
