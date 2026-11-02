# pytest (with pytest-cov and coverage)

## What it is

pytest is a Python tool that finds and runs tests. A **test** is a function that runs a piece of your code and checks the result; if the check fails, the test fails. pytest finds files named `test_*.py`, runs every function in them named `test_*`, and prints a summary. `pytest-cov` is a plugin that adds `--cov` options and uses the library `coverage` to measure which lines of your code the tests ran. This repository pins pytest 9.0.3, pytest-cov 5.0.0 and coverage 7.x (the lock file picks the 7.x release for each Python version).

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **command line**: The text you type after the prompt in a terminal to run a program, such as `npm test`. The words after the program name are its **arguments**; words that start with `-` or `--` are **options** (also called flags).
- **exit code**: A number a program leaves behind when it ends. 0 means success; any other number means failure. Build systems read it to decide whether a step passed.
- **environment variable**: A named piece of text that is handed to a program by whoever starts it, for example `HOME` or `CI`. Programs read them to learn about the setting they run in.
- **process**: A program while it is running, with its own memory. Starting a program creates a process; when it ends the process is gone.
- **standard output**: The stream where a program writes its normal results (its counterpart, standard error, is for problems).
- **regular expression**: A compact pattern that describes text, such as `^[0-9]{12}$` (exactly twelve digits). Tools use them to find or check text. Often shortened to **regex**.
- **hash**: A fixed-length fingerprint computed from some data. The same data always gives the same hash; any change gives a different one. SHA-256 and SHA-1 are two ways of computing one.
- **SHA**: A family of hash functions. A Git **commit SHA** is a 40-character hexadecimal fingerprint that names one exact commit.
- **commit**: A saved snapshot of a project's files in Git, with a message and an author. Every commit has a unique 40-character name (its SHA).
- **branch**: A movable name for a line of commits in Git. `main` is the usual name of the primary line.
- **tag**: A name attached to a commit in Git, usually a version such as `v1.0.0`. Unlike a commit's SHA, a tag can be moved to another commit.
- **workflow**: A GitHub Actions automation described in a YAML file under `.github/workflows/`. It names the events that start it and the jobs it runs.
- **artifact**: A file or folder that a job saves so that later jobs, or people, can download it.
- **CI**: Continuous integration: running checks (build, tests, linters) automatically every time code changes.
- **API**: Application programming interface: a set of requests a program can send to another program or service, with documented answers. A web API is called over the internet with HTTP.
- **YAML**: A plain-text format for structured data that uses indentation instead of braces. GitHub workflows are YAML files.
- **Markdown**: A plain-text way to write formatted documents: `#` for headings, `-` for bullets, backticks for code, `|` for tables.
- **token**: A secret text that proves who is asking when a program talks to a service, instead of a password. Tokens can be limited in what they may do and in how long they last.
- **Docker**: A tool that builds images and runs containers.
- **library**: A package of ready-made code that your program calls.
- **lock file**: A file that records the exact version, and a checksum, of every package that was installed, so that everyone installs exactly the same thing.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.
- **module**: A file, or a folder of files, that other code can load and use. In Terraform, a module is a folder of configuration used like a function.
- **function**: A named piece of code that takes inputs (parameters), does something, and may return a result.
- **class**: A blueprint for objects: it bundles data and the functions that work on it. `new Name(...)` or `Name(...)` makes an object from it.
- **variable**: A name for a place that holds a value which can be used later in the code.
- **list**: An ordered collection of values written one after another.
- **boolean**: A value that is either true or false.
- **folder**: A container for files and other folders on disk (also called a directory).
- **assert**: A statement that checks something is true and fails loudly if it is not.
- **framework**: A large library that decides the overall shape of an application.
- **decorator**: A line starting with `@` placed above a Python function or class that changes how it behaves, for example `@dataclass`.
- **docstring**: A text in triple quotes at the start of a Python file, class or function that documents it; tools and people can read it.
- **comprehension**: A short way to build a list, set or dictionary from a loop in one expression, such as `[x * 2 for x in items if x > 0]`.
- **exception**: An error raised while a program runs (`raise ValueError("message")`). Code can catch it with `try`/`except`; if nobody catches it the program stops.
- **tuple**: An unchangeable ordered list of values in Python, written `(a, b)`.
- **dictionary**: A Python mapping from keys to values, written `{"key": value}`.
- **Protocol**: A Python type that describes the methods something must have; any class with those methods satisfies it without inheriting from it.
- **XML**: A plain-text format made of nested tags such as `<testcase name="x" time="0.1"/>`.
- **JUnit**: A common XML layout for test reports: a `<testsuite>` containing one `<testcase>` per test.

</details>

<!-- /words -->

## Why this repository uses it

The CI workflow needs something real to run. 90 tests give the matrix a job to do on each of six combinations, produce a JUnit report (`junit-xml.md`) to upload as an artifact, and give the "slowest tests" summary something to list. Coverage is a quality gate: `make test` fails below 95 percent.

## Where it appears

| Path | What it does with pytest |
| --- | --- |
| `tests/unit/` | Tests of the domain, the use case (with a fake source) and the command-line arguments. |
| `tests/integration/test_pandas_source.py` | The pandas adapter with the real pandas. |
| `tests/e2e/test_cli_end_to_end.py` | The command line as a separate process, plus the "break one cell on purpose" switch. |
| `tests/pipeline/` | Tests of the `pipeline/` scripts and of the workflow YAML files. |
| `pyproject.toml` | `[tool.pytest.ini_options]` and `[tool.coverage.*]`. |
| `.github/workflows/ci.yml` | `python -m pytest --junitxml=report.xml --cov --cov-report=xml`. |

## How it works underneath

`python -m pytest` imports each test file, looks at every function whose name starts with `test`, and calls it. Inside a test you use the plain `assert` statement. pytest rewrites asserts when it loads the file so a failure prints both sides of the comparison. A test passes if it returns without an exception. A **fixture** is a helper that pytest builds and hands to a test when the test names it as a parameter (`tmp_path`, `capsys`). A **marker** (like `@pytest.mark.parametrize`) adds information to a test.

Coverage works by hooking into the interpreter while the tests run. It records every line (and with `branch = true`, every jump from one line to the next) that executed, then compares with all the lines that could have. The percent is lines run divided by lines that exist.

## Walkthrough of this repository's use

### Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
addopts = "-ra --strict-markers"
```

`testpaths` is where to look. `pythonpath` puts `src` and the repository root on the import path. `addopts` are options added to every run: `-ra` prints a short reason for every skipped or failed test at the end; `--strict-markers` turns an unknown marker name into an error.

### A plain test

```python
def test_add_returns_the_sum_of_two_numbers():
    assert mathkit.add(2, 3) == 5
