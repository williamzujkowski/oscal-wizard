from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from engine.db import get_session
from engine.workspaces import list_workspaces
from web.security import require_admin

router = APIRouter(prefix="/admin/workspaces")


@router.get("", response_class=HTMLResponse)
async def workspaces_index(request: Request, user=Depends(require_admin)) -> HTMLResponse:
    sessionmaker = request.app.state.sessionmaker
    async for session in get_session(sessionmaker):
        records = await list_workspaces(session)

    templates = request.app.state.templates
    return templates.TemplateResponse(
        "pages/workspaces.html",
        {"request": request, "user": user, "workspaces": records},
    )
