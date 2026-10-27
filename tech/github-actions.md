# GitHub Actions

## What it is

GitHub Actions is the automation service built into GitHub. You describe a job in a text file. GitHub reads the file, starts a fresh computer for each job, and runs your commands on it. Nobody has to keep a server running. This kind of automation is called **continuous integration** (CI): every time someone pushes code, a machine builds it and runs the tests, so you learn about a break within minutes.

The words you need:

- A **workflow** is one such file. It lives in `.github/workflows/` and is written in YAML (see `yaml.md`).
- An **event** is the thing that starts a workflow: a push, a pull request, a button press.
- A **job** is a list of steps that runs on one fresh machine. Jobs in one workflow run at the same time unless you say one waits for another.
- A **step** is one command (`run:`) or one ready-made **action** (`uses:`). An action is a packaged piece of automation that someone else wrote, such as "check out the code".
- A **runner** is the machine that runs a job. `ubuntu-latest` and `windows-latest` are runners that GitHub hosts.
- A **matrix** is a way to run the same job many times with different values.

## Why this repository uses it

The lesson is about making CI fast and cheap. It asks for a workflow that tests on three Python versions and two operating systems, reuses downloaded packages between runs (a **cache**), keeps test reports (**artifacts**), skips runs that cannot matter, and cancels runs that a newer push made out of date. Every one of those is a feature of GitHub Actions, so this file is the centre of the repository.

## Where it appears

| Path | What it does with GitHub Actions |
| --- | --- |
| `.github/workflows/ci.yml` | The main workflow: lint job, six-job test matrix, and the `ci-ok` gate. |
| `.github/workflows/ci-docs-only.yml` | A tiny companion that reports the check `ci-ok` when only documentation changed. |
| `.github/workflows/measure-1-plain.yml`, `measure-2-matrix.yml`, `measure-3-cache.yml` | Three "before" versions of the workflow, started by hand, used to measure what each improvement saves. |
| `ci/act-stubs/upload-artifact/action.yml` | A **composite action** (an action made of shell steps) that stands in for the real upload action when you run locally. |
| `pipeline/pins.py`, `tests/pipeline/test_workflows.py` | Python code that reads the workflow files and checks rules about them. |

## How it works underneath

1. You push a commit. GitHub looks in `.github/workflows/` of that commit and compares each file's `on:` section with the event that just happened.
2. For each matching workflow GitHub creates a **run**. For each job in the run it asks for a runner. A hosted runner is a virtual machine that is created for that one job and thrown away after.
3. The runner downloads the actions your steps name. An action name like `actions/checkout@<40 hex characters>` means "the repository `actions/checkout` at exactly that commit". A **commit SHA** is a 40-character fingerprint of one exact state of a repository, and it can never point somewhere else. A tag such as `v7` is only a label that its owner can move, so this repository pins SHAs and keeps the readable version in a comment.
4. Steps run in order. If a step fails, later steps are skipped unless they have an `if:` condition such as `always()`.
5. Every job gets a **token**, a short-lived password named `GITHUB_TOKEN`, so steps can talk to the GitHub API. The `permissions:` key says what that token may do. The safe habit is the least it needs.
6. The **cache** is a store outside the runner. A job asks for a cache by a **key** (a name). If the key exists, the stored files are restored; if not, the job runs without and saves its files at the end under that key. **Artifacts** are files a job uploads to keep after the runner is gone.
7. When every job is finished, GitHub reports each job's result as a **check** on the commit. A branch can be set to refuse merges until chosen checks are green.

## Walkthrough of this repository's use

### Triggers and the path filter

```yaml
on:
  push:
    branches: [main]
    paths-ignore: ["docs/**", "**.md"]
  pull_request:
    paths-ignore: ["docs/**", "**.md"]
```

`on:` lists the events. `push` with `branches: [main]` starts the workflow for pushes to `main` only, so a pull-request branch does not run twice (once for the push and once for the pull request). `pull_request` starts it for every pull request. `paths-ignore` lists file patterns: if *every* changed file matches a pattern, the workflow does not start. `docs/**` means "anything under `docs/`" (`**` crosses folder boundaries), and `**.md` means "any file ending in `.md`". A commit that changes only `docs/index.md` therefore starts nothing here. `pipeline/pathfilter.py` is a small Python model of these rules so the tests can check them.