```

The name reads as a sentence about behavior. `assert` fails the test when the expression is false.

### Checking that an error is raised

```python
def test_divide_by_zero_raises_a_named_error():
    with pytest.raises(DivisionByZeroError, match="zero"):
        divide(1, 0)
```

`pytest.raises` passes only if the block raises that error, and `match` checks the message against a regular expression.

### Several cases in one test

```python
@pytest.mark.parametrize(
    ("argv", "expected"),
    [(["add", "2", "3"], "5"), (["subtract", "2", "3"], "-1"), ...],
)
def test_an_operation_prints_its_result(argv, expected, capsys):
    assert main(argv) == 0
    assert capsys.readouterr().out.strip() == expected
```

`parametrize` runs the test once for each pair. `capsys` is a built-in fixture that captures what the code prints; `readouterr()` returns it.

### Files and fakes

```python
def test_a_missing_file_exits_1_with_a_message(capsys, tmp_path):
    assert main(["summarize", str(tmp_path / "missing.csv")]) == 1
```

`tmp_path` is a fresh empty folder, removed later. The use case test passes a hand-written `FakeSource` instead of pandas, so it needs no data library and runs in milliseconds.

### A test that skips itself

```python
def test_the_break_on_purpose_switch_fails_only_on_the_named_version():
    target = os.environ.get("MATHKIT_DEMO_FAIL_ON_PYTHON", "")
    if target != f"{sys.version_info.major}.{sys.version_info.minor}":
        pytest.skip("MATHKIT_DEMO_FAIL_ON_PYTHON does not name this interpreter")
    pytest.fail(f"deliberate failure on Python {target} (MATHKIT_DEMO_FAIL_ON_PYTHON)")
```

Normally this skips (that is the "1 skipped" in the summary). When the repository variable names this Python version, it fails on purpose, turning one matrix cell red.

### A test that runs another program

```python
def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run([sys.executable, "-m", "mathkit", *args], capture_output=True, text=True, env=env, check=False)
```

The end-to-end tests start `python -m mathkit` as a real process and check its output and exit code, the way a user would. `sys.executable` is the Python running the test, so the matrix version is respected.

### Tests of the workflow files

`tests/pipeline/test_workflows.py` loads `ci.yml` with PyYAML and asserts the lesson's checklist: the token starts read-only; every job states `permissions` and `timeout-minutes`; the matrix values and `fail-fast: false`; the pip cache keys; the report upload (always, with a unique name, `retention-days: 7` and `if-no-files-found: error`); the concurrency expression; `paths-ignore` on both events; the companion workflow and the same `ci-ok` name; the gate job; the manual-only measurement workflows; and that every action is pinned. The workflow becomes testable code.

### Coverage

```text
python -m pytest --cov --cov-report=term-missing --cov-fail-under=95
```

`--cov` turns on measurement using the packages named in `[tool.coverage.run] source`. `term-missing` lists the line numbers not run. `--cov-fail-under=95` makes the exit code non-zero below 95 percent. CI uses `--cov-report=xml` to write `coverage.xml` for the artifact.

<!-- walk:tests/unit/test_arithmetic.py -->
### `tests/unit/test_arithmetic.py`, line by line

Lines 1 to 5:

```python
import pytest

import mathkit
from mathkit.domain.arithmetic import divide, multiply, subtract
from mathkit.domain.errors import DivisionByZeroError
```

Imports. `import pytest` loads the test framework (for `pytest.approx` and `pytest.raises`). `import mathkit` imports the package; `mathkit.add` therefore works because `mathkit/__init__.py` re-exports it. The other lines import specific functions and the error class.

Lines 8 to 25:

```python
def test_add_returns_the_sum_of_two_numbers():
    assert mathkit.add(2, 3) == 5

def test_add_keeps_floats_exact_enough_for_a_sum_of_tenths():
    assert mathkit.add(0.5, 0.25) == pytest.approx(0.75)

def test_subtract_returns_the_difference():
    assert subtract(2, 5) == -3

def test_multiply_returns_the_product():
    assert multiply(4, 2.5) == 10

def test_divide_returns_the_quotient_as_a_float():
    assert divide(7, 2) == 3.5
```

Plain tests. pytest runs every function named `test_...` in a file named `test_*.py`; a bare `assert condition` is the check, and when it fails pytest shows the values. `add(2, 3) == 5`, `subtract(2, 5) == -3`, `multiply(4, 2.5) == 10`, `divide(7, 2) == 3.5`. For floats the test uses `pytest.approx(0.75)`, which compares with a tiny tolerance (floating-point numbers cannot store most decimals exactly).

Lines 28 to 34:

```python
def test_divide_by_zero_raises_a_named_error():
    with pytest.raises(DivisionByZeroError, match="zero"):
        divide(1, 0)

def test_the_package_exposes_the_documented_names():
    assert sorted(mathkit.__all__) == ["add", "divide", "mean", "median", "multiply", "subtract"]
```

`with pytest.raises(DivisionByZeroError, match="zero"):` is a **context manager**: the test passes only if the code inside raises that error and the error's message matches the regular expression `zero`. The last test checks that `sorted(mathkit.__all__)` is exactly the six documented names.

<!-- /walk:tests/unit/test_arithmetic.py -->

<!-- walk:tests/unit/test_statistics.py -->
### `tests/unit/test_statistics.py`, line by line

Lines 1 to 5:

```python
import pytest

from mathkit.domain.errors import EmptyInputError
from mathkit.domain.statistics import mean, median
from mathkit.domain.summary import ColumnSummary
```

Imports of the functions, error and summary class under test.

Lines 8 to 14:

```python
def test_mean_sums_exactly():
    assert mean([0.1] * 10) == 0.1

def test_mean_of_nothing_is_an_error():
    with pytest.raises(EmptyInputError):
        mean([])
```

`mean([0.1] * 10) == 0.1`: the list `[0.1] * 10` repeats the item ten times; `math.fsum` adds them exactly enough that the mean is exactly `0.1`. (Plain left-to-right addition of ten `0.1` values gives `0.9999999999999999` on Python versions before 3.12, whose built-in `sum` of floats was improved; `fsum` gives the right answer on every version, which is why the test is written this way.) `mean([])` must raise `EmptyInputError`.

Lines 17 to 27:

```python
def test_median_of_an_odd_count_is_the_middle_value():
    assert median([9, 1, 5]) == 5

def test_median_of_an_even_count_averages_the_middle_two():
    assert median([4, 1, 3, 2]) == 2.5

def test_median_of_nothing_is_an_error():
    with pytest.raises(EmptyInputError):
        median([])
