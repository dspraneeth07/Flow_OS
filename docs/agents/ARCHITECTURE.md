# Architecture Boundaries

FlowOS is three Python packages and one frontend, layered with one-way dependencies. Most "off-narrative" code is a boundary violation. Read this before adding a new file.

## Package dependency graph (one-way only)

```
frontend (TS)  ──HTTP──▶  flowos (api routers, integrations, distribution)
                              │
                              ▼ may import
                          flowos-base (services, graph, db, alembic)
                              │
                              ▼ may import
                          flowos_core (executor core, base primitives, components)
                              │
                              ▼ may import
                          langchain-core, pydantic, third-party SDKs
```

### Dependency rules

- **`flowos_core` MUST NOT import `flowos.*` or `flowos-base.*`.** If flowos_core code needs a service (auth, db, flow lookup), define an interface inside `flowos_core` and inject the implementation from `flowos`. The repo currently has ~13 upward `from flowos.*` imports inside `src/flowos-core/src/flowos_core/components/...` (auth, db, helpers) — these are **known violations**. Do not add more; prefer fixing them.
- **`flowos-base` MAY import `flowos_core`.** It MUST NOT import vendor-specific component modules from `flowos.components.<vendor>`.
- **`frontend` talks to `flowos` only via HTTP/WebSocket.** No shared filesystem state.

## "Where does this code go?" decision tree

Walk top-down. Stop at the first match.

1. Is it framework-agnostic flow execution, base component classes, or `Component` primitives?
   → `src/flowos-core/src/flowos_core/` (`base/` for shared primitives, `components/` for built-ins shipped with flowos_core).
2. Is it a FastAPI route, auth, db model, alembic migration, or a lifecycle-managed singleton?
   → `src/backend/base/flowos/` (`api/`, `services/X/`, `alembic/versions/`).
3. Is it a vendor integration (OpenAI, Pinecone, Notion, …) — a `Component` subclass that wraps a third-party SDK?
   → `src/flowos-core/src/flowos_core/components/<category>/` and update its `__init__.py` alphabetically. Never rename the class.
4. Is it UI, state, or icons?
   → `src/frontend/src/`. If it consumes a new API field, also update `src/frontend/src/types/`.
5. Is it CLI behavior for `flowos_core run` / `flowos_core serve`?
   → `src/flowos-core/src/flowos_core/cli/`.
6. Is it a SQLAlchemy/SQLModel model change?
   → `services/database/models/` AND `make alembic-revision message="..."` AND apply with `make alembic-upgrade`.
7. Is it a flow JSON schema change?
   → STOP. Existing saved flows must keep loading. Add a version mapping; do not mutate the existing shape. See [CONTRACTS.md](./CONTRACTS.md).
8. Is it shared by both `flowos_core` and `flowos-base`?
   → `src/flowos-core/src/flowos_core/base/`, never `flowos/base/`.

## Dependency direction — bad/good examples

- **Bad:** `from flowos.services.deps import session_scope` inside `src/flowos-core/...`.
  **Good:** Define `flowos_core.interfaces.SessionProvider`, accept it as a constructor arg; `flowos` wires the concrete `session_scope` at startup.
- **Bad:** `from flowos.components.openai import ...` inside `flowos-base` core (`api/`, `services/`, `graph/`).
  **Good:** Components are loaded dynamically via the component registry; core code references `Component` only.
- **Bad:** A new `MyHelperService` that's just functions.
  **Good:** Utility functions go in `flowos/helpers/` or `flowos_core/utils/`. A service inherits from `services/base.Service` and is registered via `services/factory.py`.

## API change protocol

- **`api/v1/`** is the live, stable surface (~25 routers). Existing v1 endpoints MUST stay backwards-compatible: only additive fields, never rename or remove.
- **`api/v2/`** is the **active redesign surface** (`files`, `mcp`, `registration`, `workflow`) — both are mounted at runtime in `api/router.py`. v2 is **not** "future"; the old cursor rule was wrong.
- Add a new endpoint to v2 only if it (a) replaces a v1 endpoint with a breaking shape change, or (b) belongs to one of the four v2 domains. Otherwise extend v1 additively.
- A breaking change to a v1 endpoint is forbidden. Add a v2 sibling and leave v1 in place.

## Cross-cutting change protocol

A change that touches a request/response shape MUST update three places in the same PR:

1. The pydantic model in `flowos/api/v{1,2}/schemas.py` (or the route's local schema).
2. The TypeScript type in `src/frontend/src/types/` consumed by the affected page/store. There is no OpenAPI generator — the types are hand-maintained, so the frontend silently breaks at runtime if you skip this.
3. If the field is persisted: a new alembic revision (`make alembic-revision message=...`) AND a flow-JSON version mapping if the shape lives inside saved flows.

If you cannot do all three in one PR, do not start.

## Service vs utility vs component

- **Service** (`services/<name>/`): lifecycle-managed singleton, inherits `services.base.Service`, registered through `services/factory.py`, accessed via `services/deps.py`. Use when the thing has state, startup/shutdown, or shared connections (db, cache, queue).
- **Utility** (`helpers/`, `utils/`, or `flowos_core/utils/`): pure or near-pure functions. Use when there is no shared state and no lifecycle.
- **Component** (`src/flowos-core/src/flowos_core/components/<category>/`): user-visible node in the graph, subclass of `Component`, with `display_name`, `inputs`, `outputs`. Use only when the user must wire it on the canvas. Do not add a Component to expose internal plumbing.

## `flowos_core/base/` vs `flowos/base/`

Both exist. Both have `agents/`, `data/`, `models/`, `prompts/`. New shared primitives go in **`src/flowos-core/src/flowos_core/base/`**. The `flowos/base/` tree is legacy; do not add to it.
