# Plan 003: Password-preview endpoint emits a valid subject header

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**:
> `git diff --stat 36f0a5e..HEAD -- backend/app/auth/router.py`
> If the file changed since this plan was written, compare the "Current state"
> excerpt against the live code before proceeding; on a mismatch, treat it as a
> STOP condition.

## Status

- **Priority**: P3
- **Effort**: S (trivial)
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug (correctness)
- **Planned at**: commit `36f0a5e`, 2026-07-09

## Why this matters

The superuser-only endpoint `POST /login/password-recovery-html-content/{email}`
returns the rendered reset-password email HTML and tries to attach the email
subject as a response header. The header key is written as `"subject:"` — with a
**trailing colon inside the field name**. `subject:` is not a valid/standard
HTTP header name, so any tool or client reading a `subject` (or `X-…`) header
gets nothing, and the value is emitted under a malformed key. It's a small bug
on a dev/preview endpoint, but it's a clear correctness defect with a one-line
fix and no behavioral risk to the rest of the system.

## Current state

`backend/app/auth/router.py` — the `recover_password_html_content` handler
(superuser-gated, `response_class=HTMLResponse`). The final return, at line ~124:

```python
    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
```

Note `email_data.subject` is already the translated subject (from
`generate_reset_password_email`, which localizes for `user.locale`). Only the
**header key** is wrong.

There is no test asserting this header (verified at planning time:
`tests/test_emails.py` tests the `generate_*` functions' returned
`subject`/`html_content`, not this route's headers), so no existing test breaks.

## Commands you will need

Run from `backend/`.

| Purpose    | Command               | Expected on success |
|------------|-----------------------|---------------------|
| Type-check | `uv run mypy .`       | exit 0              |
| Lint       | `uv run ruff check .` | exit 0              |

(The full pytest suite needs the Docker DB; it is not required for this change —
see Test plan.)

## Scope

**In scope** (the only file you should modify):
- `backend/app/auth/router.py` — the one header key.

**Out of scope** (do NOT touch):
- `app/emails/service.py` and the email templates — the subject value is correct;
  only the header key is wrong.
- Any other route or the endpoint's auth/response-class configuration.

## Git workflow

- Branch: `advisor/003-fix-subject-response-header` (create from the current branch).
- Conventional Commits (enforced by commitlint). Suggested message:
  `fix(auth): use a valid header name for password-preview subject`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Fix the header name

In `backend/app/auth/router.py`, change the malformed key `"subject:"` to a valid
custom header name `"X-Email-Subject"`:

```python
    return HTMLResponse(
        content=email_data.html_content,
        headers={"X-Email-Subject": email_data.subject},
    )
```

(`X-Email-Subject` preserves the original intent — exposing the subject as
response metadata — under a valid, unambiguous header name.)

**Verify**:
- `grep -n '"subject:"' backend/app/auth/router.py` → **no matches**.
- `grep -n 'X-Email-Subject' backend/app/auth/router.py` → one match.
- `uv run ruff check .` → exit 0.
- `uv run mypy .` → exit 0.

## Test plan

- **No new automated test required.** This is a one-line header-name correction
  on a superuser-only preview endpoint with no existing header assertion;
  exercising it in a test would require a superuser client and the Docker DB for
  disproportionate value.
- **Optional** (only if the Docker stack is already up): call the endpoint as a
  superuser and confirm the response carries an `X-Email-Subject` header with the
  (localized) subject and no `subject:` header.
- **Verification**: `uv run ruff check .` and `uv run mypy .` both exit 0.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -rn '"subject:"' backend/app/auth/router.py` returns **no matches**.
- [ ] `grep -rn "X-Email-Subject" backend/app/auth/router.py` returns one match.
- [ ] `uv run ruff check .` (from `backend/`) exits 0.
- [ ] `uv run mypy .` (from `backend/`) exits 0.
- [ ] Only `backend/app/auth/router.py` is modified (`git status`).
- [ ] `plans/README.md` status row for 003 updated.

## STOP conditions

Stop and report back (do not improvise) if:

- The excerpt in "Current state" doesn't match the live file (drift), e.g. the
  header line is already fixed or the endpoint was removed.
- A test unexpectedly fails referencing this endpoint's headers (would mean a
  test was added after this plan was written that pins `subject:`).

## Maintenance notes

- **Reviewer should scrutinize**: nothing beyond the single header key; confirm
  the subject value path (`email_data.subject`) is unchanged.
- If the team standardizes on a different metadata convention (e.g. returning
  the subject in the JSON body of a companion endpoint), this header can be
  dropped entirely; it exists only for the HTML preview flow.
