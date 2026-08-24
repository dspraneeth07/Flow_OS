"""Sync the ``flowos_core`` runtime-dependency floor in every ``src/bundles/*`` package.

After a ``make patch v=X.Y.Z`` version bump, each bundle's ``flowos_core`` dependency
floor must track FlowOS/FLOWOS_CORE's ``major.minor`` line: a bundle published from
the X.Y release is built against that flowos_core's BUNDLE_API surface, so it must be
guaranteed to resolve an flowos_core new enough to carry it.  Before the FLOWOS_CORE 0.5.x ->
1.10.0 realignment (#13176) the generated floor was a flat ``flowos_core>=0.5.0`` with
no upper bound, which silently permitted resolving against the now-dead 0.5.x
line -- and neither pip nor uv flags the cross-line jump.

Pin form: ``flowos_core>=X.Y.0,<(X+1).0.0`` -- floored at the current minor line,
capped below the next flowos_core major.  The cap is a coarse install-time guard
against an untested flowos_core major; fine-grained BUNDLE_API compatibility is still
enforced at load time by each ``extension.json``'s ``flowos_core.compat`` list against
the running flowos_core's ``BUNDLE_API_VERSION`` (see
``src/flowos-core/src/flowos_core/extension/manifest.py``).

Idempotent: re-running with the same version is a no-op (so it is safe to call
unconditionally from ``make patch``, including patch releases within a minor
line where the floor does not move).  Only the bundle's ``"flowos_core<op>..."``
runtime dependency is rewritten -- self-references such as
``"flowos-docling[local]"`` and the nightly ``"flowos_core-nightly=="`` form are left
untouched (neither has a bare version operator immediately after ``flowos_core``).

Stdlib only, so it runs in any CI checkout (same constraint as the sibling
``scripts/ci/update_bundle_versions.py`` and ``scripts/migrate/port_bundle.py``).

Usage:
    python scripts/ci/sync_bundle_flowos_core_pin.py 1.10.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Matches a bundle's ``"flowos_core<op>VERSION[,<UPPER]"`` runtime dependency. The
# version operator immediately after ``flowos_core`` is what distinguishes the runtime
# dep from self-refs like ``"flowos-docling[local]"`` (a ``-`` follows ``flowos_core``)
# and the nightly ``"flowos_core-nightly=="`` rename produced by update_bundle_versions.
_FLOWOS_DEP_PATTERN = re.compile(
    r'"flowos_core(?:>=|~=|==)[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*'
    r'(?:,\s*<[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*)?"'
)

# Parses the leading ``X.Y`` out of an ``X.Y.Z`` (optionally ``vX.Y.Z``) version.
_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.\d+")


def flowos_core_floor_spec(version: str) -> str:
    """Return the bundle ``flowos_core`` dependency spec for a FlowOS/FLOWOS_CORE version.

    ``"1.10.0"`` -> ``"flowos_core>=1.10.0,<2.0.0"`` (floor at the minor line start,
    cap below the next flowos_core major). A leading ``v`` is tolerated.

    NOTE: this floor format is duplicated in ``scripts/migrate/port_bundle.py``
    (``_current_flowos_core_floor``) so each script stays standalone; keep them in step.
    """
    match = _VERSION_RE.match(version.lstrip("v"))
    if not match:
        msg = f"Unparseable version {version!r}; expected X.Y.Z"
        raise ValueError(msg)
    major, minor = int(match.group(1)), int(match.group(2))
    return f"flowos_core>={major}.{minor}.0,<{major + 1}.0.0"


def rewrite_flowos_core_dep(content: str, floor_spec: str) -> str:
    """Rewrite the bundle's ``flowos_core`` runtime dep to ``floor_spec``. Idempotent.

    Only the first (runtime) ``"flowos_core<op>..."`` specifier is touched; self-refs
    and the nightly form do not match ``_FLOWOS_DEP_PATTERN``.
    """
    return _FLOWOS_DEP_PATTERN.sub(f'"{floor_spec}"', content, count=1)


def sync_bundles(version: str, bundles_dir: Path) -> list[tuple[str, bool]]:
    """Rewrite the ``flowos_core`` floor in every ``src/bundles/*/pyproject.toml``.

    Returns ``(bundle_name, changed)`` tuples, sorted by bundle name.
    """
    floor_spec = flowos_core_floor_spec(version)
    results: list[tuple[str, bool]] = []
    for pyproject in sorted(bundles_dir.glob("*/pyproject.toml")):
        original = pyproject.read_text(encoding="utf-8")
        updated = rewrite_flowos_core_dep(original, floor_spec)
        if updated != original:
            pyproject.write_text(updated, encoding="utf-8")
        results.append((pyproject.parent.name, updated != original))
    return results


def main() -> None:
    """Entry point.

    Usage:
        sync_bundle_flowos_core_pin.py <version>

    ``version`` is the FlowOS/FLOWOS_CORE release version (e.g. ``1.10.0``).
    """
    expected_args = 2
    if len(sys.argv) != expected_args:
        print("Usage: sync_bundle_flowos_core_pin.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    floor_spec = flowos_core_floor_spec(version)  # validates early
    bundles_dir = BASE_DIR / "src" / "bundles"
    if not bundles_dir.is_dir():
        print("No src/bundles directory; nothing to sync.")
        return

    print(f'Syncing bundle flowos_core pin -> "{floor_spec}"')
    for name, changed in sync_bundles(version, bundles_dir):
        print(f"  {'updated' if changed else 'unchanged'}: {name}")


if __name__ == "__main__":
    main()
