# Contributing

## Expectations

- Prefer clarity, correctness, and maintainability over cleverness.
- Work within the existing architecture and coding conventions unless there is a
  strong reason to change them.
- Keep changes small, explicit, and reviewable.
- Preserve type safety, deliberate error handling, and deterministic behavior.

## Development workflow

1. Create a branch from `main`.
2. Keep scope tied to one issue whenever practical.
3. Install development dependencies with `uv sync --dev`.
4. Run `tox -e lint`, `tox -e type`, `tox -e py312`, and `tox -e pkg`.
5. Open a draft PR early if the work spans more than a small patch.

## Review standards

- Prefer straightforward logic over hidden magic.
- Avoid introducing optional abstraction layers before they are needed.
- Add or update tests when behavior changes.
- Document new user-facing behavior or workflow changes.

## Commit and PR guidance

- Use descriptive branch names such as `feature/reporting-and-cli`.
- Keep commits logically grouped by subsystem or behavior.
- Summarize intent, validation, and follow-up risks in the PR body.

