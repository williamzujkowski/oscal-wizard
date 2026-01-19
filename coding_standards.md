# Open OSCAL Wizard - Coding Standards

**Version:** 1.0.0
**Last Updated:** 2026-01-19 (ET)
**Stack:** Python 3.11+, FastAPI, Pydantic, USWDS, Alpine.js
**Status:** Active

---

## Table of Contents

0. [Prime Directive: Determinism](#0-prime-directive-determinism)
1. [Architecture: The Modern Monolith](#1-architecture-the-modern-monolith)
2. [Python Standards (Engine)](#2-python-standards-engine)
3. [Frontend Standards (Web)](#3-frontend-standards-web)
4. [OSCAL Data Modeling](#4-oscal-data-modeling)
5. [Security & Sandbox](#5-security--sandbox)
6. [Testing & Quality Gates](#6-testing--quality-gates)
7. [Dependency Management](#7-dependency-management)

---

## 0. Prime Directive: Determinism

**Priority hierarchy for technical decisions:**


```

Accuracy > Determinism > Accessibility > Simplicity > Performance

```

### 0.1 The "Golden File" Rule
Every OSCAL export feature must include a **Golden File Test**.
- **Input:** A fixed `workspace.json` fixture.
- **Output:** A generated `ssp.json` file.
- **Assertion:** The output must match the "Golden" reference file **byte-for-byte**.

### 0.2 No "Magical" Inference
- We do not guess user intent. We ask.
- We do not auto-generate content without review.
- We do not use LLMs to hallucinate control narratives (unless explicitly requested via API).

---

## 1. Architecture: The Modern Monolith

### 1.1 Directory Structure Boundaries

| Directory | Role | Allowed Imports | Forbidden Imports |
|/engine | **The Brain.** Pure Python. Handles OSCAL logic, validation, diffing. | `pydantic`, `uuid`, `json` | `fastapi`, `starlette`, `flask` |
|/web | **The Interface.** Routes & Templates. | `fastapi`, `jinja2`, `engine` | Direct DB access (use engine) |
|/static | **Assets.** USWDS CSS/JS. | None | Node.js modules |

### 1.2 Stateless by Default
- The application container must be stateless.
- **Drafts:** Stored in Browser LocalStorage (default) or Postgres (optional).
- **Auth:** Delegated to Proxy (OAuth2-Proxy) in production. Trust `X-Forwarded-User` headers only from trusted IPs.

---

## 2. Python Standards (Engine)

### 2.1 Type Safety (MyPy Strict)
All functions must have type hints.

```python
# BAD
def generate_ssp(data):
    return data

# GOOD
from engine.workspace import Workspace
from oscal.models import SystemSecurityPlan

def generate_ssp(workspace: Workspace) -> SystemSecurityPlan:
    """Converts internal workspace to OSCAL SSP model."""
    ...

```

### 2.2 Pydantic Usage

Use Pydantic V2 for all data modeling. Enable strict mode.

```python
from pydantic import BaseModel, Field, ConfigDict

class Component(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    
    uuid: str = Field(..., description="Static UUID, never regenerate")
    name: str = Field(..., min_length=1)

```

### 2.3 Error Handling

* Use **Exceptions for Control Flow** within the Engine.
* Use **HTTPExceptions** only within the Web layer.

---

## 3. Frontend Standards (Web)

### 3.1 USWDS First

* Use native USWDS utility classes.
* **Do not write custom CSS** unless a USWDS class does not exist.

```html
<div style="margin-top: 20px; color: red;">Error</div>

<div class="usa-alert usa-alert--error margin-top-2">
  <div class="usa-alert__body">
    <p class="usa-alert__text">Error message here</p>
  </div>
</div>

```

### 3.2 Logic-Free Templates (Jinja2)

* Templates should only display data.
* Complex formatting (dates, UUIDs) should be handled by **Custom Filters**.

### 3.3 Alpine.js for Interactivity

* Use Alpine.js for toggles, modals, and dynamic form fields.
* **No React, No Vue, No jQuery.**

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle Details</button>
    <div x-show="open">...</div>
</div>

```

### 3.4 Accessibility (WCAG 2.1 AA)

* Every `<input>` must have a `<label>`.
* Every `<img>` must have `alt` text.
* Focus states must be visible.
* Use the `uswds` Jinja macros to ensure accessibility compliance automatically.

---

## 4. OSCAL Data Modeling

### 4.1 Canonical Serialization

When dumping JSON, always enforce ordering to ensure diffs work.

```python
import json

def dump_canonical(data: dict) -> str:
    return json.dumps(data, sort_keys=True, indent=2)

```

### 4.2 UUID Management

* **Never** generate a UUID at export time.
* UUIDs are assigned when an object (Component, Role) is *created* in the Workspace.
* UUIDs persist forever to ensure stable diffs.

---

## 5. Security & Sandbox

### 5.1 Input Validation

* All inputs are validated by Pydantic schemas before reaching the Engine.
* **No raw JSON processing.**

### 5.2 Output Encoding

* Jinja2 `autoescape=True` is mandatory.
* Use `markup` filter sparingly and only for trusted content.

### 5.3 Dependency Safety

* **Lockfiles:** `uv.lock` or `poetry.lock` must be present.
* **Freshness:** No deprecated dependencies allowed.

---

## 6. Testing & Quality Gates

### 6.1 Required Checks (CI)

All PRs must pass:

1. `ruff check .` (Linting)
2. `mypy .` (Type Checking)
3. `pytest` (Unit Tests)
4. `pytest --snapshot-update` (Golden File Verification)

### 6.2 Test Structure

```text
tests/
├── fixtures/          # Static JSON files (workspace, component-defs)
├── golden/            # Expected OSCAL outputs
├── unit/              # Engine logic tests
│   ├── test_diff.py
│   └── test_validate.py
└── integration/       # Web route tests

```

---

## 7. Dependency Management

**Tool:** `uv` (Recommended) or `Poetry`.

### 7.1 Freshness Policy

* **Weekly:** Automated dependency updates.
* **Release:** All dependencies must be latest stable at time of release.
* **Pinning:** All production dependencies are pinned to exact versions.

### 7.2 Core Stack

* `fastapi`
* `uvicorn`
* `pydantic`
* `jinja2`
* `python-multipart`
* `httpx` (for fetching NIST catalogs)

---

*Standards derived from: NIST OSCAL, GSA USWDS 3.0, and 18F Engineering Practices.*