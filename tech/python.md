# Python

## What it is

Python is a programming language. You write instructions in text files that end in `.py`, and a program called the **interpreter** reads them and carries them out one at a time. This repository supports Python 3.10, 3.11 and 3.12 in CI (`requires-python = ">=3.10"` in `pyproject.toml`) and was developed with 3.13.

A **module** is one `.py` file. A **package** is a folder of modules with a name. This repository has two packages: `mathkit` (the library under test, in `src/mathkit/`) and `pipeline` (scripts the workflows call, in `pipeline/`).

## Why this repository uses it

The lesson needs a small library for the CI workflow to build and test. The lesson's own starting point is a Python library, and Python makes the matrix interesting: one set of tests run on three interpreter versions. The `pipeline/` scripts are Python too, so the parts of the workflow that are more than one command can be tested like any other code.

## Where it appears

| Path | What it does with Python |
| --- | --- |
| `src/mathkit/domain/` | Pure rules: arithmetic, statistics, the summary value, named errors. Standard library only. |
| `src/mathkit/application/` | The use case `SummarizeTable` and the `ColumnSource` port (a description of what it needs). |
| `src/mathkit/infrastructure/pandas_source.py` | The only module that imports pandas and numpy. |
| `src/mathkit/interfaces/cli.py`, `__main__.py` | The command line. |
| `pipeline/*.py` | Workflow helper scripts: gate, billing, cache key, path filter, slowest tests, pin check. |
| `tests/` | Test functions (see `pytest.md`). |

## How it works underneath

You run a program with `python -m mathkit add 2 3`. The `-m` flag means "run this package by name". The interpreter finds `mathkit/__main__.py`, turns the text into **bytecode** (a compact internal form), and runs it from the first line. An `import` runs another module once and gives you names from it. The **standard library** is the set of modules that ship with Python (`math`, `argparse`, `json`, `hashlib`, `datetime`). Anything else (pandas, numpy, pytest) must be installed first (see `pip.md`).

Everything is an **object**. A variable is a name pointing at an object. A function is an object you can call. A class is a recipe for making objects.

Python does not check types while running. You can write **type hints** (`order: str`) to say what you expect. The interpreter ignores them at run time; mypy (see `mypy.md`) reads them and finds mistakes without running anything.

## Walkthrough of this repository's use

### Postponed type hints

```python
from __future__ import annotations
```

Almost every file starts with this line. It keeps type hints as text instead of evaluating them when the file loads, so a hint can name a class defined further down, and newer hint syntax works on older Python.

### Union types with `|`

```python
Number = int | float
```

`int | float` means "an int or a float". Writing a union with `|` needs Python 3.10, which is why 3.10 is the oldest version here. `Number` is just a name for that type.

### Functions, docstrings and named errors

```python
def divide(left: Number, right: Number) -> float:
    """Return ``left / right``; raise :class:`DivisionByZeroError` when ``right`` is zero."""
    if right == 0:
        raise DivisionByZeroError("cannot divide by zero")
    return left / right
```

`def` defines a function. `left: Number` is a parameter with a type hint; `-> float` is the promised result type. The triple-quoted text is a **docstring**: documentation that tools can read. `raise` stops the function and sends an error up to whoever called it. The error class is one of the repository's own:

```python
class MathkitError(Exception):
    """Base class of every error mathkit raises on purpose."""


class DivisionByZeroError(MathkitError):
    """The divisor was zero."""
```

A class in brackets inherits from another. Because every error derives from `MathkitError`, the command line can catch all deliberate errors with one `except MathkitError` and let real bugs crash loudly.

### Dataclasses: small immutable objects

```python
@dataclass(frozen=True, slots=True)
class ColumnSummary:
    name: str
    count: int
    mean: float
    median: float
    minimum: float
    maximum: float

    @classmethod
    def of(cls, name: str, values: Sequence[float]) -> ColumnSummary:
        return cls(name=name, count=len(values), mean=statistics.mean(values), ...)
```

`@dataclass` is a **decorator** (a line starting with `@` that wraps what is below). From the list of fields it writes `__init__`, `__eq__` and `__repr__`. `frozen=True` makes objects read-only after creation, so no code can change a summary by accident (an **immutable value object**). `slots=True` stores fields in a fixed layout, which uses less memory and forbids adding new fields. `@classmethod` makes `of` a factory called on the class: `ColumnSummary.of("price", [1.0])`.

### Protocols: describing a port without inheritance

```python
class ColumnSource(Protocol):
    def numeric_columns(self, table_text: str) -> dict[str, tuple[float, ...]]:
        ...
```

A `Protocol` says "any object with this method fits". The use case asks for a `ColumnSource`; the pandas adapter satisfies it without naming the protocol, and tests pass in a small fake. `tuple[float, ...]` means a tuple of any length whose items are floats.

### A class that can be called

