# Changelog

All notable changes to this project are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Drawn architecture and flow figures in `docs/diagrams/`, light and dark, shown in the README.

## [0.1.0] - 2026-10-27

### Added

- `mathkit`, a small layered library (domain, application, infrastructure, interfaces) with arithmetic, statistics and a
  pandas-backed CSV summary, so the workflow has something real to build and test.
- `ci.yml`: lint, audit and a six-job test matrix (Python 3.10, 3.11, 3.12 on Ubuntu and Windows) with the pip cache keyed
  on the lock file, reports uploaded as artifacts also on failure with seven-day retention, a slowest-tests job summary,
  path filters for documentation-only changes and cancellation of stale runs on branches.
- `ci-docs-only.yml` and the `ci-ok` gate job, so a required check never stays pending.
- `measure-1-plain.yml`, `measure-2-matrix.yml` and `measure-3-cache.yml`, started by hand, and `pipeline/billing.py` to
  turn their runs into the README table.
- Hash-pinned universal lock files, every action pinned to a full commit SHA, Dependabot for actions and pip.
- Scripts under `pipeline/` with their own tests, a test file that asserts the lesson's review checklist against the
  workflow files, and an `act` runner image to run the main workflow locally.
