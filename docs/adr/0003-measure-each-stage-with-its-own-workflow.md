# 3. Measure each stage with its own workflow

Status: accepted, 2026-10-27

## Context

The lesson asks for a table of wall time and billable minutes for four stages: plain, matrix, matrix with cache, and the
full workflow. Measuring them by editing `ci.yml` and pushing three commits per stage mixes the stages in the history
and makes a re-measurement a chore.

## Decision

Three workflows that run only on `workflow_dispatch` hold the first three stages: `measure-1-plain.yml`,
`measure-2-matrix.yml`, `measure-3-cache.yml`. The fourth stage is `ci.yml` itself. Each measurement workflow is started
three times with `gh workflow run`; `make measure` fetches the jobs of the runs from the API and
`pipeline/billing.py` turns them into the table row (each job rounded up to a whole minute, Windows counted twice, macOS
ten times, the median of the runs). The same commit is measured at every stage, so the difference is the workflow.

## Alternatives considered

- **One workflow edited per stage.** Matches the lesson's narrative, but mixes stages in the history.
- **Reading the billing page.** Aggregated by day, so it cannot separate stages run on the same day.

## Consequences

- The three measurement workflows duplicate most of `ci.yml`. That is deliberate: they are the "before" versions.
- Numbers come from GitHub-hosted runners, so they can only be produced after the first push; the repository ships the
  tool and a fixture-based worked example, not invented numbers.
