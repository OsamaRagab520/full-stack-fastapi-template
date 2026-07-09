# AGENTS.md

This file provides guidance to coding agents (Claude Code and other AGENTS.md-aware tools) when working with code in this repository.

## Stack

- **Backend**: FastAPI + SQLModel (async) + PostgreSQL + Alembic + PyJWT + pwdlib
  + slowapi (per-IP rate limiting)
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

Two services share this repo, each with its own deep context node:

- **`backend/`** — async FastAPI + SQLModel API, organized into domain packages
  (`auth`, `users`, `items`, `email`, `core`). Details: `backend/AGENTS.md`.
- **`frontend/`** — React 19 SPA (TanStack Router/Query, shadcn/ui). Its API
  client is generated from the backend's OpenAPI schema. Details: `frontend/AGENTS.md`.

## Intent Layer

Nodes form a **T-shaped view**: broad context here at the root, local detail in
the service node you're working in. Some agent tools auto-load the nearest
`AGENTS.md` plus its ancestors; the directive below is the portable fallback.

**Before modifying code in a service directory, read its `AGENTS.md` first** to
understand local patterns, contracts, and pitfalls.

- **Backend**: `backend/AGENTS.md` — domain layout, async session rules,
  settings split, shims, migrations, local-only routes.
- **Frontend**: `frontend/AGENTS.md` — file-based routing, auth state, the
  generated client, TanStack Query patterns.

### Global Invariants

- **Localization is full-stack.** Backend strings are translated via Babel
  gettext catalogs (`backend/app/locales/`); the frontend via react-i18next
  (`frontend/src/locales/`). The frontend sends `Accept-Language` on every API
  call (set in `frontend/src/main.tsx`), and persists the active language in a
  `lang` cookie + on the `User.locale` field. Supported languages:
  `en`, `ar` (RTL). See each service's `AGENTS.md` for the marker/translation
  conventions. After any backend user-facing string change, rebuild the catalog
  (`pybabel extract/update/compile`).
- **OpenAPI is the contract between the services.** After any backend
  route/schema change, regenerate the client: `bash ./scripts/generate-client.sh`
  (backend must be running). `frontend/src/client/` and `frontend/src/routeTree.gen.ts`
  are **generated — never hand-edit them**. Client service/method names derive
  from the `generate_unique_id_function` in `app/main.py` (`{tag}-{route_name}`).
- **Secrets and config live in `backend/.env`** (read via the split config
  classes), never hardcoded. `SECRET_KEY` auto-generates only in `local`.
- **Swagger/ReDoc** mount only in `local`/`staging`; the `private` router only
  in `local` (`app/main.py`, `app/api/main.py`).
- **Email**: MJML source in `backend/app/email-templates/src/`, compiled to
  `build/` via the VS Code MJML extension. Mailcatcher (port 1080) intercepts
  outgoing mail in local dev.
