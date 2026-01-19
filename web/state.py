from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from fastapi import Request

from engine.workspace import Component, Party, ResponsibleParty, Role


@dataclass
class WizardState:
    components: list[Component] = field(default_factory=list)
    roles: list[Role] = field(default_factory=list)
    parties: list[Party] = field(default_factory=list)
    responsible_parties: list[ResponsibleParty] = field(default_factory=list)
    last_export: str | None = None


def get_wizard_state(request: Request) -> tuple[str, WizardState, bool]:
    store: dict[str, WizardState] = request.app.state.wizard_store
    session_id = request.cookies.get("wizard_session")
    if session_id and session_id in store:
        return session_id, store[session_id], False

    session_id = str(uuid.uuid4())
    state = WizardState()
    store[session_id] = state
    return session_id, state, True


def attach_session_cookie(response: Any, session_id: str, is_new: bool) -> None:
    if is_new:
        response.set_cookie("wizard_session", session_id, httponly=True, samesite="lax")
