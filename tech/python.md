# Python

## What it is

Python is a programming language. You write instructions in text files that end in `.py`, and a program called the **interpreter** reads them and carries them out one at a time. This repository supports Python 3.10, 3.11 and 3.12 in CI (`requires-python = ">=3.10"` in `pyproject.toml`) and was developed with 3.13.

A **module** is one `.py` file. A **package** is a folder of modules with a name. This repository has two packages: `mathkit` (the library under test, in `src/mathkit/`) and `pipeline` (scripts the workflows call, in `pipeline/`).

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **command line**: The text you type after the prompt in a terminal to run a program, such as `npm test`. The words after the program name are its **arguments**; words that start with `-` or `--` are **options** (also called flags).
- **shell**: The program inside a terminal that reads what you type and starts other programs. Bash is a shell.
- **environment variable**: A named piece of text that is handed to a program by whoever starts it, for example `HOME` or `CI`. Programs read them to learn about the setting they run in.
- **process**: A program while it is running, with its own memory. Starting a program creates a process; when it ends the process is gone.
- **standard output**: The stream where a program writes its normal results (its counterpart, standard error, is for problems).
- **stream**: A flow of data that is written or read piece by piece, such as the text a program prints.
- **glob**: A pattern for file names with wildcards: `*` matches any characters inside one name, `**` matches across folders, `?` matches one character. `src/**/*.ts` means every `.ts` file below `src`.
- **SHA**: A family of hash functions. A Git **commit SHA** is a 40-character hexadecimal fingerprint that names one exact commit.
- **commit**: A saved snapshot of a project's files in Git, with a message and an author. Every commit has a unique 40-character name (its SHA).
- **tag**: A name attached to a commit in Git, usually a version such as `v1.0.0`. Unlike a commit's SHA, a tag can be moved to another commit.
- **runner**: The computer, usually a virtual machine, on which GitHub runs a job. It starts clean for every job.
- **secret**: A value such as a password stored in a repository's settings. Workflows can read it, but GitHub hides it in logs.
- **CI**: Continuous integration: running checks (build, tests, linters) automatically every time code changes.
- **API**: Application programming interface: a set of requests a program can send to another program or service, with documented answers. A web API is called over the internet with HTTP.
- **JSON**: A plain-text format for structured data: objects `{ "name": "value" }`, lists `[1, 2]`, texts in double quotes, numbers, `true`, `false`, `null`. It has no comments.
- **YAML**: A plain-text format for structured data that uses indentation instead of braces. GitHub workflows are YAML files.
- **Markdown**: A plain-text way to write formatted documents: `#` for headings, `-` for bullets, backticks for code, `|` for tables.
- **image**: A read-only package that holds everything needed to start a container: a file system plus settings. A running **container** is made from an image.
- **Docker**: A tool that builds images and runs containers.
- **dependency**: A package that your project needs in order to work.
- **lock file**: A file that records the exact version, and a checksum, of every package that was installed, so that everyone installs exactly the same thing.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.
- **interface**: A description of the shape something must have: which fields and methods. Code that depends only on the interface can accept any object of that shape.
- **array**: An ordered list of values.
- **list**: An ordered collection of values written one after another.
- **folder**: A container for files and other folders on disk (also called a directory).
- **UTF-8**: The usual way of storing text as bytes, able to represent every written language.
- **version**: A number such as `1.2.3` that names one release of software (major.minor.patch).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **comprehension**: A short way to build a list, set or dictionary from a loop in one expression, such as `[x * 2 for x in items if x > 0]`.
- **tuple**: An unchangeable ordered list of values in Python, written `(a, b)`.
- **pytest**: A Python test framework: it finds functions named `test_...`, runs them, and reports failures.
- **argparse**: A Python standard-library module that reads command-line arguments and options.
- **XML**: A plain-text format made of nested tags such as `<testcase name="x" time="0.1"/>`.
- **JUnit**: A common XML layout for test reports: a `<testsuite>` containing one `<testcase>` per test.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

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

<!-- walk:src/mathkit/__init__.py -->
### `src/mathkit/__init__.py`, line by line

Lines 1 to 7:

```python
"""mathkit: a tiny math library, the test subject of the fast CI workflow."""

from mathkit.domain.arithmetic import add, divide, multiply, subtract
from mathkit.domain.statistics import mean, median

__all__ = ["add", "divide", "mean", "median", "multiply", "subtract"]
__version__ = "0.1.0"
```

A package marker file. A folder of Python files becomes a **package** (importable as a unit) when it contains a file named `__init__.py`. The text in triple quotes is the package's **docstring** (documentation that tools and people can read). This one also does real work: `from mathkit.domain.arithmetic import add, divide, multiply, subtract` and the same for `mean` and `median` copy those names into the package, so users can write `from mathkit import add`. `__all__` is a list of the names that `from mathkit import *` should expose and that tools treat as the public interface. `__version__ = "0.1.0"` is the library's version number, a convention that other tools read.

<!-- /walk:src/mathkit/__init__.py -->

<!-- walk:src/mathkit/domain/__init__.py -->
### `src/mathkit/domain/__init__.py`, line by line

Lines 1 to 1:

```python
"""Pure rules of mathkit: arithmetic, statistics and the summary value object. No I/O, no third-party imports."""
```

A package marker file. A folder of Python files becomes a **package** (importable as a unit) when it contains a file named `__init__.py`. The text in triple quotes is the package's **docstring** (documentation that tools and people can read). The domain layer holds the pure rules: arithmetic, statistics and the summary value; it does no input or output and imports no third-party package.

<!-- /walk:src/mathkit/domain/__init__.py -->

<!-- walk:src/mathkit/application/__init__.py -->
### `src/mathkit/application/__init__.py`, line by line

Lines 1 to 1:

