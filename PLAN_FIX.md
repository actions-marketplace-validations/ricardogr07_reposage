# PLAN_FIX.md — M0 QA Audit Report

**Auditor:** Senior QA / Ricardo García Ramírez  
**Date:** 2026-04-16  
**Verdict:** DO NOT MERGE. NOT SHIPPABLE.

---

## Executive Summary

This is not a bootstrap. This is a pile of untracked files dropped into a working directory
with zero git history, no branch, and no PR. Codex also completely ignored the milestone
boundary and shipped M1 (all of RS-010 through RS-017) and partial M2 (RS-020) inside what
was supposed to be a lean M0 scaffold. The phased delivery model described in PLAN.md is
already dead before a single commit exists.

To make it worse, the implementation has a data-integrity bug in the core inventory model,
the pytest configuration actively disables a safety fixture it later needs, the mypy gate is
configured weakly enough to be meaningless, test fixtures have tool-cache artifacts tracked
in git, and the `total_files` field in the primary data model is arithmetically incorrect
and therefore always wrong.

Every defect below has a specific file and line citation. Fix them in priority order.

---

## P0 — Blockers (Nothing ships until these are resolved)

---

### P0-1: Zero git commits. No branch. No PR.

**Promised (RS-003, PR strategy):**
> Branch: `chore/bootstrap-public-foundation`
> Open draft PRs early.
> Require `lint`, `type`, `py312`, and `pkg` checks before merge.

**Actual state:**
`git status` shows every single file as `??` (untracked). There are no commits. No branch
named `chore/bootstrap-public-foundation` or any other. No draft PR exists. CI cannot
validate what has never been pushed.

**Why it's insufficient:**
A "first pass at M0" that has no git history is not a first pass — it's a local spike.
The entire value of a bootstrap milestone is establishing a reproducible public baseline that
other contributors can branch from. That requires commits.

**Exact fix required:**
1. Stage and commit the scaffold files under `chore/bootstrap-public-foundation` as
   described in the PR strategy section of PLAN.md.
2. Push the branch and open a draft PR titled exactly as specified:
   `Bootstrap RepoSage public package foundation`.
3. Confirm CI green on `lint`, `type`, `py312`, and `pkg` before requesting review.

---

### P0-2: M0 scope completely ignored — M1 and partial M2 shipped without authorization.

**Promised (M0 = RS-001 through RS-005):**
M0 was supposed to deliver: package scaffold, shared models, tox/pytest/ruff/mypy baseline,
CI workflow, docs/README/license, and GitHub templates. That's it.

**Actual state:**
The repository contains the full M1 implementation:
- `src/reposage/scan/` — filesystem scanner (RS-010), language detection (RS-011),
  dependency parsing (RS-012)
- `src/reposage/analysis/` — quality heuristics (RS-013), architecture heuristics (RS-014),
  risk analysis (RS-014)
- `src/reposage/reports/` — Markdown and JSON rendering (RS-015, RS-016)
- `src/reposage/pipeline.py` + full CLI (`cli.py`) — end-to-end orchestration (RS-017)
- `tests/` with fixture-based integration tests (RS-017)
- `src/reposage/ai/enrichment.py`, `src/reposage/ai/prompts.py` — M2 scope (RS-020)

**Why it's insufficient:**
The milestone boundary exists for a reason. M0 is a CI-green, reviewable, mergeable
baseline that proves the toolchain works. Dumping the entire implementation into an
unreviewed, uncommitted pile violates the incremental delivery contract. If any of this
code has fundamental design flaws (and some do — see P0-3), there is now no clean
rollback point, no reviewed baseline, and no audit trail.

**Exact fix required:**
1. The M0 bootstrap commit should contain ONLY: `src/reposage/__init__.py`,
   `src/reposage/__main__.py`, `src/reposage/models.py`, `src/reposage/config.py`,
   a stub `src/reposage/cli.py` (entry point only, no scan logic), `pyproject.toml`,
   `tox.ini`, `.github/workflows/ci.yml`, `README.md`, `CONTRIBUTING.md`, `LICENSE`,
   `PLAN.md`, `.gitignore`, and the `.github/` templates.
2. M1 content belongs in follow-on PRs as specified:
   `feature/repo-inventory-scan-core`, `feature/quality-dependency-heuristics`,
   `feature/reporting-and-cli`.
3. The `src/reposage/ai/` package must not exist until M2 is started.

