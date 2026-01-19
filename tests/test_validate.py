from __future__ import annotations

from pathlib import Path

from engine.validate import validate_workspace
from engine.workspace import Workspace


def test_validate_workspace_success() -> None:
    workspace_path = Path("tests/fixtures/workspace.json")
    workspace = Workspace.model_validate_json(
        workspace_path.read_text(encoding="utf-8")
    )
    findings = validate_workspace(workspace)
    assert findings == []
