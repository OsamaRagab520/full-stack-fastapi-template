# Deferred: Localizing Pydantic validation errors (HTTP 422)

> **Status:** Deferred (out of scope of the initial i18n rollout).
> Tracked here so we can pick it up later. No code changes were made for this.

## Current behavior

The backend does **not** customize Pydantic `ValidationError` responses. When a
request body fails validation, FastAPI returns a `422 Unprocessable Entity` with
a `detail` array produced by Pydantic v2, e.g.:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "abc"
    }
  ]
}
```

These `msg` strings are **hardcoded English** from Pydantic's own message
catalog. They are surfaced to the user by the frontend's `extractErrorMessage`
(`frontend/src/utils.ts`), which reads `detail[0].msg`.

So unlike domain errors (which are translated via the Babel catalog — see
`app/core/exceptions.py` + `app/core/i18n.py`) and unlike `Message` responses,
**request-validation errors still reach the user in English**, regardless of the
`Accept-Language` header. This is the only remaining untranslated user-facing
string surface.

## Why it was deferred

1. Pydantic v2's validation messages are numerous and structured (`type`-keyed),
   and a faithful translation table is large.
2. The frontend already translates client-side Zod messages (the common case),
   so 422s mostly surface for malformed/unexpected payloads — a lower-frequency
   path than domain errors.
3. The domain-error and email pipelines were higher value and unblocked the rest
   of the stack.

## Recommended approach (when picked up)

Register a `RequestValidationError` handler in `app/main.py` that translates each
`err["msg"]` using the Babel catalog and the request locale (same
`request.state.locale` set by `LocaleMiddleware`):

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.i18n import current_locale, translate

async def validation_exception_handler(request, exc):
    locale = getattr(request.state, "locale", None) or current_locale.get()
    details = []
    for err in exc.errors():
        details.append({**err, "msg": translate(err["msg"], locale)})
    return JSONResponse(status_code=422, content={"detail": details})

app.add_exception_handler(RequestValidationError, validation_exception_handler)
```

Then seed the catalog with Pydantic's message set. Two options:

- **Manual table** — run a pass that collects the `msg` strings Pydantic emits
  for your schemas (constraint combos), mark them with `_()` in a fixture, and
  `pybabel extract` them into `app/locales/`.
- **`pydantic-i18n`** — a dedicated library that ships a Pydantic-message
  translation vocabulary (JSON/`.po`) and an `I18n` class. It overlaps with the
  Babel catalog setup, so decide whether to unify the two catalogs or keep
  Pydantic messages in a separate domain.

## Verification checklist (when implemented)

- [ ] Add a `RequestValidationError` handler in `app/main.py`.
- [ ] Seed Pydantic message translations in `app/locales/{en,ar}/`.
- [ ] Add a test (e.g. `tests/api/routes/test_i18n.py`) asserting a 422 with
      `Accept-Language: ar` returns an Arabic `msg`.
- [ ] Regenerate the `.mo` (`pybabel compile`).
- [ ] Confirm the frontend's `extractErrorMessage` still reads `detail[0].msg`
      unchanged.
