from __future__ import annotations

from fastapi.testclient import TestClient

from web.app import app


def test_root_home_page() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Open OSCAL Wizard" in response.text


def test_system_foundation_page() -> None:
    client = TestClient(app)
    response = client.get("/system-foundation")
    assert response.status_code == 200
    assert "System Foundation" in response.text


def test_validate_page() -> None:
    client = TestClient(app)
    response = client.get("/validate")
    assert response.status_code == 200
    assert "Validate" in response.text


def test_export_page() -> None:
    client = TestClient(app)
    response = client.get("/export")
    assert response.status_code == 200
    assert "Export" in response.text


def test_workspace_export() -> None:
    client = TestClient(app)
    response = client.post(
        "/system-foundation/export",
        data={
            "system_name": "Example System",
            "impact_level": "moderate",
            "authorization_boundary": "Example boundary",
            "description": "Example description",
            "system_owner": "Owner Name",
            "authorizing_official": "AO Name",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "attachment; filename=workspace.json" in response.headers.get(
        "content-disposition", ""
    )
