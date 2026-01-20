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


def test_import_rejects_invalid_created_at() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_list_workspaces(session):
        return []

    async def fake_create_workspace_record(session, *, name, system_id, data):
        return None

    original_create = workspaces_routes.create_workspace_record
    original_list = workspaces_routes.list_workspaces
    workspaces_routes.create_workspace_record = fake_create_workspace_record
    workspaces_routes.list_workspaces = fake_list_workspaces

    try:
        client = TestClient(app)
        page = client.get("/admin/workspaces")
        assert page.status_code == 200
        token_marker = 'name="csrf_token" value="'
        start = page.text.find(token_marker)
        assert start != -1
        start += len(token_marker)
        end = page.text.find('"', start)
        csrf_token = page.text[start:end]

        response = client.post(
            "/admin/workspaces/import",
            data={"csrf_token": csrf_token},
            files={
                "workspace_file": (
                    "workspace.json",
                    b"{\"system_name\": \"Demo\", \"system_id\": \"abc\", \"created_at\": \"nope\"}",
                    "application/json",
                )
            },
        )

        assert response.status_code == 400
    finally:
        workspaces_routes.create_workspace_record = original_create
        workspaces_routes.list_workspaces = original_list
