from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from web.app import app


def test_inventory_get() -> None:
    client = TestClient(app)
    response = client.get("/inventory")
    assert response.status_code == 200
    assert "Components" in response.text


def test_inventory_post_valid() -> None:
    client = TestClient(app)
    response = client.post(
        "/inventory",
        data={
            "component_type": "software",
            "title": "Test Component",
            "description": "Example description",
        },
    )
    assert response.status_code == 200
    assert "Added components" in response.text


def test_inventory_import_invalid_path() -> None:
    client = TestClient(app)
    response = client.post(
        "/inventory",
        data={
            "component_type": "software",
            "title": "Test Component",
            "description": "Example description",
            "component_library_dir": "/does/not/exist",
        },
    )
    assert response.status_code == 422
    assert "component_library_dir" in response.text


def test_inventory_import_components(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {
        "component-definition": {
            "uuid": "11111111-1111-1111-1111-111111111111",
            "metadata": {"title": "Sample Component Definition"},
            "components": [
                {
                    "title": "Load Balancer",
                    "type": "service",
                    "description": "Handles inbound traffic.",
                }
            ],
        }
    }
    (tmp_path / "component.json").write_text(json.dumps(payload), encoding="utf-8")

    client = TestClient(app)
    response = client.post(
        "/inventory",
        data={
            "component_type": "software",
            "title": "Test Component",
            "description": "Example description",
            "component_library_dir": str(tmp_path),
        },
    )
    assert response.status_code == 200
    assert "Imported components" in response.text
