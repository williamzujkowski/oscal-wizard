from __future__ import annotations

import hashlib
from typing import Literal, TypedDict

import httpx

from engine.catalog.manifest import CatalogManifest, CatalogManifestEntry, dump_manifest
from engine.catalog.paths import get_catalog_data_dir, get_manifest_path

BASE_URL = (
    "https://raw.githubusercontent.com/usnistgov/oscal-content/"
    "main/nist.gov/SP800-53/rev5/json"
)
class CatalogEntry(TypedDict):
    kind: Literal["catalog", "profile"]
    title: str
    filename: str
    version: str

CATALOG_ENTRIES: list[CatalogEntry] = [
    {
        "kind": "catalog",
        "title": "NIST SP 800-53 Rev 5 Catalog",
        "filename": "NIST_SP-800-53_rev5_catalog.json",
        "version": "rev5",
    }
]
PROFILE_ENTRIES: list[CatalogEntry] = [
    {
        "kind": "profile",
        "title": "NIST SP 800-53 Rev 5 Low Baseline Profile",
        "filename": "NIST_SP-800-53_rev5_LOW-baseline_profile.json",
        "version": "rev5",
    },
    {
        "kind": "profile",
        "title": "NIST SP 800-53 Rev 5 Moderate Baseline Profile",
        "filename": "NIST_SP-800-53_rev5_MODERATE-baseline_profile.json",
        "version": "rev5",
    },
    {
        "kind": "profile",
        "title": "NIST SP 800-53 Rev 5 High Baseline Profile",
        "filename": "NIST_SP-800-53_rev5_HIGH-baseline_profile.json",
        "version": "rev5",
    },
]


def main() -> None:
    data_dir = get_catalog_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    entries: list[CatalogManifestEntry] = []
    for entry in CATALOG_ENTRIES + PROFILE_ENTRIES:
        filename = entry["filename"]
        url = f"{BASE_URL}/{filename}"
        content = _fetch(url)
        path = data_dir / filename
        path.write_bytes(content)
        digest = _sha256_bytes(content)
        entries.append(
            CatalogManifestEntry(
                kind=entry["kind"],
                title=entry["title"],
                filename=filename,
                version=entry["version"],
                sha256=digest,
                source_url=url,
            )
        )

    entries.sort(key=lambda item: item.filename)
    manifest = CatalogManifest(items=entries)
    manifest_path = get_manifest_path()
    manifest_path.write_text(dump_manifest(manifest), encoding="utf-8")


def _fetch(url: str) -> bytes:
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    return response.content


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    main()
