# Frontend (React SPA)

## Purpose
React 19 + TypeScript single-page app: auth flows, dashboard, and CRUD UI over
the backend API. Owns routing, UI components, and client-side auth state. Does
NOT own the API client *source* (`src/client/` is generated) or any backend
contract — those live in `../backend/AGENTS.md`.

## Entry Points
- `src/main.tsx` — bootstraps the app, router, and TanStack Query client.
- `src/routes/` — file-based TanStack Router routes. `__root.tsx` is the shell;
  `_layout.tsx` (+ `_layout/`) wraps authenticated pages; `login.tsx`,
  `signup.tsx`, `recover-password.tsx`, `reset-password.tsx` are public.
- `src/hooks/useAuth.ts` — auth state and login/signup/logout mutations.

## Contracts & Invariants
- **`src/client/` is fully generated** from the backend OpenAPI spec by
  `@hey-api/openapi-ts`. Never hand-edit it. Regenerate with
  `bash ./scripts/generate-client.sh` (backend must be running) after any
  backend schema/route change. Service/method names follow the backend's
  `{tag}-{route_name}` id function — import them from `@/client`.
- **`src/routeTree.gen.ts` is generated** by the TanStack Router plugin from the
  files in `src/routes/`. Don't hand-edit it; add/rename route files instead.
- **Auth lives in `useAuth.ts`.** JWT persistence is abstracted by
  `src/lib/tokenStore.ts` (get/set/clear/isAuthenticated); the current user is
  fetched via TanStack Query on the `["currentUser"]` query key. Read/write the
  token only through `tokenStore` or `useAuth` — never raw `localStorage`.
- **Data flows through TanStack Query.** Server state = queries/mutations keyed
  consistently; don't fetch with bare `fetch`/`axios` outside the client layer.

## Patterns
- New page: add a file under `src/routes/` (place authenticated pages inside
  `_layout/`); the route tree regenerates on dev/build. Call backend via the
  generated `@/client` services inside a TanStack Query hook.
- New UI primitive: add via shadcn/ui into `src/components/`; compose with
  Tailwind v4 utilities and `cn()` from `src/lib/utils.ts`.
- API errors: surface via `handleError` (`src/utils.ts`) + `useCustomToast`.

## Anti-patterns
- Don't edit generated files (`src/client/**`, `src/routeTree.gen.ts`).
- Don't read/write the raw JWT outside `tokenStore`/`useAuth`.
- Don't duplicate request/response types by hand — use the generated types.
- Don't bypass TanStack Query to manage server state in component state.

## Pitfalls
- `src/components/` is large (~37k tokens, mostly shadcn/ui primitives) — prefer
  reusing/extending existing ones over adding new dependencies.
- A stale client is a common bug: if a call's shape looks wrong, regenerate
  before debugging — the backend schema may have moved.
- `bun` is the runtime (not npm/node). `biome` (not eslint/prettier) lints/formats.
- Playwright e2e (`bun run test`) needs the full Docker stack up.

## Dependencies & Edges
- Uplink: `../AGENTS.md` (stack, commands, global invariants).
- Downlink: `../backend/AGENTS.md` — source of the OpenAPI schema this consumes.
- Tooling: `bun` (deps/run), `vite` + `tsc` (build), `biome` (lint), Playwright (e2e).
