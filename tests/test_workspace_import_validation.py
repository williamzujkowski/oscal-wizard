from fastapi.testclient import TestClient

import web.routes.workspaces as workspaces_routes
from web.app import create_app
from web.security import require_admin


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


def _csrf_for_import(client: TestClient) -> str:
    response = client.get("/admin/workspaces")
    assert response.status_code == 200
    marker = 'name="csrf_token" value="'
    start = response.text.find(marker)
    assert start != -1
    start += len(marker)
    end = response.text.find('"', start)
    return response.text[start:end]


def test_import_rejects_invalid_json() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyUser()

    async def fake_list_workspaces(session):
        return []

    original_list = workspaces_routes.list_workspaces
    workspaces_routes.list_workspaces = fake_list_workspaces

    try:
        client = TestClient(app)
        csrf_token = _csrf_for_import(client)
        response = client.post(
            "/admin/workspaces/import",
            data={"csrf_token": csrf_token},
            files={"workspace_file": ("workspace.json", b"not-json", "application/json")},
        )

        assert response.status_code == 400
    finally:
        workspaces_routes.list_workspaces = original_list


def test_import_rejects_missing_fields() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyUser()

    async def fake_create_workspace_record(session, *, name, system_id, data, created_at=None):
        return None

    async def fake_list_workspaces(session):
        return []

    original_create = workspaces_routes.create_workspace_record
    original_list = workspaces_routes.list_workspaces
    workspaces_routes.create_workspace_record = fake_create_workspace_record
    workspaces_routes.list_workspaces = fake_list_workspaces

    try:
        client = TestClient(app)
        csrf_token = _csrf_for_import(client)
        response = client.post(
            "/admin/workspaces/import",
            data={"csrf_token": csrf_token},
            files={
                "workspace_file": (
                    "workspace.json",
                    b"{\"system_name\": \"Demo\"}",
                    "application/json",
                )
            },
        )

        assert response.status_code == 400
    finally:
        workspaces_routes.create_workspace_record = original_create
        workspaces_routes.list_workspaces = original_list
