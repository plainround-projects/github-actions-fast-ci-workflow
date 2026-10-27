# Make

## What it is

Make is a command-line tool that runs named recipes from a file called `Makefile`. Each recipe is a **target**: a name, the things it depends on, and the shell commands that build it. Make was designed to rebuild only what is out of date by comparing file times. Today many projects also use it as a short list of named commands (`make test`, `make lint`).

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **shell**: The program inside a terminal that reads what you type and starts other programs. Bash is a shell.
- **PATH**: An environment variable listing the folders where the shell looks for programs. Typing `node` works because the folder holding `node` is in `PATH`.
- **hash**: A fixed-length fingerprint computed from some data. The same data always gives the same hash; any change gives a different one. SHA-256 and SHA-1 are two ways of computing one.
- **workflow**: A GitHub Actions automation described in a YAML file under `.github/workflows/`. It names the events that start it and the jobs it runs.
- **runner**: The computer, usually a virtual machine, on which GitHub runs a job. It starts clean for every job.
- **image**: A read-only package that holds everything needed to start a container: a file system plus settings. A running **container** is made from an image.
- **container**: A running, isolated copy of a program together with its own files, started from an image. Containers are managed by Docker.
- **Docker**: A tool that builds images and runs containers.
- **lock file**: A file that records the exact version, and a checksum, of every package that was installed, so that everyone installs exactly the same thing.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.
- **list**: An ordered collection of values written one after another.
- **folder**: A container for files and other folders on disk (also called a directory).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **pytest**: A Python test framework: it finds functions named `test_...`, runs them, and reports failures.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

## Why this repository uses it

The template for these projects says a reader should only need `make run`, `make test` and `make lint`. A Makefile gives the same commands on a laptop and in CI, so the workflow's lint step and your own lint run are the same commands.

## Where it appears

| Path | What it does with Make |
| --- | --- |
| `Makefile` | Targets: `install`, `up`, `run`, `run-fail`, `test`, `matrix-local`, `lint`, `format`, `audit`, `measure`, `check`, `down`, `clean`, `help`. |
| `.github/workflows/ci.yml` | `make lint BIN=` and `make audit BIN=` in the lint job. |
| `README.md` | Every command a reader runs is a `make` target. |

## How it works underneath

Make reads the `Makefile`, picks the target you named (or the first one), checks its **prerequisites** (the names after the colon), and builds those first. A target that is a real file is rebuilt only if a prerequisite is newer. A target that is just a command name should be listed under `.PHONY`, which tells Make "this is not a file, always run it". Each line of a recipe starts with a **tab** and runs in its own shell. A line starting with `@` is not echoed; a line starting with `-` ignores failure. `$(NAME)` expands a variable. In recipes, a shell variable needs a doubled dollar (`$$id`) so Make does not expand it first.

## Walkthrough of this repository's use

```make
STAMP := .venv/.installed
BIN ?= $(if $(CI),,.venv/bin/)
DEPS := $(if $(CI),,$(STAMP))
PYTHON ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3.10)
```

`:=` assigns once, when read. `?=` assigns only if the variable has no value yet, so a caller can override it (`make lint BIN=`). `$(if COND,THEN,ELSE)`: GitHub sets the environment variable `CI`, so inside CI `BIN` is empty (tools come from the `PATH`) and `DEPS` is empty (no virtual environment to build); on a laptop `BIN` is `.venv/bin/` and `DEPS` is the stamp file. `$(shell ...)` runs a command at read time and uses its output; `command -v` prints the path of the first interpreter that exists.

```make
.PHONY: help install up run run-fail test matrix-local lint format audit measure check down clean
```

None of these is a file.

```make
help: ## list the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort
```

A convention: the text after `##` documents a target. `help` prints them by searching the Makefile (`$(MAKEFILE_LIST)` is the list of makefiles read). `grep -E` uses extended regular expressions; `sed 's/A/B/'` replaces text; `sort` orders the lines.

```make
$(STAMP): requirements-dev.txt pyproject.toml
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q --require-hashes -r requirements-dev.txt
	.venv/bin/pip install -q --no-deps -e .
	touch $@
```

A real file target. `.venv/.installed` depends on the lock file and `pyproject.toml`: when either changes, the virtual environment is rebuilt, otherwise Make skips this. The recipe creates a virtual environment (an isolated Python folder, see `pip.md`), installs the locked tools with hash checking, installs the project itself in editable mode (`-e .`, `--no-deps` because the lock file already installed the dependencies), and `touch $@` creates the stamp file (`$@` means "this target's name").

```make
test: $(DEPS) ## every test: ...
	$(BIN)python -m pytest --cov --cov-report=term-missing --cov-fail-under=95
```

`test` depends on `$(DEPS)`, which brings the environment up to date first. `--cov-fail-under=95` makes the command fail if total coverage is below 95 percent.

```make
lint: $(DEPS)
	$(BIN)ruff check .
	$(BIN)ruff format --check .
	$(BIN)mypy
	$(BIN)lint-imports
	actionlint
	shellcheck scripts/*.sh pipeline/*.sh
	$(BIN)python -m pipeline.pins
```

