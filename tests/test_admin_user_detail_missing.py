from fastapi.testclient import TestClient

import web.routes.users as users_routes
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


def test_admin_user_detail_missing() -> None:
    app = create_app()
    app.state.sessionmaker = DummySessionMaker()
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()

    async def fake_get_user_by_id(session, user_id: str):
        return None

    original_get = users_routes.get_user_by_id
    users_routes.get_user_by_id = fake_get_user_by_id

    try:
        client = TestClient(app)
        response = client.get("/admin/users/missing")

        assert response.status_code == 404
    finally:
        users_routes.get_user_by_id = original_get
