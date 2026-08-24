"""pytest plugin hooks, fixtures, and marker registration for flowos_core.testing."""

from __future__ import annotations

import contextlib
import os
from pathlib import Path
from typing import Any

try:
    import pytest
except ImportError as exc:
    msg = "pytest is required for flowos_core.testing. Install it with: pip install pytest  (or pip install 'flowos_core[dev]')"
    raise ImportError(msg) from exc

from flowos_core.testing.runners import (
    AsyncLocalFlowRunner,
    AsyncRemoteFlowRunner,
    LocalFlowRunner,
    RemoteFlowRunner,
)

# ---------------------------------------------------------------------------
# pytest plugin hooks
# ---------------------------------------------------------------------------


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register flowos_core-specific CLI options."""
    group = parser.getgroup("flowos_core", "flowos_core local flow execution options")
    group.addoption(
        "--flowos_core-env-file",
        dest="flowos_core_env_file",
        default=None,
        metavar="PATH",
        help="Path to a .env file loaded before each flow execution.",
    )
    group.addoption(
        "--flowos_core-timeout",
        dest="flowos_core_timeout",
        default=None,
        type=float,
        metavar="SECONDS",
        help="Default timeout in seconds for flow execution (0 = no limit).",
    )
    group.addoption(
        "--flowos_core-flow-dir",
        dest="flowos_core_flow_dir",
        default=None,
        metavar="DIR",
        help="Base directory for resolving relative flow paths (default: cwd).",
    )

    # Guard against duplicate registration when flowos-sdk[testing] is also installed.
    # Both plugins expose the same --flowos-* options; only register them once.
    remote = parser.getgroup("flowos", "FlowOS remote integration testing options")
    _remote_opts = {
        "--flowos-env": {
            "dest": "flowos_env",
            "default": None,
            "metavar": "NAME",
            "help": (
                "Named environment from .flowos_core/environments.yaml or flowos-environments.toml. "
                "When set, flow_runner targets the remote instance instead of running locally."
            ),
        },
        "--flowos-url": {
            "dest": "flowos_url",
            "default": None,
            "metavar": "URL",
            "help": "Base URL of the remote FlowOS instance (overrides --flowos-env).",
        },
        "--flowos-api-key": {
            "dest": "flowos_api_key",
            "default": None,
            "metavar": "KEY",
            "help": "API key for the remote FlowOS instance.",
        },
        "--flowos-environments-file": {
            "dest": "flowos_environments_file",
            "default": None,
            "metavar": "PATH",
            "help": "Path to environments config file (.yaml or .toml; overrides default lookup).",
        },
    }
    for flag, kwargs in _remote_opts.items():
        with contextlib.suppress(ValueError):
            remote.addoption(flag, **kwargs)


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers so pytest --strict-markers does not reject them."""
    config.addinivalue_line(
        "markers",
        "flowos_core_env_file(path): path to a .env file loaded before this test's flow execution",
    )
    config.addinivalue_line(
        "markers",
        "flowos_core_timeout(seconds): timeout in seconds for this test's flow execution",
    )
    config.addinivalue_line(
        "markers",
        "integration: integration test that requires a live FlowOS instance",
    )


_SKIP_NO_REMOTE = (
    "No remote FlowOS connection configured. "
    "Pass --flowos-url <URL> or --flowos-env <NAME> to run against a live instance."
)


def _resolve_remote_client(request: pytest.FixtureRequest) -> Any | None:
    """Return a sync SDK client if remote options are configured, else ``None``.

    Priority:
    1. ``--flowos-url`` / ``FLOWOS_URL`` -- direct URL (with optional ``--flowos-api-key``)
    2. ``--flowos-env`` / ``FLOWOS_ENV`` -- named environment from TOML/YAML file
    """
    url: str | None = request.config.getoption("flowos_url", default=None) or os.environ.get("FLOWOS_URL")
    env_name: str | None = request.config.getoption("flowos_env", default=None) or os.environ.get("FLOWOS_ENV")

    if not url and not env_name:
        return None

    try:
        import flowos_sdk  # type: ignore[import-untyped]
    except ImportError:
        pytest.skip("flowos-sdk is required for remote testing. Install: pip install flowos-sdk")

    if url:
        api_key: str | None = request.config.getoption("flowos_api_key", default=None) or os.environ.get(
            "FLOWOS_API_KEY"
        )
        return flowos_sdk.Client(base_url=url, api_key=api_key)

    # Named environment
    env_file: str | None = request.config.getoption("flowos_environments_file", default=None) or os.environ.get(
        "FLOWOS_ENVIRONMENTS_FILE"
    )
    try:
        from pathlib import Path as _Path

        from flowos_sdk.environments import get_client  # type: ignore[import-untyped]

        return get_client(env_name, config_file=_Path(env_file) if env_file else None)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Could not configure FlowOS environment {env_name!r}: {exc}")