Seven checks, in order. If one fails Make stops and the target fails.

```make
matrix-local:
	@for version in 3.10 3.11 3.12; do \
	  echo "== Python $$version"; \
	  uv run --no-project --python $$version --with-requirements requirements.txt python -m pytest -q -p no:cacheprovider || exit 1; \
	done
```

A shell `for` loop. The trailing backslashes join the lines into one shell command, `$$version` is the shell's variable, and `|| exit 1` stops on the first failure.

```make
measure: $(DEPS)
	@mkdir -p build; files=""; for id in $(RUNS); do \
	  gh api repos/$${GH_REPO:-$$(gh repo view --json nameWithOwner -q .nameWithOwner)}/actions/runs/$$id/jobs --paginate > build/run-$$id.json; \
	  files="$$files build/run-$$id.json"; done; \
	$(BIN)python -m pipeline.billing --stage "$(STAGE)" $$files
```

Used as `make measure STAGE="1 plain (1 job)" RUNS="111 112 113"`. For each run id it downloads the job list with the GitHub CLI (`gh-cli.md`), then feeds the files to `pipeline/billing.py`.

```make
down:
	-docker ps -aq --filter "ancestor=$(ACT_IMAGE)" | xargs docker rm -f
```

The leading `-` keeps `make down` from failing when there is nothing to remove. `xargs` turns the list of container ids into arguments for `docker rm -f`.

<!-- walk:Makefile -->
### `Makefile`, line by line

Lines 1 to 13:

```make
# make help lists every target.   make up | run | test | lint | down

STAMP := .venv/.installed
# In CI (the CI variable is set) the tools are already on the PATH from the workflow's own install step.

BIN ?= $(if $(CI),,.venv/bin/)
DEPS := $(if $(CI),,$(STAMP))
PYTHON ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3.10)
ACT_IMAGE := gha-projects-act-runner:ubuntu-24.04
export PYTHONDONTWRITEBYTECODE ?= 1

.PHONY: help install up run run-fail test matrix-local lint format audit measure check down clean

help: ## list the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort
```

Header comment and variables. `STAMP` is the marker file `.venv/.installed`. `BIN ?= $(if $(CI),,.venv/bin/)` is the folder prefix for tools: empty when the environment variable `CI` is set (GitHub sets it, and the tools are already on the PATH), else `.venv/bin/`; `?=` lets the caller override it (`make lint BIN=`). `DEPS` is the marker on a developer's machine and empty in CI. `PYTHON ?= $(shell command -v python3.13 || ...)` picks the newest of Python 3.13, 3.12, 3.11, 3.10 found (`command -v` prints the path of a program). `ACT_IMAGE` names the runner image. `export PYTHONDONTWRITEBYTECODE ?= 1` tells Python not to write `.pyc` cache files. `.PHONY` lists targets that are commands, not files. `help` prints each target's description (the text after `##`).

Lines 15 to 24:

```make
$(STAMP): requirements-dev.txt pyproject.toml
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q --require-hashes -r requirements-dev.txt
	.venv/bin/pip install -q --no-deps -e .
	touch $@

install: $(DEPS) ## create .venv from the hash-pinned lock file

up: install ## install the tools and build the act runner image (Docker needed for run)
	docker build -q -t $(ACT_IMAGE) ci/act-runner
```

The `$(STAMP)` rule depends on `requirements-dev.txt` and `pyproject.toml`. Its recipe creates the virtual environment (`$(PYTHON) -m venv .venv`; a **virtual environment** is a private folder of installed packages for one project), installs the locked tools with hash checking (`-q` quiet, `--require-hashes`), installs the project itself in **editable** mode without dependencies (`pip install --no-deps -e .` links the source folder so edits take effect at once) and `touch`es the marker file. `install` needs that marker; `up` also builds the act runner image with Docker.

Lines 26 to 32:

```make
# The main workflow on this machine: the three Ubuntu legs of the matrix (act cannot run Windows jobs).

run: ## run the test job of ci.yml locally with act: the three Ubuntu legs of the matrix
	scripts/act-matrix.sh

# Lesson step 2: turn one matrix cell red with the DEMO_FAIL_ON_PYTHON variable and watch the others still report.

run-fail: ## run ci.yml locally with Python 3.10 failing on purpose: one red, two green
	scripts/act-matrix.sh --fail-on 3.10
```

`run` runs `scripts/act-matrix.sh`: the three Ubuntu cells of the matrix with `act` (which cannot run Windows jobs). `run-fail` passes `--fail-on 3.10` to turn one cell red on purpose.

Lines 34 to 42:

```make
test: $(DEPS) ## every test: domain, adapter, command line, and the pipeline scripts and workflows
	$(BIN)python -m pytest --cov --cov-report=term-missing --cov-fail-under=95

# The same tests on the matrix's three Python versions, in throwaway environments (needs uv and network).

matrix-local: ## run the tests on Python 3.10, 3.11 and 3.12 with uv
	@for version in 3.10 3.11 3.12; do \
	  echo "== Python $$version"; \
	  uv run --no-project --python $$version --with-requirements requirements.txt python -m pytest -q -p no:cacheprovider || exit 1; \
	done
```

