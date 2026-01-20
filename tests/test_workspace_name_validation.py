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


def _extract_csrf(client: TestClient) -> str:
    page = client.get("/admin/workspaces")
    assert page.status_code == 200
    marker = 'name="csrf_token" value="'
    start = page.text.find(marker)
    assert start != -1
    start += len(marker)
    end = page.text.find('"', start)
    return page.text[start:end]


def test_create_rejects_blank_name() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_list_workspaces(session):
        return []

    async def fake_create_workspace_record(session, *, name, system_id, data):
        return None

    original_list = workspaces_routes.list_workspaces
    original_create = workspaces_routes.create_workspace_record
    workspaces_routes.list_workspaces = fake_list_workspaces
    workspaces_routes.create_workspace_record = fake_create_workspace_record

    try:
        client = TestClient(app)
        csrf_token = _extract_csrf(client)
        response = client.post(
            "/admin/workspaces",
            data={"csrf_token": csrf_token, "name": "   "},
        )

        assert response.status_code == 400
    finally:
        workspaces_routes.list_workspaces = original_list
        workspaces_routes.create_workspace_record = original_create


def test_rename_rejects_blank_name() -> None:
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
        )

    async def fake_rename_workspace(session, workspace_id: str, name: str):
        return True

    original_get = workspaces_routes.get_workspace
    original_rename = workspaces_routes.rename_workspace
    workspaces_routes.get_workspace = fake_get_workspace
    workspaces_routes.rename_workspace = fake_rename_workspace

    try:
        client = TestClient(app)
        page = client.get("/admin/workspaces/workspace-1")
        assert page.status_code == 200
        marker = 'name="csrf_token" value="'
        start = page.text.find(marker)
        assert start != -1
        start += len(marker)
        end = page.text.find('"', start)
        csrf_token = page.text[start:end]

        response = client.post(
            "/admin/workspaces/workspace-1/rename",
            data={"csrf_token": csrf_token, "name": "  "},
        )

        assert response.status_code == 400
    finally:
        workspaces_routes.get_workspace = original_get
        workspaces_routes.rename_workspace = original_rename
