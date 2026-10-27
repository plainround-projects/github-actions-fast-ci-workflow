# TOML

## What it is

TOML is a text format for configuration files. It looks like an INI file with more rules: `[section]` headers, `key = value` lines, quoted text, lists in square brackets. A program reads it into a tree of named values. `pyproject.toml` is the file Python tools agree to use for project settings.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **package**: In Python, a folder with an `__init__.py` file that can be imported as a unit; also a bundle of code installed with pip.
- **library**: A package of ready-made code that your program calls.
- **lock file**: A file that records the exact version, and a checksum, of every package that was installed, so that everyone installs exactly the same thing.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.
- **function**: A named piece of code that takes inputs (parameters), does something, and may return a result.
- **list**: An ordered collection of values written one after another.
- **version**: A number such as `1.2.3` that names one release of software (major.minor.patch).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **docstring**: A text in triple quotes at the start of a Python file, class or function that documents it; tools and people can read it.
- **pytest**: A Python test framework: it finds functions named `test_...`, runs them, and reports failures.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

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

<!-- walk:pyproject.toml -->
### `pyproject.toml`, line by line

Lines 1 to 3:

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
```

`[build-system]` says how to build the package: it needs `setuptools` 75 or newer, and `build-backend` names the entry point of the tool that builds.

Lines 5 to 19:

```toml
[project]
name = "mathkit"
version = "0.1.0"
description = "A tiny math library: the test subject of a fast GitHub Actions CI workflow."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Sumit Srivastava" }]
dependencies = ["numpy==2.1.3", "pandas==2.2.3"]

[project.scripts]
mathkit = "mathkit.interfaces.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

`[project]`: the name (`mathkit`), version, description, readme, `requires-python = ">=3.10"`, license, authors, and `dependencies = ["numpy==2.1.3", "pandas==2.2.3"]`, the packages the library needs, pinned exactly. `[project.scripts]` creates a command `mathkit` that runs the function `main` in `mathkit.interfaces.cli`. `[tool.setuptools.packages.find] where = ["src"]` tells setuptools to look for packages under `src`.

Lines 21 to 30:

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

`[tool.ruff]`: line length 120, target Python 3.10, and the folders that hold the project's own code (`src`) so ruff can sort imports correctly. `[tool.ruff.lint] select` lists rule families (E and F basic checks, I import order, B likely bugs, UP newer syntax, SIM simplifications, N naming, C4 comprehensions, RUF ruff's own, PT pytest style, D100 to D104 docstrings). `[tool.ruff.lint.per-file-ignores]` turns the docstring rules off for tests.

Lines 32 to 48:

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

# Test functions are named for the behavior they check; annotating every one adds noise, not safety.

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
disallow_incomplete_defs = false
disallow_untyped_calls = false
```

`[tool.mypy]`: Python 3.10, `strict = true`, the folders to check, `mypy_path = ["src"]` and `explicit_package_bases = true` so module names are computed from `src`. The first `[[tool.mypy.overrides]]` (double brackets make a list of tables) tells mypy to ignore missing type information for `pandas`. The second relaxes three rules for modules matching `tests.*`, with a comment saying why: tests are named for the behavior they check and annotating each adds noise, not safety.

Lines 50 to 60:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
addopts = "-ra --strict-markers"

[tool.coverage.run]
source = ["mathkit", "pipeline"]
branch = true

[tool.coverage.report]
show_missing = true
```

`[tool.pytest.ini_options]`: tests live in `tests`; `pythonpath = ["src", "."]` adds those folders to Python's import path; `addopts = "-ra --strict-markers"` adds options to every run (`-ra` prints a short summary of all non-passing tests, `--strict-markers` makes an unknown marker an error). `[tool.coverage.run]` measures `mathkit` and `pipeline`, counting branches; `[tool.coverage.report] show_missing` lists untested lines.

<!-- /walk:pyproject.toml -->

<!-- walk:requirements.in -->
### `requirements.in`, line by line

Lines 1 to 7:

```text
# The runtime and test dependencies the matrix jobs install. numpy and pandas are here on purpose:

# their install is slow enough that the dependency cache has something to save.

numpy==2.1.3
pandas==2.2.3
pytest==9.0.3
pytest-cov==5.0.0
PyYAML==6.0.2
```

The input of the lock for the matrix jobs: a comment explaining that numpy and pandas are here on purpose, because their install is slow enough for the cache to have something to save, then five exact pins: numpy, pandas, pytest, pytest-cov, PyYAML.

<!-- /walk:requirements.in -->

<!-- walk:requirements-dev.in -->
### `requirements-dev.in`, line by line

Lines 1 to 7:

```text
# Everything in requirements.in plus the format, lint, type, import-rule and audit tools of the lint job.

-r requirements.in
ruff==0.8.4
mypy==1.13.0
types-PyYAML==6.0.12.20241230
import-linter==2.1
pip-audit==2.7.3
```

The input of the tools' lock: `-r requirements.in` includes the first file, and the rest are the lint, type, import-rule and audit tools: ruff, mypy, types-PyYAML, import-linter, pip-audit.

<!-- /walk:requirements-dev.in -->

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