---

### P0-3: `total_files` in `RepoInventory` is arithmetically wrong.

**Promised (RS-001):**
A correct shared data model as the foundation for the pipeline.

**Actual state:**
`src/reposage/scan/repo_meta.py:48`:
```python
total_files=len(file_records) + len(ignored_directories),
```
`ignored_directories` is a list of directory *paths*, not file counts. A single
`node_modules` entry in that list represents one directory path but could contain 50,000
files. Adding a directory count to a file count produces a number that is meaningless and
always wrong the moment any ignored directory exists.

**Why it's insufficient:**
`total_files` is surfaced directly in the Markdown report under "Project Summary" and in
the JSON output. Any downstream consumer or human reader will see a wildly incorrect number
and either not notice (bad) or notice and lose confidence in everything else the tool
produces (worse).

**Exact fix required:**
Option A: Remove `total_files` from `RepoInventory` entirely. The model already has
`scanned_files`. A field that cannot be correctly populated without re-walking ignored
directories is worse than no field.

Option B: Rename the field to `scanned_files_count` and remove the misleading
`total_files` concept. Document in the model docstring that total count excluding ignored
content is not tracked.

Do not attempt to "fix" the arithmetic by keeping the field — the semantics are
fundamentally broken at the design level.

---

### P0-4: `-p no:tmpdir` in pytest config breaks test isolation.

**Promised (RS-002):**
A working pytest baseline.

**Actual state:**
`pyproject.toml:62`:
```
addopts = "... -p no:cacheprovider -p no:tmpdir"
```
The `tmpdir` plugin is explicitly disabled. `tmp_path` is unavailable. As a direct
consequence, `tests/test_scan.py:16-25` rolls its own temp directory:
```python
temp_root = Path(".reposage-test-artifacts") / f"scan-{uuid.uuid4().hex}"
try:
    ...
finally:
    shutil.rmtree(temp_root, ignore_errors=True)
```
This creates directories relative to the working directory at test runtime. If the test
process is killed mid-run, the `.reposage-test-artifacts/` tree accumulates indefinitely.

**Why it's insufficient:**
pytest's `tmp_path` fixture exists precisely to solve this problem. Disabling it and
reimplementing manual cleanup is an unforced error. The `-p no:tmpdir` flag achieves
nothing except breaking the standard fixture.

**Exact fix required:**
1. Remove `-p no:tmpdir` from `addopts` in `pyproject.toml`.
2. Refactor `tests/test_scan.py` to accept `tmp_path: Path` as a fixture parameter and
   use it instead of `Path(".reposage-test-artifacts") / ...`.
3. Remove `.reposage-test-artifacts/` from `.gitignore` (it was only needed as a workaround).

---

## P1 — Regressions and Missing Contract Items

---

### P1-1: `project-management.yml` is dead YAML. Labels and milestones do not exist.

**Promised (RS-005):**
> Add issue templates, PR template, label spec, and milestone spec.

**Actual state:**
`.github/project-management.yml` is a YAML file describing the labels and milestones. It is
not a GitHub Actions workflow. It has no `on:` trigger. No script reads it. No `gh` CLI
commands apply it. GitHub has no idea it exists. Labels and milestones are NOT created.

**Why it's insufficient:**
A spec YAML that nothing executes is documentation, not tooling. If a contributor opens an
issue and tries to apply the labels defined in PLAN.md, they do not exist. The RS-005
acceptance criterion is not met.

**Exact fix required:**
Create a one-time setup script (e.g., `scripts/setup_github.sh`) that uses `gh label create`
and `gh api` to create the labels and milestones from the spec. Document in `CONTRIBUTING.md`
that this script must be run once after repo creation. Alternatively, add a manually-triggered
GitHub Actions workflow (`workflow_dispatch`) that calls the GitHub API to create them.
The YAML spec alone is not a deliverable.

---

### P1-2: mypy configuration is too weak to be a quality gate.

**Promised (RS-002):**
> mypy ... baseline

**Actual state:**
`pyproject.toml:82-88` sets `check_untyped_defs = true` but NOT `disallow_untyped_defs =
true`. Without `disallow_untyped_defs`, mypy will cheerfully type-check annotated
functions but silently skip the bodies of unannotated ones. Adding an unannotated
function — even a large, complex one — passes the `tox -e type` gate with zero warnings.

