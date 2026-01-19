from __future__ import annotations

import json
from typing import cast

from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import Response

from engine.audit import log_event
from engine.diff.json_diff import unified_json_diff
from engine.diff.narrative_diff import narrative_html_diff

router = APIRouter()


@router.get("/diff", response_class=Response)
def diff_form(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/diff_view.html",
        {
            "errors": [],
            "diff_text": "",
            "narrative_changes": [],
        },
    )
    return cast(Response, response)


@router.post("/diff", response_class=Response)
async def diff_submit(request: Request) -> Response:
    templates = request.app.state.templates
    form = await request.form()
    before_file = _as_upload_file(form.get("before_file"))
    after_file = _as_upload_file(form.get("after_file"))
    if before_file is None or after_file is None:
        response = templates.TemplateResponse(
            request,
            "wizard/diff_view.html",
            {
                "errors": ["Both JSON files are required."],
                "diff_text": "",
                "narrative_changes": [],
            },
            status_code=422,
        )
        return cast(Response, response)

    errors: list[str] = []

    before_payload = _load_json(before_file, errors)
    after_payload = _load_json(after_file, errors)
    if errors:
        response = templates.TemplateResponse(
            request,
            "wizard/diff_view.html",
            {
                "errors": errors,
                "diff_text": "",
                "narrative_changes": [],
            },
            status_code=422,
        )
        return cast(Response, response)

    diff_text = unified_json_diff(before_payload, after_payload)
    narrative_changes = _collect_narrative_changes(before_payload, after_payload)
    log_event(
        "diff_generated",
        {
            "before_filename": before_file.filename or "before.json",
            "after_filename": after_file.filename or "after.json",
        },
    )

    response = templates.TemplateResponse(
        request,
        "wizard/diff_view.html",
        {
            "errors": [],
            "diff_text": diff_text,
            "narrative_changes": narrative_changes,
        },
    )
    return cast(Response, response)


def _load_json(upload: UploadFile, errors: list[str]) -> dict[str, object]:
    content = upload.file.read()
    if not content:
        errors.append(f"{upload.filename or 'file'} is empty.")
        return {}
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        errors.append(f"{upload.filename or 'file'} is not valid JSON.")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{upload.filename or 'file'} must be a JSON object.")
        return {}
    return payload


def _as_upload_file(value: object) -> UploadFile | None:
    if isinstance(value, UploadFile):
        return value
    if hasattr(value, "filename") and hasattr(value, "file"):
        return value  # type: ignore[return-value]
    return None


def _collect_narrative_changes(
    before: dict[str, object], after: dict[str, object]
) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    before_map = _flatten_narratives(before)
    after_map = _flatten_narratives(after)
    for key in sorted(set(before_map) | set(after_map)):
        before_text = before_map.get(key, "")
        after_text = after_map.get(key, "")
        if before_text == after_text:
            continue
        changes.append(
            {
                "path": key,
                "diff": narrative_html_diff(before_text, after_text),
            }
        )
    return changes


def _flatten_narratives(payload: dict[str, object]) -> dict[str, str]:
    results: dict[str, str] = {}
    _walk_payload("$", payload, results)
    return results


def _walk_payload(path: str, value: object, results: dict[str, str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            _walk_payload(f"{path}.{key}", nested, results)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _walk_payload(f"{path}[{index}]", nested, results)
    else:
        if path.lower().endswith("narrative") and isinstance(value, str):
            results[path] = value
