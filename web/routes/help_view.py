from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()


@router.get("/help", response_class=Response)
def help_page(request: Request) -> Response:
    templates = request.app.state.templates
    response = templates.TemplateResponse(
        request,
        "wizard/help.html",
        {
            "current_nav": "help",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Help & About", "href": None},
            ],
        },
    )
    return cast(Response, response)
