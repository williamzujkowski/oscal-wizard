from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()


@router.get("/", response_class=Response)
def home(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/home.html",
        {
            "current_nav": "home",
            "breadcrumbs": [],
        },
    )
    return cast(Response, response)


@router.get("/import", response_class=Response)
def import_workspace(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/import_workspace.html",
        {
            "current_nav": "home",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Import Workspace", "href": None},
            ],
        },
    )
    return cast(Response, response)
