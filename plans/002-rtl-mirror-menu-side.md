# Plan 002: Sidebar dropdown menus mirror their side under RTL

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**:
> `git diff --stat 36f0a5e..HEAD -- frontend/src/components/Common/Language.tsx frontend/src/components/Common/Appearance.tsx frontend/src/components/Sidebar/User.tsx`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug (i18n / RTL UI)
- **Planned at**: commit `36f0a5e`, 2026-07-09

## Why this matters

The app is fully localized and supports Arabic, which flips the layout to RTL
(`useLanguageDirection` sets `<html dir="rtl">`, and `frontend/AGENTS.md`
mandates Tailwind logical utilities so the layout mirrors). But three dropdown
menus anchored to the sidebar hardcode a **physical** Radix `side="right"`.
Radix's `side` is a physical edge, not a logical one — so under `dir="rtl"`,
where the sidebar sits on the right, these menus open toward the wrong edge
(over/across the sidebar instead of away from it). The pattern for fixing this
already exists in the codebase: the in-progress edit to `components/ui/sidebar.tsx`
derives the tooltip side from `i18n.dir()` (`i18n.dir() === "rtl" ? "left" :
"right"`). This plan applies that same mirroring to the three menus that were
missed, completing the RTL behavior for the sidebar surface.

## Current state

Three files, each with a `DropdownMenuContent` whose `side` hardcodes `"right"`
for the desktop (non-mobile) case. All three components already have access to
i18n (`Appearance` and `User` destructure `useTranslation()`; `Language` imports
the `i18n` singleton). The vertical/mobile placements (`"top"`, `"bottom"`) are
correct and must stay.

`frontend/src/components/Common/Appearance.tsx` — `SidebarAppearance`, line 29
already has `const { t } = useTranslation()`; line 45-49:

```tsx
        <DropdownMenuContent
          side={isMobile ? "top" : "right"}
          align="end"
          className="w-(--radix-dropdown-menu-trigger-width) min-w-56"
        >
```

`frontend/src/components/Sidebar/User.tsx` — `User`, line 46 already has
`const { t } = useTranslation()`; line 78-83:

```tsx
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
```

`frontend/src/components/Common/Language.tsx` — `SidebarLanguage`, line 32 has
`const { t } = useTranslation()`; **line 17 already imports the singleton**
`import i18n, { type AppLanguage, LANGUAGES } from "@/i18n"`; line 47-51:

```tsx
        <DropdownMenuContent
          side={isMobile ? "top" : "right"}
          align="end"
          className="w-(--radix-dropdown-menu-trigger-width) min-w-56"
        >
```

**Pattern to match** — `frontend/src/components/ui/sidebar.tsx` (the working
tree already contains this idiom for the collapsed-menu tooltip):

```tsx
      <TooltipContent
        side={i18n.dir() === "rtl" ? "left" : "right"}
        ...
```

Why reading `i18n.dir()` inside these components is reactive: each component
calls `useTranslation()` (uses `t(...)`), so react-i18next re-renders it on
`languageChanged`; the `i18n.dir()` read re-evaluates with the new language.

## Commands you will need

Run from `frontend/`.

| Purpose    | Command          | Expected on success                     |
|------------|------------------|-----------------------------------------|
| Lint/format| `bun run lint`   | exit 0 (biome; autofixes in place)      |
| Build+types| `bun run build`  | `tsc` + `vite build` succeed, exit 0    |

`bun` is the runtime (not npm/node); `biome` is the linter (not eslint/prettier).
Do not introduce a component test framework — this repo has no frontend unit
tests (only Playwright e2e, which needs the full Docker stack); see Test plan.

## Scope

**In scope** (the only files you should modify):
- `frontend/src/components/Common/Appearance.tsx`
- `frontend/src/components/Sidebar/User.tsx`
- `frontend/src/components/Common/Language.tsx`

**Out of scope** (do NOT touch, even though they look related):
- `frontend/src/components/ui/sidebar.tsx` — a shadcn/ui primitive with
  **uncommitted work in progress** (the RTL tooltip/side mapping). Do not edit,
  stage, revert, or stash it. Leave the working tree as you found it there.
- `frontend/src/components/Common/DataTable.tsx` — its `side="top"` is a vertical
  placement, unaffected by RTL. Leave it.
- Any component using `align`/`sideOffset` only — `align="end"` is already
  logical-direction-aware in Radix; do not change `align`.
- The generated client (`src/client/**`) and `src/routeTree.gen.ts`.

## Git workflow

- Branch: `advisor/002-rtl-mirror-menu-side` (create from the current branch).
- Conventional Commits (enforced by commitlint). Suggested message:
  `fix(i18n): mirror sidebar dropdown side under RTL`.
- Do NOT push or open a PR unless the operator instructed it.
- Because `ui/sidebar.tsx` has uncommitted changes, stage **only** the three
  in-scope files (`git add` them explicitly); never `git add -A`.

## Steps

