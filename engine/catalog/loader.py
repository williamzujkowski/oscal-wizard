from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ControlSummary:
    control_id: str
    title: str


def load_catalog_controls(path: Path) -> list[ControlSummary]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    catalog = payload.get("catalog")
    if not isinstance(catalog, dict):
        raise ValueError("Catalog JSON must include a 'catalog' object.")

    controls: list[ControlSummary] = []
    _collect_controls(catalog, controls)
    controls.sort(key=lambda item: item.control_id)
    return controls


def select_controls_by_prefix(
    controls: list[ControlSummary], prefix: str, limit: int
) -> list[ControlSummary]:
    normalized = prefix.lower()
    selected = [
        control
        for control in controls
        if control.control_id.lower().startswith(normalized)
    ]
    return selected[:limit]


def _collect_controls(node: dict[str, object], output: list[ControlSummary]) -> None:
    controls = node.get("controls", [])
    if isinstance(controls, list):
        for control in controls:
            if not isinstance(control, dict):
                continue
            control_id = control.get("id")
            if not control_id:
                raise ValueError("Control entry missing id.")
            title = control.get("title", "")
            output.append(ControlSummary(control_id=control_id, title=title))
            _collect_controls(control, output)

    groups = node.get("groups", [])
    if isinstance(groups, list):
        for group in groups:
            if isinstance(group, dict):
                _collect_controls(group, output)
