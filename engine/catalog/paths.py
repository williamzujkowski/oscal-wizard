from __future__ import annotations

import os
from pathlib import Path


def get_catalog_data_dir() -> Path:
    override = os.getenv("OSCAL_WIZARD_CATALOG_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "data"


def get_manifest_path() -> Path:
    return get_catalog_data_dir() / "manifest.json"
