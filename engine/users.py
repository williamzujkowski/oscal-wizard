from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.models import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def has_admin(session: AsyncSession) -> bool:
    result = await session.execute(select(User.id).where(User.is_admin.is_(True)))
    return result.first() is not None


async def upsert_user(
    session: AsyncSession,
    *,
    provider: str,
    provider_id: str,
    email: str,
    display_name: str,
    is_admin: bool,
) -> User:
    normalized_email = normalize_email(email)
    result = await session.execute(
        select(User).where(User.provider == provider, User.provider_id == provider_id)
    )
    user = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if user is None:
        user = User(
            email=normalized_email,
            provider=provider,
            provider_id=provider_id,
            display_name=display_name,
            is_admin=is_admin,
            created_at=now,
            last_login_at=now,
        )
        session.add(user)
    else:
        user.email = normalized_email
        user.display_name = display_name
        user.last_login_at = now
        if is_admin:
            user.is_admin = True

    await session.commit()
    await session.refresh(user)
    return user
