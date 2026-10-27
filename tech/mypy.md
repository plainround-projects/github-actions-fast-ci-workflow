# mypy

## What it is

mypy is a **static type checker** for Python. Python lets you write **type hints**, such as `def add(left: int, right: int) -> int`, but the interpreter ignores them. mypy reads them without running the code and reports places where the types do not fit, for example passing text where a number is expected. This repository pins mypy 1.13.0.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **CI**: Continuous integration: running checks (build, tests, linters) automatically every time code changes.
- **YAML**: A plain-text format for structured data that uses indentation instead of braces. GitHub workflows are YAML files.
- **package**: In Python, a folder with an `__init__.py` file that can be imported as a unit; also a bundle of code installed with pip.
- **library**: A package of ready-made code that your program calls.
- **module**: A file, or a folder of files, that other code can load and use. In Terraform, a module is a folder of configuration used like a function.
- **function**: A named piece of code that takes inputs (parameters), does something, and may return a result.
- **class**: A blueprint for objects: it bundles data and the functions that work on it. `new Name(...)` or `Name(...)` makes an object from it.
- **boolean**: A value that is either true or false.
- **version**: A number such as `1.2.3` that names one release of software (major.minor.patch).
- **test**: A small program that uses your code and checks that the answer is the one you expected.

</details>

<!-- /words -->

## Why this repository uses it

The template asks for typed code checked in CI. Types catch a class of mistakes early and document what each function takes and returns. The `pipeline/` scripts are code too, so they are checked with the same strict rules.

## Where it appears

| Path | What it does with mypy |
| --- | --- |
| `pyproject.toml` | `[tool.mypy]` with `strict = true`, plus two overrides. |
| `Makefile` | `lint` runs `mypy` with no arguments (the files come from the config). |
| `src/mathkit/py.typed` | An empty marker file telling other tools that this package ships type hints. |
| `requirements-dev.in` | Pins mypy and `types-PyYAML`. |

## How it works underneath

mypy parses every listed file, builds a model of every function's declared types, and checks each call and return against them. It does not execute the program. When a library has no type information, mypy cannot check calls into it. Some libraries ship hints (a `py.typed` file); others have a separate "stubs" package (`types-PyYAML`) with only the signatures.

## Walkthrough of this repository's use

```toml
[tool.mypy]
python_version = "3.10"
strict = true
files = ["src", "tests", "pipeline"]
mypy_path = ["src"]
explicit_package_bases = true
```

`python_version = "3.10"` checks against the oldest supported syntax. `strict = true` turns on all the optional strict checks: every function must have hints, `Any` must not leak, untyped calls are errors. `files` lists what to check. `mypy_path` and `explicit_package_bases` help mypy find `mathkit` under `src/` and name modules correctly.

```toml
[[tool.mypy.overrides]]
module = ["pandas", "pandas.*"]
ignore_missing_imports = true
```

pandas ships no usable hints for strict mode. Rather than add a heavy stubs package, the override says "do not complain about pandas". All pandas use is in one module that converts to plain Python types.

```toml
[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
disallow_incomplete_defs = false
disallow_untyped_calls = false
```

Test functions are named for behavior; annotating every one would add noise, so tests are exempt from the "must have hints" checks only.

Type hints you will see: `Sequence[float]` (any read-only ordered collection of floats), `dict[str, tuple[float, ...]]`, `Mapping[str, Any]`, `Iterator[str]`, `Path | None`, and `Protocol` for ports.

A typical catch: in `tests/pipeline/test_workflows.py` the helper must return `dict[Any, Any]`, not `dict[str, Any]`, because the loaded YAML has the boolean key `True` for `on:`. mypy flagged the `str`-keyed version.

## Try it yourself

1. `.venv/bin/mypy --version` prints `mypy 1.13.0 (compiled: yes)`.
2. `.venv/bin/mypy` prints `Success: no issues found in 39 source files`.
3. Make an error in a copy: `printf 'def f(x: int) -> str:\n    return x\n' > /tmp/y.py && .venv/bin/mypy --strict /tmp/y.py` reports `Incompatible return value type (got "int", expected "str")`.
4. `.venv/bin/mypy --strict --python-version 3.10 pipeline/gate.py` checks one file.

## Mistakes people make

- Believing hints are enforced at run time. They are not.
- Using `Any` to silence an error, which switches checking off for everything it touches.
- `# type: ignore` without an error code; this repository's ignore comments name the code.
- Forgetting the stubs package for a typed-looking library.

## Check yourself

1. Does Python check type hints when it runs? *(No; mypy does, ahead of time.)*
2. What does `strict = true` do? *(Enables all optional strict checks.)*
3. Why is pandas in `ignore_missing_imports`? *(It has no usable type information for strict mode.)*
4. What is `types-PyYAML`? *(A stubs package with type hints for PyYAML.)*
5. What does `py.typed` signal? *(That the package ships type hints.)*

## Further reading

- mypy 1.13 documentation: https://mypy.readthedocs.io/en/v1.13.0/
- Type hints cheat sheet: https://mypy.readthedocs.io/en/v1.13.0/cheat_sheet_py3.html
