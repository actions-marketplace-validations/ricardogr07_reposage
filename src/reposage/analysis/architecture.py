"""Best-effort architecture summary heuristics."""

from __future__ import annotations

from collections import Counter
from pathlib import PurePosixPath

from reposage.models import ArchitectureSummary, FileRecord


def analyze_architecture(
    *,
    file_records: list[FileRecord],
    top_level_entries: list[str],
    manifest_paths: list[str],
    max_hotspots: int,
) -> ArchitectureSummary:
    """Infer high-level structure from file layout and file sizes."""

    module_counts = Counter(_module_name(record.path) for record in file_records)
    main_modules = [
        module_name
        for module_name, _count in sorted(
            module_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:5]
    ]

    probable_layers = _infer_layers(top_level_entries)
    dependency_directions = _infer_dependency_directions(top_level_entries)

    sorted_by_size = sorted(
        file_records,
        key=lambda record: (-record.line_count, -record.size_bytes, record.path),
    )
    god_modules = [
        f"{record.path} ({record.line_count} lines)"
        for record in sorted_by_size
        if record.line_count >= 200
    ][:max_hotspots]
    hotspots = [
        f"{record.path} ({record.size_bytes} bytes, {record.line_count} lines)"
        for record in sorted_by_size[:max_hotspots]
    ]

    notes: list[str] = []
    manifest_roots = {
        str(PurePosixPath(manifest_path).parent)
        for manifest_path in manifest_paths
        if PurePosixPath(manifest_path).parent != PurePosixPath(".")
    }
    if len(manifest_roots) > 1:
        notes.append("Multiple manifest roots detected; monorepo behavior is likely.")
    if any(entry.startswith("src/") for entry in top_level_entries):
        notes.append("Source code appears separated from tests/docs via a src-style layout.")
    if not notes:
        notes.append("Architecture appears relatively flat; deeper module boundaries are limited.")

    return ArchitectureSummary(
        main_modules=main_modules,
        probable_layers=probable_layers,
        dependency_directions=dependency_directions,
        god_modules=god_modules,
        hotspots=hotspots,
        architecture_notes=notes,
    )


def _module_name(path: str) -> str:
    parts = PurePosixPath(path).parts
    if len(parts) >= 2 and parts[0] in {"src", "app", "apps", "packages"}:
        return f"{parts[0]}/{parts[1]}"
    return parts[0] if parts else path


def _infer_layers(top_level_entries: list[str]) -> list[str]:
    layers: list[str] = []
    if any(entry.startswith("src/") or entry in {"src", "app"} for entry in top_level_entries):
        layers.append("application source")
    if "tests" in top_level_entries:
        layers.append("automated tests")
    if "docs" in top_level_entries:
        layers.append("documentation")
    if ".github" in top_level_entries:
        layers.append("automation")
    if "examples" in top_level_entries:
        layers.append("examples")
    if not layers:
        layers.append("flat repository layout")
    return layers


def _infer_dependency_directions(top_level_entries: list[str]) -> list[str]:
    directions: list[str] = []
    if any(entry.startswith("src/") or entry in {"src", "app"} for entry in top_level_entries) and (
        "tests" in top_level_entries
    ):
        directions.append("tests likely depend on source modules, not the reverse")
    if "docs" in top_level_entries:
        directions.append("documentation appears separate from runtime code")
    if ".github" in top_level_entries:
        directions.append("automation configuration is isolated from product code")
    if not directions:
        directions.append("dependency direction is ambiguous from top-level layout alone")
    return directions
