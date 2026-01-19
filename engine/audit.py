from __future__ import annotations

import json
from datetime import datetime, timezone


def log_event(event: str, details: dict[str, str]) -> None:
    payload = {
        "event": event,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),  # noqa: UP017
        "details": details,
    }
    print(json.dumps(payload, sort_keys=True))
