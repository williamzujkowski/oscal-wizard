from __future__ import annotations

import json
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from engine.oscal.ssp import OscalSspDocument
from engine.workspace import Workspace


@dataclass(frozen=True)
class ValidationFinding:
    severity: str
    message: str
    location: str


def validate_workspace(workspace: Workspace) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []

    if workspace.metadata.oscal_version != "1.2.0":
        findings.append(
            ValidationFinding(
                severity="error",
                message="Unsupported OSCAL version.",
                location="metadata.oscal_version",
            )
        )

    if workspace.metadata.content_version != "1.4.0":
        findings.append(
            ValidationFinding(
                severity="error",
                message="Unsupported OSCAL content version.",
                location="metadata.content_version",
            )
        )

    findings.extend(
        _validate_unique_ids("roles", [role.role_id for role in workspace.roles])
    )
    findings.extend(
        _validate_unique_ids(
            "parties", [party.party_uuid for party in workspace.parties]
        )
    )

    findings.extend(
        _validate_uuid_fields(
            "system.system_uuid",
            [workspace.system.system_uuid],
        )
    )
    findings.extend(
        _validate_uuid_fields(
            "parties.party_uuid", [party.party_uuid for party in workspace.parties]
        )
    )
    findings.extend(
        _validate_uuid_fields(
            "components.component_uuid",
            [component.component_uuid for component in workspace.components],
        )
    )

    role_ids = {role.role_id for role in workspace.roles}
    party_ids = {party.party_uuid for party in workspace.parties}
    for item in workspace.responsible_parties:
        if item.role_id not in role_ids:
            findings.append(
                ValidationFinding(
                    severity="error",
                    message="Responsible party references unknown role.",
                    location=f"responsible_parties.{item.role_id}",
                )
            )
        for party_uuid in item.party_uuids:
            if party_uuid not in party_ids:
                findings.append(
                    ValidationFinding(
                        severity="error",
                        message="Responsible party references unknown party.",
                        location=f"responsible_parties.{party_uuid}",
                    )
                )

    return findings


def validate_ssp_json(payload: dict[str, object]) -> list[ValidationFinding]:
    try:
        OscalSspDocument.model_validate(payload)
    except ValidationError as exc:
        return [
            ValidationFinding(
                severity="error",
                message=error["msg"],
                location=".".join(str(part) for part in error["loc"]),
            )
            for error in exc.errors()
        ]
    return []


def validate_ssp_file(path: Path) -> list[ValidationFinding]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return [
            ValidationFinding(
                severity="error",
                message="SSP JSON must be an object.",
                location="root",
            )
        ]
    return validate_ssp_json(payload)


def _validate_uuid_fields(
    location: str, values: Iterable[str]
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    for value in values:
        try:
            uuid.UUID(value)
        except ValueError:
            findings.append(
                ValidationFinding(
                    severity="error",
                    message="Invalid UUID.",
                    location=location,
                )
            )
    return findings


def _validate_unique_ids(location: str, values: list[str]) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    duplicates = {value for value in values if values.count(value) > 1}
    for value in sorted(duplicates):
        findings.append(
            ValidationFinding(
                severity="error",
                message="Duplicate identifier.",
                location=f"{location}.{value}",
            )
        )
    return findings
