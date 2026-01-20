from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from web.security import require_admin

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, user=Depends(require_admin)) -> HTMLResponse:
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "pages/admin.html",
        {"request": request, "user": user},
    )