**Why it's insufficient:**
A mypy config without `disallow_untyped_defs` is security theater. The gate produces a
green check while silently ignoring large swaths of code. This will cause real defects as
M1/M2 code is added, because contributors will assume the type gate is comprehensive.

**Exact fix required:**
Add to `[tool.mypy]` in `pyproject.toml`:
```toml
disallow_untyped_defs = true
disallow_incomplete_defs = true
```
Then verify `tox -e type` still passes. Fix any violations that surface.

---

### P1-3: `PACKAGE_NAME_PATTERN` regex produces garbage for URL and VCS requirements.

**Promised (RS-012, which is in fact M1):**
> Parse `pyproject.toml`, `requirements*.txt`, and `package.json` manifests.

**Actual state:**
`src/reposage/scan/dependencies.py:12`:
```python
PACKAGE_NAME_PATTERN = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*(.*)$")
```
The `_parse_requirements` function applies this regex to every non-comment,
non-`-r` requirements line. For a requirement like:
```
https://github.com/some/repo/archive/main.zip
git+https://github.com/org/pkg.git@main#egg=pkg
-e .
--hash=sha256:...
```
The regex will match `https` as the package name (for URL lines), `git` as the package
name (for VCS installs), and `-e` would have been caught by the `-r` prefix check except
it isn't — the code only skips lines starting with `-r`, not `-e`, `-c`, `--hash`, etc.

**Why it's insufficient:**
Any real-world Python repo that uses URL-based dependencies, editable installs, or hash-
pinned requirements will produce a corrupted `DependencySummary`. The tool claims to parse
these files but produces incorrect data silently.

**Exact fix required:**
In `_parse_requirements`, add a guard before calling `_parse_dependency_string`:
```python
if line.startswith(("-", "http://", "https://", "git+")):
    continue
```
Add a test fixture with a `requirements.txt` that contains URL and VCS entries and assert
they are ignored (not included as dependencies).

---

### P1-4: `_is_test_file` has no extension guard — non-test files are flagged as tests.

**Actual state:**
`src/reposage/analysis/tests.py:27`:
```python
return file_name.startswith("test_") or file_name.endswith(("_test.py", ".spec.ts", ".spec.js"))
```
The `startswith("test_")` branch has no extension check. Files like `test_data.csv`,
`test_fixtures.json`, `test_readme.md`, `test_output.txt` all match this predicate and
are counted as test files. On repos with fixture data files named this way, `has_tests`
flips to `True` and the quality score is inflated.

**Why it's insufficient:**
The quality score gates downstream risk analysis. A false positive on `has_tests` suppresses
the "Low regression confidence" HIGH risk item. This is a scoring correctness bug.

**Exact fix required:**
Add an extension allowlist to the filename check:
```python
TEST_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".rb", ".go", ".rs", ".java"}

def _is_test_file(path: str) -> bool:
    pure_path = PurePosixPath(path)
    if any(part.lower() in TEST_DIRECTORY_NAMES for part in pure_path.parts):
        return True
    file_name = pure_path.name.lower()
    ext = pure_path.suffix.lower()
    if ext not in TEST_EXTENSIONS:
        return False
    return file_name.startswith("test_") or file_name.endswith(("_test.py", ".spec.ts", ".spec.js"))
```
Add a test case with a fixture containing `test_data.csv` and assert it is NOT in the
test files list.

---

### P1-5: `LINT_FILE_NAMES` misses the entire ESLint v9 flat config format.

**Actual state:**
`src/reposage/analysis/quality.py:13`:
```python
LINT_FILE_NAMES = {".eslintrc", ".eslintrc.json", ".ruff.toml", "ruff.toml"}
```
ESLint v9 (released April 2024, now the default) uses `eslint.config.js`,
`eslint.config.mjs`, or `eslint.config.cjs`. ESLint v8 also supported `.eslintrc.js`,
`.eslintrc.cjs`, `.eslintrc.yaml`, `.eslintrc.yml` — none of which are in this set.
Any JS/TS repo using ESLint v8 or v9 with these file names will be reported as having
no lint configuration.

**Why it's insufficient:**
This is M1 scope, not M0 — but since it was shipped anyway, it needs to be correct. A tool
that claims to detect lint configuration and misses the dominant ESLint config format is
not credible.