```

`median([9, 1, 5]) == 5` (sorted: 1, 5, 9; the middle one); `median([4, 1, 3, 2]) == 2.5` (sorted: 1, 2, 3, 4; the average of 2 and 3); `median([])` raises `EmptyInputError`.

Lines 30 to 38:

```python
def test_a_column_summary_describes_its_values():
    summary = ColumnSummary.of("price", [3.0, 1.0, 2.0])
    assert (summary.count, summary.mean, summary.median, summary.minimum, summary.maximum) == (3, 2.0, 2.0, 1.0, 3.0)

def test_a_column_summary_is_immutable():
    summary = ColumnSummary.of("price", [1.0])
    with pytest.raises(AttributeError):
        summary.count = 2  # type: ignore[misc]
```

`ColumnSummary.of("price", [3.0, 1.0, 2.0])` has count 3, mean 2.0, median 2.0, minimum 1.0, maximum 3.0; the test compares two tuples. The last test shows the summary is **immutable**: assigning `summary.count = 2` raises `AttributeError`. The comment `# type: ignore[misc]` tells the type checker (mypy) to ignore the deliberate mistake on this line, naming the kind of error it would otherwise report.

<!-- /walk:tests/unit/test_statistics.py -->

<!-- walk:tests/unit/test_summarize.py -->
### `tests/unit/test_summarize.py`, line by line

Lines 1 to 12:

```python
import pytest

from mathkit.application.summarize import SummarizeTable
from mathkit.domain.errors import InvalidTableError

class FakeSource:
    def __init__(self, columns):
        self._columns = columns

    def numeric_columns(self, table_text):
        return self._columns
```

Imports and `FakeSource`, a **test double**: a tiny class that satisfies the `ColumnSource` protocol by returning whatever columns it was given, so the use case can be tested without pandas.

Lines 15 to 23:

```python
def test_each_numeric_column_gets_a_summary_in_order():
    use_case = SummarizeTable(FakeSource({"a": (1.0, 3.0), "b": (10.0,)}))
    summaries = use_case("ignored")
    assert [(s.name, s.mean) for s in summaries] == [("a", 2.0), ("b", 10.0)]

def test_a_table_without_numeric_columns_is_rejected():
    with pytest.raises(InvalidTableError, match="numeric"):
        SummarizeTable(FakeSource({}))("ignored")
```

Test 1: two columns (`a` with 1.0 and 3.0, `b` with 10.0) give two summaries in that order, with means 2.0 and 10.0 (a list comprehension builds `(name, mean)` pairs). Test 2: with no columns (`{}`) the call raises `InvalidTableError` with a message matching `numeric`.

<!-- /walk:tests/unit/test_summarize.py -->

<!-- walk:tests/unit/test_cli.py -->
### `tests/unit/test_cli.py`, line by line

Lines 1 to 3:

```python
import pytest

from mathkit.interfaces.cli import main
```

Imports the `main` function of the command-line layer.

Lines 6 to 17:

```python
@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["add", "2", "3"], "5"),
        (["subtract", "2", "3"], "-1"),
        (["multiply", "2", "3"], "6"),
        (["divide", "1", "4"], "0.25"),
    ],
)
def test_an_operation_prints_its_result(argv, expected, capsys):
    assert main(argv) == 0
    assert capsys.readouterr().out.strip() == expected
```

`@pytest.mark.parametrize(("argv", "expected"), [...])` is a decorator that runs one test several times, once per pair: `add 2 3` prints `5`, `subtract 2 3` prints `-1`, `multiply 2 3` prints `6`, `divide 1 4` prints `0.25`. The test parameter `capsys` is a built-in **fixture** (a helper pytest supplies when a test names it) that captures what the program prints; `capsys.readouterr().out` is standard output and `.err` standard error.

Lines 20 to 27:

```python
def test_division_by_zero_exits_1_with_a_message(capsys):
    assert main(["divide", "1", "0"]) == 1
    assert "zero" in capsys.readouterr().err

def test_a_missing_file_exits_1_with_a_message(capsys, tmp_path):
    assert main(["summarize", str(tmp_path / "missing.csv")]) == 1
    assert "cannot read" in capsys.readouterr().err
```

Division by zero returns exit code 1 and the error text contains `zero`. A missing file (`tmp_path` is a fixture that gives a fresh temporary folder) returns 1 and the message contains `cannot read`.

Lines 30 to 33:

```python
def test_no_command_is_a_usage_error():
    with pytest.raises(SystemExit) as raised:
        main([])
    assert raised.value.code == 2
```

With no command, `argparse` itself ends the program: it raises `SystemExit` with code 2. `pytest.raises(SystemExit) as raised` captures it and the test checks `raised.value.code == 2`.

<!-- /walk:tests/unit/test_cli.py -->

<!-- walk:tests/e2e/test_cli_end_to_end.py -->
### `tests/e2e/test_cli_end_to_end.py`, line by line

Lines 1 to 10:

```python
"""The command-line program run as a separate process, the way a user starts it."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
```

The docstring says the program runs as a **separate process**, the way a user starts it. The imports include `os`, `subprocess` and `sys`. `ROOT = Path(__file__).resolve().parents[2]` finds the repository root: this file's absolute path, two folders up.

Lines 13 to 17:

```python
def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "mathkit", *args], capture_output=True, text=True, env=env, check=False
    )
```

`run(*args)` starts `python -m mathkit <args>` (`sys.executable` is the Python running the tests, so the same version is used). `env={**os.environ, "PYTHONPATH": str(ROOT / "src")}` copies the current environment variables and adds `PYTHONPATH`, which tells Python where to find the `mathkit` package. `capture_output=True, text=True` collects output as text; `check=False` means a failing exit code does not raise an error.

Lines 20 to 37:

```python
def test_add_prints_five():
    result = run("add", "2", "3")
    assert (result.returncode, result.stdout.strip()) == (0, "5")

def test_summarize_prints_one_line_per_numeric_column(tmp_path):
    table = tmp_path / "t.csv"
    table.write_text("x,y\n1,10\n3,20\n", encoding="utf-8")
    result = run("summarize", str(table))
    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "x: count=2 mean=2 median=2 min=1 max=3",
        "y: count=2 mean=15 median=15 min=10 max=20",
    ]

def test_a_failure_has_a_nonzero_exit_code():
    assert run("divide", "1", "0").returncode == 1
```

Three tests. `add 2 3` exits 0 and prints `5`. `summarize` on a CSV written to a temporary file (`x,y` / `1,10` / `3,20`) prints one line per numeric column: `x: count=2 mean=2 median=2 min=1 max=3` and `y: count=2 mean=15 median=15 min=10 max=20`. `divide 1 0` exits with code 1.

Lines 40 to 45:

