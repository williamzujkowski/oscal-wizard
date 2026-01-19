from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WizardStep:
    label: str
    href: str
    status: str


@dataclass(frozen=True)
class WizardCurrent:
    index: int
    total: int
    label: str


_STEP_DEFS = [
    ("System", "/system-foundation"),
    ("Components", "/inventory"),
    ("Parties", "/parties"),
    ("Controls", "/controls"),
    ("Interview", "/controls/interview"),
    ("Validate", "/validate"),
    ("Export", "/export"),
]


def build_wizard_steps(current_index: int) -> tuple[list[WizardStep], WizardCurrent]:
    steps: list[WizardStep] = []
    total = len(_STEP_DEFS)
    for idx, (label, href) in enumerate(_STEP_DEFS, start=1):
        if idx < current_index:
            status = "complete"
        elif idx == current_index:
            status = "current"
        else:
            status = "upcoming"
        steps.append(WizardStep(label=label, href=href, status=status))

    current_label = _STEP_DEFS[current_index - 1][0]
    current = WizardCurrent(index=current_index, total=total, label=current_label)
    return steps, current