**Exact fix required:**
```python
LINT_FILE_NAMES = {
    ".eslintrc",
    ".eslintrc.json",
    ".eslintrc.js",
    ".eslintrc.cjs",
    ".eslintrc.yaml",
    ".eslintrc.yml",
    "eslint.config.js",
    "eslint.config.mjs",
    "eslint.config.cjs",
    ".ruff.toml",
    "ruff.toml",
    ".flake8",
    ".pylintrc",
    "biome.json",
}
```
Add a fixture JS repo using `eslint.config.mjs` and assert lint is detected.

---

### P1-6: Fixture repos have committed `.ruff_cache` directories.

**Actual state:**
```
tests/fixtures/mixed_repo/.ruff_cache/0.15.7/...
tests/fixtures/python_repo/.ruff_cache/0.15.7/...
```
These are local tool cache artifacts that were committed into test fixture repositories.
They have no place in a test fixture. They bloat the repo (binary cache files) and they
create false-positive language detection signals (the cache files have their own extensions)
when RepoSage scans its own test fixtures.

**Why it's insufficient:**
RepoSage scans repos and counts files. If `scan_repository` is run against `mixed_repo`,
the `.ruff_cache` binary blobs will be counted before the ignore policy fires — and they
WILL be counted because the ignore policy only strips directories named `.ruff_cache` at
scan time, but those ignored paths add to `ignored_directories`, which then feeds the broken
`total_files` calculation. It's defect-on-defect.

**Exact fix required:**
1. Delete all `.ruff_cache/` directories from under `tests/fixtures/`.
2. Add `tests/fixtures/**/.ruff_cache/` to `.gitignore`.
3. Verify no other tool cache directories (`.mypy_cache`, `__pycache__`, `.pytest_cache`)
   exist in fixture repos — they do: `tests/fixtures/mixed_repo/tests/__pycache__/` is
   also committed.

---

### P1-7: `scan/dependencies.py` test coverage is 72% for critical parsing logic.

**Actual state:**
Coverage report output:
```
src\reposage\scan\dependencies.py   109     31    72%   37, 91-92, 107, 141-142,
                                                         156-174, 180-181, 210,
                                                         215, 236, 241, 244-247, 268-269, 279
```
Lines 156-174 are the entire `_parse_requirements` function body. Lines 91-92 and 107
are error handling paths in `_parse_pyproject`. The `_parse_package_json` error path
(180-181) is uncovered. These are the paths that fire on malformed or edge-case manifests.

**Why it's insufficient:**
For an extraction layer whose primary job is parsing manifests, 72% coverage means almost
a third of the parsing code paths have never been exercised by any test. This is where
bugs hide.

**Exact fix required:**
Add unit tests (not just pipeline integration tests) directly against the parsing functions:
- `test_parse_requirements_basic`: standard pinned and unpinned packages
- `test_parse_requirements_skips_comments_and_options`: `# comment`, `-r other.txt`,
  `-e .`, `--hash=...`
- `test_parse_pyproject_handles_decode_error`: pass a path to a non-TOML file
- `test_parse_package_json_handles_invalid_json`: pass a path to a file with `{broken`
- `test_parse_pyproject_poetry_groups`: a `pyproject.toml` with `[tool.poetry.group.dev]`

---

## P2 — Quality and Hygiene Issues

---

### P2-1: M2 stub code (`src/reposage/ai/`) shipped in M0 with 0% test coverage.

`src/reposage/ai/enrichment.py` and `src/reposage/ai/prompts.py` are M2 scope. They are
hollow stubs (7 lines of Protocol definition, 4 lines of prompt string). They are at 0%
coverage. They add nothing to M0 and their presence implies M2 is in progress when it isn't.
Delete the entire `src/reposage/ai/` package and restore it when M2 work begins.

---

### P2-2: `conftest.py` contains an unnecessary `sys.path` hack.

`tests/conftest.py:10-11` manually inserts `src/` into `sys.path`. This is unnecessary
because `tox.ini` uses `package = wheel`, which installs the package into the test
environment before tests run. The `sys.path` manipulation is a sign this was tested
outside of tox. Remove it and verify `tox -e py312` still passes without it.

---

### P2-3: CLI `scan` command is an undocumented alias for `report --format json`.

`cli.py:63-64`: the `scan` subcommand calls `render_json_report`. `report --format json`
also calls `render_json_report`. They are the same operation. The README only documents
`scan` without clarifying it is identical to `report --format json`. This will confuse users.
Either document the distinction clearly (there is none) or remove `scan` and keep only
`report --format json`.

