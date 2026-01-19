# Open OSCAL Wizard - UX/CX Page Plan

This document defines the page map and content requirements for the wizard.
It supports OSCAL SSP creation with deterministic exports and accessible UX.

## 1. Navigation & IA

- Global primary navigation: System Foundation, Control Picker, Control Interview, Diff Viewer.
- Wizard stepper: shows current step and remaining steps across the SSP flow.
- Breadcrumbs: display hierarchy and current page.
- CTA pattern: one primary action per page, optional secondary actions.

## 2. Page Map (MVP + Near-Term)

### 2.1 Landing / Home
Purpose:
- Explain the tool and start the wizard.

Content:
- Short summary of what the wizard does.
- CTAs: "Start new workspace", "Import workspace".
- Local-only storage warning and link to settings.
- Links to Validate, Export, Diff Viewer.

### 2.2 System Foundation
Purpose:
- Capture core system metadata for SSP and workspace.

Content:
- System name, description, impact level, authorization boundary.
- System owner and authorizing official.
- Required field markers and hints.
- Save draft (local) and next-step CTA.

### 2.3 Components / Inventory
Purpose:
- Define the system components used in the SSP.

Content:
- Components list (type, title, description, UUID).
- Add/edit component form.
- Import component-definition JSON library.
- Validation for duplicates and missing required fields.

### 2.4 Parties & Roles
Purpose:
- Define parties and map roles to parties.

Content:
- Roles list with title and role-id.
- Parties list (person or organization, email).
- Responsible parties mapping (role -> parties).
- Validation for unknown references and duplicates.

### 2.5 Control Picker
Purpose:
- Select controls from pinned catalogs or profiles.

Content:
- Active catalog/profile indicator and version info.
- Search and filter for control IDs/titles.
- Selected control count and CTA to Control Interview.

### 2.6 Control Interview
Purpose:
- Capture narratives for selected controls.

Content:
- Per-control checkbox and narrative field.
- Implementation status and evidence metadata (future).
- Markdown preview (CommonMark, HTML disabled).
- Error summary focus on submit.

### 2.7 Validate
Purpose:
- Surface validation issues before export.

Content:
- Findings grouped by severity.
- Links to sections to resolve errors.
- Re-run validation CTA.

### 2.8 Export
Purpose:
- Generate deterministic artifacts.

Content:
- Export workspace JSON.
- Export SSP JSON (OSCAL v1.2.0).
- Notes about deterministic output and version metadata.

### 2.9 Diff Viewer
Purpose:
- Compare workspace or SSP JSON versions.

Content:
- Two JSON file inputs.
- Unified JSON diff output.
- Narrative inline diffs with red/green highlights.

### 2.10 Settings / Catalog Management
Purpose:
- Manage catalog and component library pins.

Content:
- Catalog manifest list with version and hash.
- Refresh/re-pin catalog action.
- Component library status.

### 2.11 Help / About
Purpose:
- Explain constraints and supported versions.

Content:
- OSCAL standard version 1.2.0 and content 1.4.0.
- Limitations (no PDF/DOCX conversion).
- Link to OSCAL resources and tool usage tips.

## 3. Shared UX Requirements

- Accessibility: WCAG 2.1 AA, visible focus states, labels for all inputs.
- Error handling: USWDS error summary, focus on error summary.
- Determinism: avoid random values in UI output.
- Empty states: guide users to next steps when lists are empty.
- Mobile: ensure layout works on narrow screens.

## 4. Page Dependencies

- System Foundation -> Components -> Parties & Roles -> Control Picker -> Control Interview -> Validate -> Export.
- Diff Viewer and Help are always accessible.
- Settings supports catalog pinning for Control Picker.
