from __future__ import annotations

import difflib
import json
from typing import Any


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, indent=2)


def unified_json_diff(before: dict[str, Any], after: dict[str, Any]) -> str:
    before_lines = canonical_json(before).splitlines(keepends=True)
    after_lines = canonical_json(after).splitlines(keepends=True)
    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile="before.json",
        tofile="after.json",
        lineterm="",
    )
    return "".join(diff)
