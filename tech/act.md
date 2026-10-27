# act

## What it is

act is a command-line tool that runs GitHub Actions workflows on your own machine. It reads the workflow YAML, starts a Docker container for each job (see `docker.md`), and runs the steps inside. It is a close imitation of GitHub's runner, not an exact copy. This repository uses act 0.2.89.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **shell**: The program inside a terminal that reads what you type and starts other programs. Bash is a shell.
- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **workflow**: A GitHub Actions automation described in a YAML file under `.github/workflows/`. It names the events that start it and the jobs it runs.
- **runner**: The computer, usually a virtual machine, on which GitHub runs a job. It starts clean for every job.
- **artifact**: A file or folder that a job saves so that later jobs, or people, can download it.
- **YAML**: A plain-text format for structured data that uses indentation instead of braces. GitHub workflows are YAML files.
- **container**: A running, isolated copy of a program together with its own files, started from an image. Containers are managed by Docker.
- **Docker**: A tool that builds images and runs containers.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.
- **variable**: A name for a place that holds a value which can be used later in the code.
- **list**: An ordered collection of values written one after another.
- **server**: A program that waits for requests and answers them.
- **folder**: A container for files and other folders on disk (also called a directory).
- **version**: A number such as `1.2.3` that names one release of software (major.minor.patch).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

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

<!-- walk:ci/act-stubs/upload-artifact/action.yml -->
### `ci/act-stubs/upload-artifact/action.yml`, line by line

Lines 1 to 24:

```yaml
# Stand-in for actions/upload-artifact when the workflow runs under act on a Mac.

#
# The real action talks to GitHub's artifact service, which act can only imitate with a server on the host that the

# runner container cannot reach when Docker runs in a VM. This stand-in does what can be checked locally: it lists the

# files that would be uploaded with their sizes and the retention, and fails when a file is missing and

# if-no-files-found is "error". On GitHub the real action runs; scripts/act-matrix.sh maps this stand-in over it with

# act's --local-repository.

name: upload-artifact (act stand-in)
description: List what actions/upload-artifact would upload, and fail on a missing file when asked to.
inputs:
  name:
    description: Artifact name.
    required: true
  path:
    description: Files to upload, one per line.
    required: true
  retention-days:
    description: Retention in days.
    required: false
    default: ""
  if-no-files-found:
    description: warn, error or ignore.
    required: false
    default: warn
```

The comment (lines 1 to 7) explains why this stand-in exists: the real `actions/upload-artifact` talks to GitHub's artifact service, which `act` can only imitate with a server that a runner container inside a virtual machine cannot reach. The stand-in lists the files that would be uploaded, with sizes and retention, and fails when a file is missing and `if-no-files-found` is `error`. `name` and `description` label the action. `inputs:` mirrors the real action's: `name` and `path` (required), `retention-days` (default empty), `if-no-files-found` (default `warn`).

Lines 25 to 47:

```yaml
runs:
  using: composite
  steps:
    - shell: bash
      env:
        ARTIFACT_NAME: ${{ inputs.name }}
        ARTIFACT_PATHS: ${{ inputs.path }}
        ARTIFACT_RETENTION: ${{ inputs.retention-days }}
        ARTIFACT_IF_MISSING: ${{ inputs.if-no-files-found }}
      run: |
        missing=0
        while IFS= read -r file; do
          [ -n "$file" ] || continue
          if [ -e "$file" ]; then
            echo "artifact ${ARTIFACT_NAME}: ${file} ($(wc -c < "$file" | tr -d ' ') bytes), expires in ${ARTIFACT_RETENTION:-90} days"
          else
            echo "artifact ${ARTIFACT_NAME}: ${file} is missing"
            missing=1
          fi
        done <<< "$ARTIFACT_PATHS"
        if [ "$missing" = 1 ] && [ "$ARTIFACT_IF_MISSING" = error ]; then
          exit 1
        fi
```

`runs.using: composite` means the action is a list of steps. The one step names `shell: bash` (required for `run:` steps of a composite action) and receives the inputs as environment variables (never pasted into the script text). The script: `missing=0` is a flag; `while IFS= read -r file; do ... done <<< "$ARTIFACT_PATHS"` reads the list of paths one line at a time (`IFS=` keeps leading spaces, `-r` keeps backslashes, `<<<` feeds a text as input); `[ -n "$file" ] || continue` skips empty lines; `[ -e "$file" ]` tests that the file exists; `wc -c < "$file"` counts bytes and `tr -d ' '` removes spaces; `${ARTIFACT_RETENTION:-90}` means the variable or 90 if empty. If a file was missing and the policy is `error`, the step exits 1 like the real action.

<!-- /walk:ci/act-stubs/upload-artifact/action.yml -->

<!-- walk:.actrc -->
### `.actrc`, line by line

Lines 1 to 4:

```ini
-P ubuntu-latest=gha-projects-act-runner:ubuntu-24.04
--pull=false
--container-architecture linux/arm64
--container-daemon-socket -
```

One option per line. `-P ubuntu-latest=gha-projects-act-runner:ubuntu-24.04` maps the runner label to the locally built image; `--pull=false` stops `act` from trying to download the image; `--container-architecture linux/arm64` runs containers as ARM (Apple Silicon); `--container-daemon-socket -` stops `act` from mounting the Docker socket into the job, which fails on Docker Desktop for Mac.

<!-- /walk:.actrc -->

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
