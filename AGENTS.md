---
id: oscal-wizard-global-context
title: "Open OSCAL Wizard - Global Context & Protocols"
type: policy
version: 2.2.0
status: active
owners:
  - "@project-maintainers"
primary_personas:
  - "System Architect (Engine-First)"
  - "Compliance Officer (NIST-Aligned)"
  - "UX Designer (Accessibility-First)"
requires:
  anchors: []
output:
  format: markdown
  contract:
    required_sections:
      - "Time Authority"
      - "Prime Directive"
      - "Architecture Constraints"
      - "Task & Git Hygiene"
      - "Q Protocol"
      - "Discovered Issue Protocol"
    prohibited_content:
      - "Node.js runtime assumptions"
      - "React/SPA logic"
      - "Guessing/Hallucinating Control Data"
      - "Giant, monolithic commits"
quality_gates:
  readability_max_grade: 9
  citations_required: true
scope:
  intended_use:
    - meta
    - coding
    - review
    - task-management
time_authority:
  required: true
  timezone: "America/New_York"
---

# Open OSCAL Wizard - Agent Instructions

**Project:** Open OSCAL Wizard (Provisional)
**Stack:** Python 3.11+, FastAPI, Pydantic, USWDS, Docker
**Mission:** A lightweight, deterministic, TurboTax-style tool for creating valid OSCAL SSPs.

---

## 1. Core Operating Principles

### 1.1 Time Authority
**All operations use America/New_York (ET) timezone.**
Before any time-sensitive operation (timestamps, logs, release versions):
- Determine `TODAY` in ET using `time.gov` or reliable system time.
- Use ISO 8601 format with timezone offset (e.g., `2025-01-19T14:00:00-05:00`).

### 1.2 Prime Directive
**Priority order for all implementation decisions:**


```

Accuracy > Determinism > Accessibility > Simplicity > Performance

```

1.  **Accuracy:** Does it match the NIST OSCAL schema and FedRAMP baselines strictly?
2.  **Determinism:** Does the same input produce the *exact same* output bytes (canonical JSON)?
3.  **Accessibility:** Is it WCAG 2.1 AA compliant? (USWDS enforced).
4.  **Simplicity:** Can a new Python dev understand it in 5 minutes? (No "magic").
5.  **Performance:** Is it fast enough?

### 1.3 Documentation Style: "Polite Linus Torvalds"
Write like a technically precise, experienced engineer who respects the reader's intelligence. Be direct, honest, and clear.

- **DO:** State exactly what the code does. Admit limitations. Use technical terms correctly.
- **DO NOT:** Use marketing fluff ("seamless", "empower"). Hide limitations. Guess.

---

## 2. Architecture & Tech Stack



### 2.1 The "Modern Monolith"
We strictly separate the **Engine** (Logic) from the **Web** (Presentation).

| Layer | Directory | Allowed Logic | Forbidden |
| :--- | :--- | :--- | :--- |
| **Engine** | `/engine` | Pydantic validation, Diffing, UUID generation, OSCAL Serialization. | HTTP dependencies, HTML rendering. |
| **Web** | `/web` | FastAPI Routes, Jinja2 Templates, HTMX/Alpine state. | Complex business logic, direct DB queries. |
| **Assets** | `/static` | Pre-compiled USWDS CSS/JS. | Node.js runtime, build pipelines. |

### 2.2 Tech Stack Enforcement
- **Language:** Python 3.11+ (Typed, strict).
- **Web:** FastAPI + Jinja2.
- **Data:** Pydantic V2 (Strict Mode).
- **Frontend:** USWDS 3.x (Native HTML) + Alpine.js (Light interactivity).
- **Package Manager:** `uv` (primary) or `poetry`.

### 2.3 Dependency Hygiene
- **Never use deprecated packages.**
- **Lockfiles are mandatory.** (`uv.lock` or `poetry.lock`).
- **No Node.js at runtime.** (CI-only for USWDS asset compilation).

---

## 3. Task & Git Hygiene (Mandatory)

### 3.1 GitHub CLI Tracking
We do not work in the dark. Every unit of work must be tracked.

- **Create Issues First:** Before starting code, create an issue.
  ```bash
  gh issue create --title "feat: Implement OSCAL Metadata model" --body "Implements the Pydantic model for Metadata..." --label "feature"

```

