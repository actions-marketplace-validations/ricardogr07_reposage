"""Markdown rendering for RepoSage audits."""

from __future__ import annotations

from reposage.models import AuditReport, Dependency, LanguageStat


def render_markdown_report(report: AuditReport) -> str:
    """Render a deterministic Markdown report."""

    inventory = report.inventory
    dependency_summary = report.dependencies
    quality = report.quality
    architecture = report.architecture
    risk = report.risk

    lines = [
        f"# RepoSage Audit: {inventory.project_name}",
        "",
        "## Project Summary",
        f"- Root path: `{inventory.root_path}`",
        f"- Scanned files: {inventory.scanned_files}",
        f"- Ignored directories: {_format_list(inventory.ignored_directories)}",
        f"- Top-level layout: {_format_list(inventory.top_level_entries)}",
        f"- Languages: {_format_languages(inventory.languages)}",
        f"- Framework signals: {_format_list(inventory.frameworks)}",
        f"- Dependency ecosystems: {_format_list(dependency_summary.ecosystems)}",
        f"- Dependency manifests: {_format_list(dependency_summary.manifests)}",
        "",
        "## Architecture Guess",
        f"- Main modules: {_format_list(architecture.main_modules)}",
        f"- Probable layers: {_format_list(architecture.probable_layers)}",
        f"- Dependency directions: {_format_list(architecture.dependency_directions)}",
        f"- Possible god modules: {_format_list(architecture.god_modules)}",
        f"- Hotspots: {_format_list(architecture.hotspots)}",
        f"- Notes: {_format_list(architecture.architecture_notes)}",
        "",
        "## Engineering Quality Checklist",
        f"- Quality score: {quality.score}/100",
        f"- Positive signals: {_format_list(quality.checklist)}",
        f"- Missing signals: {_format_list(quality.missing_signals)}",
        f"- Test files: {_format_list(quality.test_files)}",
        f"- CI files: {_format_list(quality.ci_files)}",
        f"- Docs files: {_format_list(quality.documentation_files)}",
        f"- Packaging files: {_format_list(quality.packaging_files)}",
        f"- Lint files: {_format_list(quality.lint_files)}",
        f"- Typing files: {_format_list(quality.typing_files)}",
        "",
        "## Risk Hotspots",
    ]

    for item in risk.items:
        lines.extend(
            [
                f"- [{item.severity}] {item.title}: {item.rationale}",
                f"  Suggested action: {item.suggested_action}",
            ]
        )

    lines.extend(
        [
            "",
            "## Recommended Next Issues",
            *[f"1. {suggestion}" for suggestion in risk.issue_suggestions],
            "",
            "## Dependency Summary",
            *[f"- {entry}" for entry in _format_dependencies(dependency_summary.dependencies[:15])],
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def _format_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _format_languages(values: list[LanguageStat]) -> str:
    if not values:
        return "none"
    return ", ".join(f"{item.language} ({item.file_count})" for item in values)


def _format_dependencies(values: list[Dependency]) -> list[str]:
    if not values:
        return ["none"]
    return [
        (
            f"{dependency.name} {dependency.version_spec} "
            f"[{dependency.ecosystem}/{dependency.group}] from {dependency.source_file}"
        )
        for dependency in values
    ]