```python
def test_the_break_on_purpose_switch_fails_only_on_the_named_version():
    """Lesson step 2: set the repository variable DEMO_FAIL_ON_PYTHON=3.10 to turn one matrix cell red."""
    target = os.environ.get("MATHKIT_DEMO_FAIL_ON_PYTHON", "")
    if target != f"{sys.version_info.major}.{sys.version_info.minor}":
        pytest.skip("MATHKIT_DEMO_FAIL_ON_PYTHON does not name this interpreter")
    pytest.fail(f"deliberate failure on Python {target} (MATHKIT_DEMO_FAIL_ON_PYTHON)")
```

The "break on purpose" switch of the lesson. It reads the environment variable `MATHKIT_DEMO_FAIL_ON_PYTHON` (default empty). If it does not equal the running interpreter's `major.minor` (for example `3.10`), the test is **skipped** with `pytest.skip(...)`. If it matches, `pytest.fail(...)` fails the test on purpose. The workflow sets this variable from a repository variable, so one cell of the version matrix can be turned red to prove the other cells still run and report.

<!-- /walk:tests/e2e/test_cli_end_to_end.py -->

<!-- walk:tests/integration/test_pandas_source.py -->
### `tests/integration/test_pandas_source.py`, line by line

Lines 1 to 9:

```python
"""The pandas adapter against the real pandas and numpy, the dependencies the CI cache exists for."""

import pytest

from mathkit.application.summarize import SummarizeTable
from mathkit.domain.errors import InvalidTableError
from mathkit.infrastructure.pandas_source import PandasColumnSource

CSV = "name,price,qty\nwidget,2.5,4\ngadget,3.5,\nthing,4.5,6\n"
```

The docstring: the adapter is tested against the real pandas and numpy, the dependencies the CI cache exists for. `CSV` is a four-line table as a text: columns `name`, `price`, `qty`; the `gadget` row has an empty `qty` (a missing value).

Lines 12 to 28:

```python
def test_numeric_columns_are_read_and_text_columns_are_left_out():
    columns = PandasColumnSource().numeric_columns(CSV)
    assert list(columns) == ["price", "qty"]

def test_missing_values_are_dropped_per_column():
    assert PandasColumnSource().numeric_columns(CSV)["qty"] == (4.0, 6.0)

def test_text_that_is_not_a_table_is_rejected():
    with pytest.raises(InvalidTableError):
        PandasColumnSource().numeric_columns("")

def test_the_use_case_summarizes_through_the_real_adapter():
    price = SummarizeTable(PandasColumnSource())(CSV)[0]
    assert (price.name, price.count, price.mean, price.median) == ("price", 3, 3.5, 3.5)
```

Four tests. (1) The numeric columns are `price` and `qty`; the text column `name` is left out. (2) The missing `qty` value is dropped, leaving `(4.0, 6.0)`. (3) The empty text `""` is rejected with `InvalidTableError` (pandas raises `EmptyDataError`, which the adapter converts). (4) Through the real adapter the use case reports for `price`: name `price`, count 3, mean 3.5, median 3.5.

<!-- /walk:tests/integration/test_pandas_source.py -->

<!-- walk:tests/pipeline/test_billing.py -->
### `tests/pipeline/test_billing.py`, line by line

Lines 1 to 12:

```python
import json
from pathlib import Path

import pytest

from pipeline import billing

FIXTURES = Path(__file__).parent / "fixtures"

def job(name, labels, start, end):
    return {"name": name, "labels": labels, "started_at": start, "completed_at": end}
```

Imports and `FIXTURES`, the folder `fixtures` next to this file (`Path(__file__).parent / "fixtures"`; `/` joins path parts). `job(name, labels, start, end)` builds a dictionary shaped like one job in GitHub's API answer.

Lines 15 to 29:

```python
def test_each_job_rounds_up_to_the_next_whole_minute():
    jobs = billing.parse_jobs({"jobs": [job("a", ["ubuntu-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:01:01Z")]})
    assert jobs[0].billable_minutes == 2

def test_windows_minutes_count_double_and_macos_ten_times():
    jobs = billing.parse_jobs(
        {
            "jobs": [
                job("w", ["windows-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"),
                job("m", ["macos-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"),
            ]
        }
    )
    assert [j.billable_minutes for j in jobs] == [2, 10]
```

Test 1: a job that ran from `00:00:00` to `00:01:01` (61 seconds) bills **2** minutes (rounded up). Test 2: two jobs of exactly one minute: the Windows one bills 2 and the macOS one 10 (`[j.billable_minutes for j in jobs] == [2, 10]`).

Lines 32 to 48:

```python
def test_a_skipped_job_costs_nothing():
    payload = {"jobs": [{"name": "s", "labels": [], "started_at": None, "completed_at": None}]}
    assert billing.parse_jobs(payload) == ()
    assert billing.run_cost(()) == billing.RunCost(0.0, 0)

def test_wall_time_runs_from_the_first_start_to_the_last_end():
    jobs = billing.parse_jobs(
        {
            "jobs": [
                job("a", ["ubuntu-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:02:00Z"),
                job("b", ["ubuntu-latest"], "2026-01-01T00:00:10Z", "2026-01-01T00:03:05Z"),
            ]
        }
    )
    cost = billing.run_cost(jobs)
    assert (cost.wall_seconds, cost.billable_minutes) == (185.0, 2 + 3)
```

Test 3: a skipped job (`started_at: None`) is left out, so `parse_jobs` returns an empty tuple, and a run with no jobs costs `RunCost(0.0, 0)`. Test 4: job `a` runs `00:00:00` to `00:02:00`, job `b` runs `00:00:10` to `00:03:05`; the wall time is from the first start to the last end, `185.0` seconds, and the billable minutes are `2 + 3` (120 s is 2 minutes, 175 s rounds up to 3).

Lines 51 to 72:

```python
def test_format_duration_reads_as_minutes_and_seconds():
    assert billing.format_duration(140) == "2m 20s"

def test_the_stage_table_uses_the_median_of_the_runs(capsys):
    plain = [FIXTURES / f"plain-{n}.json" for n in (1, 2, 3)]
    assert billing.main(["--stage", "1 plain (1 job)", *map(str, plain)]) == 0
    out = capsys.readouterr().out
    assert "1 plain (1 job)" in out
    assert "2m 20s" in out
    assert "(median of 3 runs)" in out

def test_the_matrix_fixture_bills_windows_double():
    payload = json.loads((FIXTURES / "matrix-1.json").read_text(encoding="utf-8"))
    cost = billing.run_cost(billing.parse_jobs(payload))
    assert cost.billable_minutes == 3 * 2 + 3 * 3 * 2

def test_a_stage_without_run_files_is_a_usage_error():
    with pytest.raises(SystemExit):
        billing.main(["--stage", "only-a-name"])
```

