from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OscalRole(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    role_id: str = Field(..., alias="id")
    title: str


class OscalParty(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    party_uuid: str = Field(..., alias="uuid")
    party_type: str = Field(..., alias="type")
    name: str
    email_addresses: list[str] = Field(default_factory=list, alias="email-addresses")


class OscalResponsibleParty(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    role_id: str = Field(..., alias="role-id")
    party_uuids: list[str] = Field(..., alias="party-uuids")


class OscalMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    title: str
    last_modified: str = Field(..., alias="last-modified")
    version: str
    oscal_version: str = Field(..., alias="oscal-version")
    roles: list[OscalRole]
    parties: list[OscalParty]
    responsible_parties: list[OscalResponsibleParty] = Field(
        ..., alias="responsible-parties"
    )


class OscalAuthorizationBoundary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    description: str


class OscalSystemCharacteristics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    system_name: str = Field(..., alias="system-name")
    description: str
    security_sensitivity_level: str = Field(
        ..., alias="security-sensitivity-level"
    )
    authorization_boundary: OscalAuthorizationBoundary = Field(
        ..., alias="authorization-boundary"
    )


class OscalComponent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    component_uuid: str = Field(..., alias="uuid")
    component_type: str = Field(..., alias="type")
    title: str
    description: str


class OscalSystemImplementation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    components: list[OscalComponent]


class OscalSystemSecurityPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    system_uuid: str = Field(..., alias="uuid")
    metadata: OscalMetadata
    system_characteristics: OscalSystemCharacteristics = Field(
        ..., alias="system-characteristics"
    )
    system_implementation: OscalSystemImplementation = Field(
        ..., alias="system-implementation"
    )


class OscalSspDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    system_security_plan: OscalSystemSecurityPlan = Field(
        ..., alias="system-security-plan"
    )