```python
"""Use cases of mathkit and the ports they need. Depends on the domain only."""
```

A package marker file. A folder of Python files becomes a **package** (importable as a unit) when it contains a file named `__init__.py`. The text in triple quotes is the package's **docstring** (documentation that tools and people can read). The application layer holds the use cases and the **ports** (descriptions of what they need from outside); it depends on the domain only.

<!-- /walk:src/mathkit/application/__init__.py -->

<!-- walk:src/mathkit/infrastructure/__init__.py -->
### `src/mathkit/infrastructure/__init__.py`, line by line

Lines 1 to 1:

```python
"""Adapters that implement the application's ports with third-party libraries."""
```

A package marker file. A folder of Python files becomes a **package** (importable as a unit) when it contains a file named `__init__.py`. The text in triple quotes is the package's **docstring** (documentation that tools and people can read). The infrastructure layer holds adapters that implement the ports with third-party libraries (here pandas).

<!-- /walk:src/mathkit/infrastructure/__init__.py -->

<!-- walk:src/mathkit/interfaces/__init__.py -->
### `src/mathkit/interfaces/__init__.py`, line by line

Lines 1 to 1:

```python
"""Entry points: the command-line program. Wires adapters into use cases; nothing depends on this layer."""
```

A package marker file. A folder of Python files becomes a **package** (importable as a unit) when it contains a file named `__init__.py`. The text in triple quotes is the package's **docstring** (documentation that tools and people can read). The interfaces layer holds the entry points, here the command line. It wires adapters into use cases; nothing depends on it.

<!-- /walk:src/mathkit/interfaces/__init__.py -->

<!-- walk:pipeline/__init__.py -->
### `pipeline/__init__.py`, line by line

Lines 1 to 1:

```python
"""Scripts the workflows call and the tests exercise: billing, cache keys, the gate, path filters, pin checks."""
```

A package marker file. A folder of Python files becomes a **package** (importable as a unit) when it contains a file named `__init__.py`. The text in triple quotes is the package's **docstring** (documentation that tools and people can read). This one makes `pipeline` importable, so the workflows can run `python -m pipeline.gate` and the tests can `from pipeline import gate`.

<!-- /walk:pipeline/__init__.py -->

<!-- walk:src/mathkit/__main__.py -->
### `src/mathkit/__main__.py`, line by line

Lines 1 to 7:

```python
"""``python -m mathkit`` entry point."""

import sys

from mathkit.interfaces.cli import main

sys.exit(main())
```

A file named `__main__.py` in a package is what runs for `python -m mathkit` (`-m` means "run this module as a program"). It imports the command-line `main` function and passes its return value to `sys.exit`, which ends the program with that number as the **exit code** (0 means success, anything else failure).

<!-- /walk:src/mathkit/__main__.py -->

<!-- walk:src/mathkit/domain/errors.py -->
### `src/mathkit/domain/errors.py`, line by line

Lines 1 to 4:

```python
"""Named errors the library raises, so callers can tell a bad input from a bug."""

from __future__ import annotations
```

Docstring and `from __future__ import annotations` (type hints are stored as text and evaluated lazily, so newer hint syntax works on every supported Python). The purpose of the module: named errors, so callers can tell a bad input from a bug.

Lines 6 to 19:

```python
class MathkitError(Exception):
    """Base class of every error mathkit raises on purpose."""

class DivisionByZeroError(MathkitError):
    """The divisor was zero."""

class EmptyInputError(MathkitError):
    """A statistic was asked of an empty sequence."""

class InvalidTableError(MathkitError):
    """The table text could not be read as numeric columns."""
```

A **class** is a blueprint; `class DivisionByZeroError(MathkitError):` creates a new kind of error that **inherits** from `MathkitError`, which inherits from the built-in `Exception`. Catching `MathkitError` therefore catches all three. Each class has only a docstring: the new *name* is the point. `MathkitError` is the base of every error raised on purpose; `DivisionByZeroError`, `EmptyInputError` (a statistic of nothing) and `InvalidTableError` (the CSV text is not a table of numbers) are the three specific ones.

<!-- /walk:src/mathkit/domain/errors.py -->

<!-- walk:src/mathkit/domain/arithmetic.py -->
### `src/mathkit/domain/arithmetic.py`, line by line

Lines 1 to 7:

```python
"""Four-function arithmetic on numbers."""

from __future__ import annotations

from mathkit.domain.errors import DivisionByZeroError

Number = int | float
```

Imports the error class. `Number = int | float` is a **type alias**: a name for "an `int` or a `float`" (`|` means "or" in type hints).

Lines 10 to 22:

```python
def add(left: Number, right: Number) -> Number:
    """Return ``left + right``."""
    return left + right

def subtract(left: Number, right: Number) -> Number:
    """Return ``left - right``."""
    return left - right

def multiply(left: Number, right: Number) -> Number:
    """Return ``left * right``."""
    return left * right
```

`add`, `subtract` and `multiply` each take two numbers (`left: Number, right: Number`), and return a `Number` (`-> Number`): a **type hint** that documents the types without enforcing them at run time. The docstring is the line in triple quotes. The body is one `return`.

Lines 25 to 29:

```python
def divide(left: Number, right: Number) -> float:
    """Return ``left / right``; raise :class:`DivisionByZeroError` when ``right`` is zero."""
    if right == 0:
        raise DivisionByZeroError("cannot divide by zero")
    return left / right
```

`divide` first checks `if right == 0:` and **raises** `DivisionByZeroError("cannot divide by zero")`, which stops the function and passes the error to the caller; otherwise it returns `left / right`. Division in Python always gives a float (`-> float`).

<!-- /walk:src/mathkit/domain/arithmetic.py -->

<!-- walk:src/mathkit/domain/statistics.py -->
### `src/mathkit/domain/statistics.py`, line by line

