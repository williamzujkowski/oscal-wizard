from __future__ import annotations

import json

from engine.oscal.ssp import (
    OscalAuthorizationBoundary,
    OscalComponent,
    OscalMetadata,
    OscalParty,
    OscalResponsibleParty,
    OscalRole,
    OscalSspDocument,
    OscalSystemCharacteristics,
    OscalSystemImplementation,
    OscalSystemSecurityPlan,
)
from engine.workspace import Workspace


def workspace_to_canonical_json(workspace: Workspace) -> str:
    payload = workspace.model_dump(mode="json")
    return json.dumps(payload, sort_keys=True, indent=2)


def export_ssp_json(workspace: Workspace) -> str:
    ssp = _build_ssp(workspace)
    payload = ssp.model_dump(by_alias=True, mode="json")
    return json.dumps(payload, sort_keys=True, indent=2)


def _build_ssp(workspace: Workspace) -> OscalSspDocument:
    roles = [
        OscalRole.model_validate({"id": role.role_id, "title": role.title})
        for role in workspace.roles
    ]
    parties = [
        OscalParty.model_validate(
            {
                "uuid": party.party_uuid,
                "type": party.party_type,
                "name": party.name,
                "email-addresses": party.email_addresses,
            }
        )
        for party in workspace.parties
    ]
    responsible_parties = [
        OscalResponsibleParty.model_validate(
            {
                "role-id": rp.role_id,
                "party-uuids": rp.party_uuids,
            }
        )
        for rp in workspace.responsible_parties
    ]
    metadata = OscalMetadata.model_validate(
        {
            "title": workspace.metadata.title,
            "last-modified": workspace.metadata.last_modified,
            "version": workspace.metadata.version,
            "oscal-version": workspace.metadata.oscal_version,
            "roles": roles,
            "parties": parties,
            "responsible-parties": responsible_parties,
        }
    )
    characteristics = OscalSystemCharacteristics.model_validate(
        {
            "system-name": workspace.system.system_name,
            "description": workspace.system.description,
            "security-sensitivity-level": workspace.system.impact_level,
            "authorization-boundary": OscalAuthorizationBoundary.model_validate(
                {"description": workspace.system.authorization_boundary}
            ),
        }
    )
    components = [
        OscalComponent.model_validate(
            {
                "uuid": component.component_uuid,
                "type": component.component_type,
                "title": component.title,
                "description": component.description,
            }
        )
        for component in workspace.components
    ]
    implementation = OscalSystemImplementation.model_validate(
        {"components": components}
    )
    ssp = OscalSystemSecurityPlan.model_validate(
        {
            "uuid": workspace.system.system_uuid,
            "metadata": metadata,
            "system-characteristics": characteristics,
            "system-implementation": implementation,
        }
    )
    return OscalSspDocument.model_validate({"system-security-plan": ssp})
