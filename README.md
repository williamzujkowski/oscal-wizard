# OSCAL Wizard

A lightweight, deterministic, and accessible wizard for producing valid OSCAL SSPs.

## Quickstart

Python (app runtime):

```bash
uv venv
source .venv/bin/activate
uv sync
```

Node (USWDS assets):

```bash
npm install
npm run build:uswds
```

Run the app:

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000

## Notes

- USWDS assets are copied into `web/static/uswds` by the Node build script.
- See `AGENTS.md` for project policy and workflow requirements.
