# Git and `.gitignore`

## What it is

Git is a version-control system: a program that records snapshots (**commits**) of a folder so you can see history, undo mistakes and share work. A **repository** is the folder plus its recorded history in a hidden `.git` folder. A **branch** is a movable name for a line of commits. `.gitignore` is a file listing patterns of files Git must not track.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **CI**: Continuous integration: running checks (build, tests, linters) automatically every time code changes.
- **library**: A package of ready-made code that your program calls.
- **cache**: A saved copy of something slow to produce (such as downloaded packages), kept so the next run can reuse it.
- **folder**: A container for files and other folders on disk (also called a directory).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **semantic**: A version scheme where the numbers carry meaning: major for breaking changes, minor for new features, patch for fixes.
- **virtual environment**: A private folder (here `.venv`) holding a copy of the Python interpreter and the packages installed for one project, so projects do not disturb each other.

</details>

<!-- /words -->

## Why this repository uses it

The lesson's whole subject lives in Git: workflows run when you push commits, path filters look at which files a commit changed, and branches are cancelled by newer pushes. This repository is also meant to become its own GitHub repository, with a clean tree.

## Where it appears

| Path | What it does with Git |
| --- | --- |
| `.git/` | The history, with semantic commit messages (`feat:`, `fix:`, `docs:`, `ci:`). |
| `.gitignore` | Keeps the virtual environment, caches, reports and local state out of the repository. |
| `.github/workflows/*` | Triggered by pushes and pull requests. |

## How it works underneath

A commit stores a snapshot of the tracked files plus a message, an author and a pointer to its parent commit. Each commit has a 40-character **SHA** computed from its contents. `git add` copies changes into the **staging area**; `git commit` turns the staged changes into a commit. `git push` sends commits to another repository (GitHub). Files matching `.gitignore` are invisible to `git add`, but a file already tracked stays tracked.

## Walkthrough of this repository's use

```text
.venv/
__pycache__/
*.pyc
*.egg-info/
build/
dist/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.import_linter_cache/
.coverage
coverage.xml
report.xml
.tools/
.env
.DS_Store
logs/
.omc/
```

A trailing `/` means a folder. `*.pyc` matches any compiled Python file. Reasons: `.venv`, caches and `*.egg-info` are rebuilt on demand; `build/` holds the local `act` logs; `report.xml` and `coverage.xml` are test output (uploaded as artifacts, not committed); `.tools/` holds the downloaded `actionlint`; `.env` would hold local settings and possibly secrets; `.DS_Store` is a macOS folder-view file. The lock files `requirements.txt` and `requirements-dev.txt` are **not** ignored: they are committed on purpose.

The commit history is split by concern: scaffold, library, pipeline scripts, CI workflows, act fixes, docs.

<!-- walk:.gitignore -->
### `.gitignore`, line by line

Lines 1 to 18:

```text
.venv/
__pycache__/
*.pyc
*.egg-info/
build/
dist/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.import_linter_cache/
.coverage
coverage.xml
report.xml
.tools/
.env
.DS_Store
logs/
.omc/
```

`.venv/` (the virtual environment), `__pycache__/` and `*.pyc` (Python's compiled bytecode), `*.egg-info/` (packaging metadata), `build/` and `dist/` (generated output; the lab writes act logs into `build/`), `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` and `.import_linter_cache/` (the tools' caches), `.coverage`, `coverage.xml` and `report.xml` (coverage and test reports), `.tools/` (the actionlint binary), `.env` (your own settings), `.DS_Store` (macOS folder metadata), `logs/` and `.omc/` (local files). A trailing `/` matches a folder; `*` matches any characters within a name. Ignoring affects only files that are not yet tracked.

<!-- /walk:.gitignore -->

## Try it yourself

1. `git status` prints `nothing to commit, working tree clean`.
2. `git log --oneline` lists the commits, newest first.
3. `git check-ignore -v .venv report.xml` prints which rule ignores each path.
4. `touch report.xml && git status --short` shows nothing, because the file is ignored.
5. `git show --stat HEAD` shows which files the last commit changed.

## Mistakes people make

- Committing `.venv`, `node_modules` or build output.
- Committing a `.env` with secrets; ignored here, with `.env.example` as the template.
- Adding a pattern to `.gitignore` for a file that is already tracked and expecting it to disappear.
- Ignoring lock files.

## Check yourself

1. What is a SHA in Git? *(The 40-character fingerprint of a commit.)*
2. Why is `report.xml` ignored? *(It is test output made by every run, not source.)*
3. Why are `requirements.txt` and `requirements-dev.txt` committed? *(They are lock files; the cache key depends on them.)*
4. What does a trailing `/` in `.gitignore` mean? *(The pattern matches folders.)*
5. What does `git status` tell you here? *(Whether anything is modified or untracked.)*

## Further reading

- Pro Git book: https://git-scm.com/book/en/v2
- gitignore patterns: https://git-scm.com/docs/gitignore
