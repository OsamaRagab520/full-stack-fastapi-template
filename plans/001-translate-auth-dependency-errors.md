# Plan 001: Auth dependency errors are translated via the domain-error pipeline

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**:
> `git diff --stat 36f0a5e..HEAD -- backend/app/auth/dependencies.py backend/app/auth/exceptions.py backend/app/locales backend/tests/api/routes/test_i18n.py`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug (i18n correctness / architecture consistency)
- **Planned at**: commit `36f0a5e`, 2026-07-09

## Why this matters

This backend translates every user-facing string — domain-error `detail`s,
`Message` responses, and emails — via a Babel gettext catalog, keyed off the
request's `Accept-Language`. The project's own `backend/AGENTS.md` states the
invariant: *"Never return a raw English literal as a domain `detail` or
`Message`."* Four `HTTPException`s in `app/auth/dependencies.py` violate it:
they hardcode English (`"Could not validate credentials"`, `"User not found"`,
`"Inactive user"`, `"The user doesn't have enough privileges"`) and bypass the
single domain-exception handler that every other error flows through. The
result: an Arabic user whose token expired, whose account was deactivated, or
who hits an admin-only route gets an **English** error. This is the only place
in the backend that still raises raw `HTTPException` for a domain failure
(besides the separately-tracked 422 validation case). Fixing it closes the
localization contract and removes the last architectural exception to the
"routers/deps never raise `HTTPException`" rule.

Three of the four strings already have Arabic translations in the catalog
(their domain-error twins were extracted earlier); only one new string needs a
translation.

## Current state

Files:
- `app/auth/dependencies.py` — FastAPI auth dependencies; raises the four raw
  `HTTPException`s (lines 21–51).
- `app/auth/exceptions.py` — auth-domain `HTTPDomainError` subclasses
  (`InvalidCredentialsError`, `InactiveUserError`, `InvalidTokenError`). This is
  where the new exception goes.
- `app/users/exceptions.py` — defines `UserNotFoundError` (404) and
  `UserAccessDeniedError` (403), both already translated.
- `app/core/exceptions.py` — the generic `http_domain_exception_handler`
  (registered in `app/main.py`) that translates any `HTTPDomainError` to a JSON
  response using the request locale. **You do not modify this** — it already
  does the translation; you just need to route through it.
- `app/locales/messages.pot`, `app/locales/ar/LC_MESSAGES/messages.po` — Babel
  catalog. `.mo` files are **not** git-tracked; they are compiled locally / in
  CI / in Docker.
- `tests/api/routes/test_i18n.py` — the localization regression tests (35 lines,
  2 tests today). New tests go here.

Current `app/auth/dependencies.py` (the parts you change):

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.auth.schemas import TokenPayload
from app.auth.tokens import decode_token
from app.core.config import settings
from app.core.db import SessionDep
from app.users.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
```

Note the name clash to avoid: `jwt.exceptions.InvalidTokenError` is imported
here and used in the `except` clause. **Do not** import the auth-domain
`InvalidTokenError` from `app.auth.exceptions` into this file — you are not
using it. Keep the `jwt` import as-is.

Current `app/auth/exceptions.py` (full):

```python
from app.core.exceptions import HTTPDomainError
from app.core.i18n import _


class InvalidCredentialsError(HTTPDomainError):
    status_code = 400
    detail = _("Incorrect email or password")


class InactiveUserError(HTTPDomainError):
    status_code = 400
    detail = _("Inactive user")


class InvalidTokenError(HTTPDomainError):
    status_code = 400
    detail = _("Invalid token")
```

Convention to match — a typed domain error subclasses `HTTPDomainError`, sets
`status_code` + a `_()`-wrapped `detail`, and is **raised, never caught** by
routers/dependencies; the generic handler maps it. See `app/users/exceptions.py`
for the exemplar (e.g. `UserAccessDeniedError` at the bottom):

```python
class UserNotFoundError(HTTPDomainError):
    status_code = 404
    detail = _("User not found")


