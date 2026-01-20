from __future__ import annotations

import hashlib


def deterministic_id(seed: str) -> str:
    """Return a stable identifier derived from input seed."""

    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return digest[:32]
