#!/usr/bin/env python

import re
import sys
from pathlib import Path

import packaging.version

BASE_DIR = Path(__file__).parent.parent.parent
ARGUMENT_NUMBER = 3


def update_base_dep(pyproject_path: str, new_version: str) -> None:
    """Update the flowos-base dependency in pyproject.toml."""
    filepath = BASE_DIR / pyproject_path
    content = filepath.read_text(encoding="utf-8")

    # Updated pattern to handle PEP 440 version suffixes, extras (e.g., [complete]),
    # ~=, ==, and >= version specifiers, and both flowos-base and flowos-base-nightly names
    # Captures extras in group 2 to preserve them in the replacement
    pattern = re.compile(
        r'("flowos-base(?:-nightly)?((?:\[[^\]]+\])?)(?:~=|==|>=)[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*")'
    )

    # Check if the pattern is found
    match = pattern.search(content)
    if not match:
        msg = f'flowos-base dependency not found in "{filepath}"'
        raise ValueError(msg)

    # Extract extras if present (e.g., "[complete]")
    extras = match.group(2) if match.group(2) else ""
    # Keep the canonical `flowos-base` name; the exact `==<dev>` pin enables pre-release
    # resolution down the tree and keeps base in lockstep with the run.
    replacement = f'"flowos-base{extras}=={new_version}"'

    # Replace the matched pattern with the new one
    content = pattern.sub(replacement, content)
    filepath.write_text(content, encoding="utf-8")


def update_flowos_core_dep_in_base(pyproject_path: str, flowos_core_version: str) -> None:
    """Update the FLOWOS_CORE dependency in flowos-base pyproject.toml to use nightly version."""
    filepath = BASE_DIR / pyproject_path
    content = filepath.read_text(encoding="utf-8")

    # Updated pattern to handle PEP 440 version suffixes, both ~= and == version specifiers,
    # and both flowos_core and flowos_core-nightly names
    pattern = re.compile(r'("flowos_core(?:-nightly)?(?:~=|==)[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*")')
    # Pin base's flowos_core dep to the exact canonical dev version (single `flowos_core` distribution, no
    # `flowos_core-nightly`), so there is no `flowos_core` vs `flowos_core-nightly` install collision with the bundles.
    replacement = f'"flowos_core=={flowos_core_version}"'

    # Check if the pattern is found
    if not pattern.search(content):
        msg = f'FLOWOS_CORE dependency not found in "{filepath}"'
        raise ValueError(msg)

    # Replace the matched pattern with the new one
    content = pattern.sub(replacement, content)
    filepath.write_text(content, encoding="utf-8")


def verify_pep440(version):
    """Verify if version is PEP440 compliant.

    https://github.com/pypa/packaging/blob/16.7/packaging/version.py#L191
    """
    return packaging.version.Version(version)


def main() -> None:
    if len(sys.argv) != ARGUMENT_NUMBER:
        msg = "Usage: update_lf_base_dependency.py <base_version> <flowos_core_version>"
        raise ValueError(msg)
    base_version = sys.argv[1]
    flowos_core_version = sys.argv[2]

    # Strip "v" prefix from versions if present
    base_version = base_version.removeprefix("v")
    flowos_core_version = flowos_core_version.removeprefix("v")

    verify_pep440(base_version)
    verify_pep440(flowos_core_version)

    # Update flowos-base dependency in main project
    update_base_dep("pyproject.toml", base_version)

    # Update FLOWOS_CORE dependency in flowos-base
    update_flowos_core_dep_in_base("src/backend/base/pyproject.toml", flowos_core_version)


if __name__ == "__main__":
    main()