Lines 1 to 13:

```python
"""Descriptive statistics on sequences of floats."""

from __future__ import annotations

import math
from collections.abc import Sequence

from mathkit.domain.errors import EmptyInputError

def _require_values(values: Sequence[float]) -> None:
    if len(values) == 0:
        raise EmptyInputError("at least one value is required")
```

`import math` loads the standard maths module. `Sequence` is a type hint for "an ordered collection" (a list or tuple). `_require_values` starts with an underscore, the convention for "internal to this file"; it raises `EmptyInputError` when `len(values) == 0`, so both statistics share the same check (`-> None` says it returns nothing).

Lines 16 to 19:

```python
def mean(values: Sequence[float]) -> float:
    """Return the arithmetic mean, summed exactly with :func:`math.fsum`."""
    _require_values(values)
    return math.fsum(values) / len(values)
```

`mean` checks the input, then returns `math.fsum(values) / len(values)`. `math.fsum` adds floating-point numbers with extra care so rounding errors do not pile up (plain `sum` can be slightly off); dividing by the count gives the mean.

Lines 22 to 29:

```python
def median(values: Sequence[float]) -> float:
    """Return the middle value, or the mean of the two middle values for an even count."""
    _require_values(values)
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
```

`median` checks the input, sorts a copy (`sorted(values)` returns a new list), and takes `middle = len(ordered) // 2` (`//` is whole-number division). With an odd count (`len(ordered) % 2 == 1`; `%` is the remainder) the median is the middle item; with an even count it is the average of the two middle items.

<!-- /walk:src/mathkit/domain/statistics.py -->

<!-- walk:src/mathkit/domain/summary.py -->
### `src/mathkit/domain/summary.py`, line by line

Lines 1 to 8:

```python
"""The summary of one numeric column, as an immutable value."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from mathkit.domain import statistics
```

Imports. `from mathkit.domain import statistics` imports the module (not single names) so the code below can write `statistics.mean(...)`. Note that this is the project's own `statistics.py`, not Python's standard `statistics` module of the same name; the package-qualified import makes that unambiguous.

Lines 11 to 32:

```python
@dataclass(frozen=True, slots=True)
class ColumnSummary:
    """Count, mean, median and range of one column."""

    name: str
    count: int
    mean: float
    median: float
    minimum: float
    maximum: float

    @classmethod
    def of(cls, name: str, values: Sequence[float]) -> ColumnSummary:
        """Summarize ``values``; raise :class:`~mathkit.domain.errors.EmptyInputError` when there are none."""
        return cls(
            name=name,
            count=len(values),
            mean=statistics.mean(values),
            median=statistics.median(values),
            minimum=min(values),
            maximum=max(values),
        )
```

`@dataclass(frozen=True, slots=True)` is a **decorator**: a line starting with `@` above a class that changes it. `dataclass` writes the constructor, equality and printed form from the list of fields; `frozen=True` makes instances unchangeable; `slots=True` stores them compactly. The six fields are `name`, `count`, `mean`, `median`, `minimum`, `maximum`. `@classmethod` makes `of` a method on the class itself (called `ColumnSummary.of(...)`, with `cls` standing for the class) instead of on an instance; it is a *factory* that builds a summary from raw values, calling `statistics.mean`, `statistics.median`, `min` and `max`. `-> ColumnSummary` is allowed before the class is finished thanks to `from __future__ import annotations`. An empty column makes `mean` raise `EmptyInputError`.

<!-- /walk:src/mathkit/domain/summary.py -->

<!-- walk:src/mathkit/application/ports.py -->
### `src/mathkit/application/ports.py`, line by line

Lines 1 to 16:

```python
"""Ports: what the use cases ask of the outside world."""

from __future__ import annotations

from typing import Protocol

class ColumnSource(Protocol):
    """Reads the numeric columns of a table given as text."""

    def numeric_columns(self, table_text: str) -> dict[str, tuple[float, ...]]:
        """Return each numeric column by name; non-numeric columns are left out.

        Raise :class:`~mathkit.domain.errors.InvalidTableError` when the text is not a table.
        """
        ...
```

A **port** names what the use case needs from outside, without saying how. `class ColumnSource(Protocol):` makes a **Protocol**: any class with a matching method counts as a `ColumnSource` without inheriting from it. The method `numeric_columns(table_text)` takes CSV text and returns `dict[str, tuple[float, ...]]`: a dictionary from a column name to a tuple (an unchangeable list) of floats of any length. The docstring states the promises: non-numeric columns are left out; `InvalidTableError` is raised for non-tables. The body is `...` (an *Ellipsis*), meaning "described here, implemented elsewhere".

<!-- /walk:src/mathkit/application/ports.py -->

<!-- walk:src/mathkit/application/summarize.py -->
### `src/mathkit/application/summarize.py`, line by line

Lines 1 to 21:

```python
"""Use case: summarize every numeric column of a table."""

from __future__ import annotations

from mathkit.application.ports import ColumnSource
from mathkit.domain.errors import InvalidTableError
from mathkit.domain.summary import ColumnSummary

class SummarizeTable:
    """Summarize the numeric columns of a table, in the order they appear."""

    def __init__(self, source: ColumnSource) -> None:
        self._source = source

    def __call__(self, table_text: str) -> tuple[ColumnSummary, ...]:
        """Return one summary per numeric column; raise ``InvalidTableError`` when there is none."""
        columns = self._source.numeric_columns(table_text)
        if not columns:
            raise InvalidTableError("the table has no numeric column")
        return tuple(ColumnSummary.of(name, values) for name, values in columns.items())
```

