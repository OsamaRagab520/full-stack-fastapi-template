# Upstream changes review (`fastapi/full-stack-fastapi-template`)

This template was created as a **fresh copy** of the upstream FastAPI template (GitHub
"Use this template" / copy + `git init`), so it shares **no git ancestor** with upstream.
Comparison is therefore done by file-tree matching, not `git merge-base`.

| | |
|---|---|
| **Fork point** (your `Initial commit` tree matches upstream) | `cd83fc1` — *2026-06-16* |
| **Upstream tip at review time** | `4cd0d9e` — *2026-07-04* |
| **Commits upstream since fork** | 44 total (22 auto "release notes", 10 dependency bumps, ~12 substantive) |
| **Reviewed on branch** | `worktree-adapt-upstream` |

Because our layout is heavily refactored (domain-based backend, i18n, async SQLAlchemy),
upstream changes cannot be merged directly — each has to be ported by hand. This file
records what was **adapted** and what is **left for you to decide**.

---

## ✅ Adapted in this branch

All of the following are applied and validated (backend: ruff, ruff-format, mypy strict,
`ty`, 76 pytest; frontend: `tsc` + `vite build`, biome lint).

| Change | Upstream PR | What we did | Notes |
|---|---|---|---|
| **`typos` pre-commit hook** | #2317 / #2343 | Added `crate-ci/typos` (v1.47.2) to `.pre-commit-config.yaml` + `[tool.typos]` config in root `pyproject.toml` | Excluded `backend/app/locales/` and `frontend/src/client/` (generated / non-English) |
| **FastAPI floor bump** | #2357 | `fastapi[standard] >=0.115` → `>=0.138.1` in `backend/pyproject.toml` | Resolved to 0.139.0 locally |
| **`emails` 0.6 → 1.1.2** | #2369 | Bumped `backend/pyproject.toml`; fixed `emails/service.py` for the now-typed lib | Dropped unused `# type: ignore`, switched to `emails.message.Message`, added `assert EMAILS_FROM_EMAIL` to narrow Optional (mirrors upstream) |
| **Models type refactor** | #2356 | `UserUpdate`/`ItemUpdate` now inherit `SQLModel` directly with explicit optional fields (removed two `# type: ignore`s); regenerated frontend client | Preserved the i18n `locale` field on `UserUpdate`. Makes partial updates correct; verified `model_dump(exclude_unset=True)` behavior unchanged |
| **Frontend npm mass-update** | #2333 | Aligned all shared deps to upstream versions, incl. **major** bumps `vite` 7→8 and `lucide-react` 0.x→1.x; kept i18n deps (`i18next`, `react-i18next`, `i18next-browser-languagedetector`) | Also bumped `@biomejs/biome` 2.3.14→2.4.16; added `!**/public/assets/images/**/*` to `biome.json` because biome 2.4 newly lints `.svg` files (false-positive `noSvgWithoutTitle` on static logo assets) |

### Adapted in the follow-up commit (previously "not adapted")

| Change | Upstream PR | What we did | Notes |
|---|---|---|---|
| **Python 3.14 upgrade** | #2352 | Bumped `requires-python`, ruff `target-version = py314`, CI python-version (test-backend / pre-commit / playwright), `Dockerfile` base image; added root `.python-version`; applied the ruff `UP043`/`UP037` modernizations that `py314` enables | **Reverses your earlier 3.11 choice (`25f9683`)** — done per your instruction. The venv already ran 3.14.4, so the runtime was pre-validated (76 tests green). `UP037` unquoted `list["Item"]` → `list[Item]`, safe under Python 3.14 PEP 649 deferred annotations (verified by tests) |
| **FastAPI `fastapi run` entrypoint** | #2360 | Dropped the explicit `app/main.py` from the Docker `CMD` | Verified: `fastapi run` auto-discovers `app.main:app` |
| **sqlmodel floor bump** | align w/ #2354 | `>=0.0.21` → `>=0.0.39` | Matches upstream; all tests pass |
| **Library-skills (FastAPI + SQLModel)** | #2354 | `uvx library-skills --all --claude --tool-skill`: relative symlinks in `.agents/skills/` **and** `.claude/skills/` (fastapi, sqlmodel) + the copied `library-skills` tool skill | Symlinks target `.venv` — see the setup note below |

> **Setup notes for a fresh clone** (neither is a code issue):
> 1. Compiled gettext catalogs (`*.mo`) are gitignored, so i18n tests fail until you run
>    `uv run pybabel compile -d backend/app/locales` (the `compile-gettext-catalogs` hook).
> 2. The library-skills symlinks point into `.venv`, so they only resolve after
>    `uv sync`; re-run `uvx library-skills --all --claude` if the Python version changes
>    (the symlink path is version-pinned to `python3.14`).
> Both are worth calling out in the README / onboarding.

---

## 📋 Not adapted — evaluate these

> Python 3.14 (#2352), the `fastapi run` entrypoint (#2360), and library-skills (#2354)
> were **since adopted** — see "Adapted in the follow-up commit" above. What remains:

### 1. `pyproject.toml` housekeeping — cosmetic — #2350, #2353
- #2350 sorted keys in `pyproject.toml`.
- #2353 moved `prek` to top-level dependencies (you already have `prek` in the backend
  `dev` group, so this is largely N/A for our layout).
**Value:** consistency with upstream diffs. **Risk:** none. **To apply:** optional tidy-up.

### 2. CI / workflow updates — mostly N/A (you disabled non-essential workflows)
You run a reduced CI set (several workflows are dispatch-only or `.disabled`), so these are
low-priority, but noted for completeness:
- **zizmor security-check update** (#2345) — hardens the security workflow. Worth taking if
  you keep `zizmor.yml` active.
- **Simplified PR workflow triggers** (#2349).
- Action bumps: `actions/checkout` 6→7, `issue-manager` 0.7→0.8.1, `latest-changes` 0.6.1,
  Playwright docker image `1.58.2`→`1.61.1`.
**To apply:** port individually only for workflows you keep enabled.

---

## 🔇 Skipped as noise
- 22 × "📝 Update release notes" (auto-generated).
- README screenshot alt-text tweak (#2359) — cosmetic, upstream-specific content.
- Dependency bumps already covered by the frontend/backend updates above.

---

## How this comparison was reproduced
```bash
git fetch upstream
# fork point = upstream commit whose tree matches your Initial commit
git rev-list upstream/master | while read c; do \
  [ "$(git rev-parse $c^{tree})" = "$(git rev-parse <initial-commit>^{tree})" ] && echo "$c"; done
# meaningful upstream commits since the fork point:
git log --oneline cd83fc1..upstream/master | grep -viE 'release notes|Bump|⬆'
```
