from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from web.app import app


def test_control_interview_get(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog_fixture(tmp_path)
    monkeypatch.setenv("OSCAL_WIZARD_CATALOG_DIR", str(tmp_path))

    client = TestClient(app)
    response = client.get("/controls/interview")
    assert response.status_code == 200
    assert "ac-1" in response.text


def test_control_interview_validation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_catalog_fixture(tmp_path)
    monkeypatch.setenv("OSCAL_WIZARD_CATALOG_DIR", str(tmp_path))

    client = TestClient(app)
    response = client.post(
        "/controls/interview",
        data={
            "control_ac-1_selected": "on",
            "control_ac-1_narrative": "",
        },
    )
    assert response.status_code == 422
    assert "Please fix the errors below" in response.text


def test_control_interview_preview(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_catalog_fixture(tmp_path)
    monkeypatch.setenv("OSCAL_WIZARD_CATALOG_DIR", str(tmp_path))

    client = TestClient(app)
    response = client.post(
        "/controls/interview",
        data={
            "control_ac-1_selected": "on",
            "control_ac-1_narrative": "We enforce access control.",
        },
    )
    assert response.status_code == 200
    assert "Preview" in response.text


def _write_catalog_fixture(tmp_path: Path) -> None:
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
    (tmp_path / "manifest.json").write_text(
        json.dumps(manifest_payload), encoding="utf-8"
    )

    catalog_payload = {
        "catalog": {
            "id": "sample",
            "title": "Sample",
            "controls": [
                {"id": "ac-1", "title": "Access Control Policy"},
                {"id": "au-1", "title": "Audit Policy"},
            ],
        }
    }
    (tmp_path / "catalog.json").write_text(
        json.dumps(catalog_payload), encoding="utf-8"
    )