`SummarizeTable` is a use case: a class with `__init__` (the constructor, storing the source it was given in `self._source`) and `__call__` (which makes an instance callable like a function: `summarize(text)`). It asks the source for the columns, raises `InvalidTableError` if there are none (`if not columns:` is true for an empty dictionary), and returns a tuple of `ColumnSummary` objects built by a **generator expression** `ColumnSummary.of(name, values) for name, values in columns.items()` (`.items()` gives key-value pairs). Dictionaries keep insertion order, so the summaries come in the order of the columns. It depends on the `ColumnSource` protocol, not on pandas.

<!-- /walk:src/mathkit/application/summarize.py -->

<!-- walk:src/mathkit/infrastructure/pandas_source.py -->
### `src/mathkit/infrastructure/pandas_source.py`, line by line

Lines 1 to 14:

```python
"""Adapter: read numeric columns from CSV text with pandas.

pandas and numpy are the heavy dependencies the CI cache exists for; nothing outside this module imports them.
"""

from __future__ import annotations

import io

import numpy as np
import pandas as pd

from mathkit.domain.errors import InvalidTableError
```

The adapter that satisfies the port with pandas. The docstring explains why pandas matters here: it and numpy are the heavy dependencies the CI cache exists for, and only this module imports them. `import io` provides `StringIO`, which makes a text behave like a file. `import numpy as np` and `import pandas as pd` load the packages under short conventional names.

Lines 16 to 28:

```python
class PandasColumnSource:
    """:class:`~mathkit.application.ports.ColumnSource` backed by ``pandas.read_csv``."""

    def numeric_columns(self, table_text: str) -> dict[str, tuple[float, ...]]:
        """Parse ``table_text`` as CSV and return its numeric columns, dropping rows with a missing value."""
        try:
            frame = pd.read_csv(io.StringIO(table_text))
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
            raise InvalidTableError(f"not a CSV table: {error}") from error
        numeric = frame.select_dtypes(include=[np.number])
        return {
            str(name): tuple(float(value) for value in numeric[name].dropna().to_numpy()) for name in numeric.columns
        }
```

