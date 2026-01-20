from fastapi.testclient import TestClient

from web.app import create_app


def test_home_route_ok() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "OSCAL Wizard" in response.text
