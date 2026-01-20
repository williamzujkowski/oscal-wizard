from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Request

from engine.db import get_session
from engine.users import get_user_by_id


def get_sessionmaker(request: Request):
    return request.app.state.sessionmaker


async def get_current_user(
    request: Request,
    sessionmaker=Depends(get_sessionmaker),
):
    return await load_user(request, sessionmaker)


async def load_user(request: Request, sessionmaker=None):
    if sessionmaker is None:
        sessionmaker = request.app.state.sessionmaker
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


def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def verify_csrf(request: Request, csrf_token: str) -> None:
    expected = request.session.get("csrf_token")
    if not expected or not secrets.compare_digest(expected, csrf_token):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
