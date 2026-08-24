"""Smoke tests: every flowos_core subcommand's --help must exit 0."""

from __future__ import annotations

import pytest
from flowos_core.__main__ import app
from typer.testing import CliRunner

runner = CliRunner()

ALL_SUBCOMMANDS = [
    "init",
    "login",
    "create",
    "requirements",
    "validate",
    "run",
    "serve",
    "status",
    "push",
    "pull",
    "export",
]


def test_root_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "flowos_core" in result.output.lower()


@pytest.mark.parametrize("cmd", ALL_SUBCOMMANDS)
def test_subcommand_help(cmd: str):
    result = runner.invoke(app, [cmd, "--help"])
    assert result.exit_code == 0, f"`flowos_core {cmd} --help` failed: {result.output}"
