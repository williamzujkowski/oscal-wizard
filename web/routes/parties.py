from __future__ import annotations

import uuid
from typing import Literal, cast

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from pydantic import ValidationError

from engine.workspace import Party, ResponsibleParty, Role

router = APIRouter()


@router.get("/parties", response_class=Response)
def parties_form(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/parties.html",
        {
            "errors": [],
            "form_data": {},
            "roles": [],
            "parties": [],
            "responsible_parties": [],
            "current_nav": "parties",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Parties & Roles", "href": None},
            ],
        },
    )
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
    roles: list[Role] = []
    parties: list[Party] = []
    responsible_parties: list[ResponsibleParty] = []

    if role_id or role_title:
        try:
            roles.append(Role(role_id=role_id, title=role_title))
        except ValidationError as exc:
            errors.extend(_validation_errors(exc))

    party_uuid = ""
    if party_name:
        party_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, party_name))
        try:
            party_type_value = cast(
                Literal["person", "organization"],
                party_type if party_type in {"person", "organization"} else "person",
            )
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
            try:
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

    response = templates.TemplateResponse(
        request,
        "wizard/parties.html",
        {
            "errors": errors,
            "form_data": {
                **form_data,
                "party_uuid": party_uuid,
            },
            "roles": roles,
            "parties": parties,
            "responsible_parties": responsible_parties,
            "current_nav": "parties",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Parties & Roles", "href": None},
            ],
        },
        status_code=422 if errors else 200,
    )
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
