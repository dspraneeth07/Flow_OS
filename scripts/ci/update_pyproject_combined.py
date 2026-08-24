#!/usr/bin/env python
# scripts/ci/update_pyproject_combined.py
import sys
from pathlib import Path

from update_lf_base_dependency import update_flowos_core_dep_in_base
from update_pyproject_version import update_pyproject_version
from update_uv_dependency import update_uv_dep as update_version_uv_dep

# Add the current directory to the path so we can import the other scripts
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))


def main():
    """Universal update script that handles both base and main updates in a single run.

    The packages keep their CANONICAL names (``flowos``, ``flowos-base``) -- they are NOT
    renamed to ``*-nightly``. This script only sets the nightly ``.devN`` versions and re-pins the
    inter-package dependencies to exact canonical dev versions. See ``src/bundles/NIGHTLY.md``.

    Usage:
    update_pyproject_combined.py main <main_tag> <base_tag> <flowos_core_tag>
    """
    arg_count = 5
    if len(sys.argv) != arg_count:
        print("Usage:")
        print("  update_pyproject_combined.py main <main_tag> <base_tag> <flowos_core_tag>")
        sys.exit(1)

    mode = sys.argv[1]
    if mode != "main":
        print("Only 'main' mode is supported")
        print("Usage: update_pyproject_combined.py main <main_tag> <base_tag> <flowos_core_tag>")
        sys.exit(1)

    main_tag = sys.argv[2]
    base_tag = sys.argv[3]
    flowos_core_tag = sys.argv[4]

    # Lockstep invariant: flowos-base's published dev version (set here from `base_tag`) and
    # flowos's exact `==` pin on it (set below from the same `base_tag`) MUST come from the same
    # value, so the latest nightly `flowos` always pins a base version published in the same run.
    # `pypi_nightly_tag.py` makes the main and base tags identical; keep both writes sourced from
    # `base_tag` or the pin can reference a version that was never published.

    # First handle base package updates (canonical name kept).
    update_pyproject_version("src/backend/base/pyproject.toml", base_tag)

    # Update FLOWOS_CORE dependency in flowos-base (exact canonical dev pin).
    flowos_core_version = flowos_core_tag.lstrip("v")
    update_flowos_core_dep_in_base("src/backend/base/pyproject.toml", flowos_core_version)

    # Then handle main package updates (canonical name kept).
    update_pyproject_version("pyproject.toml", main_tag)
    # Update flowos-base dependency version (strip 'v' prefix if present).
    base_version = base_tag.lstrip("v")
    update_version_uv_dep(base_version)


if __name__ == "__main__":
    main()
