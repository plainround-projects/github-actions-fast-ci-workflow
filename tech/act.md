# act

## What it is

act is a command-line tool that runs GitHub Actions workflows on your own machine. It reads the workflow YAML, starts a Docker container for each job (see `docker.md`), and runs the steps inside. It is a close imitation of GitHub's runner, not an exact copy. This repository uses act 0.2.89.

## Why this repository uses it

The task says the main workflow should run locally "where it works", with exact commands. `make run` runs the test job on three Ubuntu Python versions without pushing anything, and `make run-fail` shows one red job and two green ones.

## Where it appears

| Path | What it does with act |
| --- | --- |
| `.actrc` | Default options for every `act` run in this folder. |
| `scripts/act-matrix.sh` | Runs `act push` once per Python version and summarizes. |
| `Makefile` | `run`, `run-fail` and `down`. |
| `ci/act-runner/Dockerfile` | Builds the image act uses as `ubuntu-latest`. |
| `ci/act-stubs/upload-artifact/action.yml` | Replaces the real artifact upload under act. |

## How it works underneath

act reads `.github/workflows/*.yml`, picks the event you name (`push`), builds the job graph, and for each job starts a container from the image mapped to the job's `runs-on` label. It copies your working folder into the container, downloads each `uses:` action from github.com (cached in `~/.cache/act`), and executes the steps with the container's `node` or `bash`. It also starts two small local servers for the cache and artifact services. It cannot run Windows or macOS jobs.

## Walkthrough of this repository's use

### `.actrc`

```text
-P ubuntu-latest=gha-projects-act-runner:ubuntu-24.04
--pull=false
--container-architecture linux/arm64
--container-daemon-socket -
```

One option per line, read from the folder where you run `act`.

- `-P ubuntu-latest=IMAGE` maps the label `ubuntu-latest` to our own image (see `docker.md`).
- `--pull=false` never tries to download the image; it is built locally.
- `--container-architecture linux/arm64` runs native containers on Apple silicon instead of slow emulation. On an Intel machine, remove it.
- `--container-daemon-socket -` stops act from mounting Docker's socket file into the container. On Docker Desktop for Mac that path does not exist inside the virtual machine, so the container would fail to start.

### `scripts/act-matrix.sh`

```bash
flags=(--concurrent-jobs 1 --local-repository "$upload_artifact=$root/ci/act-stubs/upload-artifact")
...
act push "${flags[@]}" -W .github/workflows/ci.yml -j test --matrix os:ubuntu-latest --matrix "python:$version"
```

- `push` is the event to simulate.
- `-W FILE` runs only that workflow file. `-j test` runs only the job named `test` (the lint job needs tools not in the image).
- `--matrix os:ubuntu-latest --matrix python:3.12` keeps one cell of the matrix. Running one cell at a time keeps a laptop from running three containers that each install numpy and pandas.
- `--concurrent-jobs 1` never runs two jobs at once.
- `--var DEMO_FAIL_ON_PYTHON=3.10` (added by `--fail-on 3.10`) sets a repository variable, which is what makes one leg red on purpose.
- `--local-repository 'actions/upload-artifact@<sha>=/path'` says "when a step uses this action at this version, use the files in that folder instead of downloading". The folder holds the stand-in described next.

### Why a stand-in for the artifact upload

The real `actions/upload-artifact` talks to GitHub's artifact service. act can imitate that service with a local server, but the container cannot reach it when Docker runs in a virtual machine on a Mac, so the real action fails. The stand-in `ci/act-stubs/upload-artifact/action.yml` is a **composite action** (an action made of shell steps) with the same inputs. It prints each file it would upload with its size and retention, and fails if a file is missing and `if-no-files-found` is `error`:

```bash
echo "artifact ${ARTIFACT_NAME}: ${file} ($(wc -c < "$file" | tr -d ' ') bytes), expires in ${ARTIFACT_RETENTION:-90} days"
```

`wc -c` counts bytes; `tr -d ' '` removes padding spaces; `${VAR:-90}` shows 90 if the retention input is empty.

### The cache

The cache service has the same networking limit. `actions/setup-python`'s cache restore and save become warnings in the log (`Failed to restore: getCacheEntry failed: connect ECONNREFUSED ...`) and the job continues, so the install runs in full. A cache hit can only be seen on GitHub.

### A Docker cleanup error after a successful job

`scripts/act-matrix.sh` accepts a run as green when the log says `Job succeeded` and not `Job failed`, even if act exits with an error. On a busy Docker daemon act can time out removing volumes after the job itself finished.

## Try it yourself

1. `act --version` prints `act version 0.2.89`.
2. `act push -W .github/workflows/ci.yml -l` lists the jobs act would run, without running them.
3. `make run` (Docker needed) ends with a table `python result` and `3.10 green`, `3.11 green`, `3.12 green`.
4. `make run-fail` ends with `3.10 red`, `3.11 green`, `3.12 green` and `expected: 3.10 red, the others green and still reporting`.
5. `grep -h "artifact reports-" build/act/test-3.10-fail-on-3.10.log` shows the stand-in listing `report.xml` and `coverage.xml` with `expires in 7 days` even though the tests failed.

## Mistakes people make

- Expecting act to match GitHub exactly: services, permissions and Windows jobs differ.
- Running the whole matrix at once on a small machine.
- Forgetting that act copies the working folder, so uncommitted changes are included.
- Starting act from another folder and losing `.actrc`.

## Check yourself

1. What does `-P ubuntu-latest=IMAGE` do? *(Maps the runner label to a Docker image.)*
2. Why one matrix cell per run? *(To avoid several heavy installs at once.)*
3. Why is upload-artifact replaced? *(act's artifact service is unreachable from the container on a Mac.)*
4. Can act run `windows-latest` jobs? *(No.)*
5. What does `--var` set? *(A repository variable, readable as `vars.NAME`.)*

## Further reading

- act user guide: https://nektosact.com/
- Options for 0.2.89: https://github.com/nektos/act/tree/v0.2.89#readme
