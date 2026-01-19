from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CatalogManifestEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["catalog", "profile"]
    title: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    sha256: str = Field(..., min_length=1)
    source_url: str = Field(..., min_length=1)


class CatalogManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = Field(default="1.0.0")
    items: list[CatalogManifestEntry]


def dump_manifest(manifest: CatalogManifest) -> str:
    payload = manifest.model_dump(mode="json")
    return json.dumps(payload, sort_keys=True, indent=2)


def load_manifest(path: str) -> CatalogManifest:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    return CatalogManifest.model_validate(payload)