class UserAccessDeniedError(HTTPDomainError):
    status_code = 403
    detail = _("The user doesn't have enough privileges")
```

**Status-code mapping you must preserve** (behavior must not change for API
clients or existing tests):

| Old raw `HTTPException`                          | Status | Replace with domain error                  |
|--------------------------------------------------|--------|--------------------------------------------|
| `"Could not validate credentials"`               | 403    | **new** `CouldNotValidateCredentialsError` |
| `"User not found"`                               | 404    | `app.users.exceptions.UserNotFoundError`   |
| `"Inactive user"`                                | 400    | `app.auth.exceptions.InactiveUserError`    |
| `"The user doesn't have enough privileges"`      | 403    | `app.users.exceptions.UserAccessDeniedError` |

Catalog facts (verified at planning time):
- `"User not found"`, `"Inactive user"`, `"The user doesn't have enough
  privileges"` **already** exist in `app/locales/ar/LC_MESSAGES/messages.po`
  with Arabic translations. No new translation needed for these.
- `"Could not validate credentials"` is **not** in any catalog — it must be
  extracted and translated.
- The catalog workflow (from `backend/AGENTS.md`) is:
  `pybabel extract` → `pybabel update` → edit the `.po` → `pybabel compile`.

## Commands you will need

Run backend commands from the `backend/` directory.

| Purpose        | Command                                                        | Expected on success            |
|----------------|---------------------------------------------------------------|--------------------------------|
| Type-check     | `uv run mypy .`                                                | exit 0, no errors              |
| Lint           | `uv run ruff check .`                                          | exit 0                         |
| Format         | `uv run ruff format .`                                         | reformats / no diff            |
| Extract msgids | `uv run pybabel extract -F babel.cfg -o app/locales/messages.pot .` | writes `.pot`, exit 0    |
| Merge catalogs | `uv run pybabel update -i app/locales/messages.pot -d app/locales`  | updates `.po`, exit 0    |
| Compile `.mo`  | `uv run pybabel compile -d app/locales`                        | "compiling ..." lines, exit 0  |
| Full tests     | `bash ./scripts/test.sh`                                       | all pass (**needs Docker DB**) |

The test suite **requires a reachable PostgreSQL** (the Docker stack). If you
cannot reach the DB, see STOP conditions — do not skip the tests silently.

## Scope

**In scope** (the only files you should modify):
- `backend/app/auth/exceptions.py` — add one exception class.
- `backend/app/auth/dependencies.py` — swap four raises + imports.
- `backend/app/locales/messages.pot` — regenerated by `pybabel extract`.
- `backend/app/locales/ar/LC_MESSAGES/messages.po` — regenerated by
  `pybabel update`, then hand-edit the one new `msgstr`.
- `backend/tests/api/routes/test_i18n.py` — add regression tests.

**Out of scope** (do NOT touch, even though they look related):
- `backend/app/core/exceptions.py` — the handler already translates; changing it
  is unnecessary and risky.
- Any other `.po`/`.mo`. Only the `ar` catalog gets a hand-edit.
- `frontend/**` — the frontend already sends `Accept-Language`; nothing to change.
- The `OAuth2PasswordBearer` "Not authenticated" 401 (raised by the security
  scheme when the header is missing entirely) — that is FastAPI-internal and
  deliberately left as-is; see Maintenance notes.
- Existing English assertions in `tests/api/routes/test_users.py` — they will
  still pass unchanged (see Test plan); do not edit them.

## Git workflow

- Branch: `advisor/001-translate-auth-dependency-errors` (create from the
  current branch; do not commit directly to it if it is a protected branch).
- The repo uses **Conventional Commits** (enforced by commitlint — see
  `git log`, e.g. `feat(i18n): add localization support for UI texts and error
  messages`). Suggested message:
  `fix(auth): translate auth-dependency errors via domain-error handler`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Add the new domain exception

In `app/auth/exceptions.py`, append:

