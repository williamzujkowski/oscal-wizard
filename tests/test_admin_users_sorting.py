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


def test_users_page_ordering() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_list_users(session):
        return [
            DummyUser(
                id="user-new",
                email="new@example.com",
                display_name="New User",
                provider="github",
                is_admin=False,
                last_login_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
            ),
            DummyUser(
                id="user-old",
                email="old@example.com",
                display_name="Old User",
                provider="github",
                is_admin=False,
                last_login_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ),
        ]

    original_list = users_routes.list_users
    users_routes.list_users = fake_list_users

    try:
        client = TestClient(app)
        response = client.get("/admin/users")

        assert response.status_code == 200
        assert response.text.index("new@example.com") < response.text.index("old@example.com")
    finally:
        users_routes.list_users = original_list
