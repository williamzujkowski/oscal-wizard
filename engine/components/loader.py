from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any
from pathlib import Path


@dataclass(frozen=True)
class ComponentDefinitionFile:
    path: Path
    sha256: str
    payload: dict[str, Any]


def load_component_definitions(directory: Path) -> list[ComponentDefinitionFile]:
    if not directory.exists():
        raise FileNotFoundError(f"Component directory not found: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Component path is not a directory: {directory}")

    results: list[ComponentDefinitionFile] = []
    for path in sorted(directory.glob("*.json")):
        payload = _load_json(path)
        if "component-definition" not in payload:
            raise ValueError(f"Missing component-definition in {path.name}")
        digest = _sha256_bytes(path.read_bytes())
        results.append(
            ComponentDefinitionFile(path=path, sha256=digest, payload=payload)
        )

    return results


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Component definition must be an object: {path.name}")
    return payload


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
