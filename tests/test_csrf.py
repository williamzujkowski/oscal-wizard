from fastapi.testclient import TestClient

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


def test_workspace_create_requires_csrf() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyUser()

    client = TestClient(app)
    response = client.post("/admin/workspaces", data={"name": "Demo"})

    assert response.status_code == 400
