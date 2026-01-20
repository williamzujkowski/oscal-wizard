from typing import cast

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response

from engine.models import User
from web.security import require_admin

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, user: User = Depends(require_admin)) -> Response:
    templates = request.app.state.templates
    return cast(
        Response,
        templates.TemplateResponse(
            "pages/admin.html",
            {"request": request, "user": user},
        ),
    )
