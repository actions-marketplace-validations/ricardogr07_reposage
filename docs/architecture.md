# Architecture Overview

RepoSage is organized as a deterministic extraction pipeline with optional AI
enrichment layered on top.

## Package layout

- `reposage.scan`: filesystem traversal, language detection, dependency parsing,
  and repo metadata extraction
- `reposage.analysis`: quality heuristics, architecture guesses, and risk
  synthesis
- `reposage.reports`: Markdown and JSON serialization of the shared audit model
- `reposage.ai`: future enrichment prompts and provider boundary
- `reposage.cli`: command-line interface for scan, report, and run workflows

## Data flow

1. The scanner walks the repository using a stable ignore policy.
2. Language and manifest parsers extract inventory and dependency signals.
3. Analysis modules derive quality, architecture, and risk observations.
4. Reporters render Markdown or JSON from the same `AuditReport` dataclass tree.
5. Optional AI enrichment can add classifications later without replacing the
   deterministic extraction layer.

## Design constraints

- Deterministic outputs should stay stable across runs of the same repository.
- Heuristics should be explicit and easy to inspect.
- The shared data model should minimize loose dictionaries crossing module
  boundaries.

