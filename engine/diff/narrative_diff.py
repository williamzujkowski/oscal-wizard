from __future__ import annotations

import difflib


def narrative_html_diff(before: str, after: str) -> str:
    matcher = difflib.SequenceMatcher(None, before, after)
    fragments: list[str] = []
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == "equal":
            fragments.append(_escape(after[b0:b1]))
        elif opcode == "insert":
            fragments.append(f"<ins>{_escape(after[b0:b1])}</ins>")
        elif opcode == "delete":
            fragments.append(f"<del>{_escape(before[a0:a1])}</del>")
        elif opcode == "replace":
            fragments.append(f"<del>{_escape(before[a0:a1])}</del>")
            fragments.append(f"<ins>{_escape(after[b0:b1])}</ins>")
    return "".join(fragments)


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
