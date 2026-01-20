from fastapi.testclient import TestClient

import web.app as app_module
from web.app import create_app


class DummyUser:
    id = "user-1"
    email = "demo@example.com"
    is_admin = True


def test_logout_returns_303() -> None:
    async def fake_load_user(request, sessionmaker=None):
        return DummyUser()

    original_load_user = app_module.load_user
    app_module.load_user = fake_load_user

    try:
        app = create_app()
        client = TestClient(app)

        response = client.get("/")
        assert response.status_code == 200
        marker = 'name="csrf_token" value="'
        start = response.text.find(marker)
        assert start != -1
        start += len(marker)
        end = response.text.find('"', start)
        csrf_token = response.text[start:end]

        logout = client.post(
            "/auth/logout",
            data={"csrf_token": csrf_token},
            follow_redirects=False,
        )

        assert logout.status_code == 303
    finally:
        app_module.load_user = original_load_user
