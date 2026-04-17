"""Filesystem and language detection tests."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from reposage.config import DEFAULT_SCAN_CONFIG
from reposage.pipeline import build_audit_report
from reposage.scan.filesystem import scan_repository
from tests.conftest import fixture_path


def test_scan_repository_ignores_configured_directories() -> None:
    temp_root = Path(".reposage-test-artifacts") / f"scan-{uuid.uuid4().hex}"
    try:
        (temp_root / "src").mkdir(parents=True)
        (temp_root / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
        (temp_root / "node_modules").mkdir()
        (temp_root / "node_modules" / "index.js").write_text("export {};\n", encoding="utf-8")

        records, ignored = scan_repository(temp_root, DEFAULT_SCAN_CONFIG)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    assert [record.path for record in records] == ["src/app.py"]
    assert ignored == ["node_modules"]


def test_detect_languages_in_mixed_fixture() -> None:
    report = build_audit_report(fixture_path("mixed_repo"))
    languages = {language.language for language in report.inventory.languages}

    assert "Python" in languages
    assert "React TSX" in languages
    assert "TOML" in languages
