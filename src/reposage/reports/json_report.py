"""JSON rendering for RepoSage audits."""

from __future__ import annotations

import json

from reposage.models import AuditReport


def render_json_report(report: AuditReport) -> str:
    """Render the report as formatted JSON."""

    return json.dumps(report.to_dict(), indent=2, sort_keys=True)
