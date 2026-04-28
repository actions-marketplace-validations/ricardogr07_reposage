"""Tests for M12 Rust language support."""

from __future__ import annotations

from pathlib import Path

from reposage.pipeline import build_audit_report
from reposage.scan._dep_parsers import _parse_cargo_toml
from reposage.scan.dependencies import _is_supported_manifest
from tests.conftest import fixture_path

# --- Cargo.toml parser ---


def test_cargo_toml_runtime_deps() -> None:
    deps = _parse_cargo_toml(fixture_path("rust_repo") / "Cargo.toml", "Cargo.toml")
    names = {d.name for d in deps}
    assert "tokio" in names
    assert "axum" in names
    assert "serde" in names
    for d in deps:
        if d.name in {"tokio", "axum", "serde"}:
            assert d.group == "runtime"


def test_cargo_toml_dev_deps() -> None:
    deps = _parse_cargo_toml(fixture_path("rust_repo") / "Cargo.toml", "Cargo.toml")
    dev = [d for d in deps if d.name == "tokio-test"]
    assert len(dev) == 1
    assert dev[0].group == "dev"


def test_cargo_toml_git_dep() -> None:
    deps = _parse_cargo_toml(fixture_path("rust_repo") / "Cargo.toml", "Cargo.toml")
    sqlx = next(d for d in deps if d.name == "sqlx")
    assert sqlx.version_spec == "*"


def test_cargo_toml_ecosystem() -> None:
    deps = _parse_cargo_toml(fixture_path("rust_repo") / "Cargo.toml", "Cargo.toml")
    assert deps
    assert all(d.ecosystem == "cargo" for d in deps)


def test_cargo_toml_build_deps(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname = "x"\nversion = "0.1.0"\nedition = "2021"\n'
        '[build-dependencies]\ncc = "1.0"\n',
        encoding="utf-8",
    )
    deps = _parse_cargo_toml(tmp_path / "Cargo.toml", "Cargo.toml")
    assert any(d.name == "cc" and d.group == "build" for d in deps)


def test_cargo_toml_path_dep(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname = "x"\nversion = "0.1.0"\nedition = "2021"\n'
        '[dependencies]\nmy-lib = { path = "../my-lib" }\n',
        encoding="utf-8",
    )
    deps = _parse_cargo_toml(tmp_path / "Cargo.toml", "Cargo.toml")
    assert any(d.name == "my-lib" and d.version_spec == "*" for d in deps)


def test_cargo_toml_disabled_dep(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname = "x"\nversion = "0.1.0"\nedition = "2021"\n'
        '[dependencies]\nreal-dep = "1.0"\nserde = false\n',
        encoding="utf-8",
    )
    deps = _parse_cargo_toml(tmp_path / "Cargo.toml", "Cargo.toml")
    names = [d.name for d in deps]
    assert "serde" not in names
    assert "real-dep" in names


def test_cargo_toml_workspace_only_returns_empty(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[workspace]\nmembers = ["crate-a", "crate-b"]\n',
        encoding="utf-8",
    )
    deps = _parse_cargo_toml(tmp_path / "Cargo.toml", "Cargo.toml")
    assert deps == []


def test_cargo_toml_workspace_deps(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[workspace]\nmembers = ["crate-a"]\n[workspace.dependencies]\ntokio = "1"\n',
        encoding="utf-8",
    )
    deps = _parse_cargo_toml(tmp_path / "Cargo.toml", "Cargo.toml")
    assert any(d.name == "tokio" and d.group == "runtime" for d in deps)


def test_cargo_toml_invalid(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[[invalid\ntoml = ][[\n", encoding="utf-8")
    result = _parse_cargo_toml(tmp_path / "Cargo.toml", "Cargo.toml")
    assert result == []


# --- manifest detection ---


def test_is_supported_manifest_case_sensitive() -> None:
    assert _is_supported_manifest("Cargo.toml") is True
    assert _is_supported_manifest("cargo.toml") is False
    assert _is_supported_manifest("pyproject.toml") is True
    assert _is_supported_manifest("package.json") is True


# --- pipeline integration ---


def test_rust_language_detected() -> None:
    report = build_audit_report(fixture_path("rust_repo"))
    language_names = [ls.language for ls in report.inventory.languages]
    assert "Rust" in language_names


def test_rust_framework_detection() -> None:
    report = build_audit_report(fixture_path("rust_repo"))
    frameworks = report.inventory.frameworks
    assert "Axum" in frameworks
    assert "SQLx" in frameworks
    assert "Serde" not in frameworks
    assert "Tokio" not in frameworks


def test_rust_test_detection() -> None:
    report = build_audit_report(fixture_path("rust_repo"))
    assert report.quality.has_tests is True


def test_rust_typing_present() -> None:
    report = build_audit_report(fixture_path("rust_repo"))
    assert report.quality.typing_present is True
