from __future__ import annotations

import uuid
from pathlib import Path
from typing import cast

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from pydantic import ValidationError

from engine.components.loader import (
    extract_component_drafts,
    load_component_definitions,
)
from engine.workspace import ComponentDraft
from web.routes.wizard_steps import build_wizard_steps

router = APIRouter()


@router.get("/inventory", response_class=Response)
def inventory_form(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/inventory.html",
        {
            "errors": [],
            "form_data": {},
            "components": [],
            "imported_components": [],
            "current_nav": "inventory",
            "wizard_steps": build_wizard_steps(2)[0],
            "wizard_current": build_wizard_steps(2)[1],
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Components", "href": None},
            ],
        },
    )
    return cast(Response, response)


@router.post("/inventory", response_class=Response)
def inventory_submit(
    request: Request,
    component_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    component_library_dir: str = Form(""),
) -> Response:
    templates = request.app.state.templates
    form_data = {
        "component_type": component_type,
        "title": title,
        "description": description,
        "component_library_dir": component_library_dir,
    }
    errors: list[dict[str, str]] = []
    imported_components: list[ComponentDraft] = []

    try:
        ComponentDraft.model_validate(
            {
                "component_type": component_type,
                "title": title,
                "description": description,
            }
        )
    except ValidationError as exc:
        errors = [
            {"field": ".".join(str(part) for part in error["loc"]), "msg": error["msg"]}
            for error in exc.errors()
        ]

    if component_library_dir:
        try:
            definitions = load_component_definitions(
                Path(component_library_dir).expanduser()
            )
        except (FileNotFoundError, ValueError) as exc:
            errors.append({"field": "component_library_dir", "msg": str(exc)})
        else:
            for definition in definitions:
                imported_components.extend(extract_component_drafts(definition))

    response = templates.TemplateResponse(
        request,
        "wizard/inventory.html",
        {
            "errors": errors,
            "form_data": form_data,
            "components": [
                {
                    "component_uuid": str(uuid.uuid4()),
                    "component_type": component_type,
                    "title": title,
                    "description": description,
                }
            ]
            if not errors
            else [],
            "imported_components": imported_components,
            "current_nav": "inventory",
            "wizard_steps": build_wizard_steps(2)[0],
            "wizard_current": build_wizard_steps(2)[1],
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Components", "href": None},
            ],
        },
        status_code=422 if errors else 200,
    )
    return cast(Response, response)
