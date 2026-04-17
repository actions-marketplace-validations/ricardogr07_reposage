"""Filesystem scanning logic for RepoSage."""

from __future__ import annotations

import os
from pathlib import Path

from reposage.config import ScanConfig
from reposage.models import FileRecord


def scan_repository(root: Path, config: ScanConfig) -> tuple[list[FileRecord], list[str]]:
    """Collect file metadata for a repository root."""

    file_records: list[FileRecord] = []
    ignored_directories: set[str] = set()

    for current_root, dirnames, filenames in os.walk(root):
        current_path = Path(current_root)

        kept_directories: list[str] = []
        for dirname in sorted(dirnames):
            if dirname in config.ignored_directories:
                relative_dir = (current_path / dirname).relative_to(root).as_posix()
                ignored_directories.add(relative_dir)
                continue
            kept_directories.append(dirname)
        dirnames[:] = kept_directories

        for filename in sorted(filenames):
            path = current_path / filename
            if path.is_symlink() or not path.is_file():
                continue

            relative_path = path.relative_to(root).as_posix()
            stat_result = path.stat()
            file_records.append(
                FileRecord(
                    path=relative_path,
                    extension=path.suffix.lower() or None,
                    size_bytes=stat_result.st_size,
                    line_count=_count_lines(path),
                )
            )

    file_records.sort(key=lambda record: record.path)
    return file_records, sorted(ignored_directories)


def _count_lines(path: Path) -> int:
    """Count lines without assuming text encoding."""

    line_count = 0
    ends_with_newline = False
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 64), b""):
            line_count += chunk.count(b"\n")
            ends_with_newline = chunk.endswith(b"\n")
    if path.stat().st_size == 0:
        return 0
    return line_count if ends_with_newline else line_count + 1
