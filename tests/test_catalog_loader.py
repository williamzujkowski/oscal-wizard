from __future__ import annotations

from pathlib import Path

from engine.catalog.loader import load_catalog_controls


def test_load_catalog_controls() -> None:
    path = Path("tests/fixtures/catalogs/sample_catalog.json")
    controls = load_catalog_controls(path)
    control_ids = [control.control_id for control in controls]
    assert control_ids == ["ac-1", "au-1"]
