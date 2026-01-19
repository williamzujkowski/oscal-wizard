from __future__ import annotations

import json
from typing import cast

from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import Response

from engine.validate import validate_ssp_json, validate_workspace
from engine.workspace import Workspace

router = APIRouter()


@router.get("/validate", response_class=Response)
def validate_form(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/validate.html",
        {
            "errors": [],
            "findings": [],
            "submitted": False,
            "current_nav": "validate",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Validate", "href": None},
            ],
        },
    )
    return cast(Response, response)


@router.post("/validate", response_class=Response)
async def validate_submit(request: Request) -> Response:
    templates = request.app.state.templates
    form = await request.form()
    json_file = _as_upload_file(form.get("json_file"))
    if json_file is None:
        response = templates.TemplateResponse(
            request,
            "wizard/validate.html",
            {
                "errors": ["Workspace or SSP JSON file is required."],
                "findings": [],
                "submitted": True,
                "current_nav": "validate",
                "breadcrumbs": [
                    {"label": "Home", "href": "/"},
                    {"label": "Validate", "href": None},
                ],
            },
            status_code=422,
        )
        return cast(Response, response)

    errors: list[str] = []
    findings: list[dict[str, str]] = []

    payload = _load_json(json_file, errors)
    if errors:
        response = templates.TemplateResponse(
            request,
            "wizard/validate.html",
            {
                "errors": errors,
                "findings": [],
                "submitted": True,
                "current_nav": "validate",
                "breadcrumbs": [
                    {"label": "Home", "href": "/"},
                    {"label": "Validate", "href": None},
                ],
            },
            status_code=422,
        )
        return cast(Response, response)

    if "system-security-plan" in payload:
        validation_results = validate_ssp_json(payload)
    else:
        try:
            workspace = Workspace.model_validate(payload)
        except Exception as exc:  # pragma: no cover - fallback for unexpected errors
            errors.append(str(exc))
            validation_results = []
        else:
            validation_results = validate_workspace(workspace)

    findings = [
        {
            "severity": result.severity,
            "location": result.location,
            "message": result.message,
        }
        for result in validation_results
    ]

    response = templates.TemplateResponse(
        request,
        "wizard/validate.html",
        {
            "errors": errors,
            "findings": findings,
            "submitted": True,
            "current_nav": "validate",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Validate", "href": None},
            ],
        },
        status_code=422 if errors else 200,
    )
    return cast(Response, response)


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
