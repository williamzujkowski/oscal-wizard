from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi.testclient import TestClient

import web.routes.workspaces as workspaces_routes
from web.app import create_app
from web.security import require_admin


@dataclass
class DummyWorkspace:
    id: str
    name: str
    system_id: str
    owner_id: str | None
    created_at: datetime
    updated_at: datetime


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


def test_workspaces_page_renders() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_list_workspaces(session):
        return [
            DummyWorkspace(
                id="workspace-1",
                name="Example",
                system_id="abc123",
                owner_id=None,
                created_at=datetime(2026, 1, 19, tzinfo=timezone.utc),
                updated_at=datetime(2026, 1, 19, tzinfo=timezone.utc),
            )
        ]

    original_list = workspaces_routes.list_workspaces
    workspaces_routes.list_workspaces = fake_list_workspaces

    try:
        client = TestClient(app)
        response = client.get("/admin/workspaces")

        assert response.status_code == 200
        assert "Example" in response.text
    finally:
        workspaces_routes.list_workspaces = original_list
