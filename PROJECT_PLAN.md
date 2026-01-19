Here is the fully consolidated, updated project plan. It incorporates your original vision with the critical "Component Definition" and "Headless" capabilities found in tools like Trestle and RegScale, ensuring your tool remains lightweight but interoperable.

---

# Open OSCAL Wizard (Provisional)

## Mission

A lightweight, self-hostable web tool that guides non-technical users through creating valid, deterministic, and reviewable OSCAL System Security Plans (SSPs) using a TurboTax-style interview workflow.

**Primary success criterion:**
A user can produce an OSCAL SSP that:

* Passes OSCAL schema validation.
* Passes internal consistency and policy checks.
* Produces stable, deterministic output across exports.
* Is accessible, auditable, and contributor-maintainable.

## 1. Core Principles (Non-Negotiable)

* **Accuracy over automation:** We do not attempt magical DOCX/PDF conversion. Human-guided entry with guardrails produces better OSCAL and lower long-term maintenance cost.
* **Engine-first architecture:** OSCAL generation, validation, diffing, and determinism live in a standalone Python engine. The web UI is a thin layer. The engine must be callable via CLI for CI/CD pipelines.
* **Progressive enhancement, not SPA:** Server-rendered HTML for clarity and accessibility. JavaScript is used only for UI state, never business logic.
* **Stateless by default, storage by choice:** Drafts are local unless explicitly configured otherwise. Server persistence is optional and auditable.
* **Deterministic outputs:** Same inputs must produce byte-stable OSCAL outputs.
* **Accessibility built-in, not retrofitted:** USWDS patterns + enforced accessibility checks from day one.
* **Fresh, stable, non-deprecated dependencies:** Latest stable versions at release time. Deprecated packages or techniques are not allowed.

## 2. Architecture Overview: The “Modern Monolith”

A single deployable service with clean internal boundaries.

* No SPA build pipeline at runtime
* No Node.js required for application execution
* Optional maintainer workflows for asset updates
* Clean separation between engine and web layers

## 3. Tech Stack

**Backend**

* **Language:** Python 3.11+
* **Web framework:** FastAPI
* **Templates:** Jinja2
* **Data modeling:** Pydantic (strict)
* **Dependency management:** pyproject.toml + lockfile (uv or Poetry)
* **Testing:** pytest

**Frontend**

* **Design system:** USWDS 3.x (native HTML/CSS)
* **Interactivity:** Alpine.js (UI state only)
* **Rich Text:** Markdown support for narratives (rendered server-side)
* **Accessibility:** WCAG 2.1 AA baseline (USWDS-aligned)

**Control Catalog Source**

* **Authoritative source:** NIST-published OSCAL JSON catalogs/profiles hosted on GitHub
* **Usage:** Populate control identifiers, titles, parameters, and structure
* **Rule:** Control data is rendered from catalog JSON, not hard-coded into templates

**Deployment**

* **Local:** Docker / docker-compose
* **Hosted:** cloud.gov (Python buildpack) or equivalent
* **No runtime Node.js requirement**

## 4. Dependency Freshness & Deprecation Policy

**Policy**

* Use the latest stable versions of all dependencies at release time.
* No deprecated libraries, APIs, or techniques.
* Versions are pinned via lockfiles for reproducibility.
* Dependencies are refreshed on a scheduled cadence.

**Python**

* Managed via `pyproject.toml`
* Lockfile committed to repo
* Automated upgrade PRs (weekly/biweekly)
* **CI gates:**
* Dependency vulnerability scan
* Deprecated package detection
* Lockfile consistency check



**Frontend Assets (USWDS)**

* Vendored compiled assets committed to repo for runtime simplicity.
* Maintainer-only script to:
* Fetch/build latest stable USWDS
* Update vendored output
* Generate an asset manifest (version, hash, date)


* **CI verifies:**
* Asset manifest matches vendored files
* No deprecated USWDS major version is used



## 5. Data Model: Workspace-First

**Workspace**
A workspace is the authoritative internal representation of the SSP in progress.

* Stored as a single JSON document
* Versioned and migratable
* Contains:
* System metadata
* Parties and roles
* Components/inventory
* Control implementations
* Assigned UUIDs (persisted for determinism)
* Metadata and timestamps



**Component Library Support (The Lego Strategy)**

* Ability to ingest external OSCAL `component-definition` JSON files.
* **Inheritance:** SSP implementations can link to component definitions to pre-fill "Responsibility" and "Implementation Status" fields (e.g., importing an "AWS Cloud" component to inherit physical security controls).

**Persistence Modes**

* **Default (Local-only):**
* Draft stored in browser storage
* Explicit banner warning (“device-local only”)
* Exportable workspace JSON


* **Optional (Server-side drafts):**
* Postgres preferred (Redis for short-lived drafts only)
* Auth-protected
* Encryption at rest
* Audit log of saves and exports



## 6. Auth Strategy (Docker-First, Production-Ready)

