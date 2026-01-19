from __future__ import annotations

import json
from io import BytesIO

from fastapi.testclient import TestClient

from web.app import app


def test_diff_route_accepts_json_files() -> None:
    client = TestClient(app)
    before = json.dumps({"control": {"narrative": "old"}}).encode("utf-8")
    after = json.dumps({"control": {"narrative": "new"}}).encode("utf-8")
    response = client.post(
        "/diff",
        files={
            "before_file": ("before.json", BytesIO(before), "application/json"),
            "after_file": ("after.json", BytesIO(after), "application/json"),
        },
    )
    assert response.status_code == 200
    assert "JSON Diff" in response.text
    assert "Narrative Changes" in response.text
