from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str = Field(..., min_length=1)
    last_modified: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    oscal_version: str = Field(..., min_length=1)
    content_version: str = Field(..., min_length=1)


class Role(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    role_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)


class Party(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    party_uuid: str = Field(..., min_length=1)
    party_type: Literal["organization", "person"]
    name: str = Field(..., min_length=1)
    email_addresses: list[str] = Field(default_factory=list)


class ResponsibleParty(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    role_id: str = Field(..., min_length=1)
    party_uuids: list[str] = Field(min_length=1)


class Component(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    component_uuid: str = Field(..., min_length=1)
    component_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class ComponentDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    component_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class SystemFoundation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    system_uuid: str = Field(..., min_length=1)
    system_name: str = Field(..., min_length=1)
    impact_level: Literal["low", "moderate", "high"]
    authorization_boundary: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    system_owner: str = Field(..., min_length=1)
    authorizing_official: str = Field(..., min_length=1)


class Workspace(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(default="0.2.0")
    metadata: WorkspaceMetadata = Field(
        default_factory=lambda: WorkspaceMetadata(
            title="Untitled SSP Workspace",
            last_modified="1970-01-01T00:00:00-05:00",
            version="0.0.0",
            oscal_version="1.2.0",
            content_version="1.4.0",
        )
    )
    system: SystemFoundation
    roles: list[Role] = Field(default_factory=list)
    parties: list[Party] = Field(default_factory=list)
    responsible_parties: list[ResponsibleParty] = Field(default_factory=list)
    components: list[Component] = Field(default_factory=list)
