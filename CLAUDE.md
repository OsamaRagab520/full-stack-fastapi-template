# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Source of truth: the AGENTS.md hierarchy

This repo's authoritative agent guidance lives in `AGENTS.md` files, **not** here.
Treat them as the source of truth and keep this file thin to avoid drift:

- **`AGENTS.md`** (root) — stack, all commands, and the **global invariants**
  (localization is full-stack, OpenAPI is the service contract, config lives in
  `backend/.env`, docs/`private` router only in `local`/`staging`).
- **`backend/AGENTS.md`** — domain package layout, the selectors/service
  read-write split, typed domain exceptions, split settings, async rules, i18n
  (Babel gettext), migrations.
- **`frontend/AGENTS.md`** — file-based routing, auth state, the generated
  client, TanStack Query patterns, i18n (react-i18next) and RTL rules.

**Before modifying code in `backend/` or `frontend/`, read that directory's
`AGENTS.md` first.** They form a T-shape: broad context at the root, local detail
in the service node. Everything below is a quick reference or a delta not covered
there — defer to the AGENTS.md files for depth.

## Quick command reference

Full-stack dev runs in Docker; **tests and the e2e suite require the Docker stack
up** (the DB must be reachable).

```bash
docker compose watch                                   # start full stack, hot reload
docker compose logs backend                            # tail a service

# Backend (from backend/) — uv runtime, ruff + mypy --strict
uv run ruff check . && uv run ruff format .
uv run mypy .
bash ./scripts/test.sh                                 # full backend test run (from repo root)
docker compose exec backend bash -c "cd /app && pytest tests/api/routes/test_users.py -v"   # single test

# Frontend (from frontend/ or repo root) — bun runtime, biome, playwright
bun run dev                                            # http://localhost:5173
bun run lint                                           # biome check + autofix
bun run build                                          # tsc + vite build
bun run test                                           # playwright e2e (needs stack)

# Regenerate the OpenAPI client after ANY backend route/schema change (backend must be running)
bash ./scripts/generate-client.sh
```

## Never hand-edit generated files

`frontend/src/client/**` and `frontend/src/routeTree.gen.ts` are generated. After
any backend schema/route change, regenerate the client (command above) rather than
editing types by hand — a stale client is a common source of "wrong shape" bugs.

## Commit conventions (enforced)

Commit messages are linted as **Conventional Commits** via a `commit-msg`
pre-commit hook (`commitlint.config.js`). Format: `<type>(<scope>): <subject>`,
imperative + lowercase subject, no trailing period, header ≤ 72 chars.

- **Types**: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`,
  `style`, `chore`, `revert` (only `feat`/`fix` drive a semver bump).
- **Scopes**: `auth`, `users`, `items`, `emails`, `core`, `deps`, `ci`, `docker`,
  `frontend`, `docs` — omit the scope for repo-wide changes.

Install hooks from `backend/`: `uv run prek install -f` (this repo uses `prek`,
not classic pre-commit). Run all hooks manually: `uv run prek run --all-files`.