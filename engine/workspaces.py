from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.models import WorkspaceRecord


async def list_workspaces(session: AsyncSession) -> list[WorkspaceRecord]:
    result = await session.execute(select(WorkspaceRecord).order_by(WorkspaceRecord.created_at))
    return list(result.scalars())


async def create_workspace(
    session: AsyncSession,
    *,
    name: str,
    system_id: str,
    data: dict[str, Any],
) -> WorkspaceRecord:
    record = WorkspaceRecord(name=name, system_id=system_id, data=data)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record
