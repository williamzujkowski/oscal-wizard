from fastapi.testclient import TestClient

from web.app import create_app


def test_logout_returns_303() -> None:
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

    logout = client.post("/auth/logout", data={"csrf_token": csrf_token})

    assert logout.status_code == 303
