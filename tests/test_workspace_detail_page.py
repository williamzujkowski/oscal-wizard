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
    data: dict
    created_at: datetime


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


def test_workspace_detail_page_renders() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_get_workspace(session, workspace_id: str):
        return DummyWorkspace(
            id=workspace_id,
            name="Example",
            system_id="abc123",
            data={"system_name": "Example", "system_id": "abc123"},
            created_at=datetime(2026, 1, 19, tzinfo=timezone.utc),
        )

    original_get = workspaces_routes.get_workspace
    workspaces_routes.get_workspace = fake_get_workspace

    try:
        client = TestClient(app)
        response = client.get("/admin/workspaces/workspace-1")

        assert response.status_code == 200
        assert "Example" in response.text
    finally:
        workspaces_routes.get_workspace = original_get
