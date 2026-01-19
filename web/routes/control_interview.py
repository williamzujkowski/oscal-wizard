from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import Response

from engine.catalog.loader import (
    ControlSummary,
    load_catalog_controls,
    select_controls_by_prefix,
)
from engine.catalog.manifest import load_manifest
from engine.catalog.paths import get_catalog_data_dir, get_manifest_path

router = APIRouter()


@router.get("/controls/interview", response_class=Response)
async def control_interview_form(request: Request) -> Response:
    templates = request.app.state.templates
    controls = _load_control_subset()
    response = templates.TemplateResponse(
        request,
        "wizard/control_interview.html",
        {
            "controls": controls,
            "errors": [],
            "form_data": {},
            "selected_controls": [],
            "preview": [],
            "current_nav": "control-interview",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Control Interview", "href": None},
            ],
        },
    )
    return cast(Response, response)


@router.post("/controls/interview", response_class=Response)
async def control_interview_submit(request: Request) -> Response:
    templates = request.app.state.templates
    controls = _load_control_subset()
    form = await request.form()

    form_data: dict[str, str] = {}
    selections: dict[str, bool] = {}
    for control in controls:
        selected_key = f"control_{control.control_id}_selected"
        narrative_key = f"control_{control.control_id}_narrative"
        selections[control.control_id] = selected_key in form
        form_data[narrative_key] = str(form.get(narrative_key, "")).strip()

    errors: list[dict[str, str]] = []
    for control in controls:
        narrative_key = f"control_{control.control_id}_narrative"
        if selections[control.control_id] and not form_data[narrative_key]:
            errors.append(
                {
                    "field": narrative_key,
                    "msg": "Provide a narrative for selected controls.",
                }
            )

    preview = [
        {
            "control_id": control.control_id,
            "title": control.title,
            "narrative": form_data[f"control_{control.control_id}_narrative"],
        }
        for control in controls
        if selections[control.control_id]
    ]

    response = templates.TemplateResponse(
        request,
        "wizard/control_interview.html",
        {
            "controls": controls,
            "errors": errors,
            "form_data": form_data,
            "selected_controls": [
                control_id
                for control_id, selected in selections.items()
                if selected
            ],
            "preview": preview,
            "current_nav": "control-interview",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Control Interview", "href": None},
            ],
        },
        status_code=422 if errors else 200,
    )
    return cast(Response, response)


def _load_control_subset() -> list[ControlSummary]:
    data_dir = get_catalog_data_dir()
    manifest_path = get_manifest_path()
    if not manifest_path.exists():
        return []
    manifest = load_manifest(str(manifest_path))
    catalog_entry = next(
        (item for item in manifest.items if item.kind == "catalog"), None
    )
    if not catalog_entry:
        return []
    catalog_path = data_dir / catalog_entry.filename
    controls = load_catalog_controls(catalog_path)
    subset = select_controls_by_prefix(controls, prefix="ac-", limit=6)
    return subset