* **Track Epics:** For large phases (e.g., "Phase 1"), use a tracking issue.
```bash
gh issue create --title "EPIC: Phase 1 - Walking Skeleton" --body "- [ ] Task 1..." --label "epic"

```



### 3.2 Commit Discipline

* **Frequency:** Commit early and often. Do not wait for "perfection."
* **Atomicity:** One logical change per commit.
* **Message Format:** Conventional Commits (`type: subject`).
* `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`



### 3.3 PR & Merge Protocol

* **No Direct Pushes to Main.** (Except for initial setup or docs-only).
* **Create PRs:**
```bash
gh pr create --title "feat: Add Metadata model" --body "Closes #123"

```


* **Self-Merge is OK:** If you are the sole dev, you must still open a PR to let CI run, then merge it yourself using:
```bash
gh pr merge --squash --delete-branch

```



---

## 4. Protocols

### 4.1 Q Protocol (Mandatory for Uncertain Actions)

Before executing any action where the outcome is ambiguous or risky:

```text
DOING: [Specific action]
EXPECT: [Observable outcome]
IF YES: [Next step]
IF NO: [Fallback action]

```

After execution:

```text
RESULT: [What actually happened]
MATCHES: yes/no
THEREFORE: [Conclusion/Next Action]

```

### 4.2 The "Golden File" Rule

Every OSCAL export feature must include a **Golden File Test**.

* **Input:** A fixed `workspace.json` fixture.
* **Output:** A generated `ssp.json` file.
* **Assertion:** The output must match the "Golden" reference file **byte-for-byte**.

### 4.3 Discovered Issue Protocol

If you find an issue while working on something else, **flag it immediately** using the CLI. Do not ignore it.

```bash
# Bug discovered
gh issue create --title "bug: UUID regeneration detected in export" --body "..." --label "bug"

# Tech debt found
gh issue create --title "debt: Hardcoded paths in catalog loader" --body "..." --label "debt"

```

### 4.4 Ask vs Assume

**Always clarify (never assume) for:**

| Topic | Example Question |
| --- | --- |
| **Control Logic** | "Does this control require a parameter value, or is it optional?" |
| **NIST Interpretation** | "Should we default to the 'Low' or 'Moderate' baseline?" |
| **Persistence** | "Should this draft be saved to disk or just LocalStorage?" |
| **Accessibility** | "What is the aria-label for this dynamic toggle?" |

**Safe to assume:** Python strict typing, UTF-8, Pydantic validation, USWDS class availability.

---

## 5. Development Workflow

### 5.1 Feature Implementation Steps

1. **Ticket:** `gh issue create ...`
2. **Branch:** `git checkout -b feature/issue-number-description`
3. **Plan:** Define Pydantic models in `engine/` first.
4. **Test:** Create a failing test case in `tests/`.
5. **Implement:** Write the Engine logic.
6. **UI:** Connect via FastAPI route and Jinja2 template.
7. **Verify:** Run `pytest` and `ruff`.
8. **PR:** `gh pr create ...`
9. **Merge:** `gh pr merge ...`

### 5.2 Quality Gates (Must Pass)

* [ ] `ruff check .` (Zero errors).
* [ ] `mypy .` (Strict mode pass).
* [ ] `pytest` (All tests pass).
* [ ] Golden File tests match exactly.
* [ ] No file > 400 lines (Split if necessary).

---

## 6. Quick Reference Commands

```bash
# Setup
uv venv
source .venv/bin/activate
uv sync

# Run Local Dev
docker-compose up --build

# GitHub CLI Flow
gh issue list
gh issue create
gh pr create
gh pr merge --squash --delete-branch

# Testing
pytest                     # Run all tests
pytest --snapshot-update   # Update Golden Files (Use with caution)

# Quality
ruff check .               # Lint
ruff format .              # Format
mypy .                     # Type check

```

---

## 7. Implementation Task Output Format

For non-trivial tasks, structure your output as follows:

**1. Assumptions**
State what you are taking as true (e.g., "Assuming FedRAMP Rev 5 baselines").

**2. Plan**

* `engine/models.py`: [Changes]
* `engine/logic.py`: [Changes]
* `web/templates/`: [Changes]
* `tests/`: [New Coverage]

**3. Implementation**
(The Code)

**4. Verification**
"Ran `pytest tests/unit/test_export.py` - Passed."

**5. Tradeoffs**
"Chose not to implement XML export in this iteration to preserve velocity."
