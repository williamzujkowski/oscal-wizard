# OSCAL Wizard

A lightweight, deterministic, and accessible wizard for producing valid OSCAL SSPs.

## Quickstart

Python (app runtime):

```bash
uv venv
source .venv/bin/activate
uv sync
```

Postgres (dev):

```bash
docker-compose up -d db
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

## Auth configuration

Set these environment variables before running the app:

- `DATABASE_URL` (Postgres, async URL)
- `SECRET_KEY` (session signing key)
- `SESSION_COOKIE_NAME` (optional)
- `SESSION_HTTPS_ONLY` (`true` in production)
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `ADMIN_ALLOWLIST` (comma-separated emails)

Use `.env.example` as a starting point for local configuration.

## Database migrations

```bash
alembic upgrade head
```

## Quality checks

```bash
ruff check .
mypy .
pytest
```