def _resolve_async_remote_client(request: pytest.FixtureRequest) -> Any | None:
    """Return an async SDK client if remote options are configured, else ``None``."""
    url: str | None = request.config.getoption("flowos_url", default=None) or os.environ.get("FLOWOS_URL")
    env_name: str | None = request.config.getoption("flowos_env", default=None) or os.environ.get("FLOWOS_ENV")

    if not url and not env_name:
        return None

    try:
        import flowos_sdk  # type: ignore[import-untyped]
    except ImportError:
        pytest.skip("flowos-sdk is required for remote testing. Install: pip install flowos-sdk")

    if url:
        api_key: str | None = request.config.getoption("flowos_api_key", default=None) or os.environ.get(
            "FLOWOS_API_KEY"
        )
        return flowos_sdk.AsyncClient(base_url=url, api_key=api_key)

    env_file: str | None = request.config.getoption("flowos_environments_file", default=None) or os.environ.get(
        "FLOWOS_ENVIRONMENTS_FILE"
    )
    try:
        from pathlib import Path as _Path

        from flowos_sdk.environments import get_async_client  # type: ignore[import-untyped]

        return get_async_client(env_name, config_file=_Path(env_file) if env_file else None)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Could not configure FlowOS environment {env_name!r}: {exc}")


def _get_marker_arg(request: pytest.FixtureRequest, name: str) -> Any:
    """Return the first positional argument of marker *name*, or ``None``."""
    marker = request.node.get_closest_marker(name)
    return marker.args[0] if marker and marker.args else None


def _resolve_runner_config(
    request: pytest.FixtureRequest,
) -> tuple[str | None, float | None, Path | None]:
    """Return ``(env_file, timeout, base_dir)`` with marker > CLI > env-var precedence."""
    # env_file: marker > --flowos_core-env-file > FLOWOS_ENV_FILE
    env_file: str | None = (
        _get_marker_arg(request, "flowos_core_env_file")
        or request.config.getoption("flowos_core_env_file", default=None)
        or os.environ.get("FLOWOS_ENV_FILE")
    )

    # timeout: marker > --flowos_core-timeout > FLOWOS_TIMEOUT
    timeout: float | None = _get_marker_arg(request, "flowos_core_timeout")
    if timeout is None:
        raw_t = request.config.getoption("flowos_core_timeout", default=None) or os.environ.get("FLOWOS_TIMEOUT")
        if raw_t is not None:
            with contextlib.suppress(TypeError, ValueError):
                timeout = float(raw_t)

    # base_dir: --flowos_core-flow-dir > FLOWOS_FLOW_DIR > None (defaults to cwd in runner)
    dir_str: str | None = request.config.getoption("flowos_core_flow_dir", default=None) or os.environ.get("FLOWOS_FLOW_DIR")
    base_dir: Path | None = Path(dir_str) if dir_str else None

    return env_file, timeout, base_dir


@pytest.fixture
def flow_runner(
    request: pytest.FixtureRequest,
) -> LocalFlowRunner | RemoteFlowRunner:
    """Fixture providing a sync flow runner -- local or remote depending on CLI options.

    **Local mode** (default)
        Runs the flow in-process.  Configure with:

        * ``@pytest.mark.flowos_core_env_file(path)`` / ``@pytest.mark.flowos_core_timeout(seconds)``
        * ``--flowos_core-env-file`` / ``--flowos_core-timeout`` / ``--flowos_core-flow-dir``
        * ``FLOWOS_ENV_FILE`` / ``FLOWOS_TIMEOUT`` / ``FLOWOS_FLOW_DIR``

    **Remote mode** (when ``--flowos-env`` or ``--flowos-url`` is supplied)
        Calls the live FlowOS API.  Requires ``flowos-sdk``.

        * ``--flowos-env <NAME>`` -- named environment from ``.flowos_core/environments.yaml``
        * ``--flowos-url <URL>`` -- direct URL
        * ``--flowos-api-key <KEY>`` / ``FLOWOS_API_KEY``
        * ``--flowos-environments-file <PATH>`` / ``FLOWOS_ENVIRONMENTS_FILE``
        * ``FLOWOS_ENV`` / ``FLOWOS_URL``

    Example (local)::

        def test_greeting(flow_runner):
            result = flow_runner("flows/greeting.json", input_value="Hello")
            assert result.ok

    Example (remote -- run with ``pytest --flowos-env staging``)::

        @pytest.mark.integration
        def test_greeting(flow_runner):
            result = flow_runner("greeting-endpoint", "Hello!")
            assert result.first_text_output() is not None
    """
    client = _resolve_remote_client(request)
    if client is not None:
        return RemoteFlowRunner(client)

    env_file, timeout, base_dir = _resolve_runner_config(request)
    return LocalFlowRunner(
        default_env_file=env_file,
        default_timeout=timeout,
        base_dir=base_dir,
    )


@pytest.fixture
def async_flow_runner(
    request: pytest.FixtureRequest,
) -> AsyncLocalFlowRunner | AsyncRemoteFlowRunner:
    """Fixture providing an async flow runner -- local or remote depending on CLI options.

    Same mode-selection logic as :func:`flow_runner`.

    Example (local)::

        async def test_greeting(async_flow_runner):
            result = await async_flow_runner("flows/greeting.json", input_value="Hi")
            assert result.ok

    Example (remote)::

        @pytest.mark.integration
        async def test_greeting(async_flow_runner):
            result = await async_flow_runner("greeting-endpoint", "Hi!")
            assert result.first_text_output() is not None
    """
    client = _resolve_async_remote_client(request)
    if client is not None:
        return AsyncRemoteFlowRunner(client)

    env_file, timeout, base_dir = _resolve_runner_config(request)
    return AsyncLocalFlowRunner(
        default_env_file=env_file,
        default_timeout=timeout,
        base_dir=base_dir,
    )