`format_duration(140)` is `2m 20s`. The table test passes three fixture files and checks the printed table contains the stage name, the median time `2m 20s` and `(median of 3 runs)`; `*map(str, plain)` turns each `Path` into text and spreads them into the argument list. The matrix fixture bills `3 * 2 + 3 * 3 * 2` = 24 minutes: three Linux jobs of 100 s (2 minutes each) and three Windows jobs of 180 s (3 minutes, twice the rate). A `--stage` with a name but no run file makes `argparse` exit, which `pytest.raises(SystemExit)` catches.

<!-- /walk:tests/pipeline/test_billing.py -->

<!-- walk:tests/pipeline/test_cache_key.py -->
### `tests/pipeline/test_cache_key.py`, line by line

Lines 1 to 10:

```python
import hashlib

from pipeline import cache_key

def test_the_hash_is_a_sha256_of_the_file_digest_like_hashfiles(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_bytes(b"numpy==2.1.3\n")
    inner = hashlib.sha256(b"numpy==2.1.3\n").digest()
    assert cache_key.hash_files([lock]) == hashlib.sha256(inner).hexdigest()
```

Test 1 reproduces `hashFiles()` by hand: write the bytes `numpy==2.1.3\n`, hash them (`hashlib.sha256(...).digest()` gives the 32-byte digest) and hash that digest again; the module's `hash_files` must give the same hex text. `write_bytes` writes raw bytes.

Lines 13 to 26:

```python
def test_the_key_names_the_os_architecture_python_and_hash(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_text("pandas==2.2.3\n", encoding="utf-8")
    key = cache_key.setup_python_key("Linux", "x64", "3.12.7", lock)
    assert key.startswith("setup-python-Linux-x64-python-3.12.7-pip-")
    assert key.endswith(cache_key.hash_files([lock]))

def test_changing_one_pinned_version_changes_the_key_so_the_cache_misses(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_text("pandas==2.2.3\n", encoding="utf-8")
    before = cache_key.setup_python_key("Linux", "x64", "3.12.7", lock)
    lock.write_text("pandas==2.2.2\n", encoding="utf-8")
    assert cache_key.setup_python_key("Linux", "x64", "3.12.7", lock) != before
```

Test 2: the key starts with `setup-python-Linux-x64-python-3.12.7-pip-` and ends with the file's hash. Test 3: changing the pinned `pandas==2.2.3` to `2.2.2` changes the key, so the cache would miss.

Lines 29 to 41:

```python
def test_the_same_file_gives_the_same_key_so_the_second_run_hits(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_text("pandas==2.2.3\n", encoding="utf-8")
    assert cache_key.setup_python_key("Linux", "x64", "3.12.7", lock) == cache_key.setup_python_key(
        "Linux", "x64", "3.12.7", lock
    )

def test_the_command_prints_the_key(tmp_path, capsys):
    lock = tmp_path / "requirements.txt"
    lock.write_text("x\n", encoding="utf-8")
    assert cache_key.main(["--file", str(lock), "--os", "Windows"]) == 0
    assert capsys.readouterr().out.startswith("setup-python-Windows-x64-python-3.12.7-pip-")
```

Test 4: the same file gives the same key twice, so a second run would hit. Test 5: `main(['--file', path, '--os', 'Windows'])` returns 0 and prints a key starting `setup-python-Windows-x64-python-3.12.7-pip-` (the defaults fill in architecture and version).

<!-- /walk:tests/pipeline/test_cache_key.py -->

<!-- walk:tests/pipeline/test_gate.py -->
### `tests/pipeline/test_gate.py`, line by line

Lines 1 to 16:

```python
import json

from pipeline import gate

def test_all_success_passes():
    assert gate.failed_jobs({"lint": {"result": "success"}, "test": {"result": "success"}}) == []

def test_a_skipped_job_passes():
    assert gate.failed_jobs({"test": {"result": "skipped"}}) == []

def test_failure_and_cancellation_are_named_in_order():
    needs = {"test": {"result": "failure"}, "lint": {"result": "success"}, "audit": {"result": "cancelled"}}
    assert gate.failed_jobs(needs) == ["audit", "test"]
```

Imports `json` and the module. Tests of `failed_jobs`: all `success` passes (empty list); a `skipped` job passes; with `failure` and `cancelled` among the needs, the result is the sorted names `['audit', 'test']`.

Lines 19 to 28:

```python
def test_main_exits_1_and_names_the_failed_job(monkeypatch, capsys):
    monkeypatch.setenv("NEEDS", json.dumps({"test": {"result": "failure"}}))
    assert gate.main() == 1
    assert "test" in capsys.readouterr().err

def test_main_exits_0_when_everything_passed(monkeypatch, capsys):
    monkeypatch.setenv("NEEDS", json.dumps({"lint": {"result": "success"}, "test": {"result": "success"}}))
    assert gate.main() == 0
    assert "2 jobs green" in capsys.readouterr().out
```

Tests of `main` use pytest's `monkeypatch` fixture, which changes things for one test and restores them afterwards: `monkeypatch.setenv("NEEDS", json.dumps({...}))` sets the environment variable the gate reads (`json.dumps` turns a dictionary into JSON text). A failed job gives exit 1 and the name on standard error; all green gives exit 0 and `2 jobs green` on standard output.

<!-- /walk:tests/pipeline/test_gate.py -->

<!-- walk:tests/pipeline/test_pathfilter.py -->
### `tests/pipeline/test_pathfilter.py`, line by line

Lines 1 to 5:

```python
import pytest

from pipeline.pathfilter import matches, starts_workflow

IGNORE = ["docs/**", "**.md"]
```

Imports and `IGNORE = ["docs/**", "**.md"]`, the `paths-ignore` list used by the workflow.

Lines 8 to 27:

```python
@pytest.mark.parametrize(
    ("path", "pattern", "expected"),
    [
        ("docs/index.md", "docs/**", True),
        ("docs/adr/0001-x.md", "docs/**", True),
        ("src/docs/index.md", "docs/**", False),
        ("README.md", "**.md", True),
        ("src/notes/a.md", "**.md", True),
        ("src/mathkit/__init__.py", "**.md", False),
        ("src/mathkit/a.py", "src/*.py", False),
        ("src/a.py", "src/*.py", True),
        ("a.yml", "*.y?ml", True),
        ("a.ml", "*.y?ml", True),
        ("a.yaml", "*.y?ml", False),
        ("a.py", "[ab].py", True),
        ("c.py", "[ab].py", False),
    ],
)
def test_glob_patterns_follow_the_documented_syntax(path, pattern, expected):
    assert matches(path, [pattern]) is expected
```