### Least privilege

```yaml
permissions:
  contents: read
```

At the top of the workflow this says the token may only read repository contents. Each job repeats it (`permissions: contents: read`), and the `measure-*` workflows and the docs-only companion do the same or use `permissions: {}` (nothing at all). Without this key the token's rights depend on a repository setting that may allow writing.

### Cancelling stale runs

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

`concurrency` lets only one run per **group** be active. The group name is built from `github.ref` (the branch or pull-request reference), so each branch has its own group. `${{ ... }}` is an **expression**: GitHub computes it before the workflow runs. When a newer push arrives in the same group, `cancel-in-progress: true` stops the older run. The expression `github.ref != 'refs/heads/main'` is `false` on `main`, so a run on `main` is never cancelled: every commit there must finish its tests.

### The lint job

```yaml
  lint:
    name: lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements-dev.txt
      - run: pip install --require-hashes -r requirements-dev.txt
      - run: pipeline/install-actionlint.sh
      - run: echo "$PWD/.tools/bin" >> "$GITHUB_PATH"
      - run: make lint BIN=
      - run: make audit BIN=
```

`timeout-minutes` stops a stuck job from burning minutes. `actions/checkout` copies the repository onto the runner; `persist-credentials: false` stops it from leaving the token in the repository's git settings where later steps could read it. `actions/setup-python` installs Python. Its `cache: pip` input turns on caching of the pip download folder, and `cache-dependency-path` names the file whose contents decide the cache key: change that file and the key changes. `pip install --require-hashes` installs only packages whose hash matches the lock file (see `pip.md`). `echo ... >> "$GITHUB_PATH"` is how a step adds a folder to the `PATH` of the *later* steps. `make lint BIN=` runs the Makefile with `BIN` set to empty so it uses the tools already on the `PATH` (see `make.md`).

### The test matrix

```yaml
  test:
    name: test (${{ matrix.os }}, ${{ matrix.python }})
    runs-on: ${{ matrix.os }}
    timeout-minutes: 15
    permissions:
      contents: read
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.10", "3.11", "3.12"]
    defaults:
      run:
        shell: bash
    env:
      MATHKIT_DEMO_FAIL_ON_PYTHON: ${{ vars.DEMO_FAIL_ON_PYTHON }}
```

`strategy.matrix` with two lists makes every combination: two systems times three versions is six jobs, and they run at the same time. In the job, `${{ matrix.os }}` and `${{ matrix.python }}` hold the values of the current combination. `fail-fast: false` keeps the other five jobs running when one fails; the default would cancel them and hide which combinations are broken. The versions are quoted because YAML would read `3.10` as the number 3.1 (see `yaml.md`). `defaults.run.shell: bash` makes every `run:` step use Bash, even on Windows, so one set of commands works everywhere. `vars.DEMO_FAIL_ON_PYTHON` reads a **repository variable** (a named setting stored in GitHub, empty unless you set it); the test suite fails on the named Python version when it is set. That is the lesson's "break one cell on purpose" exercise.

```yaml
      - run: python -m pytest --junitxml=report.xml --cov --cov-report=xml
      - name: Slowest tests on the summary page
        if: always() && hashFiles('report.xml') != ''
        run: python -m pipeline.slowest_tests report.xml >> "$GITHUB_STEP_SUMMARY"
      - name: Keep the reports, also when the tests fail
        if: always()
        uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        with:
          name: reports-${{ matrix.os }}-${{ matrix.python }}
          path: |
            report.xml
            coverage.xml
          retention-days: 7
          if-no-files-found: error
```

`if: always()` makes a step run even after an earlier step failed. Without it, the upload would be skipped exactly when you need the report. `hashFiles('report.xml') != ''` is true only if the file exists. `$GITHUB_STEP_SUMMARY` is the path of a file; whatever Markdown a step appends to it appears on the run's summary page. `name:` for an artifact must be unique within a run, which is why it contains both matrix values. `retention-days: 7` deletes the files after a week (the default is 90). `if-no-files-found: error` fails the step when a listed file is missing.

