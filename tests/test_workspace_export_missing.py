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


def test_workspace_export_missing_returns_404() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_get_workspace(session, workspace_id: str):
        return None

    original_get = workspaces_routes.get_workspace
    workspaces_routes.get_workspace = fake_get_workspace

    try:
        client = TestClient(app)
        response = client.get("/admin/workspaces/missing/export")

        assert response.status_code == 404
    finally:
        workspaces_routes.get_workspace = original_get