One test run thirteen times with `parametrize`; each row is `(path, pattern, expected)`. `docs/**` matches `docs/index.md` and `docs/adr/0001-x.md` (the `**` crosses folders) but not `src/docs/index.md` (the pattern is anchored to the start). `**.md` matches `README.md` and `src/notes/a.md` but not a `.py` file. `src/*.py` matches `src/a.py` but not `src/mathkit/a.py` (`*` does not cross `/`). `*.y?ml` matches `a.yml` and also `a.ml` (the `?` makes the `y` optional) but not `a.yaml`. `[ab].py` matches `a.py` but not `c.py`. `is expected` compares with `True`/`False` by identity.

Lines 30 to 53:

```python
def test_a_documentation_only_change_starts_nothing():
    assert starts_workflow(["docs/index.md", "README.md"], paths_ignore=IGNORE) is False

def test_a_change_under_the_source_starts_the_workflow():
    assert starts_workflow(["src/mathkit/domain/arithmetic.py"], paths_ignore=IGNORE) is True

def test_a_mixed_change_starts_the_workflow():
    assert starts_workflow(["docs/index.md", "src/mathkit/__init__.py"], paths_ignore=IGNORE) is True

def test_paths_starts_the_workflow_when_one_file_matches():
    assert starts_workflow(["docs/a.md", "x.py"], paths=["docs/**"]) is True
    assert starts_workflow(["x.py"], paths=["docs/**"]) is False

def test_no_filter_always_starts():
    assert starts_workflow(["anything"]) is True

def test_both_filters_on_one_event_are_rejected():
    with pytest.raises(ValueError, match="together"):
        starts_workflow(["a"], paths=["a"], paths_ignore=["b"])
```

Tests of `starts_workflow`: a docs-only change (`docs/index.md`, `README.md`) starts nothing under `paths_ignore`; a source change starts it; a mixed change starts it (not every file is ignored); with `paths=["docs/**"]` the workflow starts when one changed file matches; with no filter it always starts; giving both filters raises `ValueError` matching `together`.

<!-- /walk:tests/pipeline/test_pathfilter.py -->

<!-- walk:tests/pipeline/test_pins.py -->
### `tests/pipeline/test_pins.py`, line by line

Lines 1 to 9:

```python
from pipeline import pins

SHA = "a" * 40

def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
```

Imports and helpers. `SHA = "a" * 40` is a fake 40-character commit hash. `write(root, relative, text)` writes a file, creating the missing folders (`path.parent.mkdir(parents=True, exist_ok=True)`).

Lines 12 to 21:

```python
def test_a_full_sha_a_local_path_and_a_digest_are_pinned():
    assert pins.is_pinned(f"actions/checkout@{SHA}")
    assert pins.is_pinned("./.github/actions/setup")
    assert pins.is_pinned("docker://rhysd/actionlint@sha256:" + "b" * 64)

def test_a_tag_a_branch_and_a_short_sha_are_not_pinned():
    assert not pins.is_pinned("actions/checkout@v4")
    assert not pins.is_pinned("actions/checkout@main")
    assert not pins.is_pinned("actions/checkout@abc1234")
```

Pinned: a full SHA, a local path and a 64-hex Docker digest. Not pinned: a tag `@v4`, a branch `@main`, a short hash `@abc1234`.

Lines 24 to 40:

```python
def test_violations_name_the_file_and_the_reference(tmp_path):
    write(
        tmp_path,
        ".github/workflows/a.yml",
        f"jobs:\n  j:\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/cache@{SHA}\n",
    )
    assert pins.violations(tmp_path) == [".github/workflows/a.yml: actions/checkout@v4"]

def test_job_level_uses_and_composite_action_steps_are_checked(tmp_path):
    write(tmp_path, ".github/workflows/b.yml", "jobs:\n  call:\n    uses: org/repo/.github/workflows/x.yml@v1\n")
    write(
        tmp_path,
        ".github/actions/t/action.yml",
        "runs:\n  using: composite\n  steps:\n    - uses: actions/setup-python@v5\n",
    )
    assert len(pins.violations(tmp_path)) == 2
```

`tmp_path` is a built-in fixture (a fresh temporary folder per test). Test 1: one workflow with an unpinned and a pinned `uses`; only the unpinned one is reported as `.github/workflows/a.yml: actions/checkout@v4`. Test 2: a job-level `uses` (a reusable workflow called by tag) and a step inside a composite action file (`using: composite`) are both checked: 2 violations.

Lines 43 to 48:

```python
def test_main_exits_1_on_a_violation_and_0_when_clean(tmp_path, capsys):
    write(tmp_path, ".github/workflows/a.yml", "jobs:\n  j:\n    steps:\n      - uses: actions/checkout@v4\n")
    assert pins.main([str(tmp_path)]) == 1
    assert "not pinned" in capsys.readouterr().err
    write(tmp_path, ".github/workflows/a.yml", f"jobs:\n  j:\n    steps:\n      - uses: actions/checkout@{SHA}\n")
    assert pins.main([str(tmp_path)]) == 0
```

`main` returns 1 and prints `not pinned` for a violation; after the file is fixed to use the SHA it returns 0.

<!-- /walk:tests/pipeline/test_pins.py -->

<!-- walk:tests/pipeline/test_slowest_tests.py -->
### `tests/pipeline/test_slowest_tests.py`, line by line

Lines 1 to 9:

```python
from pipeline import slowest_tests

REPORT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="3">
<testcase classname="tests.unit.test_a" name="test_fast" time="0.001"/>
<testcase classname="tests.unit.test_a" name="test_slow" time="1.250"/>
<testcase classname="tests.unit.test_b" name="test_middle" time="0.300"/>
</testsuite></testsuites>
"""
```

`REPORT` is a small JUnit XML text (see `junit-xml.md`) with three `<testcase>` elements and times 0.001, 1.250 and 0.300 seconds.

Lines 12 to 38:

```python
def test_the_slowest_tests_come_first(tmp_path):
    report = tmp_path / "report.xml"
    report.write_text(REPORT, encoding="utf-8")
    assert [name for name, _ in slowest_tests.slowest(report, count=2)] == [
        "tests.unit.test_a::test_slow",
        "tests.unit.test_b::test_middle",
    ]

def test_the_table_is_markdown(tmp_path):
    report = tmp_path / "report.xml"
    report.write_text(REPORT, encoding="utf-8")
    text = slowest_tests.markdown(slowest_tests.slowest(report))
    assert text.startswith("### Slowest tests")
    assert "| `tests.unit.test_a::test_slow` | 1.250 |" in text

def test_main_prints_the_table(tmp_path, capsys):
    report = tmp_path / "report.xml"
    report.write_text(REPORT, encoding="utf-8")
    assert slowest_tests.main([str(report)]) == 0
    assert "Slowest tests" in capsys.readouterr().out

def test_main_without_a_path_is_a_usage_error(capsys):
    assert slowest_tests.main([]) == 2
    assert "usage" in capsys.readouterr().err
```

