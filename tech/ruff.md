# Ruff

## What it is

Ruff is a **linter** and a **formatter** for Python, written in Rust. A linter reads source code without running it and reports likely mistakes and style problems. A formatter rewrites code into one agreed layout (line breaks, quotes, spacing). Ruff does both, very fast. This repository pins ruff 0.8.4.

## Why this repository uses it

The template requires "a formatter and a linter configured in the repository and run in CI". One tool for both keeps the setup small. The `lint` job and `make lint` run `ruff check` and `ruff format --check`.

## Where it appears

| Path | What it does with ruff |
| --- | --- |
| `pyproject.toml` | `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.per-file-ignores]`. |
| `Makefile` | `lint` runs `ruff check .` and `ruff format --check .`; `format` runs `ruff check --fix .` and `ruff format .`. |
| `requirements-dev.txt` | The pin and its hashes. |

## How it works underneath

Ruff parses each Python file into a tree (the **abstract syntax tree**), then runs rules over the tree. Each rule has a code: a letter group and a number (`E501` line too long, `I001` imports not sorted). `ruff check` prints findings and exits non-zero if any exist; `--fix` applies the safe automatic fixes. `ruff format` is a formatter compatible with the Black style; with `--check` it only reports files that would change.

## Walkthrough of this repository's use

```toml
[tool.ruff]
line-length = 120
target-version = "py310"
src = ["src", "tests", "pipeline"]
```

`line-length = 120` is the wrap width. `target-version = "py310"` tells ruff the oldest Python to support, so it does not suggest syntax that 3.10 lacks. `src` lists the folders that hold first-party code, which the import-sorting rule needs to decide what is "ours".

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "N", "C4", "RUF", "PT", "D100", "D101", "D102", "D103", "D104"]
```

The rule families turned on:

| Code | Family |
| --- | --- |
| `E` | pycodestyle errors (such as long lines) |
| `F` | pyflakes (unused imports, undefined names) |
| `I` | isort (import order) |
| `B` | bugbear (likely bugs) |
| `UP` | pyupgrade (use newer syntax when `target-version` allows) |
| `SIM` | simplifications |
| `N` | naming |
| `C4` | comprehension style |
| `RUF` | ruff's own rules |
| `PT` | pytest style |
| `D100`..`D104` | a docstring is required on public modules, classes, methods, functions and packages |

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D"]
```

Tests do not need docstrings: the test name is the documentation.

In practice: `make format` fixes layout; `make lint` fails on a long line, an unsorted import, or a public function without a docstring.

## Try it yourself

1. `.venv/bin/ruff --version` prints `ruff 0.8.4`.
2. `.venv/bin/ruff check .` prints `All checks passed!`.
3. `.venv/bin/ruff format --check .` prints `39 files already formatted` (the count may change).
4. Break a rule in a copy: `printf 'import os\n' > /tmp/x.py && .venv/bin/ruff check /tmp/x.py` reports `F401 os imported but unused`.
5. `.venv/bin/ruff rule D103` explains one rule.

## Mistakes people make

- Running the formatter and the linter in different tools with different widths.
- Silencing a rule everywhere instead of for the one file that needs it.
- Not setting `target-version`, so ruff suggests syntax newer than the oldest supported Python.
- Letting `--fix` rewrite files in CI; CI here only checks.

## Check yourself

1. Linter versus formatter? *(A linter reports problems; a formatter rewrites layout.)*
2. What does `--check` do on `ruff format`? *(Reports files that would change and exits non-zero, without writing.)*
3. Why `target-version = "py310"`? *(So suggestions respect the oldest supported Python.)*
4. What do `D100` to `D104` require? *(Docstrings on public modules, classes, methods, functions and packages.)*
5. Why are tests exempt from `D`? *(Their names are written as behavior; docstrings would be noise.)*

## Further reading

- Ruff 0.8 documentation: https://docs.astral.sh/ruff/
- Rule list: https://docs.astral.sh/ruff/rules/
