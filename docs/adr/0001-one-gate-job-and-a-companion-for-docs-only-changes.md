# 1. One gate job to require, and a companion workflow for documentation-only changes

Status: accepted, 2026-10-27

## Context

The lesson skips the workflow for documentation-only changes with `paths-ignore`. A workflow that is skipped by a path
filter reports no check at all, so a required check from it stays "pending" and a documentation pull request can never
merge. The lesson offers two ways out: do not require the check, or add a small job that reports the same name.
Separately, six matrix names (`test (ubuntu-latest, 3.12)` and so on) are fragile to require: add a Python version and
the required list is out of date.

## Decision

- `ci.yml` has one final job, `ci-ok`, that `needs` every other job, runs with `if: always()` and fails when any of them
  failed or was cancelled (`pipeline/gate.py`, unit-tested). `ci-ok` is the only check required for `main`.
- `ci-docs-only.yml` starts on the inverse filter (`paths: docs/**, **.md`) and has one job, also named `ci-ok`, that
  succeeds. A documentation-only pull request therefore gets a green `ci-ok` and starts no test jobs.
- `tests/pipeline/test_workflows.py` asserts that both jobs have the same name and that the two filters are inverses on
  sample changes (using `pipeline/pathfilter.py`, a model of GitHub's glob syntax).

## Alternatives considered

- **Not requiring the check.** Simple, but then nothing stops a red pull request from merging.
- **No path filter; a `changes` job decides and every job has `if:`.** One workflow, one `ci-ok`, no duplicates. It starts a
  run (two small jobs) even for documentation, and the lesson asks for no run at all. This is the fallback below.
- **Requiring the six matrix names.** Breaks when the matrix changes.

## Consequences

- A change that mixes documentation and code starts both workflows. Both report a check named `ci-ok`; the companion's
  is a no-op and the real one decides. The repository's ruleset should treat a failure of either as blocking. This was
  not testable without a GitHub repository: open a throwaway pull request with a deliberately failing test plus a
  documentation change and confirm that merging is blocked. If it merges, switch to the second alternative.
- Skipped jobs count as passing in the gate (`skipped` is accepted), so a deliberately skipped job never blocks a merge.
