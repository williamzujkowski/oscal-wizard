from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient

import web.routes.users as users_routes
from web.app import create_app
from web.security import require_admin


@dataclass
class DummyUser:
    email: str
    provider: str
    is_admin: bool
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


def test_admin_users_page_renders() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_list_users(session):
        return [
            DummyUser(
                email="admin@example.com",
                provider="github",
                is_admin=True,
                last_login_at=datetime(2026, 1, 19, tzinfo=timezone.utc),
            )
        ]

    original_list_users = users_routes.list_users
    users_routes.list_users = fake_list_users

    try:
        client = TestClient(app)
        response = client.get("/admin/users")

        assert response.status_code == 200
        assert "admin@example.com" in response.text
    finally:
        users_routes.list_users = original_list_users
