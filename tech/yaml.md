# YAML

## What it is

YAML is a text format for writing structured data: lists, named values, and nests of both. People read and write it easily, and programs read it too. It is a **file format**, not a language that runs. GitHub Actions workflows, Dependabot settings and the action stand-in in this repository are all YAML files (`.yml` or `.yaml`).

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **shell**: The program inside a terminal that reads what you type and starts other programs. Bash is a shell.
- **workflow**: A GitHub Actions automation described in a YAML file under `.github/workflows/`. It names the events that start it and the jobs it runs.
- **list**: An ordered collection of values written one after another.
- **boolean**: A value that is either true or false.
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **dictionary**: A Python mapping from keys to values, written `{"key": value}`.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

## Why this repository uses it

GitHub Actions only understands YAML for workflow files, and Dependabot only reads a YAML settings file. The repository also has Python code that *reads* the YAML files to check rules about them, so the format matters twice.

## Where it appears

| Path | What it does with YAML |
| --- | --- |
| `.github/workflows/*.yml` | The five workflows. |
| `.github/dependabot.yml` | Settings for the update bot. |
| `ci/act-stubs/upload-artifact/action.yml` | A small action definition used under `act`. |
| `tests/pipeline/test_workflows.py`, `pipeline/pins.py` | Python code that loads workflow YAML with PyYAML (see `pyyaml.md`). |

## How it works underneath

A YAML file is plain text. A program called a **parser** reads it and builds ordinary objects in memory: a **mapping** (names with values, like a dictionary), a **sequence** (a list), and **scalars** (single values: text, numbers, true/false, null).

- Indentation shows nesting. Use spaces, never tabs. Two spaces per level is the habit here.
- `key: value` is a mapping entry. `- item` is a list entry.
- `[a, b]` and `{x: 1}` are the compact forms of a list and a mapping.
- `#` starts a comment that runs to the end of the line.
- `|` after a key starts a **block scalar**: the following indented lines are taken as one text with the line breaks kept.
- Quotes make a value text. Without quotes the parser **guesses** the type: `3.10` becomes the number 3.1, `yes` can become true, `on` can become true.

## Walkthrough of this repository's use

```yaml
python: ["3.10", "3.11", "3.12"]
```

Each version is quoted. Unquoted, `3.10` would be the number 3.1 and `setup-python` would install the wrong version. The quotes are the whole reason this line is safe.

```yaml
run: |
  set -uo pipefail
  ...
```

The `|` keeps several lines as one script. (In the `act` stand-in `ci/act-stubs/upload-artifact/action.yml`, the `run: |` block holds a small shell loop.)

```yaml
paths-ignore: ["docs/**", "**.md"]
```

The quotes matter here too: a plain `*` at the start of a YAML value has a special meaning (an *alias*), so a pattern that starts with `*` must be quoted. `docs/**` is quoted for consistency.

```yaml
cache-dependency-path: requirements.txt
```

A plain scalar. No quotes needed because nothing in it is special.

```yaml
name: reports-${{ matrix.os }}-${{ matrix.python }}
```

`${{ ... }}` is not YAML. It is GitHub's expression syntax; to the YAML parser the whole line is just text, and GitHub fills in the holes later.

A trap that is easy to hit: a colon followed by a space inside an unquoted value, such as `run: echo "Result: ok"`. YAML reads `Result:` as the start of a nested mapping and the file fails to parse with "mapping values are not allowed in this context". Use a block scalar (`run: |`) or quote the whole value.

### YAML in the Python tests

```python
def load(name: str) -> dict[Any, Any]:
    document: dict[Any, Any] = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    document["on"] = document.pop(True)  # YAML 1.1 reads the key `on` as the boolean True
    return document
```

PyYAML (version 6.0.2) follows an older YAML rule set (1.1) in which the bare word `on` means true. So the workflow key `on:` arrives as the Python value `True`, and the test renames it. `safe_load` reads data only; it will not build arbitrary Python objects from a file, which keeps loading untrusted files safe.

## Try it yourself

1. Parse a workflow and print its jobs: `.venv/bin/python -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/ci.yml')); print(list(d['jobs']))"` prints `['lint', 'test', 'ci-ok']`.
2. See the `on` surprise: `.venv/bin/python -c "import yaml; print(list(yaml.safe_load(open('.github/workflows/ci.yml'))))"` shows `True` among the keys instead of `'on'`.
3. See the version trap: `.venv/bin/python -c "import yaml; print(yaml.safe_load('v: 3.10'), yaml.safe_load('v: \"3.10\"'))"` prints `{'v': 3.1} {'v': '3.10'}`.
4. Break a file on purpose in a copy and lint it: `actionlint` reports the YAML error with a line number.

## Mistakes people make

- Unquoted version numbers (`3.10`). Quote them.
- Tabs for indentation. YAML forbids them.
- A colon and a space inside an unquoted value. Use `|` or quotes.
- Assuming `on`, `yes`, `no` are text. In YAML 1.1 parsers they are booleans.
- Wrong indentation by one space, which moves a key to a different parent without any error.

## Check yourself

1. Why is `"3.10"` quoted in the matrix? *(Unquoted it is the number 3.1.)*
2. What does `|` after a key do? *(Starts a block of text with its line breaks kept.)*
3. Why does the test rename `True` to `"on"`? *(PyYAML reads the bare key `on` as the boolean True.)*
4. Is `${{ matrix.os }}` YAML? *(No, it is GitHub's expression syntax inside a YAML text value.)*
5. What does `safe_load` protect you from? *(Building arbitrary Python objects from the file's contents.)*

## Further reading

- YAML 1.2.2 specification: https://yaml.org/spec/1.2.2/
- PyYAML (pinned: 6.0.2): https://pyyaml.org/wiki/PyYAMLDocumentation