```python
class CouldNotValidateCredentialsError(HTTPDomainError):
    status_code = 403
    detail = _("Could not validate credentials")
```

**Verify**: `uv run ruff check app/auth/exceptions.py` → exit 0.

### Step 2: Route the four dependency raises through domain errors

Edit `app/auth/dependencies.py`:

1. Change the FastAPI import from
   `from fastapi import Depends, HTTPException, status` to
   `from fastapi import Depends` (the file no longer uses `HTTPException` or
   `status`).
2. Add these imports (keep the existing `from jwt.exceptions import
   InvalidTokenError` untouched):
   ```python
   from app.auth.exceptions import (
       CouldNotValidateCredentialsError,
       InactiveUserError,
   )
   from app.users.exceptions import UserAccessDeniedError, UserNotFoundError
   ```
3. Replace the four `raise HTTPException(...)` blocks per the mapping table:
   - in the `except (InvalidTokenError, ValidationError):` block →
     `raise CouldNotValidateCredentialsError`
   - `if not user:` → `raise UserNotFoundError`
   - `if not user.is_active:` → `raise InactiveUserError`
   - in `get_current_active_superuser`, `if not current_user.is_superuser:` →
     `raise UserAccessDeniedError`

The resulting functions should look like:

```python
async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise CouldNotValidateCredentialsError
    user = await session.get(User, token_data.sub)
    if not user:
        raise UserNotFoundError
    if not user.is_active:
        raise InactiveUserError
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise UserAccessDeniedError
    return current_user
```

**Verify**:
- `uv run ruff check app/auth/dependencies.py` → exit 0 (no unused-import
  warnings for `HTTPException`/`status`).
- `uv run mypy .` → exit 0.
- `grep -nE "HTTPException|Could not validate|Inactive user|User not found|enough privileges" app/auth/dependencies.py` → **no matches**.

### Step 3: Extract and merge the new msgid into the catalog

From `backend/`:

```bash
uv run pybabel extract -F babel.cfg -o app/locales/messages.pot .
uv run pybabel update -i app/locales/messages.pot -d app/locales
```

**Verify**: `grep -n "Could not validate credentials" app/locales/messages.pot`
→ one match. `grep -n "Could not validate credentials"
app/locales/ar/LC_MESSAGES/messages.po` → one match (with an empty
`msgstr ""` directly beneath it, possibly marked `#, fuzzy`).

STOP if `pybabel update` reports it is **obsoleting or deleting** existing
translated entries, or marks the pre-existing `"Inactive user"` / `"User not
found"` / `"...enough privileges"` entries `fuzzy` (that would blank them at
compile time). See STOP conditions.

### Step 4: Add the Arabic translation for the new string

In `app/locales/ar/LC_MESSAGES/messages.po`, find the entry:

```po
msgid "Could not validate credentials"
msgstr ""
```

Set the translation and remove any `#, fuzzy` flag line immediately above it:

```po
msgid "Could not validate credentials"
msgstr "تعذّر التحقق من بيانات الاعتماد"
```

Then compile:

```bash
uv run pybabel compile -d app/locales
```

**Verify**: `uv run pybabel compile -d app/locales` exits 0 and prints a line
for the `ar` catalog. `grep -c 'msgstr ""' app/locales/ar/LC_MESSAGES/messages.po`
should not have increased versus before Step 3 for real (non-header) entries —
i.e. every non-header `msgid` still has a non-empty `msgstr`.

### Step 5: Add i18n regression tests

Append to `tests/api/routes/test_i18n.py`. Model them on the two existing tests
in that file (they already import `settings` and use the `client` fixture and
`pytestmark = pytest.mark.anyio`). The `normal_user_token_headers` fixture is
provided by `tests/conftest.py` (used throughout `test_users.py`).

```python
async def test_invalid_token_error_translated(client: AsyncClient) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={
            "Authorization": "Bearer not-a-real-token",
            "Accept-Language": "ar",
        },
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "تعذّر التحقق من بيانات الاعتماد"


async def test_superuser_privileges_error_translated(
    client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/",
        headers={**normal_user_token_headers, "Accept-Language": "ar"},
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "لا يمتلك المستخدم صلاحيات كافية"
```

