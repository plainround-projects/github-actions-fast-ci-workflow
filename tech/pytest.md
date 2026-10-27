# pytest (with pytest-cov and coverage)

## What it is

pytest is a Python tool that finds and runs tests. A **test** is a function that runs a piece of your code and checks the result; if the check fails, the test fails. pytest finds files named `test_*.py`, runs every function in them named `test_*`, and prints a summary. `pytest-cov` is a plugin that adds `--cov` options and uses the library `coverage` to measure which lines of your code the tests ran. This repository pins pytest 9.0.3, pytest-cov 5.0.0 and coverage 7.x (the lock file picks the 7.x release for each Python version).

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

`tests/pipeline/test_workflows.py` loads `ci.yml` with PyYAML and asserts the lesson's checklist: matrix values, `fail-fast: false`, `retention-days: 7`, the concurrency expression, and so on. The workflow becomes testable code.

### Coverage

```text
python -m pytest --cov --cov-report=term-missing --cov-fail-under=95
```

`--cov` turns on measurement using the packages named in `[tool.coverage.run] source`. `term-missing` lists the line numbers not run. `--cov-fail-under=95` makes the exit code non-zero below 95 percent. CI uses `--cov-report=xml` to write `coverage.xml` for the artifact.

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
