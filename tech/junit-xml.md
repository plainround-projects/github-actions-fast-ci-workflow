# JUnit XML

## What it is

JUnit XML is a file format for test results. It started with the Java test tool JUnit, and almost every test tool can now write it. It is XML: text with nested tags such as `<testcase name="...">`. Because many tools understand it, one report can be uploaded, archived, or turned into a summary by any program.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **workflow**: A GitHub Actions automation described in a YAML file under `.github/workflows/`. It names the events that start it and the jobs it runs.
- **artifact**: A file or folder that a job saves so that later jobs, or people, can download it.
- **Markdown**: A plain-text way to write formatted documents: `#` for headings, `-` for bullets, backticks for code, `|` for tables.
- **library**: A package of ready-made code that your program calls.
- **list**: An ordered collection of values written one after another.
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **comprehension**: A short way to build a list, set or dictionary from a loop in one expression, such as `[x * 2 for x in items if x > 0]`.
- **pytest**: A Python test framework: it finds functions named `test_...`, runs them, and reports failures.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

## Why this repository uses it

The lesson uploads test reports as artifacts and asks that a failing run still has its report. `pytest --junitxml=report.xml` writes that file in each matrix job. The repository also reads it: `pipeline/slowest_tests.py` turns it into a table of the five slowest tests for the job summary page.

## Where it appears

| Path | What it does with the format |
| --- | --- |
| `.github/workflows/ci.yml` | Passes `--junitxml=report.xml`, then uploads `report.xml` as an artifact. |
| `pipeline/slowest_tests.py` | Parses `report.xml` and prints Markdown. |
| `tests/pipeline/test_slowest_tests.py` | Feeds it a small hand-written report. |

## How it works underneath

The root has one or more `<testsuite>` elements. Each holds one `<testcase>` per test with attributes `classname`, `name` and `time` (seconds). A failed test has a child element such as `<failure message="...">`. The file is plain text, so you can open it in any editor.

## Walkthrough of this repository's use

```python
def slowest(report: Path, count: int = 5) -> list[tuple[str, float]]:
    cases = [
        (f"{case.get('classname', '')}::{case.get('name', '')}", float(case.get("time", "0")))
        for case in ElementTree.parse(report).getroot().iter("testcase")
    ]
    return sorted(cases, key=lambda item: item[1], reverse=True)[:count]
```

`ElementTree` (standard library) parses XML. `.iter("testcase")` walks the whole tree and yields every `testcase` element. `case.get("time", "0")` reads an attribute with a default. The list comprehension builds `(name, seconds)` pairs. `sorted(..., key=lambda item: item[1], reverse=True)` sorts by the second item, biggest first; `[:count]` keeps the first five. The file is the one pytest wrote a moment earlier in the same job, so it is trusted input (reading untrusted XML needs more care).

```python
lines = ["### Slowest tests", "", "| Test | Seconds |", "| --- | ---: |"]
lines += [f"| `{name}` | {seconds:.3f} |" for name, seconds in rows]
```

Builds a Markdown table. `{seconds:.3f}` formats a number with three decimals. The workflow appends the output to `$GITHUB_STEP_SUMMARY`.

## Try it yourself

1. `.venv/bin/python -m pytest tests/unit -q --junitxml=/tmp/r.xml && head -c 400 /tmp/r.xml` shows `<testsuites>` and the first `<testcase ...>` tags.
2. `.venv/bin/python -m pipeline.slowest_tests /tmp/r.xml` prints a Markdown table with five rows.
3. `grep -c "<testcase" /tmp/r.xml` counts the test cases.

## Mistakes people make

- Assuming the file exists after a crash; the workflow checks `hashFiles('report.xml') != ''` first.
- Parsing untrusted XML with the standard parser; it can be tricked with entity expansion.
- Forgetting that `time` is in seconds, not milliseconds.

## Check yourself

1. What does a `<testcase>` carry? *(`classname`, `name`, `time`, and a child element if it failed.)*
2. Why is it safe to parse here? *(The file was written by pytest in the same job.)*
3. What does `.iter("testcase")` do? *(Walks the tree and yields every testcase element.)*
4. Where does the table go? *(Appended to `$GITHUB_STEP_SUMMARY`.)*
5. Why upload it as an artifact? *(To keep the report after the runner is gone, also when tests fail.)*

## Further reading

- Python `xml.etree.ElementTree`: https://docs.python.org/3.12/library/xml.etree.elementtree.html
- pytest `--junitxml`: https://docs.pytest.org/en/9.0.x/how-to/output.html#creating-junitxml-format-files
