# justfile — shortcuts for the important dev commands.
# Run `just` (or `just --list`) to see everything. Requires https://github.com/casey/just
#
# Plain `docker compose` auto-merges compose.yml + compose.override.yml (local dev).
# Production uses `-f compose.yml` only, so nothing here touches a deploy.

# Default command to list all available commands.
default:
    @just --list

## ─────────────────────────────  Stack  ─────────────────────────────

# up: Start the full stack in the background (frontend served as prod build).
up:
    @echo "Starting up containers..."
    @docker compose up -d --remove-orphans

# watch: Start the stack with backend hot-reload (frontend stays a prod build).
watch:
    @echo "Starting stack in watch mode..."
    @docker compose watch

# dev: Start the stack with a live Vite frontend (HMR + devtools) via compose.dev.yml.
dev:
    @echo "Starting stack with frontend dev server..."
    @bash scripts/dev-watch.sh

# down: Stop containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# build: Build images.
build *args:
    @echo "Building images..."
    @docker compose build {{args}}

# logs: Tail container logs, e.g. `just logs backend`.
logs *args:
    @docker compose logs -f {{args}}

# ps: Show running containers.
ps:
    @docker compose ps

# shell: Open a bash shell in the backend container.
shell:
    @docker compose exec backend bash

# prune: Stop containers and remove their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v --remove-orphans {{args}}

## ────────────────────────────  Backend  ────────────────────────────

# be-test: Full backend test run (builds stack, runs pytest + coverage).
be-test *args:
    @bash ./scripts/test.sh {{args}}

# be-test-one: Run a single test file/node, e.g. `just be-test-one tests/api/routes/test_users.py -v`.
be-test-one +args:
    @docker compose exec backend bash -c "cd /app && pytest {{args}}"

# be-lint: Ruff check (lint) the backend.
be-lint:
    @cd backend && uv run ruff check .

# be-format: Ruff format the backend.
be-format:
    @cd backend && uv run ruff format .

# be-typecheck: Run mypy --strict on the backend.
be-typecheck:
    @cd backend && uv run mypy .

# be-migrate: Apply Alembic migrations (upgrade to head).
be-migrate:
    @docker compose exec backend alembic upgrade head

# be-makemigration: Autogenerate a migration, e.g. `just be-makemigration "add user bio"`.
be-makemigration +message:
    @docker compose exec backend alembic revision --autogenerate -m "{{message}}"

# hooks: Run all pre-commit (prek) hooks against every file.
hooks:
    @cd backend && uv run prek run --all-files

## ───────────────────────────  Frontend  ────────────────────────────

# fe-dev: Run the Vite dev server on the host (http://localhost:5173).
fe-dev:
    @cd frontend && bun run dev

# fe-lint: Biome check + autofix the frontend.
fe-lint:
    @cd frontend && bun run lint

# fe-build: Type-check and build the frontend.
fe-build:
    @cd frontend && bun run build

# fe-test: Run the Playwright e2e suite (needs the stack up).
fe-test *args:
    @cd frontend && bunx playwright test {{args}}

## ────────────────────────────  Client  ─────────────────────────────

# gen-client: Regenerate the OpenAPI client (backend must be running).
gen-client:
    @bash ./scripts/generate-client.sh
