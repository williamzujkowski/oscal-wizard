from __future__ import annotations

import json
from pathlib import Path

from engine.export import export_workspace
from engine.workspace import Workspace

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GOLDEN_DIR = Path(__file__).parent / "golden_exports"


def test_golden_export_matches_fixture() -> None:
    payload = json.loads((FIXTURES_DIR / "workspace.json").read_text())
    workspace = Workspace.from_payload(payload)
    result = export_workspace(workspace)
    expected = (GOLDEN_DIR / "ssp.json").read_bytes()
    assert result == expected
