# Development Guide

## Tooling baseline

- Python 3.12+
- Hatchling build backend
- `tox` as the canonical validation runner
- `uv` as the preferred local dependency manager
- Ruff for lint and formatting checks
- mypy for static types
- pytest for unit and integration tests

## Common commands

```bash
uv sync --dev
tox -e lint
tox -e type
tox -e py312
tox -e pkg
```

## Testing strategy

- Unit tests cover parsing logic, ignore rules, and heuristic scoring.
- Fixture-based integration tests cover Python, JS/TS, mixed-language, and
  low-signal repositories.
- Output tests should verify deterministic Markdown sections and JSON shape.

## Branch protection contract

`main` should require these checks before merge:

- `lint`
- `type`
- `py312`
- `pkg`

