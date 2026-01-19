from __future__ import annotations

import json
from pathlib import Path


def test_uswds_assets_present() -> None:
    base = Path("web/static/uswds")
    css = base / "uswds.min.css"
    js = base / "uswds.min.js"
    manifest_path = base / "manifest.json"

    assert css.exists()
    assert js.exists()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["version"] == "3.7.0"
