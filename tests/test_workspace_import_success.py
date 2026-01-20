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


class DummyAdmin:
    is_admin = True


def test_import_accepts_valid_payload() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_list_workspaces(session):
        return []

    captured = {}

    async def fake_create_workspace_record(session, *, name, system_id, data, created_at=None):
        captured["created_at"] = created_at
        return None

    original_list = workspaces_routes.list_workspaces
    original_create = workspaces_routes.create_workspace_record
    workspaces_routes.list_workspaces = fake_list_workspaces
    workspaces_routes.create_workspace_record = fake_create_workspace_record

    try:
        client = TestClient(app)
        page = client.get("/admin/workspaces")
        assert page.status_code == 200
        marker = 'name="csrf_token" value="'
        start = page.text.find(marker)
        assert start != -1
        start += len(marker)
        end = page.text.find('"', start)
        csrf_token = page.text[start:end]

        payload = (
            b"{\"system_name\": \"Demo\", \"system_id\": \"abc\", "
            b"\"created_at\": \"1970-01-01T00:00:00+00:00\"}"
        )

        response = client.post(
            "/admin/workspaces/import",
            data={"csrf_token": csrf_token},
            files={"workspace_file": ("workspace.json", payload, "application/json")},
        )

        assert response.status_code == 303
        assert captured["created_at"].isoformat() == "1970-01-01T00:00:00+00:00"
    finally:
        workspaces_routes.list_workspaces = original_list
        workspaces_routes.create_workspace_record = original_create
