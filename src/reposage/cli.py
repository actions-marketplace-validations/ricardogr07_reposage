"""Command-line interface for RepoSage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reposage.pipeline import build_audit_report
from reposage.reports.json_report import render_json_report
from reposage.reports.markdown import render_markdown_report


def build_parser() -> argparse.ArgumentParser:
    """Construct the RepoSage CLI parser."""

    parser = argparse.ArgumentParser(
        prog="reposage",
        description="Generate deterministic repository audits.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="Render a repository report.")
    report_parser.add_argument("path", help="Path to the repository to analyze.")
    report_parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    report_parser.add_argument("--output", help="Optional path for report output.")

    run_parser = subparsers.add_parser(
        "run",
        help="Run the default human-readable audit workflow.",
    )
    run_parser.add_argument("path", help="Path to the repository to analyze.")
    run_parser.add_argument("--output", help="Optional path for Markdown output.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)
    target_path = Path(args.path)

    if not target_path.exists():
        print(f"error: path does not exist: {target_path}", file=sys.stderr)
        return 2
    if not target_path.is_dir():
        print(f"error: path is not a directory: {target_path}", file=sys.stderr)
        return 2

    report = build_audit_report(target_path)

    if args.command == "report":
        output = (
            render_markdown_report(report)
            if args.format == "markdown"
            else render_json_report(report)
        )
    else:
        output = render_markdown_report(report)

    output_path = getattr(args, "output", None)
    if output_path:
        Path(output_path).write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0
