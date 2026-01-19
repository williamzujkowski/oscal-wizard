from __future__ import annotations

from typing import Literal, cast

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from pydantic import ValidationError

from engine.ids import deterministic_uuid
from engine.workspace import Party, ResponsibleParty, Role
from web.routes.wizard_steps import build_wizard_steps
from web.state import attach_session_cookie, get_wizard_state

router = APIRouter()


@router.get("/parties", response_class=Response)
def parties_form(request: Request) -> Response:
    templates = request.app.state.templates
    session_id, state, is_new = get_wizard_state(request)
    response = templates.TemplateResponse(
        request,
        "wizard/parties.html",
        {
            "errors": [],
            "form_data": {},
            "roles": state.roles,
            "parties": state.parties,
            "responsible_parties": state.responsible_parties,
            "current_nav": "parties",
            "wizard_steps": build_wizard_steps(3)[0],
            "wizard_current": build_wizard_steps(3)[1],
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Parties & Roles", "href": None},
            ],
        },
    )
    attach_session_cookie(response, session_id, is_new)
    return cast(Response, response)


@router.post("/parties", response_class=Response)
def parties_submit(
    request: Request,
    role_id: str = Form(""),
    role_title: str = Form(""),
    party_type: str = Form("person"),
    party_name: str = Form(""),
    party_email: str = Form(""),
    responsible_role_id: str = Form(""),
    responsible_party_uuid: str = Form(""),
) -> Response:
    templates = request.app.state.templates
    session_id, state, is_new = get_wizard_state(request)
    form_data = {
        "role_id": role_id,
        "role_title": role_title,
        "party_type": party_type,
        "party_name": party_name,
        "party_email": party_email,
        "responsible_role_id": responsible_role_id,
        "responsible_party_uuid": responsible_party_uuid,
    }

    errors: list[dict[str, str]] = []
    roles: list[Role] = list(state.roles)
    parties: list[Party] = list(state.parties)
    responsible_parties: list[ResponsibleParty] = list(state.responsible_parties)

    if role_id or role_title:
        try:
            if any(role.role_id == role_id for role in roles):
                errors.append({"field": "role_id", "msg": "Role already exists."})
            else:
                roles.append(Role(role_id=role_id, title=role_title))
        except ValidationError as exc:
            errors.extend(_validation_errors(exc))

    party_uuid = ""
    if party_name:
        party_uuid = deterministic_uuid(
            "party",
            party_type,
            party_name,
            party_email,
        )
        try:
            party_type_value = cast(
                Literal["person", "organization"],
                party_type if party_type in {"person", "organization"} else "person",
            )
            if any(party.party_uuid == party_uuid for party in parties):
                errors.append({"field": "party_name", "msg": "Party already exists."})
            else:
                parties.append(
                    Party(
                        party_uuid=party_uuid,
                        party_type=party_type_value,
                        name=party_name,
                        email_addresses=_split_emails(party_email),
                    )
                )
        except ValidationError as exc:
            errors.extend(_validation_errors(exc))

    if responsible_role_id or responsible_party_uuid:
        if responsible_role_id and responsible_party_uuid:
            if not any(role.role_id == responsible_role_id for role in roles):
                errors.append(
                    {
                        "field": "responsible_role_id",
                        "msg": "Unknown role id.",
                    }
                )
            if not any(
                party.party_uuid == responsible_party_uuid for party in parties
            ):
                errors.append(
                    {
                        "field": "responsible_party_uuid",
                        "msg": "Unknown party UUID.",
                    }
                )
            try:
                if not errors:
                    responsible_parties.append(
                        ResponsibleParty(
                            role_id=responsible_role_id,
                            party_uuids=[responsible_party_uuid],
                        )
                    )
            except ValidationError as exc:
                errors.extend(_validation_errors(exc))
        else:
            errors.append(
                {
                    "field": "responsible_party",
                    "msg": "Provide both role id and party UUID.",
                }
            )

    if not errors:
        state.roles = roles
        state.parties = parties
        state.responsible_parties = responsible_parties

    response = templates.TemplateResponse(
        request,
        "wizard/parties.html",
        {
            "errors": errors,
            "form_data": {
                **form_data,
                "party_uuid": party_uuid,
            },
            "roles": state.roles,
            "parties": state.parties,
            "responsible_parties": state.responsible_parties,
            "current_nav": "parties",
            "wizard_steps": build_wizard_steps(3)[0],
            "wizard_current": build_wizard_steps(3)[1],
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Parties & Roles", "href": None},
            ],
        },
        status_code=422 if errors else 200,
    )
    attach_session_cookie(response, session_id, is_new)
    return cast(Response, response)


def _validation_errors(exc: ValidationError) -> list[dict[str, str]]:
    return [
        {"field": ".".join(str(part) for part in error["loc"]), "msg": error["msg"]}
        for error in exc.errors()
    ]


def _split_emails(value: str) -> list[str]:
    if not value:
        return []
    return [email.strip() for email in value.split(",") if email.strip()]
