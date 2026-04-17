"""Prompt-building helpers for future enrichment features."""

from __future__ import annotations

from reposage.models import AuditReport


def build_module_classification_prompt(report: AuditReport) -> str:
    """Return a conservative prompt scaffold for future enrichment work."""

    return (
        "Classify module responsibilities using only the provided deterministic "
        f"audit summary for project {report.inventory.project_name}."
    )
