from __future__ import annotations

import json
from io import BytesIO

from fastapi.testclient import TestClient

from web.app import app


def test_export_route_ssp() -> None:
    client = TestClient(app)
    payload = json.dumps(
        {
            "version": "0.2.0",
            "metadata": {
                "title": "Example SSP Workspace",
                "last_modified": "2025-01-19T12:00:00-05:00",
                "version": "2025.01",
                "oscal_version": "1.2.0",
                "content_version": "1.4.0",
            },
            "system": {
                "system_uuid": "22222222-2222-2222-2222-222222222222",
                "system_name": "Example System",
                "impact_level": "moderate",
                "authorization_boundary": "Boundary includes the VPC.",
                "description": "Example system.",
                "system_owner": "Jordan Lee",
                "authorizing_official": "Riley Chen",
            },
            "roles": [],
            "parties": [],
            "responsible_parties": [],
            "components": [],
        }
    ).encode("utf-8")

    response = client.post(
        "/export/ssp",
        files={
            "workspace_file": (
                "workspace.json",
                BytesIO(payload),
                "application/json",
            )
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
