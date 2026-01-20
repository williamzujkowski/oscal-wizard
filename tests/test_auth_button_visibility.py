from fastapi.testclient import TestClient

from web.app import create_app


def test_home_shows_sso_not_configured() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "SSO not configured" in response.text
