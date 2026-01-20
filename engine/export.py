from __future__ import annotations

import json
from typing import Any

from engine.workspace import Workspace


def export_workspace(workspace: Workspace) -> bytes:
    payload: dict[str, Any] = {
        "workspace": workspace.to_export_payload(),
    }
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
