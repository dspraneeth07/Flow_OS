# Porting a component from `flowos_core.components.<provider>` to `src/bundles/<provider>`

This is the step-by-step recipe for extracting a provider package from the
in-tree `src/flowos-core/src/flowos_core/components/<provider>/` directory into a standalone
Extension Bundle distribution under `src/bundles/<provider>/`. The DuckDuckGo
bundle ([`src/bundles/duckduckgo`](duckduckgo/)) is the reference
implementation; every section below maps to a single, copy-pasteable change
and a verification command.

If you'd rather automate the mechanical steps, use
[`scripts/migrate/port_bundle.py`](../../scripts/migrate/port_bundle.py)
(see [§ Automation](#automation)). It writes the same files this doc
describes — review the diff before committing.

---

## 0. Prerequisites — pick a candidate

Before you start, confirm the component is a good fit:

- [ ] The provider directory `src/flowos-core/src/flowos_core/components/<provider>/` exists
      and contains one or more `Component` subclasses.
- [ ] Imports from `flowos_core.*` only (no `from flowos...`); the bundle is
      installed against the public `BUNDLE_API` surface, not FlowOS internals.
      Check with: `grep -r "from flowos" src/flowos-core/src/flowos_core/components/<provider>/`
- [ ] No deactivated / legacy duplicate exists under `src/flowos-core/src/flowos_core/components/deactivated/<provider>/`.
- [ ] The runtime dependencies the component pulls in (e.g. `langchain-community`,
      a vendor SDK) can be declared in the bundle's `pyproject.toml` without
      cycling through `flowos_core` or `flowos-base`.

Pick the **bundle name** (snake_case, lowercase, matches the directory name —
e.g. `duckduckgo`, `arxiv`, `wikipedia`) and the **distribution name**
(`flowos_core-<bundle>`, e.g. `flowos-duckduckgo`). These two strings are the only
identifiers you'll repeat throughout the port.

---

## 1. Lay out the bundle directory

Create `src/bundles/<bundle>/` with this exact tree (mirrors
`src/bundles/duckduckgo/`):

```
src/bundles/<bundle>/
├── README.md
├── pyproject.toml
└── src/
    └── flowos_core_<bundle>/
        ├── __init__.py
        ├── extension.json
        └── components/
            └── <bundle>/
                ├── __init__.py
                └── <source>.py        # one file per component class
```

> **Why nested `src/flowos-core_<bundle>/components/<bundle>/`?** The outer
> `flowos_core_<bundle>` is the importable Python package (matches the wheel layout
> `importlib.metadata.files()` walks). The inner `components/<bundle>/`
> is the path declared in `extension.json:bundles[].path` — keeping it as
> `components/<bundle>` means saved flows that referenced
> `flowos_core.components.<bundle>.<file>.<Class>` migrate cleanly via a single
> import-path entry in the migration table.

### 1a. `pyproject.toml`

Copy [`src/bundles/duckduckgo/pyproject.toml`](duckduckgo/pyproject.toml) and
substitute names + the runtime-dep block. The non-obvious bits:

- `dependencies` lists every runtime dep the component imports. Floor `flowos_core`
  at the current FlowOS/FLOWOS_CORE `major.minor` line and cap below the next `flowos_core`
  major — e.g. `"flowos_core>=1.10.0,<2.0.0"`. You normally don't hand-write this:
  `port_bundle.py` fills it in from `src/flowos-core/pyproject.toml` at port time, and
  `make patch` re-syncs every existing bundle via
  [`scripts/ci/sync_bundle_flowos_core_pin.py`](../../scripts/ci/sync_bundle_flowos_core_pin.py).
  Fine-grained BUNDLE_API compatibility is enforced separately via
  `extension.json`'s `"flowos_core": {"compat": [...]}` contract against the running
  flowos_core's `BUNDLE_API_VERSION`, not the version cap.
- **Platform-gated deps:** if a runtime dep has no wheel on some platform
  (e.g. `ibm-db` ships none for linux/aarch64), gate it with a PEP 508 marker
  so `pip install flowos` still succeeds there, e.g.
  `"ibm-db>=3.2.9,<4.0.0; sys_platform != 'linux' or platform_machine != 'aarch64'"`.
  Import that dep *lazily* (inside the method that uses it, not at module top
  level) so the bundle still loads on the excluded platform and the affected
  component degrades gracefully instead of breaking discovery. The
  cross-platform install test gates a hard-dep bundle through flowos's main
  install; if the **bundle itself** (not just a transitive dep) cannot install
  on a platform, also add the same marker to its dependency line in the root
  [`pyproject.toml`](../../pyproject.toml) so flowos does not require it there.
- `[project.entry-points."flowos.extensions"]`: `<dist-name> = "flowos_core_<bundle>"`.
  This is what `flowos_core.extension.loader._plugins._manifest_via_entry_point`
  reads to find the manifest; an editable install with no `dist.files`
  visibility falls back to this entry point.
- `[tool.hatch.build.targets.wheel]` MUST include
  `src/flowos-core_<bundle>/extension.json` and the components glob — wheel
  installs read the manifest via `dist.files` and skip the bundle if the
  file isn't packaged.

### 1b. `src/flowos-core_<bundle>/extension.json`

```json
{
  "$schema": "https://schemas.flowos.org/extension/v1.json",
  "id": "flowos_core-<bundle>",
  "version": "0.1.0",
  "name": "<Human-readable bundle name>",
  "description": "<One-line description>.",
  "flowos_core": { "compat": ["1"] },
  "bundles": [
    { "name": "<bundle>", "path": "components/<bundle>" }
  ]
}
```

The `id` is the distribution name (with a hyphen). The `bundles[0].name`
is the snake_case bundle name used in saved-flow IDs
(`ext:<bundle>:<Class>@official`). They differ by one character (`-` vs
`_`); don't mix them up.

### 1c. `src/flowos-core_<bundle>/__init__.py`

Re-export the component class(es) from the package root so
`flowos_core_<bundle>.<Class>` resolves. The migration table's `bare_class_name`
entry depends on this import working.

```python
"""flowos_core-<bundle>: <description>."""

from flowos_core_<bundle>.components.<bundle>.<source> import <Class>

__all__ = ["<Class>"]
```

### 1d. `src/flowos-core_<bundle>/components/<bundle>/__init__.py`

```python
from .<source> import <Class>

__all__ = ["<Class>"]
```

### 1e. `src/flowos-core_<bundle>/components/<bundle>/<source>.py`

This is the **moved** file. Copy it byte-for-byte from
`src/flowos-core/src/flowos_core/components/<bundle>/<source>.py` — do **not** rewrite
imports. The component's `from flowos_core.*` imports work unchanged because
`flowos_core` is a runtime dep of the bundle.

### 1f. `README.md`

A short page explaining what the bundle ships, how to install it, and how
to develop against it. Use [`duckduckgo/README.md`](duckduckgo/README.md)
as the template.

---

## 2. Remove the in-tree component

Delete the whole legacy directory:

```bash
git rm -r src/flowos-core/src/flowos_core/components/<bundle>/
```

Then surgically remove the three references in
[`src/flowos-core/src/flowos_core/components/__init__.py`](../flowos_core/src/flowos-core/components/__init__.py):

1. The `<bundle>,` line in the import block (around line 10).
2. The `"<bundle>": "__module__",` entry in the type-mapping dict.
3. The `"<bundle>",` string in the `__all__`-style list.

> **Sanity check:** after the edit,
> `grep -n "<bundle>" src/flowos-core/src/flowos_core/components/__init__.py` returns
> nothing.

---

## 3. Wire the workspace

### 3a. Root [`pyproject.toml`](../../pyproject.toml)

Three edits — all mechanical:

```toml
# 1. Add to [project] dependencies (regular dep so `pip install flowos`
#    still pulls the component in -- no user-visible change at install time).
dependencies = [
    "flowos-base[complete]>=0.10.0",
    "flowos-duckduckgo>=0.1.0",
    "flowos_core-<bundle>>=0.1.0",                 # <-- add this line
]

# 2. Add to [tool.uv.sources]
flowos_core-<bundle> = { workspace = true }

# 3. Add to [tool.uv.workspace] members
members = [
    "src/backend/base",
    ".",
    "src/flowos-core",
    "src/sdk",
    "src/bundles/duckduckgo",
    "src/bundles/<bundle>",                # <-- add this line
]
```

### 3b. `src/backend/base/pyproject.toml` (optional)

Only touch this if the component had a `flowos-base[<bundle>]` extra.
Remove the extra and any `flowos-base[<bundle>]` reference from
`complete`. The duckduckgo port did this; if the component had no extras
(e.g. arxiv), skip this section entirely.

### 3c. Lockfile

```bash
uv lock
git add uv.lock
```

---

## 4. Add migration entries

Append to
[`src/flowos-core/src/flowos_core/extension/migration/migration_table.json`](../flowos_core/src/flowos-core/extension/migration/migration_table.json).
The schema requires **three** legacy forms covering every shape a saved
flow may have used:

```json
{
  "bare_class_name": "<Class>",
  "target": "ext:<bundle>:<Class>@official",
  "added_in": "<release>"
},
{
  "import_path": "flowos_core.components.<bundle>.<source>.<Class>",
  "target": "ext:<bundle>:<Class>@official",
  "added_in": "<release>"
},
{
  "import_path": "flowos_core.components.<bundle>.<Class>",
  "target": "ext:<bundle>:<Class>@official",
  "added_in": "<release>"
},
{
  "legacy_slot": "ext:<bundle>:<Class>@official-pre-a",
  "target": "ext:<bundle>:<Class>@official",
  "added_in": "<release>"
}
```

If the component declared multiple classes, repeat the four-entry block
per class (the bare-name entry is only added when the class name is
globally unique across every Bundle in the release;
`scripts/migrate/check_bare_names.py` enforces this).

The migration table is **append-only**. Never remove or rewrite an
existing entry — CI rejects removals so a flow saved years ago against a
long-extracted bundle still loads.

---

## 5. Regenerate the component index

The pre-built component index drives lazy loading; the moved component's
old entry must be removed.

```bash
FLOWOS_DEV=1 uv run python scripts/build_component_index.py
```

`FLOWOS_DEV=1` forces dynamic discovery via `pkgutil.walk_packages`; without
it the script reads the existing index and reproduces the stale entry
even when the source module is gone.

The diff should only delete the `<bundle>` block; if it touches anything
else, your local checkout has unrelated drift.

---

## 6. Add an integration test

Create
`src/flowos-core/tests/integration/extension/test_pilot_<bundle>_upgrade.py`,
modelled on
[`test_pilot_duckduckgo_upgrade.py`](../flowos_core/tests/integration/extension/test_pilot_duckduckgo_upgrade.py).
The four test cases that matter:

1. Bare class name → canonical ID.
2. Full import path → canonical ID.
3. Package-level import path → canonical ID.
4. The `flowos_core-<bundle>` distribution is importable AND ships
   `extension.json` in a location `importlib.metadata.files` can discover
   (or, for editable installs, that `direct_url.json` resolves).

The integration test is the only place the saved-flow contract is
exercised end-to-end; do **not** skip it.

### Coverage that moves with the port

The in-tree `test_<bundle>_component.py` under
`src/backend/tests/unit/components/<bundle>/` typically includes a
`test_component_versions` case that walks a `file_names_mapping` fixture
to verify saved fixtures from older schema versions still instantiate.
That fixture imports from `tests.base`, which is not importable inside a
bundle. The new bundle-local test (`src/bundles/<bundle>/tests/`) drops
it, and `test_pilot_<bundle>_upgrade.py` covers namespace migration but
not intra-class schema evolution.

If the legacy fixture had non-empty entries, replicate the version check
in some bundle-friendly form (parametrise the bundle test over the same
mapping, no `tests.base` import). If it was empty, call out the
regression in the PR description so reviewers can weigh in on whether
the case should be replicated before merge.

---

## 7. Verify

Run, in order, the smallest commands that will fail loudly when a step is
wrong:

```bash
# 1. The bundle's manifest is structurally valid.  Point ``validate`` at
#    the package directory (where extension.json lives), not the bundle
#    root -- the manifest is nested inside ``src/flowos-core_<bundle>/`` so the
#    wheel ships it.  The validator accepts both ``def build(self): ...``
#    and ``outputs = [Output(method="...")]`` shapes; a component that
#    uses neither will fail with ``build-method-missing`` -- add an
#    ``outputs`` declaration in that case.
uv run flowos_core extension validate src/bundles/<bundle>/src/flowos-core_<bundle>

# 2. Workspace resolves and the bundle is importable.
uv sync
uv run python -c "from flowos_core_<bundle> import <Class>; print(<Class>.__name__)"

# 3. Migration table parses and the new entries are visible.
uv run pytest src/flowos-core/tests/unit/extension/migration -q

# 4. Loader discovers the editable install via direct_url.json.
uv run python -c "
from flowos_core.extension.loader._plugins import installed_extension_roots
roots = installed_extension_roots()
assert 'flowos_core-<bundle>' in roots, roots
print('discovered:', roots['flowos_core-<bundle>'])
"

# 5. The integration test passes.
uv run pytest src/flowos-core/tests/integration/extension/test_pilot_<bundle>_upgrade.py -q

# 6. Ruff is clean across the touched Python files.  (Don't pass the
#    JSON migration table to ruff -- it lints it as Python and complains
#    about the top-level expression.)
uv run ruff check src/bundles/<bundle> src/flowos-core/src/flowos_core/components/__init__.py src/flowos-core/tests/integration/extension/test_pilot_<bundle>_upgrade.py
```

**End-to-end smoke test** (optional but cheap): start a dev server with
the bundle on the palette and click Reload.

```bash
uv run flowos_core extension dev src/bundles/<bundle>
# In a browser at http://localhost:7860:
#   - Confirm <Class> appears under the <bundle> bundle group.
#   - Right-click the <bundle> header -> Reload. No errors.
```

---

## 8. Docker images (only if shipping a new bundle to the runtime image)

The four `docker/build_and_push*.Dockerfile` images already `COPY
./src/bundles` into the build context, so a new bundle directory is
picked up automatically by the workspace `uv sync`. The two **non**-uv-sync
Dockerfiles need an extra line:

- [`docker/build_and_push_backend.Dockerfile`](../../docker/build_and_push_backend.Dockerfile):
  add `./src/bundles/<bundle>` to the explicit `uv pip install` line.
- [`docker/build_and_push_base.Dockerfile`](../../docker/build_and_push_base.Dockerfile):
  add a `uv pip install --no-deps /app/src/bundles/<bundle>` step after
  the workspace sync, alongside the bundle's runtime deps if they aren't
  already in the base lock.

If your bundle has no extras and its deps are already in
`flowos-base[complete]`, the `--no-deps` install is enough.

---

## Common pitfalls

- **Component imports `from flowos...`**: the bundle is installed against
  `flowos_core`, not `flowos`. Either rewrite the import to use the public
  `BUNDLE_API` surface or leave the component in-tree.
- **`extension.json` not in the wheel**: `dist.files` doesn't surface it,
  so non-editable installs skip the bundle. Confirm the `[tool.hatch.build.targets.wheel] include` glob picks it up.
- **Bundle name has a hyphen**: only the *distribution* name uses
  hyphens (`flowos-duckduckgo`); the *bundle* name is snake_case
  (`duckduckgo`). The schema rejects hyphens in `bundles[].name`.
- **Forgot the `flowos.extensions` entry-point**: editable installs
  fail discovery silently — `installed_extension_roots()` returns an
  empty dict and the bundle never enters the registry.
- **Migration entries missing**: saved flows still validate, but the
  palette can't render the legacy node — the user sees a "component not
  found" toast. The four-entry block in step 4 covers every shape FlowOS
  has serialized in the past.

---

## Automation

[`scripts/migrate/port_bundle.py`](../../scripts/migrate/port_bundle.py)
generates the bundle skeleton, removes the in-tree directory, edits the
two `__init__.py` references, and patches the root `pyproject.toml`. It
**does not** edit the migration table or the integration test — those
require human judgement (release version, class-name uniqueness check).

```bash
# Dry run -- prints the planned changes; reviewer signs off before --apply.
uv run python scripts/migrate/port_bundle.py --bundle arxiv --apply
```

After running the script, work through this doc's verification block (§7);
if anything fails, the script's diff is the single artefact to review.
