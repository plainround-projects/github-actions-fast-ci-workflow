# TOML

## What it is

TOML is a text format for configuration files. It looks like an INI file with more rules: `[section]` headers, `key = value` lines, quoted text, lists in square brackets. A program reads it into a tree of named values. `pyproject.toml` is the file Python tools agree to use for project settings.

## Why this repository uses it

One file, `pyproject.toml`, holds the settings for the package (name, version, dependencies, entry point) and for every tool that checks the code: ruff, mypy, pytest, coverage and import-linter. Keeping them in one place means one file to read to see how the project is checked.

## Where it appears

| Path | What it does with TOML |
| --- | --- |
| `pyproject.toml` | All project metadata and tool settings. |

## How it works underneath

Each tool opens `pyproject.toml` itself and reads only its own section. A section name like `[tool.ruff.lint]` means "inside `tool`, inside `ruff`, inside `lint`". `[[tool.mypy.overrides]]` with double brackets means "one more item in a list of tables called `overrides`": you can write it many times. Python 3.11 added a TOML reader to the standard library (`tomllib`); older versions use a small package (`tomli`, which the lock file lists for Python 3.10).

## Walkthrough of this repository's use

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
```

Says how to build the package into an installable form: with setuptools version 75 or newer.

```toml
[project]
name = "mathkit"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["numpy==2.1.3", "pandas==2.2.3"]

[project.scripts]
mathkit = "mathkit.interfaces.cli:main"
```

`requires-python` is the oldest Python allowed. `dependencies` are installed together with the package. `[project.scripts]` creates a command named `mathkit` that calls the function `main` in `mathkit/interfaces/cli.py`.

```toml
[tool.ruff]
line-length = 120
target-version = "py310"
src = ["src", "tests", "pipeline"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "N", "C4", "RUF", "PT", "D100", "D101", "D102", "D103", "D104"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D"]
```

Ruff (see `ruff.md`) settings. `select` is the list of rule families to turn on; each letter group is a rule family (for example `I` is import sorting and `D1xx` asks for docstrings). `per-file-ignores` turns off the docstring rules for tests.

```toml
[tool.mypy]
python_version = "3.10"
strict = true
files = ["src", "tests", "pipeline"]
mypy_path = ["src"]
explicit_package_bases = true

[[tool.mypy.overrides]]
module = ["pandas", "pandas.*"]
ignore_missing_imports = true
```

Mypy (see `mypy.md`) in strict mode, checking three folders. The override says "do not complain that pandas has no type information". A second override relaxes the rules for test modules.

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
addopts = "-ra --strict-markers"
```

Pytest (see `pytest.md`) looks for tests in `tests/`, puts `src` and the repository root on the import path so `import mathkit` and `import pipeline` work without installing, and always adds `-ra` (summarize skipped tests) and `--strict-markers` (typos in marker names are errors).

```toml
[tool.coverage.run]
source = ["mathkit", "pipeline"]
branch = true
```

Measure coverage of the two packages, counting branches (both sides of every `if`), not just lines.

```toml
[tool.importlinter]
root_package = "mathkit"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Layers: interfaces -> infrastructure -> application -> domain, never upward"
type = "layers"
layers = ["mathkit.interfaces", "mathkit.infrastructure", "mathkit.application", "mathkit.domain"]
```

Import-linter (see `import-linter.md`): a layer may import only from layers listed after it.

## Try it yourself

1. Read it with Python: `.venv/bin/python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['name'], d['project']['requires-python'])"` prints `mathkit >=3.10`.
2. List the tool sections: `.venv/bin/python -c "import tomllib; print(list(tomllib.load(open('pyproject.toml','rb'))['tool']))"` prints `['setuptools', 'ruff', 'mypy', 'pytest', 'coverage', 'importlinter']`.
3. Run the command the file defines: `.venv/bin/mathkit add 2 3` prints `5`.

## Mistakes people make

- Forgetting quotes around text values.
- Single brackets where double are needed (`[tool.mypy.overrides]` instead of `[[tool.mypy.overrides]]`), which makes a table instead of a list item.
- Putting the same tool's settings in two files (`pyproject.toml` and `setup.cfg`), so nobody knows which wins.

## Check yourself

1. What does `[[tool.mypy.overrides]]` mean? *(One more item in a list of override tables.)*
2. What creates the `mathkit` command? *(`[project.scripts]`.)*
3. Why is `pythonpath` set for pytest? *(So tests can import the code without installing it.)*
4. Which tool reads `[tool.importlinter]`? *(import-linter, via `lint-imports`.)*
5. What does `branch = true` add to coverage? *(It counts each side of a decision, not only whether a line ran.)*

## Further reading

- TOML 1.0 specification: https://toml.io/en/v1.0.0
- Python packaging guide for `pyproject.toml`: https://packaging.python.org/en/latest/specifications/pyproject-toml/
