from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.components.loader import load_component_definitions


def test_load_component_definitions(tmp_path: Path) -> None:
    fixture_path = Path("tests/fixtures/component_definitions/sample_component.json")
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    target = tmp_path / "sample_component.json"
    target.write_text(json.dumps(payload), encoding="utf-8")

    results = load_component_definitions(tmp_path)
    assert len(results) == 1
    assert results[0].payload["component-definition"]["uuid"].startswith("11111111")


def test_component_definition_missing_root(tmp_path: Path) -> None:
    target = tmp_path / "bad_component.json"
    target.write_text("{\"wrong-key\": {}}", encoding="utf-8")

    with pytest.raises(ValueError, match="component-definition"):
        load_component_definitions(tmp_path)
