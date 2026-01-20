from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> Response:
    templates = request.app.state.templates
    return cast(
        Response,
        templates.TemplateResponse(
            "pages/home.html",
            {"request": request},
        ),
    )
