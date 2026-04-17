"""Quality and risk heuristic tests."""

from __future__ import annotations

from reposage.pipeline import build_audit_report
from tests.conftest import fixture_path


def test_missing_signal_fixture_flags_quality_gaps() -> None:
    report = build_audit_report(fixture_path("missing_signals_repo"))

    assert report.quality.has_tests is False
    assert report.quality.ci_present is False
    assert report.quality.documentation_present is False
    assert any(
        item == "Automated tests were not detected." for item in report.quality.missing_signals
    )
    assert any(risk_item.title == "Low regression confidence" for risk_item in report.risk.items)


def test_monorepo_fixture_notes_multiple_manifest_roots() -> None:
    report = build_audit_report(fixture_path("monorepo_repo"))

    assert any("monorepo" in note.lower() for note in report.architecture.architecture_notes)
