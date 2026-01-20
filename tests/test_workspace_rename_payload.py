from dataclasses import dataclass
from datetime import datetime, timezone
import asyncio

import engine.workspaces as workspaces


@dataclass
class DummyRecord:
    name: str
    data: dict
    updated_at: datetime


class DummySession:
    async def commit(self):
        return None


def test_rename_updates_payload_system_name(monkeypatch) -> None:
    record = DummyRecord(
        name="Old",
        data={"system_name": "Old", "system_id": "abc"},
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    async def fake_get_workspace(session, workspace_id: str):
        return record

    monkeypatch.setattr(workspaces, "get_workspace", fake_get_workspace)

    session = DummySession()
    asyncio.run(workspaces.rename_workspace(session, "workspace-1", "New"))

    assert record.name == "New"
    assert record.data["system_name"] == "New"