`pd.read_csv(io.StringIO(table_text))` parses CSV text into a **DataFrame** (pandas' table type). Two pandas error kinds, `EmptyDataError` (no text) and `ParserError` (not a table), are converted into the domain's `InvalidTableError` with `raise ... from error`, which keeps the original error attached. `frame.select_dtypes(include=[np.number])` keeps only columns whose values are numbers. The dictionary comprehension builds `{column name: tuple of floats}`: `numeric[name].dropna()` removes missing values, `.to_numpy()` converts to a numpy array, and `float(value)` makes each a plain Python float. `str(name)` makes sure keys are texts.

<!-- /walk:src/mathkit/infrastructure/pandas_source.py -->

<!-- walk:src/mathkit/interfaces/cli.py -->
### `src/mathkit/interfaces/cli.py`, line by line

Lines 1 to 20:

```python
"""Command-line program: ``python -m mathkit add 2 3`` and ``python -m mathkit summarize data.csv``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from mathkit.application.summarize import SummarizeTable
from mathkit.domain import arithmetic
from mathkit.domain.errors import MathkitError
from mathkit.infrastructure.pandas_source import PandasColumnSource

_OPERATIONS = {
    "add": arithmetic.add,
    "subtract": arithmetic.subtract,
    "multiply": arithmetic.multiply,
    "divide": arithmetic.divide,
}
```

The docstring shows the two kinds of command. The imports bring in `argparse` (command-line parsing), `sys`, `Path` and the other layers: this is the only layer that imports them all, because it wires the pieces together. `_OPERATIONS` is a dictionary from a command word to the function that does it.

Lines 23 to 33:

```python
def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser; one sub-command per operation plus ``summarize``."""
    parser = argparse.ArgumentParser(prog="mathkit", description="Small math helpers.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in _OPERATIONS:
        command = commands.add_parser(name, help=f"{name} two numbers")
        command.add_argument("left", type=float)
        command.add_argument("right", type=float)
    summarize = commands.add_parser("summarize", help="summarize the numeric columns of a CSV file")
    summarize.add_argument("path", type=Path)
    return parser
```

`build_parser` describes the command line with `argparse`. `add_subparsers(dest="command", required=True)` makes the first word a **sub-command** (`add`, `subtract`, `multiply`, `divide`, `summarize`) and stores which one in `args.command`. A loop adds one sub-command per operation, each with two positional arguments `left` and `right` converted by `type=float`. `summarize` takes one argument `path`, converted to a `Path`.

Lines 36 to 55:

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Run the program; return the exit code (0 success, 1 a mathkit error, 2 a usage error)."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "summarize":
            summaries = SummarizeTable(PandasColumnSource())(args.path.read_text(encoding="utf-8"))
            for item in summaries:
                print(
                    f"{item.name}: count={item.count} mean={item.mean:g} median={item.median:g} "
                    f"min={item.minimum:g} max={item.maximum:g}"
                )
        else:
            print(f"{_OPERATIONS[args.command](args.left, args.right):g}")
    except MathkitError as error:
        print(f"mathkit: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"mathkit: cannot read the file: {error}", file=sys.stderr)
        return 1
    return 0
```

`main` parses the arguments (`parse_args(argv)` reads `sys.argv` when `argv` is `None`). In the `try` block: for `summarize`, it reads the file as UTF-8 text, runs `SummarizeTable(PandasColumnSource())` on it and prints one line per column. The format `{item.mean:g}` is a **format specifier**: `g` prints a number in its shortest natural form (`2.5` not `2.500000`). For the other commands `_OPERATIONS[args.command](args.left, args.right)` looks the function up by name and calls it. A `MathkitError` prints `mathkit: <message>` to standard error and the function returns 1; an `OSError` (a file that cannot be read) does the same. Otherwise it returns 0. Wrong usage is handled by `argparse`, which exits with code 2 on its own.

<!-- /walk:src/mathkit/interfaces/cli.py -->

<!-- walk:pipeline/billing.py -->
### `pipeline/billing.py`, line by line

Lines 1 to 7:

```python
"""Wall time and billable minutes of a workflow run, from the job list the GitHub API returns.

GitHub bills each job on its own: the duration rounds up to the next whole minute, and the minutes are multiplied
by the runner's rate (Linux 1, Windows 2, macOS 10). Fetch a run's jobs with::

    gh api repos/OWNER/REPO/actions/runs/RUN_ID/jobs --paginate > run.json
"""
```

The docstring explains the rule being modelled: GitHub bills each job on its own, rounding the duration **up** to the next whole minute, then multiplying by the runner's rate (Linux 1, Windows 2, macOS 10). The `::` followed by an indented line is reStructuredText for a code example: the `gh api ... --paginate` command that downloads a run's jobs as JSON.

Lines 9 to 22:

```python
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

RATES = {"linux": 1, "windows": 2, "macos": 10}
```

Imports, all from Python's standard library: `argparse` (command-line arguments), `json`, `math`, `statistics`, `sys`, type-hint helpers, `dataclass`, `datetime` (dates and times), `Path`. `RATES` is a dictionary from an operating-system family to its rate.

Lines 25 to 42:

```python
@dataclass(frozen=True, slots=True)
class Job:
    """One job that ran: its name, the operating system family of its runner and its start and end."""

    name: str
    family: str
    started_at: datetime
    completed_at: datetime

    @property
    def seconds(self) -> float:
        """Seconds between start and completion."""
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def billable_minutes(self) -> int:
        """Whole minutes, rounded up, times the runner's rate."""
        return math.ceil(self.seconds / 60) * RATES[self.family]
```

`@dataclass(frozen=True, slots=True)` (a decorator: it writes the constructor and other boilerplate for a class that holds data; frozen means unchangeable). A `Job` has a name, the OS family of its runner and two `datetime` values. `@property` turns a method into something read like a field (`job.seconds`). `seconds` subtracts two datetimes, which gives a `timedelta`, and `.total_seconds()` converts it to a number. `billable_minutes` is `math.ceil(self.seconds / 60) * RATES[self.family]`: `math.ceil` rounds up, so 61 seconds is 2 minutes.

Lines 45 to 50:

```python
@dataclass(frozen=True, slots=True)
class RunCost:
    """The cost of one run: wall time (first job start to last job end) and billable minutes."""

    wall_seconds: float
    billable_minutes: int
```

`RunCost` holds the wall time (from the first job's start to the last job's end) and the total billable minutes of one run.

Lines 53 to 62:

```python
def _timestamp(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))

def _family(labels: Sequence[str]) -> str:
    joined = " ".join(labels).lower()
    for family in ("windows", "macos"):
        if family in joined:
            return family
    return "linux"
```

`_timestamp` turns GitHub's timestamp text such as `2026-01-01T10:00:00Z` into a `datetime`: Python's `fromisoformat` did not accept the trailing `Z` (meaning UTC) in older versions, so it is replaced with `+00:00`. `_family(labels)` joins the runner's labels into one lower-case text and returns `windows` or `macos` if either word appears, otherwise `linux`; the underscore prefix means "internal".

Lines 65 to 79:

```python
def parse_jobs(payload: Mapping[str, Any]) -> tuple[Job, ...]:
    """Read the jobs of a run; jobs that never started (skipped) are left out."""
    jobs = []
    for raw in payload["jobs"]:
        if not raw.get("started_at") or not raw.get("completed_at"):
            continue
        jobs.append(
            Job(
                raw["name"],
                _family(raw.get("labels", [])),
                _timestamp(raw["started_at"]),
                _timestamp(raw["completed_at"]),
            )
        )
    return tuple(jobs)
```

`parse_jobs(payload)` reads the API answer. For each raw job a dictionary is read with `raw[...]` (fails if the key is missing) or `raw.get(...)` (gives `None`). A job without `started_at` or `completed_at` (skipped) is left out: `continue` jumps to the next loop turn. Otherwise a `Job` is built and added to the list with `jobs.append(...)`; the function returns an unchangeable `tuple`.

Lines 82 to 87:

```python
def run_cost(jobs: Sequence[Job]) -> RunCost:
    """Return the wall time and billable minutes of a run; a run with no job that ran costs nothing."""
    if not jobs:
        return RunCost(0.0, 0)
    wall = (max(job.completed_at for job in jobs) - min(job.started_at for job in jobs)).total_seconds()
    return RunCost(wall, sum(job.billable_minutes for job in jobs))
```

`run_cost` returns zero for no jobs. Otherwise: wall time is the latest end minus the earliest start, found with `max(...)` and `min(...)` over **generator expressions** like `job.completed_at for job in jobs`; billable minutes is the sum over the jobs.

Lines 90 to 93:

```python
def format_duration(seconds: float) -> str:
    """Format seconds as ``2m 20s``."""
    whole = round(seconds)
    return f"{whole // 60}m {whole % 60:02d}s"
```

`format_duration` rounds the seconds and prints minutes and seconds: `whole // 60` is whole minutes (`//` is whole-number division) and `whole % 60` the remainder (`%`); `:02d` pads the seconds to two digits. For 140 seconds it prints `2m 20s`.

Lines 96 to 100:

```python
def stage_row(name: str, runs: Sequence[RunCost]) -> str:
    """One README table row for a stage: the median wall time and median billable minutes of its runs."""
    wall = statistics.median(run.wall_seconds for run in runs)
    minutes = statistics.median(run.billable_minutes for run in runs)
    return f"{name:<34}{format_duration(wall):<12}{minutes:g}   (median of {len(runs)} runs)"
```

`stage_row` builds one line of the README table. `statistics.median(...)` of the wall times and of the billable minutes of the runs. In the f-string, `{name:<34}` pads the text on the right to 34 characters (left-aligned), `{minutes:g}` prints a number without a pointless `.0`.

Lines 103 to 120:

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Print the stage table for ``--stage NAME run.json [run.json ...]`` arguments."""
    parser = argparse.ArgumentParser(prog="pipeline.billing", description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument("--stage", nargs="+", action="append", metavar=("NAME", "RUN_JSON"), required=True)
    args = parser.parse_args(argv)
    print(f"{'stage':<34}{'wall time':<12}billable minutes")
    for name, *files in args.stage:
        if not files:
            parser.error(f"stage {name!r} needs at least one run file")
        runs = [run_cost(parse_jobs(json.loads(Path(file).read_text(encoding="utf-8")))) for file in files]
        print(stage_row(name, runs))
        for number, run in enumerate(runs, start=1):
            print(f"  run {number}: {format_duration(run.wall_seconds)}, {run.billable_minutes} billable minutes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`main` reads the command line. `parser.add_argument("--stage", nargs="+", action="append", metavar=("NAME", "RUN_JSON"), required=True)` accepts `--stage` several times; each time it takes one or more words (`nargs="+"`), and `append` collects each use into a list. `for name, *files in args.stage:` unpacks each list: the first word is the name, `*files` collects the rest. A stage with no file ends with `parser.error(...)`. For each file it loads the JSON (`json.loads(Path(file).read_text(...))`), parses jobs, and computes the cost; it prints the stage row and then each run's own line (`enumerate(runs, start=1)` counts from 1). The last two lines are the usual start-up guard: the code runs only when the file is started directly, and its return value becomes the exit code.

<!-- /walk:pipeline/billing.py -->

<!-- walk:pipeline/cache_key.py -->
### `pipeline/cache_key.py`, line by line

Lines 1 to 5:

```python
"""Model of the cache key ``actions/setup-python`` builds, so a change to the lock file can be shown to miss.

The key is ``setup-python-<OS>-<arch>-python-<version>-pip-<hash>``. The hash is what ``hashFiles()`` computes:
the SHA-256 of the concatenated SHA-256 digests of the matched files.
"""
```

The docstring: a model of the cache key `actions/setup-python` builds, so a change to the lock file can be shown to cause a cache miss. The key is `setup-python-<OS>-<arch>-python-<version>-pip-<hash>`; the hash is what GitHub's `hashFiles()` computes: the SHA-256 of the concatenated SHA-256 digests of the matched files.

Lines 7 to 26:

```python
from __future__ import annotations

import argparse
import hashlib
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

def hash_files(paths: Iterable[Path]) -> str:
    """Return the ``hashFiles()`` value of ``paths``, taken in the order given."""
    outer = hashlib.sha256()
    for path in paths:
        outer.update(hashlib.sha256(path.read_bytes()).digest())
    return outer.hexdigest()

def setup_python_key(runner_os: str, arch: str, python_version: str, dependency_file: Path) -> str:
    """Return the primary cache key for one matrix job."""
    return f"setup-python-{runner_os}-{arch}-python-{python_version}-pip-{hash_files([dependency_file])}"
```

Imports (`hashlib` provides SHA-256). `hash_files(paths)` creates an outer hash object (`hashlib.sha256()`), and for each path hashes the file's bytes (`path.read_bytes()`), takes the 32-byte digest (`.digest()`) and feeds it into the outer hash with `.update(...)`. `.hexdigest()` returns the result as 64 hexadecimal characters. A **hash** is a fixed-length fingerprint of data: the same bytes give the same hash, any change gives a different one. `setup_python_key` assembles the key text from its parts with an f-string.

Lines 29 to 42:

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Print the key for the given runner OS, Python version and dependency file."""
    parser = argparse.ArgumentParser(prog="pipeline.cache_key")
    parser.add_argument("--os", default="Linux")
    parser.add_argument("--arch", default="x64")
    parser.add_argument("--python", default="3.12.7", dest="python_version")
    parser.add_argument("--file", type=Path, default=Path("requirements.txt"))
    args = parser.parse_args(argv)
    print(setup_python_key(args.os, args.arch, args.python_version, args.file))
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`main` builds the command line: options `--os` (default `Linux`), `--arch` (`x64`), `--python` (stored under the name `python_version` because of `dest=`), and `--file` (a `Path`, default `requirements.txt`), prints the key, and returns 0. The last two lines are the usual start-up guard.

<!-- /walk:pipeline/cache_key.py -->

<!-- walk:pipeline/gate.py -->
### `pipeline/gate.py`, line by line

Lines 1 to 15:

```python
"""The ``ci-ok`` gate: one job to require for ``main`` that fails when any job it needs did not succeed.

Reads the ``needs`` context as JSON from the ``NEEDS`` environment variable, so no job output is ever pasted
into a shell command.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from typing import Any

PASSING = frozenset({"success", "skipped"})
```

The docstring explains the `ci-ok` **gate**: one job to require for `main`, which fails when any job it `needs` did not succeed. It reads the `needs` context as JSON from the environment variable `NEEDS`, so no job output is ever pasted into a shell command. `PASSING` is a `frozenset` (an unchangeable set) of the two results that count as fine: `success` and `skipped`.

Lines 18 to 20:

```python
def failed_jobs(needs: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """Return the names of the needed jobs whose result is neither ``success`` nor ``skipped``."""
    return sorted(name for name, job in needs.items() if job.get("result") not in PASSING)
```

`failed_jobs` takes a mapping from job name to its info and returns the sorted names whose `result` is not in `PASSING`. `job.get("result")` is `None` for a missing key, which is also not passing.

Lines 23 to 35:

```python
def main() -> int:
    """Exit 0 when every needed job passed, 1 otherwise, naming the jobs that did not."""
    needs = json.loads(os.environ["NEEDS"])
    failed = failed_jobs(needs)
    if failed:
        print(f"ci-ok: not green: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"ci-ok: {len(needs)} jobs green")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`main` reads the environment variable (`os.environ["NEEDS"]`; a missing variable raises `KeyError`, which is right: the gate must not pass by accident), parses the JSON with `json.loads`, lists the failures and exits 1 with a message on standard error naming them (`', '.join(failed)` glues the names with commas), else 0 with `ci-ok: N jobs green`. The last two lines are the usual start-up guard.

<!-- /walk:pipeline/gate.py -->

<!-- walk:pipeline/pathfilter.py -->
### `pipeline/pathfilter.py`, line by line

Lines 1 to 11:

```python
"""Model of GitHub's ``paths`` and ``paths-ignore`` filters: does a push that changed these files start a workflow?

Pattern syntax (from the workflow syntax reference): ``*`` matches any characters except ``/``, ``**`` matches any
characters including ``/``, ``?`` makes the preceding character optional, ``+`` repeats it, ``[...]`` is a class.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
```

The docstring says it models GitHub's `paths` and `paths-ignore` filters: does a push that changed these files start a workflow? The pattern rules: `*` matches any characters except `/`; `**` matches any characters including `/`; `?` makes the preceding character optional; `+` repeats it; `[...]` is a class of characters.

Lines 13 to 34:

```python
def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate one filter pattern into an anchored regular expression."""
    out: list[str] = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if char == "*":
            out.append("[^/]*")
        elif char in "?+":
            out.append(char)
        elif char == "[":
            end = pattern.index("]", i)
            out.append(pattern[i : end + 1])
            i = end
        else:
            out.append(re.escape(char))
        i += 1
    return re.compile("".join(out))
```

`glob_to_regex` translates one filter pattern into a **regular expression**. It walks the text with an index `i`. If the pattern has `**` at `i` (`startswith("**", i)`), it appends `.*` (any characters, including `/`), skips both, and `continue`s. A single `*` becomes `[^/]*` (any characters except `/`). `?` and `+` are copied. A `[` copies the bracket class up to the matching `]` (`pattern.index("]", i)` finds it; `pattern[i : end + 1]` is a slice, a part of the text). Any other character is escaped with `re.escape` so that, for example, `.` means a literal dot. `re.compile("".join(out))` joins the pieces and builds the pattern.

Lines 37 to 39:

```python
def matches(path: str, patterns: Iterable[str]) -> bool:
    """Return whether ``path`` matches any of ``patterns``."""
    return any(glob_to_regex(pattern).fullmatch(path) for pattern in patterns)
```

`matches(path, patterns)`: true if `any(...)` of the patterns, turned into regular expressions, matches the **whole** path (`fullmatch`).

Lines 42 to 54:

```python
def starts_workflow(changed: Sequence[str], *, paths: Sequence[str] = (), paths_ignore: Sequence[str] = ()) -> bool:
    """Return whether a push that changed ``changed`` starts a workflow with these filters.

    With ``paths`` the workflow starts when any changed file matches; with ``paths-ignore`` it starts unless every
    changed file matches. GitHub does not allow both on one event.
    """
    if paths and paths_ignore:
        raise ValueError("paths and paths-ignore cannot be used together on one event")
    if paths:
        return any(matches(path, paths) for path in changed)
    if paths_ignore:
        return not all(matches(path, paths_ignore) for path in changed)
    return True
```

`starts_workflow(changed, *, paths=(), paths_ignore=())` answers: does a push that changed these files start a workflow? The bare `*` in the parameter list makes the following parameters **keyword-only** (they must be written `paths=...`). Both filters at once raise `ValueError`, because GitHub does not allow it on one event. With `paths`, the workflow starts if any changed file matches. With `paths-ignore`, it starts unless **every** changed file matches (`not all(...)`). With neither, it always starts.

<!-- /walk:pipeline/pathfilter.py -->

<!-- walk:pipeline/pins.py -->
### `pipeline/pins.py`, line by line

Lines 1 to 5:

```python
"""Check that every ``uses:`` in the workflows and local actions names a full commit SHA.

A tag can be moved by whoever owns it; a 40-character commit hash names one tree of files for ever.
Local actions (``./path``) and Docker images pinned by digest are allowed.
"""
```

The docstring: every `uses:` in the workflows and local actions must name a full commit SHA, because a tag can be moved by whoever owns it, while a 40-character commit hash names one set of files forever. Local actions (`./path`) and Docker images pinned by digest are allowed.

Lines 7 to 18:

```python
from __future__ import annotations

import re
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import yaml

_PINNED = re.compile(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}")
_DIGEST = re.compile(r"docker://\S+@sha256:[0-9a-f]{64}")
```

Imports, including `yaml` (PyYAML, which reads YAML files). Two compiled regular expressions: `_PINNED` is `owner/name@` plus exactly 40 hexadecimal characters; `_DIGEST` is `docker://image@sha256:` plus 64 hexadecimal characters.

Lines 21 to 33:

```python
def uses_values(document: Any) -> Iterator[str]:
    """Yield every ``uses`` value of a parsed workflow or action: job-level and step-level."""
    if not isinstance(document, dict):
        return
    for job in (document.get("jobs") or {}).values():
        if "uses" in job:
            yield str(job["uses"])
        for step in job.get("steps") or []:
            if "uses" in step:
                yield str(step["uses"])
    for step in (document.get("runs") or {}).get("steps") or []:
        if "uses" in step:
            yield str(step["uses"])
```

`uses_values` is a **generator** (it produces values one at a time with `yield`). If the parsed document is not a dictionary it returns nothing. For every job (`(document.get("jobs") or {}).values()`), it yields the job's own `uses` (a job that calls a reusable workflow) and each step's `uses`; then the same for `runs.steps`, where a composite action keeps its steps.

Lines 36 to 38:

```python
def is_pinned(reference: str) -> bool:
    """Return whether a ``uses`` value is local, a digest-pinned image, or a full-SHA reference."""
    return reference.startswith("./") or bool(_DIGEST.fullmatch(reference)) or bool(_PINNED.fullmatch(reference))
```

`is_pinned` is true for a local path (`startswith("./")`), a digest-pinned image or a full-SHA reference (`fullmatch` requires the whole text to match). `bool(...)` turns a match object or `None` into `True` or `False`.

Lines 41 to 48:

```python
def violations(root: Path) -> list[str]:
    """Return ``path: uses-value`` for each unpinned reference under ``root/.github``."""
    found = []
    files = sorted([*root.glob(".github/workflows/*.y*ml"), *root.glob(".github/actions/**/action.y*ml")])
    for file in files:
        document = yaml.safe_load(file.read_text(encoding="utf-8"))
        found += [f"{file.relative_to(root)}: {ref}" for ref in uses_values(document) if not is_pinned(ref)]
    return found
```

`violations(root)` finds the YAML files (`root.glob(...)` with the pattern `.github/workflows/*.y*ml` and every `action.y*ml` below `.github/actions`), loads each (`yaml.safe_load` parses without building arbitrary objects), and collects `path: reference` for each reference that is not pinned, using a list comprehension with an `if`.

Lines 51 to 64:

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Exit 1 and list the unpinned references when there are any."""
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]) if args else Path(".")
    found = violations(root)
    for line in found:
        print(f"not pinned to a full commit SHA: {line}", file=sys.stderr)
    if not found:
        print("pins: every uses: is a full commit SHA, a local path or a digest")
    return 1 if found else 0

if __name__ == "__main__":
    sys.exit(main())
```

`main` takes an optional root folder argument (default `.`), prints each problem to standard error, or a success line if there are none, and returns 1 when there were problems, else 0.

<!-- /walk:pipeline/pins.py -->

<!-- walk:pipeline/slowest_tests.py -->
### `pipeline/slowest_tests.py`, line by line

Lines 1 to 11:

```python
"""Turn a JUnit report into a Markdown table of the slowest tests, for the job summary page.

The report is the one pytest wrote in the same job, so it is trusted input.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from xml.etree import ElementTree
```

The docstring: turn a JUnit report (the XML file pytest wrote) into a Markdown table of the slowest tests for the job's summary page; it is trusted input, written by the same job. `ElementTree` is Python's built-in XML reader.

Lines 14 to 20:

```python
def slowest(report: Path, count: int = 5) -> list[tuple[str, float]]:
    """Return the ``count`` slowest test cases as ``(classname::name, seconds)``, slowest first."""
    cases = [
        (f"{case.get('classname', '')}::{case.get('name', '')}", float(case.get("time", "0")))
        for case in ElementTree.parse(report).getroot().iter("testcase")
    ]
    return sorted(cases, key=lambda item: item[1], reverse=True)[:count]
```

`slowest(report, count=5)` parses the XML (`ElementTree.parse(report).getroot()`), loops over every `<testcase>` element (`.iter("testcase")`) and builds a list of pairs `(classname::name, seconds)`; `case.get("classname", "")` reads an attribute with a default. `float(...)` converts the time text. `sorted(cases, key=lambda item: item[1], reverse=True)[:count]` sorts by the second item (a **lambda** is a small unnamed function) with the largest first, then slices the first `count`.

Lines 23 to 27:

```python
def markdown(rows: Sequence[tuple[str, float]]) -> str:
    """Render the rows as a GitHub-flavored Markdown table."""
    lines = ["### Slowest tests", "", "| Test | Seconds |", "| --- | ---: |"]
    lines += [f"| `{name}` | {seconds:.3f} |" for name, seconds in rows]
    return "\n".join(lines) + "\n"
```

`markdown(rows)` builds the table as a list of lines: a heading `### Slowest tests`, a blank line, the header row and the separator row `| --- | ---: |` (`---:` right-aligns that column); then one row per test with the name in backticks and the seconds to three decimals (`{seconds:.3f}`). `"\n".join(lines) + "\n"` makes the text.

Lines 30 to 41:

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Print the table for the report path given as the first argument."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python -m pipeline.slowest_tests REPORT.xml", file=sys.stderr)
        return 2
    print(markdown(slowest(Path(args[0]))), end="")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`main` requires exactly one argument (the report path) and returns 2 with a usage message otherwise. `print(..., end="")` prints without adding another line break. The last two lines are the start-up guard.

<!-- /walk:pipeline/slowest_tests.py -->

<!-- walk:.env.example -->
### `.env.example`, line by line

Lines 1 to 8:

```hcl
# Every variable the project reads. None is a secret.

# The "break one matrix cell on purpose" exercise (lesson step 2). Set to a Python version such as 3.10 and the

# end-to-end test fails on that interpreter only. In CI it comes from the repository variable DEMO_FAIL_ON_PYTHON.

MATHKIT_DEMO_FAIL_ON_PYTHON=

# The repository `make measure` reads run data from (OWNER/NAME). Defaults to the repository the gh CLI is in.

GH_REPO=
```

A template of the variables the project reads; none is a secret. `MATHKIT_DEMO_FAIL_ON_PYTHON` (empty by default) is read by the end-to-end test: set it to a Python version such as `3.10` and the test fails on that interpreter only; in CI the value comes from the repository variable `DEMO_FAIL_ON_PYTHON`. `GH_REPO` is the `OWNER/NAME` that `make measure` reads run data from, defaulting to the repository `gh` is in. Copy to `.env` (ignored by Git) to use.

<!-- /walk:.env.example -->

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
