from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from pydantic import ValidationError

from engine.components.loader import (
    extract_component_drafts,
    load_component_definitions,
)
from engine.ids import deterministic_uuid
from engine.workspace import Component, ComponentDraft
from web.routes.wizard_steps import build_wizard_steps
from web.state import attach_session_cookie, get_wizard_state

router = APIRouter()


@router.get("/inventory", response_class=Response)
def inventory_form(request: Request) -> Response:
    templates = request.app.state.templates
    session_id, state, is_new = get_wizard_state(request)
    response = templates.TemplateResponse(
        request,
        "wizard/inventory.html",
        {
            "errors": [],
            "form_data": {},
            "components": state.components,
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
    attach_session_cookie(response, session_id, is_new)
    return cast(Response, response)


@router.post("/inventory", response_class=Response)
def inventory_submit(
    request: Request,
    action: str = Form("add"),
    component_type: str = Form(""),
    title: str = Form(""),
    description: str = Form(""),
    component_library_dir: str = Form(""),
) -> Response:
    templates = request.app.state.templates
    session_id, state, is_new = get_wizard_state(request)
    form_data = {
        "component_type": component_type,
        "title": title,
        "description": description,
        "component_library_dir": component_library_dir,
    }
    errors: list[dict[str, str]] = []
    imported_components: list[ComponentDraft] = []

    if action == "add":
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
                {
                    "field": ".".join(str(part) for part in error["loc"]),
                    "msg": error["msg"],
                }
                for error in exc.errors()
            ]
        else:
            component_uuid = deterministic_uuid(
                "component",
                component_type,
                title,
                description,
            )
            if any(
                component.component_uuid == component_uuid
                for component in state.components
            ):
                errors.append(
                    {
                        "field": "component",
                        "msg": "Component already exists.",
                    }
                )
            else:
                state.components.append(
                    Component(
                        component_uuid=component_uuid,
                        component_type=component_type,
                        title=title,
                        description=description,
                    )
                )

    if action == "import" and component_library_dir:
        try:
            definitions = load_component_definitions(
                Path(component_library_dir).expanduser()
            )
        except (FileNotFoundError, ValueError) as exc:
            errors.append({"field": "component_library_dir", "msg": str(exc)})
        else:
            for definition in definitions:
                imported_components.extend(extract_component_drafts(definition))
            for draft in imported_components:
                component_uuid = deterministic_uuid(
                    "component",
                    draft.component_type,
                    draft.title,
                    draft.description,
                )
                if any(
                    component.component_uuid == component_uuid
                    for component in state.components
                ):
                    continue
                state.components.append(
                    Component(
                        component_uuid=component_uuid,
                        component_type=draft.component_type,
                        title=draft.title,
                        description=draft.description,
                    )
                )

    response = templates.TemplateResponse(
        request,
        "wizard/inventory.html",
        {
            "errors": errors,
            "form_data": form_data,
            "components": state.components,
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
    attach_session_cookie(response, session_id, is_new)
    return cast(Response, response)
