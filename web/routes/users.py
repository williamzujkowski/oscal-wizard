from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response

from engine.db import get_session
from engine.models import User
from engine.users import get_user_by_id, list_users
from web.security import require_admin

router = APIRouter(prefix="/admin/users")


@router.get("", response_class=HTMLResponse)
async def users_index(request: Request, user: User = Depends(require_admin)) -> Response:
    sessionmaker = request.app.state.sessionmaker
    async for session in get_session(sessionmaker):
        users = await list_users(session)

    templates = request.app.state.templates
    return cast(
        Response,
        templates.TemplateResponse(
            "pages/users.html",
            {"request": request, "user": user, "users": users},
        ),
    )


@router.get("/{user_id}", response_class=HTMLResponse)
async def user_detail(
    request: Request,
    user_id: str,
    user: User = Depends(require_admin),
) -> Response:
    sessionmaker = request.app.state.sessionmaker
    async for session in get_session(sessionmaker):
        record = await get_user_by_id(session, user_id)

    if record is None:
        raise HTTPException(status_code=404, detail="User not found")

    templates = request.app.state.templates
    return cast(
        Response,
        templates.TemplateResponse(
            "pages/user_detail.html",
            {"request": request, "user": user, "record": record},
        ),
    )
