from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient

import web.routes.users as users_routes
from web.app import create_app
from web.security import require_admin


@dataclass
class DummyUser:
    id: str
    email: str
    display_name: str
    provider: str
    provider_id: str
    is_admin: bool
    created_at: datetime
    last_login_at: datetime


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummySessionMaker:
    def __call__(self):
        return DummySession()


class DummyAdmin:
    is_admin = True


def test_admin_user_detail_renders() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_get_user_by_id(session, user_id: str):
        return DummyUser(
            id=user_id,
            email="admin@example.com",
            display_name="Admin User",
            provider="github",
            provider_id="123",
            is_admin=True,
            created_at=datetime(2026, 1, 19, tzinfo=timezone.utc),
            last_login_at=datetime(2026, 1, 20, tzinfo=timezone.utc),
        )

    original_get = users_routes.get_user_by_id
    users_routes.get_user_by_id = fake_get_user_by_id

    try:
        client = TestClient(app)
        response = client.get("/admin/users/user-1")

        assert response.status_code == 200
        assert "admin@example.com" in response.text
    finally:
        users_routes.get_user_by_id = original_get
