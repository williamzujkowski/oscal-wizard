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


def test_workspace_rename_requires_csrf() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_get_workspace(session, workspace_id: str):
        return DummyWorkspace(
            id=workspace_id,
            name="Example",
            system_id="abc",
            data={},
            created_at=datetime(2026, 1, 19, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 19, tzinfo=timezone.utc),
        )

    async def fake_rename_workspace(session, workspace_id: str, name: str):
        return True

    original_get = workspaces_routes.get_workspace
    original_rename = workspaces_routes.rename_workspace
    workspaces_routes.get_workspace = fake_get_workspace
    workspaces_routes.rename_workspace = fake_rename_workspace

    try:
        client = TestClient(app)
        response = client.post(
            "/admin/workspaces/workspace-1/rename",
            data={"name": "Renamed"},
        )

        assert response.status_code == 400
    finally:
        workspaces_routes.get_workspace = original_get
        workspaces_routes.rename_workspace = original_rename
