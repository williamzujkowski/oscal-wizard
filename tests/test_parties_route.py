from __future__ import annotations

from fastapi.testclient import TestClient

from engine.ids import deterministic_uuid
from web.app import app


def test_parties_get() -> None:
    client = TestClient(app)
    response = client.get("/parties")
    assert response.status_code == 200
    assert "Parties & Roles" in response.text


def test_parties_post_valid() -> None:
    client = TestClient(app)
    response = client.post(
        "/parties",
        data={
            "role_id": "system-owner",
            "role_title": "System Owner",
            "party_type": "person",
            "party_name": "Jordan Lee",
            "party_email": "jordan@example.com",
            "responsible_role_id": "system-owner",
            "responsible_party_uuid": deterministic_uuid(
                "party",
                "person",
                "Jordan Lee",
                "jordan@example.com",
            ),
        },
    )
    assert response.status_code == 200
    assert "Roles" in response.text


def test_parties_post_error() -> None:
    client = TestClient(app)
    response = client.post(
        "/parties",
        data={
            "role_id": "",
            "role_title": "",
            "party_type": "person",
            "party_name": "Jordan Lee",
            "party_email": "jordan@example.com",
            "responsible_role_id": "system-owner",
            "responsible_party_uuid": "",
        },
    )
    assert response.status_code == 422
    assert "Provide both role id and party UUID." in response.text
