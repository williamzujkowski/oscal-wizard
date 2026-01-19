from __future__ import annotations

import json
from typing import cast

from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import Response

from engine.export import export_ssp_json
from engine.workspace import Workspace
from web.routes.wizard_steps import build_wizard_steps
from web.state import attach_session_cookie, get_wizard_state

router = APIRouter()


@router.get("/export", response_class=Response)
def export_form(request: Request) -> Response:
    templates = request.app.state.templates
    session_id, state, is_new = get_wizard_state(request)
    response = templates.TemplateResponse(
        request,
        "wizard/export.html",
        {
            "errors": [],
            "current_nav": "export",
            "wizard_steps": build_wizard_steps(7)[0],
            "wizard_current": build_wizard_steps(7)[1],
            "export_ready": state.last_export is not None,
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Export", "href": None},
            ],
        },
    )
    attach_session_cookie(response, session_id, is_new)
    return cast(Response, response)


@router.post("/export/ssp", response_class=Response)
async def export_ssp(request: Request) -> Response:
    templates = request.app.state.templates
    session_id, state, is_new = get_wizard_state(request)
    form = await request.form()
    workspace_file = _as_upload_file(form.get("workspace_file"))
    if workspace_file is None:
        response = templates.TemplateResponse(
            request,
            "wizard/export.html",
            {
                "errors": ["Workspace JSON file is required."],
                "current_nav": "export",
                "wizard_steps": build_wizard_steps(7)[0],
                "wizard_current": build_wizard_steps(7)[1],
                "export_ready": state.last_export is not None,
                "breadcrumbs": [
                    {"label": "Home", "href": "/"},
                    {"label": "Export", "href": None},
                ],
            },
            status_code=422,
        )
        attach_session_cookie(response, session_id, is_new)
        return cast(Response, response)

    errors: list[str] = []
    payload = _load_json(workspace_file, errors)
    if errors:
        response = templates.TemplateResponse(
            request,
            "wizard/export.html",
            {
                "errors": errors,
                "current_nav": "export",
                "wizard_steps": build_wizard_steps(7)[0],
                "wizard_current": build_wizard_steps(7)[1],
                "export_ready": state.last_export is not None,
                "breadcrumbs": [
                    {"label": "Home", "href": "/"},
                    {"label": "Export", "href": None},
                ],
            },
            status_code=422,
        )
        attach_session_cookie(response, session_id, is_new)
        return cast(Response, response)

    workspace = Workspace.model_validate(payload)
    state.last_export = export_ssp_json(workspace)
    response = templates.TemplateResponse(
        request,
        "wizard/export.html",
        {
            "errors": [],
            "current_nav": "export",
            "wizard_steps": build_wizard_steps(7)[0],
            "wizard_current": build_wizard_steps(7)[1],
            "export_ready": True,
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Export", "href": None},
            ],
        },
    )
    attach_session_cookie(response, session_id, is_new)
    return cast(Response, response)


@router.get("/export/download", response_class=Response)
def export_download(request: Request) -> Response:
    session_id, state, is_new = get_wizard_state(request)
    if state.last_export is None:
        response = Response(
            content="No exported SSP available.",
            media_type="text/plain",
            status_code=404,
        )
        attach_session_cookie(response, session_id, is_new)
        return response

    headers = {"Content-Disposition": "attachment; filename=ssp.json"}
    response = Response(
        content=state.last_export,
        media_type="application/json",
        headers=headers,
    )
    attach_session_cookie(response, session_id, is_new)
    return response


def _load_json(upload: UploadFile, errors: list[str]) -> dict[str, object]:
    content = upload.file.read()
    if not content:
        errors.append("Uploaded file is empty.")
        return {}
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        errors.append("Uploaded file is not valid JSON.")
        return {}
    if not isinstance(payload, dict):
        errors.append("Uploaded JSON must be an object.")
        return {}
    return payload


def _as_upload_file(value: object) -> UploadFile | None:
    if isinstance(value, UploadFile):
        return value
    if hasattr(value, "filename") and hasattr(value, "file"):
        return value  # type: ignore[return-value]
    return None
