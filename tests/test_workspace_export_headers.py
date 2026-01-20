from dataclasses import dataclass

from fastapi.testclient import TestClient

import web.routes.workspaces as workspaces_routes
from web.app import create_app
from web.security import require_admin


@dataclass
class DummyRecord:
    id: str
    data: dict


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummySessionMaker:
    def __call__(self):
        return DummySession()


class DummyUser:
    is_admin = True


def test_workspace_export_sets_download_header() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyUser()

    async def fake_get_workspace(session, workspace_id: str):
        return DummyRecord(id=workspace_id, data={"system_name": "Demo"})

    original_get_workspace = workspaces_routes.get_workspace
    workspaces_routes.get_workspace = fake_get_workspace

    try:
        client = TestClient(app)
        response = client.get("/admin/workspaces/demo/export")

        assert response.status_code == 200
        expected = "attachment; filename=\"workspace-demo.json\""
        assert response.headers.get("content-disposition") == expected
    finally:
        workspaces_routes.get_workspace = original_get_workspace
