from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

USWDS_VERSION = "3.7.0"
CSS_URL = (
    f"https://cdn.jsdelivr.net/npm/@uswds/uswds@{USWDS_VERSION}"
    "/dist/css/uswds.min.css"
)
JS_URL = (
    f"https://cdn.jsdelivr.net/npm/@uswds/uswds@{USWDS_VERSION}"
    "/dist/js/uswds.min.js"
)
TARGET_DIR = Path("web/static/uswds")


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    css_bytes = _download(CSS_URL)
    js_bytes = _download(JS_URL)
    (TARGET_DIR / "uswds.min.css").write_bytes(css_bytes)
    (TARGET_DIR / "uswds.min.js").write_bytes(js_bytes)

    manifest = {
        "version": USWDS_VERSION,
        "date": datetime.now(tz=timezone.utc).isoformat(),  # noqa: UP017
        "css_sha256": _sha256(css_bytes),
        "js_sha256": _sha256(js_bytes),
        "css_source_url": CSS_URL,
        "js_source_url": JS_URL,
    }
    (TARGET_DIR / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2),
        encoding="utf-8",
    )


def _download(url: str) -> bytes:
    response = httpx.get(url, timeout=60.0)
    response.raise_for_status()
    return response.content


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    main()
