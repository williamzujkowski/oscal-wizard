from __future__ import annotations

import uuid


def deterministic_uuid(*parts: str, namespace: uuid.UUID | None = None) -> str:
    clean_parts = [part.strip().lower() for part in parts if part.strip()]
    seed = "|".join(clean_parts)
    effective_namespace = namespace or uuid.NAMESPACE_URL
    return str(uuid.uuid5(effective_namespace, seed))
