from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from engine.db import get_session
from engine.ids import deterministic_id
from engine.workspace import Workspace
from engine.workspaces import create_workspace as create_workspace_record
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


@router.post("")
async def workspaces_create(
    request: Request,
    name: str = Form(...),
    user=Depends(require_admin),
) -> RedirectResponse:
    system_id = deterministic_id(name)
    workspace = Workspace(
        system_name=name,
        system_id=system_id,
        created_at=datetime.now(timezone.utc),
    )
    sessionmaker = request.app.state.sessionmaker
    async for session in get_session(sessionmaker):
        await create_workspace_record(
            session,
            name=name,
            system_id=system_id,
            data=workspace.to_export_payload(),
        )

    return RedirectResponse(url="/admin/workspaces", status_code=303)


@router.get("/import", response_class=HTMLResponse)
def workspaces_import_form(request: Request, user=Depends(require_admin)) -> HTMLResponse:
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "pages/workspaces_import.html",
        {"request": request, "user": user},
    )


@router.post("/import")
async def workspaces_import(
    request: Request,
    workspace_file: UploadFile = File(...),
    user=Depends(require_admin),
) -> RedirectResponse:
    raw = await workspace_file.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON file") from exc

    workspace = Workspace.from_payload(payload)
    sessionmaker = request.app.state.sessionmaker
    async for session in get_session(sessionmaker):
        await create_workspace_record(
            session,
            name=workspace.system_name,
            system_id=workspace.system_id,
            data=workspace.to_export_payload(),
        )

    return RedirectResponse(url="/admin/workspaces", status_code=303)
