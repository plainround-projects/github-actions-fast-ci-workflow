# Technology notes for github-actions-fast-ci-workflow

This folder teaches every technology the repository uses, from zero, through the repository's own files. Each note says what the technology is, why this repository uses it, where it appears, how it works underneath, and then walks through the repository's own lines, flag by flag. You need no earlier knowledge.

## The files and the order to read them

Read from the top: the idea of the project first, then the language, then the file formats, then the build and test tools, then the code checkers, then the pieces that run it locally, then the tools around the code.

| # | Note | Role in this repository |
| ---: | --- | --- |
| 1 | [GitHub Actions](github-actions.md) | the service that runs the workflows: triggers, matrix, cache, artifacts, cancellation |
| 2 | [YAML](yaml.md) | the file format of every workflow, with its traps |
| 3 | [Python](python.md) | the language of the library, the tests and the helper scripts |
| 4 | [TOML](toml.md) | the format of `pyproject.toml`, which configures every Python tool |
| 5 | [pip, virtual environments and lock files](pip.md) | installs packages; the hashed lock file keys the cache |
| 6 | [uv](uv.md) | makes the universal lock files and runs the tests on three Pythons |
| 7 | [pytest, pytest-cov and coverage](pytest.md) | runs the 90 tests and enforces 95 percent coverage |
| 8 | [JUnit XML](junit-xml.md) | the test report that is uploaded and summarized |
| 9 | [pandas](pandas.md) | the heavy dependency the cache saves; reads CSV |
| 10 | [NumPy](numpy.md) | pandas' base library; decides which columns are numeric |
| 11 | [PyYAML](pyyaml.md) | lets Python code read workflow files |
| 12 | [Ruff](ruff.md) | lints and formats the Python |
| 13 | [mypy](mypy.md) | checks the type hints |
| 14 | [import-linter](import-linter.md) | enforces the layer rules between folders |
| 15 | [pip-audit](pip-audit.md) | checks the locked packages for known vulnerabilities |
| 16 | [Bash](bash.md) | the scripts: install a tool, run the matrix, set branch protection |
| 17 | [Make](make.md) | the `make test`, `make lint`, `make run` commands |
| 18 | [actionlint](actionlint.md) | checks workflow files before GitHub sees them |
| 19 | [ShellCheck](shellcheck.md) | checks the shell scripts |
| 20 | [Docker](docker.md) | the Dockerfile for the image `act` uses |
| 21 | [act](act.md) | runs the workflow on your machine |
| 22 | [Dependabot](dependabot.md) | proposes updates to the pinned actions and packages |
| 23 | [GitHub CLI](gh-cli.md) | measures real runs and requires the `ci-ok` check |
| 24 | [Git and .gitignore](git.md) | history, and what is kept out of it |
| 25 | [EditorConfig](editorconfig.md) | the same indentation and line endings in every editor |
| 26 | [Markdown and Mermaid](markdown.md) | the documents and the diagram |

## If you have ten minutes

Read these three, in this order:

1. [GitHub Actions](github-actions.md): the matrix, the cache, the artifacts and the cancellation are the whole lesson.
2. [pip, virtual environments and lock files](pip.md): why one hashed file makes the cache correct.
3. [act](act.md): how to watch the workflow run without pushing.
