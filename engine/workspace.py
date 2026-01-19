from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SystemFoundation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    system_name: str = Field(..., min_length=1)
    impact_level: Literal["low", "moderate", "high"]
    authorization_boundary: str = Field(..., min_length=1)
    system_owner: str = Field(..., min_length=1)
    authorizing_official: str = Field(..., min_length=1)


class Workspace(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(default="0.1.0")
    system: SystemFoundation
