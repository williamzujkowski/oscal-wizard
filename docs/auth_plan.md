# Auth and Admin Bootstrap Plan

## Goals
- SSO-first login with GitHub and Google.
- Simple admin bootstrap path with an explicit allowlist.
- Deterministic, auditable session behavior.
- Minimal surface area in the web layer; keep auth logic isolated.

## Non-goals
- No local password auth in the first iteration.
- No multi-tenant org management in the first iteration.
- No React/SPA client or Node runtime requirement.

## Recommended approach
Use OAuth2/OIDC via Authlib with server-side sessions and a database-backed user table.

Rationale:
- Authlib is actively maintained and integrates cleanly with FastAPI and Starlette.
- It supports standard OAuth2/OIDC providers without forcing a full auth framework.
- We can keep a small, explicit user model and admin bootstrap flow.

## Data model (minimal)
- User: id (uuid), email, provider ("github"|"google"), provider_id, display_name, is_admin, created_at, last_login_at.
- AuthSession (optional): session_id, user_id, created_at, expires_at (if we want to track server-side sessions explicitly).

## Bootstrap admin flow
- Environment variable allowlist (comma-separated emails) for initial admin access.
- On first login, if email is in allowlist, set is_admin true.
- After an admin exists, allowlist remains for additional admin users only if explicitly enabled.

## Auth flow summary
1) User clicks "Sign in with GitHub" or "Sign in with Google".
2) Redirect to provider; callback exchanges code for token.
3) Read user profile, normalize email.
4) Upsert user record, set is_admin if allowlisted.
5) Create session and set secure cookie.
6) Redirect to /.

## Security defaults
- Cookies: HttpOnly, Secure in production, SameSite=Lax.
- CSRF: use Double Submit or Starlette CSRF middleware if we add unsafe form posts.
- Provider scopes: email + profile only.
- Admin routes guarded by dependency; deny by default.

## Open questions
- What persistence should we use for users and sessions (SQLite vs Postgres)?
- Should we require GitHub org membership for admin access?
- Do we want a one-time bootstrap token instead of email allowlist?
- Should logout revoke provider tokens or only clear local session?

## Implementation steps (next issue)
- Add Authlib dependency and settings.
- Implement provider registration and callback routes.
- Add user model and migration.
- Add admin dependency and a minimal admin page.
