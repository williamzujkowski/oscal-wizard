from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, Response

from engine.db import get_session
from engine.users import has_admin, upsert_user
from web.settings import get_settings

router = APIRouter(prefix="/auth")


async def _get_oauth_client(request: Request, provider: str) -> Any:
    oauth = request.app.state.oauth
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=404, detail="Provider not configured")
    return client


@router.get("/login/{provider}")
async def login(request: Request, provider: str) -> Response:
    client = await _get_oauth_client(request, provider)
    redirect_uri = request.url_for("auth_callback", provider=provider)
    return cast(Response, await client.authorize_redirect(request, redirect_uri))


@router.get("/callback/{provider}", name="auth_callback")
async def callback(request: Request, provider: str) -> RedirectResponse:
    client = await _get_oauth_client(request, provider)
    token = await client.authorize_access_token(request)

    user_info: dict[str, Any]

    if provider == "github":
        profile = await client.get("user", token=token)
        emails = await client.get("user/emails", token=token)
        profile_data = profile.json()
        emails_data = emails.json()
        primary_email = next(
            (email["email"] for email in emails_data if email.get("primary")),
            None,
        )
        user_info = {
            "email": primary_email or profile_data.get("email"),
            "provider_id": str(profile_data.get("id")),
            "display_name": profile_data.get("name") or profile_data.get("login"),
        }
    elif provider == "google":
        userinfo = await client.get("userinfo", token=token)
        userinfo_data = userinfo.json()
        user_info = {
            "email": userinfo_data.get("email"),
            "provider_id": userinfo_data.get("sub"),
            "display_name": userinfo_data.get("name") or userinfo_data.get("email"),
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    email = user_info.get("email")
    provider_id = user_info.get("provider_id")
    display_name = user_info.get("display_name")

    if not email or not provider_id:
        raise HTTPException(status_code=400, detail="Email not available from provider")

    settings = get_settings()
    sessionmaker = request.app.state.sessionmaker
    async for session in get_session(sessionmaker):
        allowlist = settings.admin_allowlist_set()
        allowlist_match = email.lower() in allowlist
        existing_admin = await has_admin(session)
        is_admin = allowlist_match and (
            settings.admin_allowlist_enabled or not existing_admin
        )
        user = await upsert_user(
            session,
            provider=provider,
            provider_id=provider_id,
            email=email,
            display_name=display_name or email,
            is_admin=is_admin,
        )

    request.session["user_id"] = user.id

    return RedirectResponse(url="/")


@router.post("/logout")
async def logout(request: Request, csrf_token: str | None = Form(None)) -> RedirectResponse:
    from web.security import verify_csrf

    verify_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
