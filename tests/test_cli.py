"""CLI integration tests."""

from __future__ import annotations

from reposage.cli import main
from tests.conftest import fixture_path


def test_cli_report_command_emits_markdown(capsys) -> None:
    exit_code = main(["report", str(fixture_path("python_repo")), "--format", "markdown"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "RepoSage Audit: python_repo" in captured.out


def test_cli_scan_command_emits_json(capsys) -> None:
    exit_code = main(["scan", str(fixture_path("python_repo"))])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"project_name": "python_repo"' in captured.out


def test_cli_returns_error_for_missing_path(capsys) -> None:
    exit_code = main(["run", "missing-path"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "path does not exist" in captured.err
