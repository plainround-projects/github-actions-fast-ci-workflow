# Make

## What it is

Make is a command-line tool that runs named recipes from a file called `Makefile`. Each recipe is a **target**: a name, the things it depends on, and the shell commands that build it. Make was designed to rebuild only what is out of date by comparing file times. Today many projects also use it as a short list of named commands (`make test`, `make lint`).

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
