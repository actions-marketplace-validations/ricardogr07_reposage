"""Shared pytest helpers."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def fixture_path(name: str) -> Path:
    """Return the path to a named test fixture repository."""

    return PROJECT_ROOT / "tests" / "fixtures" / name