If the `AsyncClient` import is not already at the top of the file, it is:
`from httpx import AsyncClient` (already present — the existing tests use it).

**Verify** (needs Docker DB): `bash ./scripts/test.sh` → all pass, including the
two new tests. If the stack is already up, you may instead run
`docker compose exec backend bash -c "cd /app && pytest tests/api/routes/test_i18n.py -v"`.

## Test plan

- **New tests** (in `tests/api/routes/test_i18n.py`):
  - `test_invalid_token_error_translated` — the `get_current_user` bad-token
    path returns 403 with the Arabic detail. This is the exact regression this
    plan fixes.
  - `test_superuser_privileges_error_translated` — the
    `get_current_active_superuser` path returns 403 with the Arabic detail.
- **Structural pattern**: model after the existing
  `test_error_detail_translated_by_accept_language` in the same file.
- **Existing tests stay green without edits**: `test_users.py` asserts the
  English strings `"User not found"` and `"The user doesn't have enough
  privileges"` on these paths (e.g. lines 100, 144, 158, 410, 510, 543). Under
  the default locale (`en`), `translate()` returns the msgid unchanged, so those
  assertions still hold. Do not modify them. If any of them fail, STOP — it
  means a status code or string drifted.
- **Verification**: `bash ./scripts/test.sh` → all pass (existing + 2 new).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `uv run mypy .` (from `backend/`) exits 0.
- [ ] `uv run ruff check .` (from `backend/`) exits 0.
- [ ] `grep -nE "HTTPException|Could not validate credentials|\"Inactive user\"|\"User not found\"|enough privileges" backend/app/auth/dependencies.py` returns **no matches**.
- [ ] `grep -n "Could not validate credentials" backend/app/locales/ar/LC_MESSAGES/messages.po` shows a non-empty Arabic `msgstr`.
- [ ] `uv run pybabel compile -d app/locales` exits 0.
- [ ] `bash ./scripts/test.sh` passes, including the two new tests (needs DB).
- [ ] No files outside the in-scope list are modified (`git status`).
- [ ] `plans/README.md` status row for 001 updated.

## STOP conditions

Stop and report back (do not improvise) if:

- The code at the locations in "Current state" doesn't match the excerpts
  (the codebase drifted since this plan was written).
- `pybabel update` obsoletes/deletes existing entries or marks the three
  pre-existing Arabic translations `fuzzy` (compiling would blank them). Report
  the `pybabel update` output.
- The DB is unreachable and you cannot run the test suite. Complete Steps 1–5,
  run `mypy`/`ruff`/`pybabel compile` to green, then report that the full test
  run is pending a database — do **not** mark the plan DONE.
- An existing `test_users.py` assertion for `"User not found"` /
  `"...enough privileges"` fails (a status code or string changed unexpectedly).
- The fix appears to require editing `app/core/exceptions.py` or any file
  outside the in-scope list.

## Maintenance notes

- **Remaining untranslated surface**: (1) the `OAuth2PasswordBearer` "Not
  authenticated" 401 raised when the `Authorization` header is missing entirely
  — intentionally out of scope here; (2) Pydantic 422 validation messages,
  tracked in `backend/docs/i18n-pydantic-422.md`. This plan does **not** address
  either.
- **Reviewer should scrutinize**: that status codes are unchanged (403/404/400),
  that no pre-existing Arabic translation was blanked by the catalog merge, and
  that the new Arabic string reads correctly (a native reviewer can refine
  `"تعذّر التحقق من بيانات الاعتماد"` — it is a faithful MSA rendering but wording
  is a judgment call).
- **Future work that interacts**: if someone adds a `WWW-Authenticate` header or
  changes the 403→401 convention for auth failures, revisit
  `CouldNotValidateCredentialsError`'s status code.
