from __future__ import annotations

import json

from engine.workspace import Workspace


def workspace_to_canonical_json(workspace: Workspace) -> str:
    payload = workspace.model_dump(mode="json")
    return json.dumps(payload, sort_keys=True, indent=2)

