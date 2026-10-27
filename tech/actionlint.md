# actionlint

## What it is

actionlint is a command-line checker for GitHub Actions workflow files. Like a spell-checker for workflows, it reads the YAML and reports mistakes: unknown keys, wrong types, bad `${{ }}` expressions, undefined job names in `needs`, and (with ShellCheck installed) problems inside `run:` scripts. This repository uses version 1.7.12.

## Why this repository uses it

Workflow mistakes otherwise show up only after a push, on GitHub, minutes later. The task for this repository says `actionlint` runs locally and in CI, so a typo fails `make lint` instead of a real run.

## Where it appears

| Path | What it does with actionlint |
| --- | --- |
| `Makefile` | `lint` runs `actionlint` (no arguments: it finds `.github/workflows/*.yml` itself). |
| `.github/workflows/ci.yml` | Installs a pinned binary with `pipeline/install-actionlint.sh`, then runs `make lint`. |
| `pipeline/install-actionlint.sh` | Downloads release 1.7.12 and verifies its SHA-256 checksum. |

## How it works underneath

actionlint parses each workflow file into a tree, then checks it in layers: the YAML shape, then the syntax of every `${{ }}` expression, then the types (`matrix.os` exists only if the matrix defines `os`), then the context rules (`needs.lint.result` is valid only when the job needs `lint`). For each `run:` step it passes the script to ShellCheck (`shellcheck.md`) if that program is on the `PATH`. It does not contact GitHub, so it cannot know whether a remote action exists.

## Walkthrough of this repository's use

```bash
actionlint
```

Run from the repository root. Silence with exit code 0 means every workflow passed. In CI the lint job installs it first:

```yaml
- run: pipeline/install-actionlint.sh
- run: echo "$PWD/.tools/bin" >> "$GITHUB_PATH"
- run: make lint BIN=
```

The installer puts the binary in `.tools/bin` (ignored by git), the second step adds that folder to the `PATH` of later steps, and `make lint` then finds `actionlint`. The installer checks the download's SHA-256 against a value written in the script, so a swapped download is rejected (see `bash.md`).

## Try it yourself

1. `actionlint -version` prints `1.7.12` and build details.
2. `actionlint` prints nothing and exits 0.
3. Break a copy: `mkdir -p /tmp/w/.github/workflows && printf 'on: push\njobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ${{ matrix.os }}\n' > /tmp/w/.github/workflows/x.yml && (cd /tmp/w && actionlint)` reports `property "os" is not defined`.
4. `actionlint -format '{{json .}}'` prints findings as JSON.

## Mistakes people make

- Believing a clean actionlint run means the workflow works. It cannot see GitHub's servers, secrets or remote actions.
- Skipping ShellCheck, which silently drops the script checks.
- Running a different actionlint version locally and in CI.

## Check yourself

1. What does actionlint read? *(Workflow YAML files.)*
2. What extra checking does ShellCheck add? *(Mistakes inside `run:` shell scripts.)*
3. Does it contact GitHub? *(No.)*
4. How does CI get the binary? *(`pipeline/install-actionlint.sh` downloads a pinned release and verifies the checksum.)*
5. What would `matrix.os` without a matrix key cause? *(An error: the property is not defined.)*

## Further reading

- actionlint 1.7 documentation: https://github.com/rhysd/actionlint/blob/v1.7.12/docs/usage.md
- Checks reference: https://github.com/rhysd/actionlint/blob/v1.7.12/docs/checks.md
