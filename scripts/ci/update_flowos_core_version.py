"""Update the canonical ``flowos_core`` package (and its SDK dep) for nightly builds.

The nightly publishes ``flowos_core`` and ``flowos-sdk`` under their CANONICAL names as ``.devN``
pre-releases -- it does NOT rename them to ``flowos_core-nightly`` / ``flowos-sdk-nightly``, and it does
NOT give the ``src/bundles/*`` packages their own nightly track. The stable ``flowos_core-*`` bundles
(pinning ``flowos_core>=X.Y.0,<(X+1).0.0``) then resolve against the single canonical ``flowos_core`` distribution,
so there is no ``flowos_core`` vs ``flowos_core-nightly`` install collision. See ``src/bundles/NIGHTLY.md``.

This script therefore only (a) sets ``flowos_core``'s version to the nightly ``.devN`` and (b) re-pins
flowos_core's ``flowos-sdk`` dependency to the exact canonical dev version.
"""

import re
import sys
from pathlib import Path

from update_pyproject_version import update_pyproject_version

# Add the current directory to the path so we can import the other scripts
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

BASE_DIR = Path(__file__).parent.parent.parent


def update_sdk_dependency_in_flowos_core(pyproject_path: str, sdk_version: str) -> None:
    """Pin flowos_core's ``flowos-sdk`` dependency to the exact canonical dev version.

    An exact ``==<dev>`` pin keeps the SDK in lockstep with the flowos_core built in the same run and,
    because it names a pre-release explicitly, enables pre-release resolution for ``flowos-sdk``
    down the dependency tree without requiring ``--pre``.
    """
    filepath = BASE_DIR / pyproject_path
    content = filepath.read_text(encoding="utf-8")

    pattern = re.compile(r'"flowos-sdk(?:-nightly)?(?:==|~=|>=)[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*"')
    replacement = f'"flowos-sdk=={sdk_version}"'

    if not pattern.search(content):
        msg = f"SDK dependency not found in {filepath}"
        raise ValueError(msg)

    content = pattern.sub(replacement, content)
    filepath.write_text(content, encoding="utf-8")


def update_flowos_core_for_nightly(flowos_core_tag: str, sdk_tag: str):
    """Update the canonical ``flowos_core`` package for a nightly build.

    Args:
        flowos_core_tag: The nightly tag for FLOWOS_CORE (e.g., "v1.11.0.dev0").
        sdk_tag: The nightly tag for the SDK (e.g., "v0.1.0.dev0").
    """
    flowos_core_pyproject_path = "src/flowos-core/pyproject.toml"

    # Set the version (strip 'v' prefix if present); the package keeps its canonical `flowos_core` name.
    version = flowos_core_tag.lstrip("v")
    update_pyproject_version(flowos_core_pyproject_path, version)

    # Re-pin flowos_core's SDK dependency to the exact canonical dev version.
    sdk_version = sdk_tag.lstrip("v")
    update_sdk_dependency_in_flowos_core(flowos_core_pyproject_path, sdk_version)

    print(f"Updated flowos_core to nightly version {version}")


def main():
    """Update FLOWOS_CORE for nightly builds.

    Usage:
    update_flowos_core_version.py <flowos_core_tag> <sdk_tag>
    """
    expected_args = 3
    if len(sys.argv) != expected_args:
        print("Usage: update_flowos_core_version.py <flowos_core_tag> <sdk_tag>")
        sys.exit(1)

    flowos_core_tag = sys.argv[1]
    sdk_tag = sys.argv[2]
    update_flowos_core_for_nightly(flowos_core_tag, sdk_tag)


if __name__ == "__main__":
    main()
