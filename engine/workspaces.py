from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.models import WorkspaceRecord


async def list_workspaces(session: AsyncSession) -> list[WorkspaceRecord]:
    result = await session.execute(
        select(WorkspaceRecord).order_by(WorkspaceRecord.updated_at.desc())
    )
    return list(result.scalars())


async def get_workspace(session: AsyncSession, workspace_id: str) -> WorkspaceRecord | None:
    result = await session.execute(
        select(WorkspaceRecord).where(WorkspaceRecord.id == workspace_id)
    )
    return result.scalar_one_or_none()


async def delete_workspace(session: AsyncSession, workspace_id: str) -> bool:
    record = await get_workspace(session, workspace_id)
    if record is None:
        return False
    await session.delete(record)
    await session.commit()
    return True


async def rename_workspace(session: AsyncSession, workspace_id: str, name: str) -> bool:
    record = await get_workspace(session, workspace_id)
    if record is None:
        return False
    record.name = name
    if isinstance(record.data, dict):
        record.data = {**record.data, "system_name": name}
    record.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return True


async def create_workspace(
    session: AsyncSession,
    *,
    name: str,
    system_id: str,
    data: dict[str, Any],
    created_at: datetime | None = None,
    owner_id: str | None = None,
) -> WorkspaceRecord:
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    record = WorkspaceRecord(
        name=name,
        system_id=system_id,
        owner_id=owner_id,
        data=data,
        created_at=created_at,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record
