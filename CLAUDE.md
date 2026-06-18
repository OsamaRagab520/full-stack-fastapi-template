# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **Backend**: FastAPI + SQLModel (async) + PostgreSQL + Alembic + PyJWT + pwdlib
- **Frontend**: React 19 + TypeScript + Vite + TanStack Router + TanStack Query + shadcn/ui + Tailwind CSS v4
- **Runtime**: `uv` (Python), `bun` (JS), Docker Compose for full-stack
- **Linting/formatting**: `ruff` + `mypy --strict` (backend), `biome` (frontend), `prek` for pre-commit hooks

## Commands

### Full stack (Docker)
```bash
docker compose watch          # start with hot reload
docker compose logs backend   # tail a service's logs
```

### Backend (from `backend/`)
```bash
uv sync                                        # install deps
fastapi dev app/main.py                        # run dev server (outside Docker)
uv run ruff check . && uv run ruff format .    # lint + format
uv run mypy .                                  # type-check (strict)
```

### Backend tests
```bash
# Requires the Docker stack running (DB must be accessible)
bash ./scripts/test.sh                                       # full test run
docker compose exec backend bash scripts/tests-start.sh      # if stack is already up
docker compose exec backend bash scripts/tests-start.sh -x   # stop on first failure
# Run a single test file
docker compose exec backend bash -c "cd /app && pytest tests/api/routes/test_users.py -v"
```

### Frontend (from `frontend/` or repo root)
```bash
bun install
bun run dev           # dev server at http://localhost:5173
bun run lint          # biome check + autofix
bun run build         # tsc + vite build
bun run test          # Playwright e2e (requires Docker stack)
bun run test:ui       # Playwright with browser UI
```

### Generate frontend API client
```bash
# Backend must be running; regenerate after any OpenAPI schema change
bash ./scripts/generate-client.sh
```

### Alembic migrations (inside backend container or with venv active)
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Pre-commit hooks
```bash
# From backend/, installs git hook:
uv run prek install -f
# Run manually on all files:
uv run prek run --all-files
```

## Architecture

### Backend domain structure
The backend is split into domain packages under `backend/app/`:

| Domain | Contents |
|--------|----------|
| `app/auth/` | JWT auth logic: `config.py` (AuthConfig/SECRET_KEY), `dependencies.py` (SessionDep, CurrentUser, get_current_active_superuser), `router.py` (login/password-reset endpoints), `schemas.py` |
| `app/users/` | User domain: `models.py` (SQLModel table), `schemas.py` (Pydantic I/O), `service.py` (DB operations), `router.py` (CRUD endpoints) |
| `app/items/` | Item domain: same layout as users |
| `app/email/` | `config.py` (EmailConfig, emails_enabled) |
| `app/core/` | `config.py` (Settings/AppBaseConfig, CORS, DB URI), `db.py` (async engine + AsyncSessionFactory + init_db), `security.py` (hashing/JWT helpers) |
| `app/api/` | `main.py` assembles the router; `routes/` has `utils.py` and `private.py` (local-only debug routes); `deps.py` is a backward-compat re-export shim |

**`app/models.py` and `app/api/deps.py`** are backward-compat shims — import directly from domain packages in new code.

### Settings are split by domain
- `Settings` (core/config.py) — DB, CORS, project name, environment
- `AuthConfig` (auth/config.py) — SECRET_KEY, token expiry; auto-generates SECRET_KEY in `local` env
- `EmailConfig` (email/config.py) — SMTP credentials; `emails_enabled` is a computed field

All three inherit from `AppBaseConfig` which reads from `../.env` (relative to `backend/`).

### Async-first backend
All routes and service functions are `async`. The DB session is `sqlmodel.ext.asyncio.session.AsyncSession` via `AsyncSessionFactory`. Tests use `anyio` with `asyncio` backend and override `get_db` via FastAPI's dependency system.

### OpenAPI docs visibility
Swagger UI and ReDoc are only mounted when `ENVIRONMENT` is `local` or `staging` (`app/main.py`). The `private` router (local-only test helpers) is only registered when `ENVIRONMENT == "local"`.

### Frontend routing and auth
TanStack Router with file-based routes under `frontend/src/routes/`. The `_layout.tsx` wraps authenticated pages; `__root.tsx` is the shell. Auth state lives in `useAuth.ts` — JWT token stored in `localStorage`, user fetched via TanStack Query on `currentUser` key.

### Frontend API client
`frontend/src/client/` is fully generated from the OpenAPI spec via `@hey-api/openapi-ts`. Never edit these files manually; regenerate with `generate-client.sh` after backend changes. Route function names come from the `generate_unique_id_function` in `app/main.py` which uses `{tag}-{route_name}` format.

### Email templates
MJML source files in `backend/app/email-templates/src/`, compiled to HTML in `build/` using the VS Code MJML extension. Mailcatcher (port 1080) intercepts all outgoing email in local development.
