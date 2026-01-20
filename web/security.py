from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from engine.db import get_session
from engine.users import get_user_by_id


def get_sessionmaker(request: Request):
    return request.app.state.sessionmaker


async def get_current_user(
    request: Request,
    sessionmaker=Depends(get_sessionmaker),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    async for session in get_session(sessionmaker):
        user = await get_user_by_id(session, user_id)
        return user

    return None


def require_user(user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_admin(user=Depends(require_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
