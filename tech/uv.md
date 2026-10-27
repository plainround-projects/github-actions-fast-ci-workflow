# uv

## What it is

uv is a fast Python package tool written in Rust. It can do much of what pip and venv do, and it can also **resolve** dependencies: given the packages you name, work out which exact versions of everything satisfy all the requirements at once. This repository uses uv in two places only, and only on a developer's machine, never in CI: `uv pip compile` to make the lock files, and `uv run` to test on several Python versions.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **commit**: A saved snapshot of a project's files in Git, with a message and an author. Every commit has a unique 40-character name (its SHA).
- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **package**: In Python, a folder with an `__init__.py` file that can be imported as a unit; also a bundle of code installed with pip.
- **lock file**: A file that records the exact version, and a checksum, of every package that was installed, so that everyone installs exactly the same thing.
- **folder**: A container for files and other folders on disk (also called a directory).
- **version**: A number such as `1.2.3` that names one release of software (major.minor.patch).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **pytest**: A Python test framework: it finds functions named `test_...`, runs them, and reports failures.

</details>

<!-- /words -->

## Why this repository uses it

The CI cache is keyed on the lock file, and one lock file has to work for Python 3.10, 3.11 and 3.12 on Linux and Windows. pip alone cannot make such a file. `uv pip compile --universal` can: it resolves once for every platform and writes environment markers (see `pip.md`) where the answers differ.

## Where it appears

| Path | What it does with uv |
| --- | --- |
| `requirements.txt`, `requirements-dev.txt` | Header comments record the exact `uv pip compile` command that made them. |
| `Makefile` target `matrix-local` | `uv run --no-project --python $version --with-requirements requirements.txt python -m pytest` for each version. |
| `README.md`, `docs/adr/0002-hash-pinned-universal-lock-files.md` | The commands and the reasons. |

## How it works underneath

`uv pip compile requirements.in -o requirements.txt` reads the top-level requirements, asks the package index which versions exist and what each needs, finds a consistent set, and writes it with hashes. `--universal` makes the answer valid for all platforms and Python versions at once instead of only the current machine. `--python-version 3.10` sets the oldest Python it must support. `uv run --python 3.11 ...` finds or downloads that Python, builds a throwaway environment, and runs the command in it.

## Walkthrough of this repository's use

```bash
uv pip compile requirements.in --universal --generate-hashes --python-version 3.10 -o requirements.txt
uv pip compile requirements-dev.in --universal --generate-hashes --python-version 3.10 -o requirements-dev.txt
```

`--generate-hashes` writes the `--hash=sha256:...` lines. `-o` names the output. Run these two commands after editing an `.in` file, then commit the `.txt` files.

```make
uv run --no-project --python $$version --with-requirements requirements.txt python -m pytest -q -p no:cacheprovider
```

`--no-project` says "do not treat this folder as a uv project". `--with-requirements requirements.txt` installs the lock into the throwaway environment. `-p no:cacheprovider` turns off pytest's cache folder so no files are left behind.

## Try it yourself

1. `uv --version` prints the version.
2. `uv pip compile requirements.in --universal --python-version 3.10 -o /tmp/r.txt` writes a lock without hashes; `grep -c "^[a-z]" /tmp/r.txt` counts the packages.
3. `uv run --no-project --python 3.12 python --version` runs a command on 3.12 (downloads it the first time).
4. `make matrix-local` runs the whole test suite on 3.10, 3.11 and 3.12, one after the other.

## Mistakes people make

- Editing `requirements.txt` by hand instead of the `.in` file.
- Forgetting `--universal` and getting a lock that is wrong on Windows.
- Running `uv` commands that change the project (like `uv add`) when the repository manages dependencies by hand.

## Check yourself

1. What does "resolve" mean? *(Choose exact versions of all packages that satisfy every requirement.)*
2. What does `--universal` add? *(A lock valid for every platform, with environment markers.)*
3. Why `--python-version 3.10`? *(The oldest supported Python decides which versions can be chosen.)*
4. Is uv used in CI? *(No. CI uses pip with the committed lock.)*
5. What does `--no-project` do in `matrix-local`? *(Runs without treating the folder as a uv project.)*

## Further reading

- uv documentation (pinned locally: 0.11.x): https://docs.astral.sh/uv/
- `uv pip compile`: https://docs.astral.sh/uv/pip/compile/
