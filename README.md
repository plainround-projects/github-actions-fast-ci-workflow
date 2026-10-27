# github-actions-fast-ci-workflow

A fast GitHub Actions CI workflow for a small Python library: it tests on three Python versions and two operating systems, caches dependencies by the lock file's hash, keeps test reports as artifacts even on failure, skips documentation-only changes, cancels runs that a newer commit made stale, and comes with the tools to measure what each change saves in minutes.

| | |
| --- | --- |
| **Lesson** | `/prep/github-actions/project-fast-ci-workflow`, "A fast CI workflow with a matrix, a cache and measured savings" (`data-structure-explainer/src/content/tracks/github-actions/13-project-fast-ci-workflow.md` in the Plainround app) |
| **Planned hours** | 4 |
| **Level** | Beginner |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md), decisions in [docs/adr](docs/adr) |
| **Technology notes** | [tech/README.md](tech/README.md): one beginner-level note for every technology used here |

## Prerequisites

| Tool | Version | Used for |
| --- | --- | --- |
| Python | 3.10 to 3.13 (tested locally with 3.13; the CI matrix uses 3.10, 3.11 and 3.12) | the library, the scripts and the tests |
| GNU Make | 3.81 or newer (the one on macOS works) | every command below |
| [act](https://github.com/nektos/act) | 0.2.89 (`brew install act`) | running the workflow locally |
| Docker | 24 or newer, Apple silicon or x86 | act's runner container, built from [ci/act-runner/Dockerfile](ci/act-runner/Dockerfile) (Ubuntu 24.04 with Node, git, jq and python3) |
| [actionlint](https://github.com/rhysd/actionlint) and shellcheck | 1.7.12 and 0.11 (`brew install actionlint shellcheck`) | linting the workflows and the shell scripts |
| [uv](https://docs.astral.sh/uv/) | any recent (only for `make matrix-local` and to recompile the lock files) | the three-version test run and `uv pip compile` |
| `gh` CLI and a GitHub account | only for the parts that need GitHub: `make measure`, `scripts/protect-main.sh` | measuring real runs, requiring the check |

No cloud account and no secrets. Python packages are pinned with hashes in `requirements.txt` (what the matrix jobs install) and `requirements-dev.txt` (adds ruff, mypy, import-linter and pip-audit); `make` installs the second into `.venv/`.

## Setup, run, test, stop

```bash
make up                 # create .venv from the hash-pinned lock file and build the act runner image
make test               # all tests with coverage (library, adapter, command line, pipeline scripts, workflow checks)
make lint               # ruff, format check, mypy, import-linter, actionlint, shellcheck, pin check
make audit              # known-vulnerability check of the locked dependencies
make run                # ci.yml on this machine with act: the three Ubuntu legs of the matrix
make run-fail           # the same with Python 3.10 failing on purpose: one red job, two green, reports kept
make matrix-local       # the tests on Python 3.10, 3.11 and 3.12 in throwaway environments (uv)
make measure STAGE="1 plain (1 job)" RUNS="111 112 113"   # a README table row from three real run ids (gh)
make down               # remove leftover act containers
```

`make help` lists every target. `make lint` and `make test` need only Python; `make run` needs Docker and act.

What `make test` ends with (counts may grow; the gate is 95% coverage):

```text
Required test coverage of 95% reached. Total coverage: 96.84%
======================== 90 passed, 1 skipped in 43.07s ========================
```

The one skip is `test_the_break_on_purpose_switch_fails_only_on_the_named_version`, which only runs when `MATHKIT_DEMO_FAIL_ON_PYTHON` names the interpreter (see Done when, step 2).

## Done when: the lesson's checklist and the proof for each line

The lesson has six steps, each with one "Done when" line. The first three need numbers or log lines only GitHub-hosted runners produce, so for each the table gives (a) what the repository proves on your machine and (b) the exact command on GitHub.

| # | Done when (from the lesson) | Proof on this machine | Proof on GitHub |
| --- | --- | --- | --- |
| 1 | The workflow runs green, and you have its duration for three runs. | `make run` runs the test job's steps (checkout, setup-python, `pip install --require-hashes`, pytest) in the runner image and ends green. `make test` runs the same pytest. | `gh workflow run measure-1-plain.yml` three times, then `make measure STAGE="1 plain (1 job)" RUNS="id1 id2 id3"`. [`measure-1-plain.yml`](.github/workflows/measure-1-plain.yml) is the lesson's plain solution with `permissions: contents: read`. |
| 2 | Six jobs run in parallel, and a failure on one combination still lets the other five report. | `tests/pipeline/test_workflows.py` asserts 3 quoted versions x 2 systems and `fail-fast: false`. `make run-fail` makes Python 3.10 fail on purpose through the variable `DEMO_FAIL_ON_PYTHON`: that leg is red, the others still run and upload their reports (output below). | The run page lists `test (ubuntu-latest, 3.10)` ... `test (windows-latest, 3.12)`. Set the repository variable `gh variable set DEMO_FAIL_ON_PYTHON --body 3.10`, push, and one job goes red while five report; `gh variable delete DEMO_FAIL_ON_PYTHON` removes it. |
| 3 | A second run shows a cache hit and a shorter install step, and changing the lock file causes a miss. | `python -m pipeline.cache_key` prints the key `actions/setup-python` builds; editing one pin in `requirements.txt` changes the hash (`tests/pipeline/test_cache_key.py`, output below). act cannot show a hit: its cache service is not reachable from a runner container when Docker runs in a VM, so under `make run` the restore and the save are warnings and the install runs in full. | The setup step's log: `Cache not found for input keys: setup-python-Linux-x64-python-3.12.x-pip-<hash>` on the first run, `Cache hit occurred on the primary key ...` on the second, and the first line again after editing `requirements.txt`. |
| 4 | A failing run still has its report attached, and the retention setting shows on the artifact. | `make run-fail` writes the artifacts of the failing leg too; the test asserts `if: always()`, a name per matrix cell, `retention-days: 7` and `if-no-files-found: error`. | The summary page lists `reports-ubuntu-latest-3.10`, `reports-windows-latest-3.10` ... with "expires in 7 days", also for the red run. |
| 5 | A documentation-only commit starts no test jobs, and pushing two commits quickly cancels the first run. | `tests/pipeline/test_pathfilter.py` runs the workflow's real `paths-ignore` patterns against sample changes: `docs/index.md` and `README.md` start nothing, a file under `src/` starts the workflow. The `concurrency` block is asserted verbatim. | Commit a change to `docs/index.md` only: no `ci` run and no test job (the companion `ci-docs-only` run is one no-op job). Push two commits to a branch quickly: the first run log says `Canceling since a higher priority waiting request for ci-refs/heads/<branch> exists`. |
| 6 | The table shows duration and billable minutes for each stage, and a pull request can't merge while the check is red. | `make test` runs `pipeline/billing.py` on fixture runs (worked example below). `scripts/protect-main.sh` with `DRY_RUN=1` prints the exact `gh api` call. | After the three measurement workflows and `ci.yml` have run three times each: `make measure` for each stage. `scripts/protect-main.sh OWNER/REPO` requires the check `ci-ok`, which is one job that survives matrix changes and is also reported by `ci-docs-only.yml`. |

### Step 1 locally: the Ubuntu legs of the matrix (`make run`)

`make run` runs the `test` job of [`ci.yml`](.github/workflows/ci.yml) with act, one Python version at a time, in the runner image. The cache lines are warnings because act's cache service cannot be reached from a runner container when Docker runs in a VM; on GitHub they are the hit and miss lines. The pytest durations are long because Docker on that laptop was shared with dozens of other jobs.

```text
== Python 3.10
   [ci/test (ubuntu-latest, 3.10)]   🚧  ::warning::Failed to restore: getCacheEntry failed: connect ECONNREFUSED 10.14.0.2:63841
   [ci/test (ubuntu-latest, 3.10)]   | pip cache is not found
   [ci/test (ubuntu-latest, 3.10)]   | ================== 90 passed, 1 skipped in 887.40s (0:14:47) ===================
   [ci/test (ubuntu-latest, 3.10)]   🚧  ::warning::Failed to save: reserveCache failed: connect ECONNREFUSED 10.14.0.2:63841
== Python 3.11
   [ci/test (ubuntu-latest, 3.11)]   🚧  ::warning::Failed to restore: getCacheEntry failed: connect ECONNREFUSED 10.14.0.2:55087
   [ci/test (ubuntu-latest, 3.11)]   | pip cache is not found
   [ci/test (ubuntu-latest, 3.11)]   | ================== 90 passed, 1 skipped in 2907.93s (0:48:27) ==================
   [ci/test (ubuntu-latest, 3.11)]   🚧  ::warning::Failed to save: reserveCache failed: connect ECONNREFUSED 10.14.0.2:55087
== Python 3.12
   [ci/test (ubuntu-latest, 3.12)]   🚧  ::warning::Failed to restore: getCacheEntry failed: connect ECONNREFUSED 10.14.0.2:64956
   [ci/test (ubuntu-latest, 3.12)]   | pip cache is not found
   [ci/test (ubuntu-latest, 3.12)]   | =================== 90 passed, 1 skipped in 83.38s (0:01:23) ===================
   [ci/test (ubuntu-latest, 3.12)]   🚧  ::warning::Failed to save: reserveCache failed: connect ECONNREFUSED 10.14.0.2:64956

python   result
3.10     green
3.11     green
3.12     green
```

### Step 2 and 4 locally: one red job, the others still report

`make run-fail` (Python 3.10 told to fail on purpose; Ubuntu legs only, because `act` cannot run Windows jobs). The script exits 0 only when exactly that leg is red:

```text
== Python 3.10
   [ci/test (ubuntu-latest, 3.10)]   🚧  ::warning::Failed to restore: getCacheEntry failed: connect ECONNREFUSED 10.14.0.2:59111
   [ci/test (ubuntu-latest, 3.10)]   | pip cache is not found
   [ci/test (ubuntu-latest, 3.10)]   | >       pytest.fail(f"deliberate failure on Python {target} (MATHKIT_DEMO_FAIL_ON_PYTHON)")
   [ci/test (ubuntu-latest, 3.10)]   | E       Failed: deliberate failure on Python 3.10 (MATHKIT_DEMO_FAIL_ON_PYTHON)
   [ci/test (ubuntu-latest, 3.10)]   | FAILED tests/e2e/test_cli_end_to_end.py::test_the_break_on_purpose_switch_fails_only_on_the_named_version - Failed: deliberate failure on Python 3.10 (MATHKIT_DE
   [ci/test (ubuntu-latest, 3.10)]   | =================== 1 failed, 90 passed in 68.36s (0:01:08) ====================
   [ci/test (ubuntu-latest, 3.10)]   ❌  Failure - Main python -m pytest --junitxml=report.xml --cov --cov-report=xml [1m26.069677084s]
   [ci/test (ubuntu-latest, 3.10)] 🏁  Job failed
   Error: Job 'test (${{ matrix.os }}, ${{ matrix.python }})' failed
== Python 3.11
   [ci/test (ubuntu-latest, 3.11)]   🚧  ::warning::Failed to restore: getCacheEntry failed: connect ECONNREFUSED 10.14.0.2:58237
   [ci/test (ubuntu-latest, 3.11)]   | pip cache is not found
   [ci/test (ubuntu-latest, 3.11)]   | ======================== 90 passed, 1 skipped in 6.13s =========================
   [ci/test (ubuntu-latest, 3.11)]   🚧  ::warning::Failed to save: reserveCache failed: connect ECONNREFUSED 10.14.0.2:58237
== Python 3.12
   [ci/test (ubuntu-latest, 3.12)]   🚧  ::warning::Failed to restore: getCacheEntry failed: connect ECONNREFUSED 10.14.0.2:59623
   [ci/test (ubuntu-latest, 3.12)]   | pip cache is not found
   [ci/test (ubuntu-latest, 3.12)]   | ================== 90 passed, 1 skipped in 117.74s (0:01:57) ===================
   [ci/test (ubuntu-latest, 3.12)]   🚧  ::warning::Failed to save: reserveCache failed: connect ECONNREFUSED 10.14.0.2:59623

python   result
3.10     red
3.11     green
3.12     green
expected: 3.10 red, the others green and still reporting
```

The log of the red leg itself (`build/act/test-3.10-fail-on-3.10.log`) shows the slowest-tests summary written and the reports still uploaded, with the seven-day retention, after the tests failed. The upload is act's stand-in, which lists the files the real action would upload:

```text
[ci/test (ubuntu-latest, 3.10)]   ✅  Success - Main Slowest tests on the summary page [1.70531275s]
[ci/test (ubuntu-latest, 3.10)]   ⚙  Summary - ### Slowest tests
[ci/test (ubuntu-latest, 3.10)]   | artifact reports-ubuntu-latest-3.10: report.xml (12284 bytes), expires in 7 days
[ci/test (ubuntu-latest, 3.10)]   | artifact reports-ubuntu-latest-3.10: coverage.xml (18439 bytes), expires in 7 days
```

### Step 3 locally: the cache key and what changes it

```text
$ python -m pipeline.cache_key --file requirements.txt
setup-python-Linux-x64-python-3.12.7-pip-b399ff5e75d6965b3d85cc54ae3988e69f53b5152ee59b7ef038bfd78d3629c6
$ sed -i '' 's/numpy==2.1.3/numpy==2.1.2/' requirements.txt    # one pin edited, nothing else
$ python -m pipeline.cache_key --file requirements.txt
setup-python-Linux-x64-python-3.12.7-pip-7605b5853f2b1facd737bce3977f54015191f24c5547b331f183104c163ad09a
```

### The measurement table (step 6)

The numbers depend on GitHub-hosted runners and your account, so the table is yours to fill; the tool does the arithmetic. Each job rounds up to a whole minute, Windows minutes count double, macOS ten times, and a stage's row is the median of its runs.

```text
stage                           wall time   billable minutes
1 plain (1 job)
2 matrix (6 jobs)
3 + dependency cache
5 + docs skip and cancel (docs-only commit)
```

Worked example from the repository's fixtures (`tests/pipeline/fixtures`, invented run data, not a measurement):

```text
$ python -m pipeline.billing --stage "1 plain (1 job)" tests/pipeline/fixtures/plain-1.json tests/pipeline/fixtures/plain-2.json tests/pipeline/fixtures/plain-3.json --stage "2 matrix (6 jobs)" tests/pipeline/fixtures/matrix-1.json
stage                             wall time   billable minutes
1 plain (1 job)                   2m 20s      3   (median of 3 runs)
  run 1: 2m 20s, 3 billable minutes
  run 2: 2m 18s, 3 billable minutes
  run 3: 2m 25s, 3 billable minutes
2 matrix (6 jobs)                 3m 05s      24   (median of 1 runs)
  run 1: 3m 05s, 24 billable minutes
```

The matrix fixture bills 24 minutes: three Ubuntu jobs of 100 s round up to 2 minutes each (6), three Windows jobs of 180 s are 3 minutes at the doubled rate (18).

## Stretch goals

| Stretch (from the lesson) | Built? |
| --- | --- |
| Add a job summary that lists the slowest tests in each run. | Yes. [`pipeline/slowest_tests.py`](pipeline/slowest_tests.py) turns `report.xml` into a Markdown table; the `test` job appends it to `$GITHUB_STEP_SUMMARY`. |
| Run the matrix only on pull requests to `main`, and a single fast job on other branches. | No. It is a few lines (a `fromJSON` matrix chosen by `github.event_name`), but it changes which cells the required check covers; [ARCHITECTURE.md](ARCHITECTURE.md#how-to-extend-it) says where it would go. |
| Compare a larger runner with the standard one for your test suite and decide whether it pays for itself. | No. Larger runners need a paid organization plan. `make measure` produces the numbers once a runner label exists; the decision rule is in the architecture notes. |

## What is simplified for teaching

Only what the lesson scopes out, plus where this build differs from the lesson's text:

- **No real GitHub run was possible while this repository was written.** Everything that needs GitHub-hosted runners (the durations and billable minutes of the table, the second-run cache hit on a real cache service, the Windows legs, path filters and cancellation as GitHub applies them, branch protection) is covered by the models and structure tests above and by the commands in the "Proof on GitHub" column. The table is empty on purpose.
- The lesson's tiny `mathkit` has one function; this one is layered (domain, application, infrastructure, interfaces) with a pandas-backed CSV summary, so the heavy dependencies the lesson asks for have something real to do.
- The lesson pins `pytest==8.3.3` and `pytest-cov==5.0.0`; `pip-audit` flags pytest 8.3.3 (PYSEC-2026-1845), so pytest is 9.0.3 here. numpy 2.1.3 and pandas 2.2.3 are pinned as the lesson asks (versions that have wheels for Python 3.10 to 3.13).
- The lesson uses `actions/checkout@v4` and `actions/setup-python@v5`; every action here is pinned to a full commit SHA of the current major (checkout v7, setup-python v7, upload-artifact v7), as the hardening project does. Dependabot proposes new SHAs.
- Documentation-only changes use `paths-ignore` as the lesson says, plus a companion workflow so the required check never stays pending ([ADR 0001](docs/adr/0001-one-gate-job-and-a-companion-for-docs-only-changes.md) explains the one edge that needs checking on GitHub).
- `act` stands in for the hosted runner; its image is Ubuntu 24.04 with Node, git, jq and python3, not GitHub's runner image.

## Project structure

```text
src/mathkit/
  domain/            arithmetic, statistics, the ColumnSummary value object, named errors.
                     Depends on nothing outside the standard library.
  application/       the SummarizeTable use case and the ColumnSource port. Depends on domain only.
  infrastructure/    the pandas adapter for the port (the only module that imports pandas or numpy).
  interfaces/        the command line (python -m mathkit). Depends on everything below; nothing depends on it.
tests/
  unit/              domain, use case with a fake source, command line arguments.
  integration/       the pandas adapter against real pandas and numpy.
  e2e/               the command line as a separate process, and the "break one cell on purpose" switch.
  pipeline/          the scripts below, and test_workflows.py: the lesson's review checklist as assertions on the YAML.
pipeline/            scripts the workflows call: gate, billing, cache_key, slowest_tests, pathfilter, pins, install-actionlint.sh.
scripts/             protect-main.sh: require the ci-ok check (run by hand).
.github/workflows/   ci.yml (stage 5), ci-docs-only.yml, measure-1-plain.yml, measure-2-matrix.yml, measure-3-cache.yml.
ci/act-runner/       the Dockerfile of the image act uses as ubuntu-latest.
docs/                index.md (the folder the path filter ignores) and docs/adr (three decision records).
tech/                one beginner-level note per technology used here (start at tech/README.md).
pyproject.toml       project metadata and every tool's configuration (ruff, mypy, pytest, coverage, import-linter).
requirements*.in/.txt  top-level pins and the hash-pinned universal locks compiled from them with uv.
Makefile             the only commands a reader needs (make help).
```

The dependency rule (domain depends on nothing; application on domain; infrastructure and interfaces on both; nothing on interfaces) is enforced by `make lint` through import-linter. A second contract forbids `domain` and `application` from importing pandas or numpy.

To change a dependency: edit `requirements.in` (or `requirements-dev.in`), then

```bash
uv pip compile requirements.in --universal --generate-hashes --python-version 3.10 -o requirements.txt
uv pip compile requirements-dev.in --universal --generate-hashes --python-version 3.10 -o requirements-dev.txt
```

## Troubleshooting

- **`make run` says the image is missing:** run `make up` once; it builds `gha-projects-act-runner:ubuntu-24.04` (a few minutes the first time).
- **act asks which image size to use:** it should not; `.actrc` maps `ubuntu-latest` to the local image. Delete `~/.config/act/actrc` if an old choice overrides it.
- **setup-python cannot find a version in act:** the runner image must be Ubuntu; a Debian image has no prebuilt Python for the toolcache.
- **Apple silicon:** `.actrc` sets `--container-architecture linux/arm64` so no emulation is used. On an x86 machine remove that line.
- **`make lint` fails on `actionlint: command not found`:** `brew install actionlint shellcheck`.

## Verification status (2026-10-27)

- Passed on this machine, from a fresh clone: `make check` (lint, ruff, mypy, import-linter, actionlint, shellcheck, pin check; 90 tests passed, 1 skipped, coverage 96.84%).
- Passed with `act` in Docker, on a laptop whose load average was in the dozens (the long pytest durations in the outputs above come from that): `make run` (Python 3.10, 3.11 and 3.12 legs green) and `make run-fail` (3.10 red on purpose, 3.11 and 3.12 green, reports still listed with 7-day retention).
- Pending capacity: the runner image was built from this `ci/act-runner/Dockerfile` (the build client reported a deadline error after the layers were done, but the tagged image was present and was the one used), and `make up` was not re-run from a fresh clone. After Docker Desktop is restarted with free disk (Docker.raw was at its 60 GiB cap on 2026-10-28), run `make up` and then `make run && make run-fail`.
- Could not run anywhere here, only on GitHub: the real durations and billable minutes of the table, the second-run cache hit, the Windows legs, path filters and cancellation as GitHub applies them, `scripts/protect-main.sh` (dry run only).

## Author and license

Written by Sumit Srivastava. Released under the MIT License, see [LICENSE](LICENSE). Changes are in [CHANGELOG.md](CHANGELOG.md).
