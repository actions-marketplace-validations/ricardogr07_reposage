# RepoSage

RepoSage is an AI-assisted repository analysis tool that produces a structured
technical audit of a codebase.

The emphasis is deterministic repo intelligence first, not an ungrounded
"chat with your repo" experience. The MVP scans a local repository, extracts
static signals engineers already care about, and turns those signals into a
Markdown or JSON audit report.

## Current MVP scope

- Local repository scanning
- Static file, manifest, and layout analysis
- Language and dependency summaries
- Tests, docs, CI, packaging, lint, and typing heuristics
- Architecture and hotspot guesses
- Markdown and JSON output
- Optional AI enrichment only after deterministic extraction

## Commands

```bash
reposage scan PATH
reposage report PATH --format markdown
reposage report PATH --format json
reposage run PATH
```

`scan` emits JSON to stdout by default. `report` supports explicit Markdown or
JSON output. `run` is a convenience alias for the human-readable Markdown
report.

## Development

RepoSage targets Python 3.12+ and uses Hatchling for packaging. The preferred
local workflow is `uv` for environment setup and `tox` for repeatable checks.

```bash
uv sync --dev
tox -e py312
tox -e lint
tox -e type
tox -e pkg
```

If `uv` is unavailable, install the development tools with your normal Python
environment manager or with `python -m pip install -e .[dev]`, then run the
same `tox` commands.

## Project documents

- [PLAN.md](PLAN.md): roadmap, issue backlog, PR strategy, and acceptance criteria
- [docs/architecture.md](docs/architecture.md): package and data-flow overview
- [docs/development.md](docs/development.md): contributor workflow and quality gates
- [CONTRIBUTING.md](CONTRIBUTING.md): contribution and review expectations

## Status

This repository contains the bootstrap baseline plus a deterministic Sprint 1
audit pipeline. AI enrichment remains optional and is intentionally separated
from the extraction layer.