Tests write the text to a file and check: with `count=2` the slowest two come first, `test_slow` then `test_middle`; the Markdown starts with `### Slowest tests` and contains the row `| `tests.unit.test_a::test_slow` | 1.250 |`; `main` prints the table and returns 0; without an argument it returns 2 and prints `usage`.

<!-- /walk:tests/pipeline/test_slowest_tests.py -->

<!-- walk:tests/pipeline/test_workflows.py -->
### `tests/pipeline/test_workflows.py`, line by line

Lines 1 to 13:

```python
"""The lesson's review checklist, asserted against the real workflow files."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from pipeline import pins
from pipeline.pathfilter import starts_workflow

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
```

The docstring: the lesson's review checklist, asserted against the real workflow files. `ROOT` is the repository root (this file's folder, two levels up) and `WORKFLOWS` the workflows folder.

Lines 16 to 24:

```python
def load(name: str) -> dict[Any, Any]:
    document: dict[Any, Any] = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    document["on"] = document.pop(True)  # YAML 1.1 reads the key `on` as the boolean True
    return document

@pytest.fixture(scope="module")
def ci() -> dict[Any, Any]:
    return load("ci.yml")
```

`load(name)` parses a workflow with `yaml.safe_load`. A comment explains the quirk: YAML 1.1 reads the key `on` as the boolean `True`, so the function renames that key to the text `"on"` (`document.pop(True)` removes it and returns its value). `@pytest.fixture(scope="module")` makes `ci` a **fixture**: a helper whose result is passed to tests naming it as a parameter; `scope="module"` builds it once per file.

Lines 27 to 35:

```python
def test_the_workflow_token_starts_read_only(ci):
    assert ci["permissions"] == {"contents": "read"}

def test_every_job_of_every_workflow_states_its_permissions():
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for name, job in load(path.name)["jobs"].items():
            assert "permissions" in job, f"{path.name}: job {name} has no permissions block"
            assert "timeout-minutes" in job, f"{path.name}: job {name} has no timeout"
```

Checks: the workflow's token starts read-only (`{"contents": "read"}`); every job of every workflow states its `permissions` and `timeout-minutes` (the assertion message names the file and job).

Lines 38 to 57:

```python
def test_the_matrix_is_three_quoted_versions_on_two_systems_and_does_not_fail_fast(ci):
    strategy = ci["jobs"]["test"]["strategy"]
    assert strategy["fail-fast"] is False
    assert strategy["matrix"]["python"] == ["3.10", "3.11", "3.12"]
    assert strategy["matrix"]["os"] == ["ubuntu-latest", "windows-latest"]

def test_the_dependency_cache_is_keyed_on_the_lock_file(ci):
    setup = next(s for s in ci["jobs"]["test"]["steps"] if "setup-python" in s.get("uses", ""))
    assert setup["with"]["cache"] == "pip"
    assert setup["with"]["cache-dependency-path"] == "requirements.txt"

def test_the_report_is_uploaded_also_on_failure_with_a_unique_name_and_short_retention(ci):
    upload = next(s for s in ci["jobs"]["test"]["steps"] if "upload-artifact" in s.get("uses", ""))
    assert upload["if"] == "always()"
    assert "${{ matrix.os }}" in upload["with"]["name"]
    assert "${{ matrix.python }}" in upload["with"]["name"]
    assert upload["with"]["retention-days"] == 7
    assert upload["with"]["if-no-files-found"] == "error"
```

The matrix is `fail-fast: false`, Python versions exactly `["3.10", "3.11", "3.12"]` (quoted, so `3.10` stays text) on `ubuntu-latest` and `windows-latest`. The `setup-python` step has `cache: pip` keyed on `requirements.txt`. The upload step runs `always()`, has `matrix.os` and `matrix.python` in its name (a unique artifact name per cell), `retention-days: 7` and `if-no-files-found: error`. `next(generator)` returns the first matching step.

Lines 60 to 82:

```python
def test_a_newer_push_cancels_the_older_run_on_a_branch_but_never_on_main(ci):
    assert ci["concurrency"]["group"] == "ci-${{ github.ref }}"
    assert ci["concurrency"]["cancel-in-progress"] == "${{ github.ref != 'refs/heads/main' }}"

def test_documentation_only_changes_are_ignored_on_both_events(ci):
    ignore = ["docs/**", "**.md"]
    assert ci["on"]["push"]["paths-ignore"] == ignore
    assert ci["on"]["pull_request"]["paths-ignore"] == ignore

def test_a_docs_only_change_starts_only_the_companion_and_a_source_change_starts_only_ci(ci):
    ignore = ci["on"]["pull_request"]["paths-ignore"]
    companion = load("ci-docs-only.yml")["on"]["pull_request"]["paths"]
    assert not starts_workflow(["docs/index.md"], paths_ignore=ignore)
    assert starts_workflow(["docs/index.md"], paths=companion)
    assert starts_workflow(["src/mathkit/domain/arithmetic.py"], paths_ignore=ignore)
    assert not starts_workflow(["src/mathkit/domain/arithmetic.py"], paths=companion)

def test_the_companion_workflow_reports_the_same_check_name_as_the_gate(ci):
    assert load("ci-docs-only.yml")["jobs"]["ci-ok"]["name"] == ci["jobs"]["ci-ok"]["name"] == "ci-ok"
```

Concurrency group `ci-${{ github.ref }}` and `cancel-in-progress` true except on `main`. `paths-ignore` is `[docs/**, **.md]` on push and pull_request. Using the path-filter model: a docs-only change starts only the companion workflow and a source change starts only `ci`; both workflows have a job named `ci-ok`, so the required check is always reported.

Lines 84 to 94:

```python
def test_the_gate_always_runs_and_needs_every_other_job(ci):
    gate = ci["jobs"]["ci-ok"]
    assert gate["if"] == "always()"
    assert sorted(gate["needs"]) == ["lint", "test"]

def test_the_gate_reads_job_results_from_the_environment_not_from_the_shell_text(ci):
    gate = ci["jobs"]["ci-ok"]
    run_step = next(s for s in gate["steps"] if "run" in s)
    assert "${{" not in run_step["run"]
    assert run_step["env"]["NEEDS"] == "${{ toJSON(needs) }}"
```

The gate job `ci-ok` has `if: always()` and needs exactly `lint` and `test`; its script contains no `${{` and receives `NEEDS` from `toJSON(needs)`, so job results reach the script as data.

Lines 97 to 115:

