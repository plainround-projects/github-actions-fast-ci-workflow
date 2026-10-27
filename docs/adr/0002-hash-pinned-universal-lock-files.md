# 2. Hash-pinned, universal lock files compiled with uv

Status: accepted, 2026-10-27

## Context

The cache key is built from the lock file's hash, so the lock file must be one file that every matrix cell installs
(three Python versions on two systems) and that changes only when a dependency changes. A plain `pip freeze` is
specific to the machine that ran it: it would miss `colorama` on Windows and `tomli` before Python 3.11.

## Decision

`requirements.in` and `requirements-dev.in` list the direct dependencies with exact versions. `uv pip compile --universal
--generate-hashes --python-version 3.10` turns each into `requirements.txt` and `requirements-dev.txt`: one resolution
for every platform and Python the project supports, with environment markers and SHA-256 hashes. Every install uses
`pip install --require-hashes`. The matrix jobs install `requirements.txt` (runtime and test tools); the lint job
installs `requirements-dev.txt` (adds ruff, mypy, import-linter and pip-audit), and `pip-audit` checks it in CI.

## Alternatives considered

- **Unhashed pins.** Simpler, but a registry compromise or a re-uploaded file would install silently.
- **`uv sync` and `uv.lock`.** A better workflow, but the lesson is about `actions/setup-python`'s pip cache keyed on
  `requirements.txt`; `uv` is used only to compile.

## Consequences

- To change a dependency: edit the `.in` file, run the two `uv pip compile` commands in the README, commit the `.txt` files.
  The cache misses once, which is the proof that the key follows the lock file.