**Local / Dev**

* No auth by default
* Optional basic auth flag for exposed environments

**Production (Recommended)**

* **Auth at the edge, not in the app**
* OIDC-capable reverse proxy (e.g., oauth2-proxy) or platform gateway
* SAML terminated at proxy/gateway if required
* App trusts identity headers only from trusted network paths

**Rationale**

* Avoids fragile in-app SAML implementations
* Keeps FastAPI code simple and testable
* Matches common government platform patterns (UAA, enterprise IdPs)

## 7. Validation & Deterministic Export

**Validation Layers**

* **OSCAL JSON schema validation:** Strict validation against official NIST schemas.
* **Referential integrity checks:** Ensures all UUIDs, component refs, and links are valid.
* **Policy checks:** Required narratives, formatting rules, ownership rules.

**Headless Validation (CI/CD Ready)**

* The `engine.validate` module is exposed as a CLI command (e.g., `python main.py validate --file ssp.json`).
* Allows power users to validate artifacts in pipelines without the UI.

**Determinism Rules**

* Stable UUID assignment stored in workspace
* Canonical JSON ordering
* Canonical formatting
* Golden-file tests enforce byte-stable output

**Output Formats**

* OSCAL SSP JSON (MVP)
* OSCAL SSP XML (optional, later)

## 8. Diffing & Review

**Diff Capabilities**

* **Workspace diff:** Structured JSON diff (RFC-6902 style)
* **Export diff:** Canonicalized OSCAL JSON diff
* **Narrative Diffing:**
* Text fields are treated as Markdown.
* Visual "Track Changes" style diff for long narrative fields (Red/Green text highlighting) rather than raw JSON string comparison.


* **Optional semantic grouping:**
* System metadata
* Components
* Controls



**UI**

* “Changes since last save/export”
* Reviewer-friendly change summary
* Optional export-embedded changelog

## 9. Accessibility (Mandatory)

**Standards**

* WCAG 2.1 AA baseline
* USWDS-compliant components and patterns

**Requirements**

* USWDS error summaries
* Focus management on validation errors
* Keyboard-only navigation
* Proper labels, hints, and required markers
* No hidden required fields

**Testing**

* Automated accessibility scans on key pages
* Manual checklist for MVP workflows

## 10. Repository Structure

```text
/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── uv.lock / poetry.lock
├── main.py
├── engine/
│   ├── workspace/
│   ├── oscal/
│   ├── catalog/
│   ├── components/       <-- New: Component definition loader
│   ├── validate/
│   ├── export/
│   └── diff/
├── web/
│   ├── routes/
│   ├── templates/
│   │   ├── layouts/
│   │   ├── components/
│   │   └── wizard/
│   └── static/
│       ├── uswds/
│       └── app/
├── scripts/
│   ├── fetch_nist_catalogs.py
│   └── update_uswds_assets.*
└── tests/
    ├── fixtures/
    ├── golden_exports/
    └── test_*.py

```

## 11. User Workflow (Wizard)

1. **System Foundation:** System name, impact level, authorization context, parties.
2. **Components / Inventory:**
* Free-text component entry.
* Optional: "Import Component" from library (OSCAL `component-definition`).


3. **Control Interview:**
* Catalog-driven control selection.
* Narrative (Markdown supported), evidence metadata, responsibility split.
* Server-driven logic; Alpine for UI toggles only.


4. **Validate & Generate:**
* Validation report (Schema + Logic).
* OSCAL export.
* Workspace export.


5. **Review & Diff:**
* Compare with previous versions.
* Reviewer-friendly summary (Visual Markdown diffs).



## 12. Roadmap (Realistic)

**Phase 1: Walking Skeleton (Weeks 1–2)**

* Dockerized FastAPI app
* USWDS base layout
* System Foundation form
* Local workspace export
* Smoke tests

**Phase 2: Catalog & Component Ingestion (Weeks 3–4)**

* Fetch/pin NIST OSCAL catalogs
* **Component Loader:** Capability to load a "Standard Component Library" (JSON files)
* Control picker UI
* Catalog ingestion tests

**Phase 3: Engine & Deterministic Export (Weeks 5–7)**

* Workspace schema
* SSP JSON export
* Golden-file tests
* Validation layers
* **Headless CLI validation command**

**Phase 4: Control Interview UX (Weeks 8–10)**

* Limited control set
* Accessible wizard UI
* Error summaries and keyboard navigation
* Markdown rendering for narratives

**Phase 5: Diff & Server Drafts (Optional)**

* Workspace/export diff UI with visual narrative diffs
* Auth-protected persistence
* Audit logging

## 13. Explicit Non-Goals

* Automated DOCX/PDF narrative conversion (Focus is structured data).
* Full GRC system replacement (Focus is creation/editing).
* In-app SAML implementation (Delegated to proxy).
* Maintaining a full CMDB (Focus is SSP inventory).
* Supporting all control families in MVP.