### The gate job

```yaml
  ci-ok:
    name: ci-ok
    if: always()
    needs: [lint, test]
    runs-on: ubuntu-latest
    ...
      - run: python3 -m pipeline.gate
        env:
          NEEDS: ${{ toJSON(needs) }}
```

`needs` makes this job wait for `lint` and every `test` job. `if: always()` makes it run even when they failed, so it can report. `needs` is also a **context**: an object with each needed job's result. `toJSON(needs)` turns it into JSON text, and putting it in an environment variable (`NEEDS`) instead of pasting it into the command keeps job data out of shell text. `pipeline/gate.py` reads it and exits with an error unless every job is `success` or `skipped`. One job named `ci-ok` is easier to require on a branch than six matrix names.

### The companion for documentation-only changes

`ci-docs-only.yml` uses `paths:` (the opposite filter: start only when a changed file matches) and has one job named `ci-ok` that only echoes a line. A skipped workflow reports no check, so a required check would wait for ever on a documentation pull request. This workflow reports the same name and passes. `permissions: {}` is used because the job reads nothing.

### The measurement workflows

```yaml
on: workflow_dispatch
```

`workflow_dispatch` means "only when someone starts it by hand" (the Actions tab, or `gh workflow run measure-1-plain.yml`). `measure-1-plain.yml` runs one job with no cache; `measure-2-matrix.yml` adds the matrix; `measure-3-cache.yml` adds `cache: pip`. Running each three times and reading the durations gives the before and after numbers.

## Try it yourself

1. List the workflow files and count the jobs: `grep -c "runs-on" .github/workflows/*.yml`. You see one count per file (3 for `ci.yml`, 1 for each of the others).
2. Check the rules the lesson cares about, without GitHub: `.venv/bin/python -m pytest tests/pipeline/test_workflows.py -q`. All tests pass; they read the YAML and assert the matrix, the cache, the artifact settings and the concurrency expression.
3. Check that every `uses:` is pinned: `.venv/bin/python -m pipeline.pins`. It prints `pins: every uses: is a full commit SHA, a local path or a digest`.
4. Lint the syntax: `actionlint`. No output means no problems.
5. Run the test job on your machine (needs Docker, see `act.md`): `make run`.

## Mistakes people make

- Leaving `fail-fast` at its default, so one red combination hides the others.
- Writing `python: [3.10]` without quotes: YAML reads it as 3.1 and the job installs the wrong version.
- Forgetting `if: always()` on the upload step, so a failing run has no report.
- Using one artifact name in every matrix job. The second upload fails because the name is taken.
- Requiring a workflow that path filters can skip: the check never reports and the pull request cannot merge. This repository adds `ci-docs-only.yml` for that.
- Cancelling runs on `main`: a commit that never finished its tests could be merged. The `cancel-in-progress` expression avoids it.
- Putting `${{ github.event... }}` text straight into a `run:` command. This repository passes data through `env:` instead.

## Check yourself

1. How many jobs does the `test` matrix create, and why do they not wait for each other? *(Six: two systems times three versions. Jobs of one workflow run in parallel unless `needs` says otherwise.)*
2. Why does `cancel-in-progress` use an expression instead of `true`? *(So runs on `main` are never cancelled while runs on other branches are.)*
3. What does `paths-ignore: ["docs/**", "**.md"]` do when a commit changes `docs/a.md` and `src/mathkit/__init__.py`? *(The workflow starts, because not every changed file matches an ignored pattern.)*
4. Why is the action pinned as a 40-character SHA with `# v7.0.1` after it? *(A tag can be moved to different code; a SHA cannot. The comment tells people and update tools which version it is.)*
5. Why does `ci-ok` have `if: always()`? *(Without it, a failed job would make `ci-ok` skipped instead of failed, and a skipped required check could look like a pass or stay pending.)*

## Further reading

- Workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Events that trigger workflows: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- Concurrency: https://docs.github.com/en/actions/using-jobs/using-concurrency
- Caching and artifacts: https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching
- Actions used here, pinned: `actions/checkout` v7.0.1, `actions/setup-python` v7.1.0, `actions/upload-artifact` v7.0.2 (each repository's README on github.com/actions).
