"""Filesystem and language detection tests."""

from __future__ import annotations

from pathlib import Path

from reposage.config import DEFAULT_SCAN_CONFIG
from reposage.pipeline import build_audit_report
from reposage.scan.filesystem import scan_repository
from tests.conftest import fixture_path


def test_scan_repository_ignores_configured_directories(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "index.js").write_text("export {};\n", encoding="utf-8")

    records, ignored = scan_repository(tmp_path, DEFAULT_SCAN_CONFIG)

    assert [record.path for record in records] == ["src/app.py"]
    assert ignored == ["node_modules"]


def test_detect_languages_in_mixed_fixture() -> None:
    report = build_audit_report(fixture_path("mixed_repo"))
    languages = {language.language for language in report.inventory.languages}

    assert "Python" in languages
    assert "React TSX" in languages
    assert "TOML" in languages