```python
class SummarizeTable:
    def __init__(self, source: ColumnSource) -> None:
        self._source = source

    def __call__(self, table_text: str) -> tuple[ColumnSummary, ...]:
        columns = self._source.numeric_columns(table_text)
        if not columns:
            raise InvalidTableError("the table has no numeric column")
        return tuple(ColumnSummary.of(name, values) for name, values in columns.items())
```

`__init__` runs when you build the object and stores its dependency in `self`. A name starting with `_` is "private by habit". `__call__` lets you write `SummarizeTable(source)(text)`. `(... for ... in ...)` inside `tuple(...)` is a **generator expression**: it makes the items one by one.

### Generators and iterators

```python
def uses_values(document: Any) -> Iterator[str]:
    ...
        yield str(job["uses"])
```

A function with `yield` is a **generator**. Calling it returns an object; each request for the next item runs the body to the next `yield`. `pipeline/pins.py` uses this so it never builds a full list it does not need.

### Command line with `argparse`

```python
parser = argparse.ArgumentParser(prog="mathkit", description="Small math helpers.")
commands = parser.add_subparsers(dest="command", required=True)
for name in _OPERATIONS:
    command = commands.add_parser(name, help=f"{name} two numbers")
    command.add_argument("left", type=float)
```

`argparse` (standard library) turns `["add", "2", "3"]` into named values. Sub-parsers give each word (`add`, `summarize`) its own arguments. `type=float` converts the text. `f"{name} two numbers"` is an **f-string**: text with `{expression}` holes.

### The entry point and exit codes

```python
def main(argv: Sequence[str] | None = None) -> int:
    ...
    except MathkitError as error:
        print(f"mathkit: {error}", file=sys.stderr)
        return 1
    return 0
```

```python
sys.exit(main())
```

`main` returns a number and `__main__.py` passes it to `sys.exit`. By convention 0 means success and anything else means failure; the shell and CI read it. Errors go to `sys.stderr` (the error stream), results to standard output.

### Time, hashes and regular expressions in `pipeline/`

`pipeline/billing.py` uses `datetime.fromisoformat(text.replace("Z", "+00:00"))` because Python 3.10 cannot read a trailing `Z` itself. `pipeline/cache_key.py` uses `hashlib.sha256` to copy GitHub's `hashFiles()` rule. `pipeline/pathfilter.py` builds a **regular expression** (a pattern language for matching text) from GitHub's glob rules, for example `*` becomes `[^/]*` and `**` becomes `.*`.

## Try it yourself

1. `.venv/bin/python -m mathkit add 2 3` prints `5`.
2. `.venv/bin/python -m mathkit divide 1 0; echo "exit $?"` prints `mathkit: cannot divide by zero` and `exit 1`.
3. `printf 'x,y\n1,10\n3,20\n' > /tmp/t.csv && .venv/bin/python -m mathkit summarize /tmp/t.csv` prints `x: count=2 mean=2 median=2 min=1 max=3` and a similar line for `y`.
4. `.venv/bin/python -c "from mathkit.domain.summary import ColumnSummary as C; s=C.of('a',[1.0]); s.count=2"` raises `FrozenInstanceError`, showing `frozen=True` at work.
5. `.venv/bin/python -c "print(0.1 + 0.2, __import__('math').fsum([0.1] * 10))"` prints `0.30000000000000004 1.0`: floats are binary approximations, and `math.fsum` (used in `statistics.py`) adds many floats with the least possible rounding error. On Python 3.11 and older, plain `sum([0.1] * 10)` gives `0.9999999999999999`; 3.12 improved `sum`, and `fsum` keeps the result the same on every version in the matrix.

## Mistakes people make

- Unquoted or mis-typed type hints that crash on older versions; `from __future__ import annotations` avoids it.
- Changing a list while looping over it.
- Using a mutable default argument (`def f(x=[])`). This code uses `None` and builds the value inside.
- Catching `Exception` everywhere and hiding bugs. Here only the repository's own error base class is caught.
- Treating `0.1 + 0.2` as exact. Floats are binary approximations.

## Check yourself

1. What does `python -m mathkit` run? *(The package's `__main__.py`.)*
2. What does `frozen=True` change? *(Objects cannot be modified after they are built.)*
3. Why do all errors derive from `MathkitError`? *(One `except` can catch the deliberate ones and leave bugs visible.)*
4. What makes `uses_values` a generator? *(It contains `yield`.)*
5. Why must `main` return a number? *(`sys.exit` turns it into the process's exit code, which shells and CI read.)*

## Further reading

- Python 3.12 tutorial and reference (this repository supports 3.10 to 3.12): https://docs.python.org/3.12/
- `dataclasses`: https://docs.python.org/3.12/library/dataclasses.html
- `typing.Protocol`: https://docs.python.org/3.12/library/typing.html#typing.Protocol
- `argparse`: https://docs.python.org/3.12/library/argparse.html
