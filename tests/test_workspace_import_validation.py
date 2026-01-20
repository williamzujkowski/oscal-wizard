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


def test_import_rejects_invalid_json() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyUser()

    client = TestClient(app)
    response = client.post(
        "/admin/workspaces/import",
        files={"workspace_file": ("workspace.json", b"not-json", "application/json")},
    )

    assert response.status_code == 400


def test_import_rejects_missing_fields() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyUser()

    async def fake_create_workspace_record(session, *, name, system_id, data, created_at=None):
        return None

    original_create = workspaces_routes.create_workspace_record
    workspaces_routes.create_workspace_record = fake_create_workspace_record

    try:
        client = TestClient(app)
        response = client.post(
            "/admin/workspaces/import",
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