### Step 1: `Appearance.tsx` — mirror the menu side

In `SidebarAppearance`, replace the hardcoded desktop side. The component
already has `const { t } = useTranslation()` (line 29); change it to also pull
`i18n`:

```tsx
  const { t, i18n } = useTranslation()
```

Then change the `DropdownMenuContent` `side` prop:

```tsx
        <DropdownMenuContent
          side={isMobile ? "top" : i18n.dir() === "rtl" ? "left" : "right"}
          align="end"
          className="w-(--radix-dropdown-menu-trigger-width) min-w-56"
        >
```

Leave the second component in this file (`Appearance`, the non-sidebar toggle)
unchanged — its menu has no `side` prop.

**Verify**: `bun run lint` → exit 0.

### Step 2: `User.tsx` — mirror the menu side

In `User`, change line 46 to also pull `i18n`:

```tsx
  const { t, i18n } = useTranslation()
```

Then change the `DropdownMenuContent` `side` prop:

```tsx
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? "bottom" : i18n.dir() === "rtl" ? "left" : "right"}
            align="end"
            sideOffset={4}
          >
```

**Verify**: `bun run lint` → exit 0.

### Step 3: `Language.tsx` — mirror the menu side

This file already imports the `i18n` singleton at line 17, so **no hook change
is needed** — use the singleton directly (the component re-renders via its
`t(...)` usage). Change only the `DropdownMenuContent` `side` in
`SidebarLanguage`:

```tsx
        <DropdownMenuContent
          side={isMobile ? "top" : i18n.dir() === "rtl" ? "left" : "right"}
          align="end"
          className="w-(--radix-dropdown-menu-trigger-width) min-w-56"
        >
```

Leave the second component (`Language`, the non-sidebar dropdown) unchanged — its
menu has no `side` prop.

**Verify**: `bun run lint` → exit 0.

### Step 4: Build and type-check

**Verify**: `bun run build` → exit 0 (`tsc -p tsconfig.build.json` then
`vite build` both succeed). Then confirm the change set:
`git status --short frontend/src/components` shows exactly the three in-scope
files modified (plus the pre-existing `ui/sidebar.tsx` you did not touch).

## Test plan

- **No new automated test.** This repo has no frontend unit-test runner; the
  only frontend tests are Playwright e2e (`bun run test`) which require the full
  Docker stack, and an RTL-placement assertion there would be disproportionate
  to a cosmetic fix. Verification is `bun run lint` + `bun run build` (green) plus
  the manual check below.
- **Manual verification** (do this if a dev server is already running; do not
  start the stack solely for this):
  1. `bun run dev`, open the app, log in.
  2. Switch language to العربية via the sidebar language menu.
  3. Confirm `<html dir="rtl">` (DevTools) and that the user, language, and
     appearance dropdowns open toward the **inside** of the viewport (to the
     left of the right-side sidebar), not across/over the sidebar.
  4. Switch back to English; confirm the menus open to the right as before.
- If you cannot run the app, state that manual verification is pending and rely
  on lint + build gates; still mark the automated done-criteria complete.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `bun run lint` (from `frontend/`) exits 0.
- [ ] `bun run build` (from `frontend/`) exits 0.
- [ ] `grep -rn 'side={isMobile ? "\(top\|bottom\)" : "right"}' frontend/src/components/Common/Language.tsx frontend/src/components/Common/Appearance.tsx frontend/src/components/Sidebar/User.tsx` returns **no matches** (the hardcoded desktop `"right"` is gone from all three).
- [ ] `git status --short` shows only the three in-scope files changed by you (the pre-existing `ui/sidebar.tsx` modification is untouched and unstaged).
- [ ] `plans/README.md` status row for 002 updated.

## STOP conditions

Stop and report back (do not improvise) if:

- The excerpts in "Current state" don't match the live files (drift).
- `bun run build` fails with a type error about `i18n.dir()` — that would mean
  the react-i18next version changed its API; report it.
- Adding `i18n` to a `useTranslation()` destructure triggers a biome
  no-shadow/unused error you cannot resolve without touching an out-of-scope
  file.
- You find you need to edit `ui/sidebar.tsx` (which has uncommitted WIP) to make
  the fix — you do not; if it seems necessary, stop and report.

## Maintenance notes

- **Follow-up deliberately deferred**: the working-tree `ui/sidebar.tsx` still
  contains a hardcoded English `sr-only` string
  (`const sidebarCopy = open ? "Collapse Sidebar" : "Open Sidebar"`). That file
  is the user's in-progress work and is out of scope here; flag it to the owner
  rather than fixing it in this plan.
- **Reviewer should scrutinize**: that only the `side` prop changed (not
  `align`, which is already logical), and that the mobile placements
  (`"top"`/`"bottom"`) are preserved.
- **Future work that interacts**: if the sidebar is ever moved to the right edge
  in LTR (via the `side` prop of `<Sidebar>`), revisit this — the assumption
  here is sidebar-on-start-edge, menus-open-inward.
