"""Provider-agnostic interface for optional AI enrichment."""

from __future__ import annotations

from typing import Protocol

from reposage.models import AuditReport


class EnrichmentProvider(Protocol):
    """Interface for optional report enrichment providers."""

    def enrich(self, report: AuditReport) -> dict[str, object]:
        """Return enrichment fields derived from an audit report."""


def enrich_report(report: AuditReport, provider: EnrichmentProvider) -> dict[str, object]:
    """Delegate enrichment to a configured provider."""

    return provider.enrich(report)