---

### P2-4: `pyproject.toml` has a placeholder homepage URL.

`pyproject.toml:33`:
```toml
Homepage = "https://github.com/example/reposage"
```
`example/reposage` is a placeholder. Publishing this to PyPI as-is points users to a
non-existent repository. Replace with the actual repo URL before any release.

---

### P2-5: `analysis/risk.py` uses a hardcoded magic number not present in `ScanConfig`.

`analysis/risk.py:93`:
```python
if len(dependencies.dependencies) >= 25:
```
The threshold `25` is arbitrary and unexplained. `ScanConfig` already exists as the
correct place for tunable parameters. This threshold should be added to `ScanConfig` as
`dependency_count_risk_threshold: int = 25` and passed into `analyze_risk`.

---

### P2-6: No test covers the `--output` CLI flag.

`cli.py:74-76` implements writing output to a file path. No test exercises this code path.
The `cli.py` coverage shows lines 76 as uncovered. Add a test using `tmp_path` (once P0-4
is fixed) that calls `main(["report", str(path), "--output", str(tmp_path / "out.md")])`
and asserts the file was written with correct content.

---

### P2-7: `analysis/risk.py` leaves 18% of branches uncovered including the dep-risk path.

Coverage shows `src\reposage\analysis\risk.py 33 6 82% 55-71, 90-103`. Lines 55-71 and
90-103 correspond to the "No CI enforcement" risk item and "Dependency surface area is
growing" risk item respectively. These code paths exist but no fixture exercises them.
Add a `no_ci_repo` fixture and a `heavy_deps_repo` fixture (or parametrize `test_quality.py`)
to cover these branches.

---

## Remediation Checklist for Codex

Complete in this exact order. Do not proceed to the next item until the current one passes
`tox -e py312 && tox -e lint && tox -e type && tox -e pkg`.

- [ ] **P0-1**: Create initial commit on branch `chore/bootstrap-public-foundation` containing
      only M0 files. Push. Open draft PR.
- [ ] **P0-3**: Remove `total_files` from `RepoInventory` model and all call sites. Update
      Markdown and JSON report renderers. Update `test_reports.py`.
- [ ] **P0-4**: Remove `-p no:tmpdir` from `pyproject.toml`. Refactor `test_scan.py` to use
      `tmp_path` fixture.
- [ ] **P1-4**: Add extension guard to `_is_test_file`. Add negative test case.
- [ ] **P1-3**: Add prefix guards in `_parse_requirements` for URLs, VCS, and pip options.
      Add test fixture + test case.
- [ ] **P1-2**: Add `disallow_untyped_defs = true` and `disallow_incomplete_defs = true` to
      `[tool.mypy]`. Fix any new mypy violations.
- [ ] **P1-6**: Delete `.ruff_cache/` and `__pycache__/` from all fixture repos. Add
      `tests/fixtures/**/.ruff_cache/` and `tests/fixtures/**/__pycache__/` to `.gitignore`.
- [ ] **P1-5**: Expand `LINT_FILE_NAMES` to include ESLint v9 flat config formats and other
      missing linters.
- [ ] **P1-7**: Add direct unit tests for parsing functions in `scan/dependencies.py` to reach
      ≥95% coverage on that module.
- [ ] **P1-1**: Create `scripts/setup_github.sh` using `gh` CLI to apply labels and milestones.
      Document in `CONTRIBUTING.md`.
- [ ] **P2-1**: Delete `src/reposage/ai/` entirely.
- [ ] **P2-2**: Remove the `sys.path` hack from `tests/conftest.py`. Verify tox passes.
- [ ] **P2-4**: Replace placeholder `Homepage` URL in `pyproject.toml`.
- [ ] **P2-5**: Move the `25` threshold into `ScanConfig` and thread it into `analyze_risk`.
- [ ] **P2-6**: Add `--output` flag test using `tmp_path`.
- [ ] **P2-7**: Add fixtures/tests covering "No CI" and "Dependency surface area" risk paths.
- [ ] **P2-3**: Either remove `scan` subcommand or document its relationship to
      `report --format json`.
- [ ] Confirm `tox -e py312`, `tox -e lint`, `tox -e type`, `tox -e pkg` all green.
- [ ] Confirm coverage ≥ 90% on every non-stub module (target 95% on `scan/dependencies.py`).
- [ ] Push branch, open PR, verify CI passes.
