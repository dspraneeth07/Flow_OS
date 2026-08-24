"""FLOWOS_CORE CLI entry point."""

from importlib.metadata import version as _pkg_version

import typer

from flowos_core.cli._authoring_commands import register as _register_authoring
from flowos_core.cli._extension_commands import register as _register_extension
from flowos_core.cli._remote_commands import register as _register_remote
from flowos_core.cli._running_commands import register as _register_running
from flowos_core.cli._setup_commands import register as _register_setup
from flowos_core.cli._upgrade_commands import register as _register_upgrade


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"flowos_core {_pkg_version('flowos_core')}")
        raise typer.Exit(0)


app = typer.Typer(
    name="flowos_core",
    help="flowos_core - FlowOS Executor",
    add_completion=False,
)


@app.callback()
def _app_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the flowos_core version and exit.",
        is_eager=True,
        callback=_version_callback,
    ),
) -> None:
    """FlowosCore - FlowOS Executor."""


# Register command groups (order determines help-panel ordering)
_register_setup(app)
_register_authoring(app)
_register_upgrade(app)
_register_extension(app)
_register_running(app)
_register_remote(app)


def main():
    """Main entry point for the FLOWOS_CORE CLI."""
    app()


if __name__ == "__main__":
    main()
