from __future__ import annotations

from engine.diff.json_diff import unified_json_diff
from engine.diff.narrative_diff import narrative_html_diff


def test_unified_json_diff_contains_change() -> None:
    before = {"control": {"narrative": "old"}}
    after = {"control": {"narrative": "new"}}
    diff = unified_json_diff(before, after)
    assert "-    \"narrative\": \"old\"" in diff
    assert "+    \"narrative\": \"new\"" in diff


def test_narrative_html_diff_marks_changes() -> None:
    diff = narrative_html_diff("old text", "new text")
    assert "<del>old" in diff
    assert "<ins>new" in diff
