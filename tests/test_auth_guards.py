from fastapi.testclient import TestClient

from web.app import create_app


def test_admin_requires_auth() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/admin")

    assert response.status_code == 401


def test_unconfigured_provider_returns_404() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/auth/login/github")

    assert response.status_code == 404
