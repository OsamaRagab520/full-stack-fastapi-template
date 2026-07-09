# Backend (FastAPI service)

## Purpose
Async FastAPI + SQLModel REST API over PostgreSQL. Owns auth, user/item domains,
transactional email, and DB migrations. Does NOT own the UI or the generated
frontend client (see `../frontend/AGENTS.md`) — but its OpenAPI schema is the
contract that generates that client.

## Entry Points
- `app/main.py` — FastAPI app: mounts `api_router`, CORS, Sentry, custom
  `generate_unique_id_function` (`{tag}-{route_name}`), conditional docs.
- `app/api/main.py` — assembles `api_router` from each domain's `router.py`.
  `private.router` is included **only** when `ENVIRONMENT == "local"`.
- `app/backend_pre_start.py` / `app/tests_pre_start.py` — wait for DB readiness.
- `app/initial_data.py` — seeds the first superuser via `init_db`.

## Domain layout
Each domain package follows the same shape:
`models.py` (SQLModel table) · `schemas.py` (Pydantic I/O) · `selectors.py` (reads)
· `service.py` (writes/mutations) · `exceptions.py` (typed domain errors) · `router.py`
(endpoints). Domains: `auth/` (also `config.py`, `dependencies.py`, `tokens.py`),
`users/`, `items/`, `emails/` (`config.py`, `service.py`, `exceptions.py`). Shared
infra in `core/`: `config.py`, `db.py`, `exceptions.py` (`HTTPDomainError` base),
`passwords.py` (pwdlib Argon2/bcrypt hashing), `i18n.py` + `validation_i18n.py`
(gettext + 422 translation), `rate_limit.py` (slowapi limiter), `time.py`
(`utc_now`). JWT/token creation lives in `auth/tokens.py` — there is **no**
`core/security.py`.

**Read/write split:** `selectors.py` owns all data fetching (queries, filters,
counts, `session.get`) and returns models / `(rows, count)` tuples — never raises
HTTP errors. `service.py` owns mutations and business rules, raising typed exceptions
from `exceptions.py` (e.g. `ItemNotFoundError`, `EmailAlreadyRegisteredError`) — never
`HTTPException`. Each typed exception subclasses `core/exceptions.HTTPDomainError` and
carries its own `status_code` + `detail`. **Routers never catch them or raise
`HTTPException` for domain failures** — they let the exception propagate; a single
generic handler (registered in `app/main.py`) maps every `HTTPDomainError` to its HTTP
response. Routers never touch the ORM directly.

## Contracts & Invariants
- **Async everywhere.** Every route and service fn is `async`. The session is
  `sqlmodel.ext.asyncio.session.AsyncSession` from `AsyncSessionFactory`
  (`core/db.py`). Never call blocking I/O in a route — it stalls the event loop.
- **Routes stay thin.** Reads live in each domain's `selectors.py`, writes in
  `service.py`; routers call those, they never query the ORM directly.
- **Auth dependencies** come from `auth/dependencies.py`: `SessionDep`,
  `CurrentUser`, `TokenDep`, `get_current_active_superuser`. Use these.
- **Settings are split by domain**, all inheriting `AppBaseConfig` (reads
  `../.env` relative to `backend/`): `Settings` (core — DB/CORS/env),
  `AuthConfig` (SECRET_KEY, token expiry; auto-generates SECRET_KEY in `local`),
  `EmailConfig` (SMTP; `emails_enabled` is a computed field). Import the config
  for the domain you need — don't add unrelated keys to `Settings`.
- **Docs visibility:** Swagger/ReDoc mount only when `ENVIRONMENT` is `local` or
  `staging` (`app/main.py`).
- **Rate limiting** is per-IP via slowapi (`core/rate_limit.py`). The shared
  `limiter` is wired in `app/main.py` (`app.state.limiter` + a `RateLimitExceeded`
  handler returning a translated `429 "Too many requests"`). Apply it with
  `@limiter.limit("5/minute")` on a route, which **must** then take a
  `request: Request` parameter (slowapi reads the client IP from it). Current
  limits: login `5/minute`, password-recovery `3/minute` (`auth/router.py`),
  signup `10/hour` (`users/router.py`).
- **User-facing strings are translated**, not hardcoded. Wrap them in `_()` and
  translate via `translate()` at response time. Never return a raw English
  literal as a domain `detail` or `Message`. See the i18n section below.

## Internationalization (i18n)

User-facing backend strings (domain-error `detail`, router `Message` responses,
and email subjects/bodies) are translated via **Babel gettext** catalogs.

- **Catalogs**: `app/locales/<lang>/LC_MESSAGES/messages.po` (source) → compiled
  to `.mo` by `pybabel compile`. `.mo` is gitignored; it's compiled in the
  Dockerfile build and by the `compile-gettext-catalogs` pre-commit hook (on
  `.po` change). Locally run `uv run pybabel compile -d app/locales` after
  editing a `.po`.