```python
def test_the_measurement_workflows_are_started_by_hand_only():
    for name in ("measure-1-plain.yml", "measure-2-matrix.yml", "measure-3-cache.yml"):
        assert load(name)["on"] == "workflow_dispatch"

def test_only_the_cache_stage_uses_the_cache():
    def caches(name: str) -> bool:
        steps = load(name)["jobs"]["test"]["steps"]
        return any(s.get("with", {}).get("cache") == "pip" for s in steps)

    assert [caches(n) for n in ("measure-1-plain.yml", "measure-2-matrix.yml", "measure-3-cache.yml")] == [
        False,
        False,
        True,
    ]

def test_every_action_is_pinned_to_a_full_commit_sha():
    assert pins.violations(ROOT) == []
```

The three `measure-*` workflows start only by hand (`on: workflow_dispatch`); only the third uses the pip cache; every action in the repository is pinned to a full SHA (`pins.violations(ROOT) == []`).

<!-- /walk:tests/pipeline/test_workflows.py -->

<!-- walk:tests/pipeline/fixtures/plain-1.json -->
### `tests/pipeline/fixtures/plain-1.json`, line by line

Lines 1 to 12:

```json
{
  "jobs": [
    {
      "name": "test",
      "labels": [
        "ubuntu-latest"
      ],
      "started_at": "2026-10-01T09:00:00Z",
      "completed_at": "2026-10-01T09:02:20Z"
    }
  ]
}
```

A fixture shaped like GitHub's answer for the jobs of a run: one job `test` on `ubuntu-latest`, from `09:00:00` to `09:02:20` (140 seconds). JSON is explained in `json.md`: `jobs` is a list of objects with `name`, `labels`, `started_at` and `completed_at`.

<!-- /walk:tests/pipeline/fixtures/plain-1.json -->

<!-- walk:tests/pipeline/fixtures/plain-2.json -->
### `tests/pipeline/fixtures/plain-2.json`, line by line

Lines 1 to 12:

```json
{
  "jobs": [
    {
      "name": "test",
      "labels": [
        "ubuntu-latest"
      ],
      "started_at": "2026-10-01T09:00:00Z",
      "completed_at": "2026-10-01T09:02:18Z"
    }
  ]
}
```

The same shape: the second run of the "plain" stage, 138 seconds (`09:02:18`).

<!-- /walk:tests/pipeline/fixtures/plain-2.json -->

<!-- walk:tests/pipeline/fixtures/plain-3.json -->
### `tests/pipeline/fixtures/plain-3.json`, line by line

Lines 1 to 12:

```json
{
  "jobs": [
    {
      "name": "test",
      "labels": [
        "ubuntu-latest"
      ],
      "started_at": "2026-10-01T09:00:00Z",
      "completed_at": "2026-10-01T09:02:25Z"
    }
  ]
}
```

The third run of the "plain" stage, 145 seconds (`09:02:25`). The median of 140, 138 and 145 is 140 seconds, `2m 20s`, which the table test expects.

<!-- /walk:tests/pipeline/fixtures/plain-3.json -->

<!-- walk:tests/pipeline/fixtures/matrix-1.json -->
### `tests/pipeline/fixtures/matrix-1.json`, line by line

Lines 1 to 51:

```json
{
  "jobs": [
    {
      "name": "test (ubuntu-latest, 3.10)",
      "labels": [
        "ubuntu-latest"
      ],
      "started_at": "2026-10-01T09:00:00Z",
      "completed_at": "2026-10-01T09:01:40Z"
    },
    {
      "name": "test (ubuntu-latest, 3.11)",
      "labels": [
        "ubuntu-latest"
      ],
      "started_at": "2026-10-01T09:00:00Z",
      "completed_at": "2026-10-01T09:01:40Z"
    },
    {
      "name": "test (ubuntu-latest, 3.12)",
      "labels": [
        "ubuntu-latest"
      ],
      "started_at": "2026-10-01T09:00:00Z",
      "completed_at": "2026-10-01T09:01:40Z"
    },
    {
      "name": "test (windows-latest, 3.10)",
      "labels": [
        "windows-latest"
      ],
      "started_at": "2026-10-01T09:00:05Z",
      "completed_at": "2026-10-01T09:03:05Z"
    },
    {
      "name": "test (windows-latest, 3.11)",
      "labels": [
        "windows-latest"
      ],
      "started_at": "2026-10-01T09:00:05Z",
      "completed_at": "2026-10-01T09:03:05Z"
    },
    {
      "name": "test (windows-latest, 3.12)",
      "labels": [
        "windows-latest"
      ],
      "started_at": "2026-10-01T09:00:05Z",
      "completed_at": "2026-10-01T09:03:05Z"
    }
  ]
```

A run of the matrix stage with six jobs: three on `ubuntu-latest` (`09:00:00` to `09:01:40`, 100 seconds each, billed 2 minutes) and three on `windows-latest` (`09:00:05` to `09:03:05`, 180 seconds each, billed 3 minutes at twice the rate = 6). Total: 3 x 2 + 3 x 6 = 24 minutes, as `test_the_matrix_fixture_bills_windows_double` expects (`3 * 2 + 3 * 3 * 2`).

<!-- /walk:tests/pipeline/fixtures/matrix-1.json -->

## Try it yourself

1. `make test` (or `.venv/bin/python -m pytest -q`) ends with a line like `90 passed, 1 skipped` and a coverage table.
2. `.venv/bin/python -m pytest tests/unit/test_arithmetic.py -v` lists each test name with PASSED.
3. `.venv/bin/python -m pytest -k divide -v` runs only tests with "divide" in the name.
4. `MATHKIT_DEMO_FAIL_ON_PYTHON=3.13 .venv/bin/python -m pytest tests/e2e -q` fails exactly one test with `deliberate failure on Python 3.13`.
5. `.venv/bin/python -m pytest --junitxml=/tmp/r.xml -q && head -c 300 /tmp/r.xml` writes and shows the JUnit report.

## Mistakes people make

- Tests that depend on each other's order or leftover files.
- Asserting on floating-point numbers with `==` (use `pytest.approx`).
- Chasing 100 percent coverage with tests that assert nothing.
- Running pytest from a folder where the package is not importable; this repository sets `pythonpath` for that.
- Forgetting `if: always()` on the upload step so the report is lost when tests fail.

## Check yourself

1. How does pytest find a test? *(File `test_*.py`, function `test_*`.)*
2. What is `tmp_path`? *(A built-in fixture giving a fresh temporary folder.)*
3. Why does the summary say "1 skipped"? *(The break-on-purpose test skips unless the variable names this Python.)*
4. What does `--cov-fail-under=95` do? *(Fails the run if total coverage is below 95 percent.)*
5. What does `parametrize` do? *(Runs one test function once per set of values.)*

## Further reading

- pytest 9 documentation: https://docs.pytest.org/en/9.0.x/
- pytest-cov 5.0: https://pytest-cov.readthedocs.io/en/v5.0.0/
- coverage.py 7: https://coverage.readthedocs.io/en/7.6.0/
