"""Dependency parsing tests."""

from __future__ import annotations

from reposage.pipeline import build_audit_report
from tests.conftest import fixture_path


def test_dependency_summary_covers_python_and_npm_manifests() -> None:
    report = build_audit_report(fixture_path("mixed_repo"))
    dependency_names = {dependency.name for dependency in report.dependencies.dependencies}

    assert report.dependencies.ecosystems == ["npm", "python"]
    assert "fastapi" in dependency_names
    assert "react" in dependency_names
    assert "mypy" in dependency_names


def test_framework_detection_uses_dependency_signals() -> None:
    report = build_audit_report(fixture_path("js_repo"))

    assert "Next.js" in report.inventory.frameworks
    assert "React" in report.inventory.frameworks