- **Marker contract**: wrap any user-facing string in `_()` (an identity marker
  in `app/core/i18n.py`). `pybabel extract` (config `babel.cfg`) finds these.
  `_()` returns the English string unchanged; **never** let it do real work —
  the English value is the gettext `msgid` regardless of `DEFAULT_LANGUAGE`.
  Translate at response time with `translate(msgid, locale)`.
- **Per-request locale**: `LocaleMiddleware` (`app/main.py`) parses
  `Accept-Language` → `request.state.locale` + the `current_locale` context var.
  Routes call `translate(_(...))` (reads the context var implicitly). The
  domain-exception handler reads `request.state.locale` directly.
- **Supported languages / default**: `SUPPORTED_LANGUAGES` + `DEFAULT_LANGUAGE`
  in `core/config.py` (Settings). English has no compiled `.mo` — the
  `NullTranslations` fallback returns the msgid, which *is* English.
- **Emails**: `emails/service.py` `generate_*` functions take a `locale` param
  (from the User's `locale` field), build a translated `t` dict, and pass it
  into the MJML-rendered Jinja2 template. Edit `email-templates/src/*.mjml`
  (using `{{ t.key }}`) and recompile with `bunx mjml` — never hand-edit
  `build/`.
- **User locale**: `User.locale` (default `"en"`), editable via `UserUpdateMe`
  and `UserCreate`, validated against `SUPPORTED_LANGUAGES` by a `field_validator`
  in `users/schemas.py` (unsupported codes are rejected). Drives email localization.
- **Workflow after touching strings**:
  ```bash
  pybabel extract -F babel.cfg -o app/locales/messages.pot .   # find new _() strings
  pybabel update  -i app/locales/messages.pot -d app/locales   # merge into .po (review fuzzies!)
  # edit app/locales/<lang>/LC_MESSAGES/messages.po
  pybabel compile -d app/locales                                # build .mo
  ```
- **Pydantic 422 errors are translated** by `validation_exception_handler`
  (`core/validation_i18n.py`), registered on `RequestValidationError` in
  `app/main.py`. It maps each error's Pydantic `type` (e.g. `string_too_short`,
  `missing`) to a translated template via `_PYDANTIC_MSG_MAP`, formatting in the
  `ctx` values; unmapped types fall back to Pydantic's English `msg`. When you hit
  an untranslated error type, add a new `_()` template to that map.
  (`docs/i18n-pydantic-422.md` predates this work and is now historical.)

## Patterns
Add an endpoint to an existing domain:
1. I/O models → that domain's `schemas.py`.
2. Read logic → that domain's `selectors.py`; write logic → `service.py` (async);
   new failure cases → a `HTTPDomainError` subclass in `exceptions.py` carrying
   `status_code` + `detail`.
3. Route → that domain's `router.py`, depending on `SessionDep`/`CurrentUser`;
   let typed exceptions propagate (don't catch them) and declare their status
   codes in `responses={...}` for the OpenAPI docs.
4. After any schema/route change, regenerate the frontend client (root invariant).

Add a new domain: create `app/<name>/` with the five-file shape (`models`,
`schemas`, `selectors`, `service`, `exceptions`, `router`), then
`include_router` it in `app/api/main.py`.

Schema/DB change: `alembic revision --autogenerate -m "..."` → review →
`alembic upgrade head` (inside the backend container or with the venv active).

## Anti-patterns
- Don't query the ORM from a router. Reads go through `selectors.py`, writes
  through `service.py`.
- Don't raise `HTTPException` from a router/service for a domain failure —
  raise a `HTTPDomainError` subclass instead; the generic handler maps it.
- Don't catch domain exceptions in a router; let them propagate.
- Don't put DB credentials/SMTP keys in code — they live in `../.env` via configs.
- Don't register the `private` router or expose docs outside `local`/`staging`.
- Don't hand-edit Alembic migrations to skip a review of the autogenerated diff.

## Pitfalls
- **Shared model** `app/models.py` defines the `Message` response schema used across domains.
- **Email templates** are MJML in `app/email-templates/src/`, compiled to
  `build/` via the VS Code MJML extension (edit the `src/`, don't hand-edit
  `build/`). Mailcatcher (port 1080) intercepts outgoing mail in local dev.
- Tests need the DB reachable (run the Docker stack) and override `get_db` via
  FastAPI dependencies; `anyio` runs on the `asyncio` backend.
- `SECRET_KEY` is auto-generated only in `local`; staging/prod must set it.

## Dependencies & Edges
- Uplink: `../AGENTS.md` (stack, commands, global invariants).
- Downlink: `../frontend/AGENTS.md` — consumes this service's OpenAPI schema.
- Tooling: `uv` (deps/run), `ruff` (lint/format), `mypy --strict`, `pytest`.
