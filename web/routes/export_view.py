from __future__ import annotations

import json
from typing import cast

from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import Response

from engine.export import export_ssp_json
from engine.workspace import Workspace

router = APIRouter()


@router.get("/export", response_class=Response)
def export_form(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/export.html",
        {
            "errors": [],
            "current_nav": "export",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Export", "href": None},
            ],
        },
    )
    return cast(Response, response)


@router.post("/export/ssp", response_class=Response)
async def export_ssp(request: Request) -> Response:
    templates = request.app.state.templates
    form = await request.form()
    workspace_file = _as_upload_file(form.get("workspace_file"))
    if workspace_file is None:
        response = templates.TemplateResponse(
            request,
            "wizard/export.html",
            {
                "errors": ["Workspace JSON file is required."],
                "current_nav": "export",
                "breadcrumbs": [
                    {"label": "Home", "href": "/"},
                    {"label": "Export", "href": None},
                ],
            },
            status_code=422,
        )
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
                "breadcrumbs": [
                    {"label": "Home", "href": "/"},
                    {"label": "Export", "href": None},
                ],
            },
            status_code=422,
        )
        return cast(Response, response)

    workspace = Workspace.model_validate(payload)
    ssp_json = export_ssp_json(workspace)
    headers = {"Content-Disposition": "attachment; filename=ssp.json"}
    return Response(content=ssp_json, media_type="application/json", headers=headers)


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
