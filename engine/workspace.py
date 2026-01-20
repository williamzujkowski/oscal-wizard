from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

DEFAULT_CREATED_AT = datetime(1970, 1, 1, tzinfo=timezone.utc)

@dataclass(frozen=True)
class Workspace:
    """Minimal workspace state for deterministic export."""

    system_name: str
    system_id: str
    created_at: datetime = field(
        default=DEFAULT_CREATED_AT
    )

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Workspace":
        created_at = datetime.fromisoformat(payload["created_at"])
        return cls(
            system_name=payload["system_name"],
            system_id=payload["system_id"],
            created_at=created_at,
        )

    def to_export_payload(self) -> dict[str, Any]:
        return {
            "system_name": self.system_name,
            "system_id": self.system_id,
            "created_at": self.created_at.isoformat(),
        }
