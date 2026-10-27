# PyYAML

## What it is

PyYAML is a Python **library**: code someone else wrote that you install and import. It reads YAML text (see `yaml.md`) and turns it into Python dictionaries, lists, strings and numbers. This repository pins version 6.0.2.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **SHA**: A family of hash functions. A Git **commit SHA** is a 40-character hexadecimal fingerprint that names one exact commit.
- **commit**: A saved snapshot of a project's files in Git, with a message and an author. Every commit has a unique 40-character name (its SHA).
- **tag**: A name attached to a commit in Git, usually a version such as `v1.0.0`. Unlike a commit's SHA, a tag can be moved to another commit.
- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **YAML**: A plain-text format for structured data that uses indentation instead of braces. GitHub workflows are YAML files.
- **package**: In Python, a folder with an `__init__.py` file that can be imported as a unit; also a bundle of code installed with pip.
- **list**: An ordered collection of values written one after another.
- **UTF-8**: The usual way of storing text as bytes, able to represent every written language.
- **version**: A number such as `1.2.3` that names one release of software (major.minor.patch).
- **dictionary**: A Python mapping from keys to values, written `{"key": value}`.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

## Why this repository uses it

Two pieces of this repository need to read workflow files as data. `pipeline/pins.py` checks that every `uses:` line names a full commit SHA. `tests/pipeline/test_workflows.py` turns the lesson's review checklist into assertions about `ci.yml` (three quoted versions, `fail-fast: false`, seven-day retention, and so on). Both would be fragile with plain text search, so they parse the YAML.

## Where it appears

| Path | What it does with PyYAML |
| --- | --- |
| `pipeline/pins.py` | `import yaml`, then `yaml.safe_load(...)` on each workflow file. |
| `tests/pipeline/test_workflows.py` | `yaml.safe_load` on each workflow, then assertions on the result. |
| `requirements.in`, `requirements.txt` | Pins `PyYAML==6.0.2`; the second file also lists its hashes. |
| `requirements-dev.in` | Adds `types-PyYAML`, a separate package that carries type hints so mypy can check code that calls PyYAML. |

## How it works underneath

PyYAML is a **parser**. It reads characters, splits them into tokens (words, colons, dashes, indentation), builds a tree, and converts the tree into Python objects. `yaml.safe_load(text)` does this with a short list of allowed types. The non-safe `yaml.load` can build any Python object named in the file, which makes loading an untrusted file a security hole; that is why only `safe_load` is used. The YAML rules PyYAML follows are version 1.1, where `on`, `yes` and `no` are booleans (see `yaml.md`).

## Walkthrough of this repository's use

```python
def uses_values(document: Any) -> Iterator[str]:
    if not isinstance(document, dict):
        return
    for job in (document.get("jobs") or {}).values():
        if "uses" in job:
            yield str(job["uses"])
        for step in job.get("steps") or []:
            if "uses" in step:
                yield str(step["uses"])
```

After `safe_load` the workflow is a dictionary. `document.get("jobs")` is the mapping of job names to jobs; `or {}` handles a file with no jobs. A job that calls a reusable workflow has a job-level `uses`; a normal job has `steps`, each of which may have `uses`. `yield` hands the values out one by one (see `python.md`).

```python
files = sorted([*root.glob(".github/workflows/*.y*ml"), *root.glob(".github/actions/**/action.y*ml")])
for file in files:
    document = yaml.safe_load(file.read_text(encoding="utf-8"))
```

`Path.glob` finds the files; `*.y*ml` matches both `.yml` and `.yaml`. Each file is read as UTF-8 text and parsed.

## Try it yourself

1. `.venv/bin/python -c "import yaml; print(yaml.__version__)"` prints `6.0.2`.
2. `.venv/bin/python -c "import yaml; print(yaml.safe_load('a: [1, 2]\nb: {c: x}'))"` prints `{'a': [1, 2], 'b': {'c': 'x'}}`.
3. `.venv/bin/python -c "import yaml; yaml.safe_load('a: !!python/object/apply:os.system [echo hi]')"` ends with a `yaml.constructor.ConstructorError`: the safe loader refuses the `!!python/object/apply` tag.
4. `.venv/bin/python -m pipeline.pins` runs the parser over all workflow files and prints the all-pinned message.

## Mistakes people make

- Using `yaml.load` without a safe loader on a file you did not write.
- Forgetting that `on:` becomes `True`.
- Reading a file without `encoding="utf-8"` and getting garbled text on Windows (the matrix tests run there).
- Installing PyYAML but not `types-PyYAML`, so mypy cannot check the calls.

## Check yourself

1. What does `safe_load` return for a mapping? *(A Python dict.)*
2. Why not `yaml.load`? *(It can construct arbitrary Python objects, so a hostile file can run code.)*
3. What is `types-PyYAML` for? *(Type hints for the library, used by mypy.)*
4. Why does `uses_values` check `"uses" in job` before looking at steps? *(A job can call a reusable workflow directly with a job-level `uses`.)*
5. Which version of the YAML rules does PyYAML follow? *(1.1.)*

## Further reading

- PyYAML documentation (pinned: 6.0.2): https://pyyaml.org/wiki/PyYAMLDocumentation