`test` runs pytest with coverage: `--cov` measures, `--cov-report=term-missing` prints the lines no test ran, `--cov-fail-under=95` fails below 95 percent. `matrix-local` uses `uv` to run the tests on Python 3.10, 3.11 and 3.12 in a shell `for` loop: `$$version` has two dollar signs because Make would otherwise consume one; `\` continues the line; `uv run --no-project --python $$version --with-requirements requirements.txt` builds a throwaway environment per version; `|| exit 1` stops at the first failure.

Lines 44 to 58:

```make
lint: $(DEPS) ## ruff, format check, mypy, import-linter, actionlint, pin check
	$(BIN)ruff check .
	$(BIN)ruff format --check .
	$(BIN)mypy
	$(BIN)lint-imports
	actionlint
	shellcheck scripts/*.sh pipeline/*.sh
	$(BIN)python -m pipeline.pins

format: $(DEPS) ## apply ruff's formatting and safe fixes
	$(BIN)ruff check --fix .
	$(BIN)ruff format .

audit: $(DEPS) ## check the locked dependencies for known vulnerabilities
	$(BIN)pip-audit --no-deps --disable-pip -r requirements-dev.txt
```

`lint` runs, in order: `ruff check .`, `ruff format --check .`, `mypy`, `lint-imports` (the import-linter layer rules), `actionlint`, `shellcheck scripts/*.sh pipeline/*.sh` and `python -m pipeline.pins`. `format` applies ruff's safe fixes and formatting. `audit` runs `pip-audit --no-deps --disable-pip -r requirements-dev.txt`.

Lines 60 to 74:

```make
# make measure STAGE="1 plain (1 job)" RUNS="111 112 113"   (run ids from: gh run list --workflow measure-1-plain.yml)

STAGE ?= stage
measure: $(DEPS) ## print a README table row from three run ids: STAGE="..." RUNS="id id id"
	@mkdir -p build; files=""; for id in $(RUNS); do \
	  gh api repos/$${GH_REPO:-$$(gh repo view --json nameWithOwner -q .nameWithOwner)}/actions/runs/$$id/jobs --paginate > build/run-$$id.json; \
	  files="$$files build/run-$$id.json"; done; \
	$(BIN)python -m pipeline.billing --stage "$(STAGE)" $$files

check: lint test ## lint plus test

down: ## remove leftover act containers of this project's runner image
	-docker ps -aq --filter "ancestor=$(ACT_IMAGE)" | xargs docker rm -f

clean: down
	rm -rf .venv build .pytest_cache .mypy_cache .ruff_cache .import_linter_cache .coverage coverage.xml report.xml .tools
```

`measure` prints a README table row from run ids: `STAGE ?= stage` is a default. The recipe is one long shell command: it makes `build/`, loops over the run ids in `$(RUNS)`, downloads each run's job list with `gh api repos/<owner/repo>/actions/runs/<id>/jobs --paginate` into `build/run-<id>.json` (`$${GH_REPO:-$$(gh repo view ...)}` uses the variable or asks `gh` for the current repository; `$$` is how a dollar sign reaches the shell), then runs `python -m pipeline.billing --stage "$(STAGE)" <files>`. `check` is `lint` plus `test`. `down` removes leftover act containers of this project's image (`docker ps -aq --filter "ancestor=..."` lists their ids; `xargs docker rm -f` removes them; the leading `-` ignores failure). `clean` depends on `down` and deletes the virtual environment, caches and generated files.

<!-- /walk:Makefile -->

## Try it yourself

1. `make help` prints each target with its text, sorted.
2. `make -n test` prints what `make test` would run, without running it.
3. `make lint` runs all seven checks; the last line is `pins: every uses: is a full commit SHA, a local path or a digest`.
4. `CI=true make -n lint` prints the same commands without the `.venv/bin/` prefix.
5. `touch pyproject.toml && make -n install` shows the environment would be rebuilt, because a prerequisite is newer than the stamp.

## Mistakes people make

- Spaces instead of a tab at the start of a recipe line ("missing separator").
- Forgetting `.PHONY`, so a file named `test` stops `make test` from running.
- Using `$id` in a recipe when the shell variable needs `$$id`.
- Assuming each recipe line shares shell state with the line above it; each line is its own shell (so joined lines with `\` are used).
- Relying on features of GNU Make 4 on macOS, which ships GNU Make 3.81. This Makefile avoids them.

## Check yourself

1. What does `?=` do? *(Assigns only if the variable is not already set, so callers can override it.)*
2. Why is `.venv/.installed` a target with prerequisites? *(So the environment is rebuilt only when the lock file or `pyproject.toml` changes.)*
3. What does `$$version` mean in a recipe? *(The shell variable `version`; Make turns `$$` into one `$`.)*
4. What does a leading `-` on a recipe line do? *(Make ignores that line's failure.)*
5. Why does `make lint BIN=` work in CI? *(An empty `BIN` makes the recipe call tools by name from the `PATH`.)*

## Further reading

- GNU Make manual (macOS has 3.81; Linux CI has 4.3): https://www.gnu.org/software/make/manual/make.html
