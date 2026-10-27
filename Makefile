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

$(STAMP): requirements-dev.txt pyproject.toml
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q --require-hashes -r requirements-dev.txt
	.venv/bin/pip install -q --no-deps -e .
	touch $@

install: $(DEPS) ## create .venv from the hash-pinned lock file

up: install ## install the tools and build the act runner image (Docker needed for run)
	docker build -q -t $(ACT_IMAGE) ci/act-runner

# The main workflow on this machine: the three Ubuntu legs of the matrix (act cannot run Windows jobs).
run: ## run the test job of ci.yml locally with act: the three Ubuntu legs of the matrix
	scripts/act-matrix.sh

# Lesson step 2: turn one matrix cell red with the DEMO_FAIL_ON_PYTHON variable and watch the others still report.
run-fail: ## run ci.yml locally with Python 3.10 failing on purpose: one red, two green
	scripts/act-matrix.sh --fail-on 3.10

test: $(DEPS) ## every test: domain, adapter, command line, and the pipeline scripts and workflows
	$(BIN)python -m pytest --cov --cov-report=term-missing --cov-fail-under=95

# The same tests on the matrix's three Python versions, in throwaway environments (needs uv and network).
matrix-local: ## run the tests on Python 3.10, 3.11 and 3.12 with uv
	@for version in 3.10 3.11 3.12; do \
	  echo "== Python $$version"; \
	  uv run --no-project --python $$version --with-requirements requirements.txt python -m pytest -q -p no:cacheprovider || exit 1; \
	done

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
