from __future__ import annotations

import uuid
from typing import Any, cast

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from pydantic import ValidationError

from engine.export import workspace_to_canonical_json
from engine.workspace import SystemFoundation, Workspace

router = APIRouter()


@router.get("/system-foundation", response_class=Response)
def system_foundation_form(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/system_foundation.html",
        {
            "errors": [],
            "form_data": {},
            "current_nav": "system-foundation",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "System Foundation", "href": None},
            ],
        },
    )
    return cast(Response, response)


@router.post("/system-foundation/export", response_class=Response)
def export_system_foundation(
    request: Request,
    system_name: str = Form(...),
    impact_level: str = Form(...),
    authorization_boundary: str = Form(...),
    description: str = Form(...),
    system_owner: str = Form(...),
    authorizing_official: str = Form(...),
) -> Response:
    templates = request.app.state.templates
    form_data: dict[str, Any] = {
        "system_name": system_name,
        "impact_level": impact_level,
        "authorization_boundary": authorization_boundary,
        "description": description,
        "system_owner": system_owner,
        "authorizing_official": authorizing_official,
    }

    try:
        system_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, system_name))
        system = SystemFoundation(system_uuid=system_uuid, **form_data)
        workspace = Workspace(system=system)
    except ValidationError as exc:
        errors = [
            {"field": ".".join(str(part) for part in error["loc"]), "msg": error["msg"]}
            for error in exc.errors()
        ]
        response = templates.TemplateResponse(
            request,
            "wizard/system_foundation.html",
            {
                "errors": errors,
                "form_data": form_data,
                "current_nav": "system-foundation",
                "breadcrumbs": [
                    {"label": "Home", "href": "/"},
                    {"label": "System Foundation", "href": None},
                ],
            },
            status_code=422,
        )
        return cast(Response, response)

    payload = workspace_to_canonical_json(workspace)
    headers = {"Content-Disposition": "attachment; filename=workspace.json"}
    return Response(content=payload, media_type="application/json", headers=headers)
