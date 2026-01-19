from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from web.app import app


def test_control_picker_route(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_path = tmp_path / "manifest.json"
    catalog_path = tmp_path / "catalog.json"
    catalog_payload = {
        "catalog": {
            "id": "sample",
            "title": "Sample",
            "controls": [{"id": "ac-1", "title": "Access Control Policy"}],
        }
    }
    catalog_path.write_text(json.dumps(catalog_payload), encoding="utf-8")

    manifest_payload = {
        "schema_version": "1.0.0",
        "items": [
            {
                "kind": "catalog",
                "title": "Sample Catalog",
                "filename": "catalog.json",
                "version": "rev5",
                "sha256": "deadbeef",
                "source_url": "https://example.com/catalog.json",
            }
        ],
    }
    manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")

    monkeypatch.setenv("OSCAL_WIZARD_CATALOG_DIR", str(tmp_path))

    client = TestClient(app)
    response = client.get("/controls")
    assert response.status_code == 200
    assert "ac-1" in response.text
