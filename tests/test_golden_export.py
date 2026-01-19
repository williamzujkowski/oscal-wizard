from __future__ import annotations

from pathlib import Path

from engine.export import export_ssp_json
from engine.workspace import Workspace


def test_ssp_export_matches_golden_file() -> None:
    workspace_path = Path("tests/fixtures/workspace.json")
    workspace = Workspace.model_validate_json(
        workspace_path.read_text(encoding="utf-8")
    )
    golden_path = Path("tests/golden_exports/ssp.json")
    expected = golden_path.read_text(encoding="utf-8")
    actual = export_ssp_json(workspace)
    assert actual == expected
