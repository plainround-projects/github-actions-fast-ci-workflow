# Bash

## What it is

Bash is a **shell**: a program that reads commands you type (or write in a file) and runs them. A file of such commands is a **shell script**. On macOS and Linux, Bash is the usual shell. Windows does not have it by default, but the Windows runners GitHub provides include it (Git Bash), which is why workflow steps here set `shell: bash`.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **command line**: The text you type after the prompt in a terminal to run a program, such as `npm test`. The words after the program name are its **arguments**; words that start with `-` or `--` are **options** (also called flags).
- **stdout**: Standard output: the stream where a program writes its normal results. A **stream** is a flow of data written or read piece by piece. Standard error (`stderr`) is a second stream for problems.
- **regular expression**: A compact pattern that describes text, such as `^[0-9]{12}$` (exactly twelve digits). Tools use them to find or check text. Often shortened to **regex**.
- **checksum**: A short fingerprint computed from a file's content. If one byte changes the fingerprint changes, so comparing fingerprints shows whether a file is the one you expected.
- **pull request**: A proposal on GitHub to merge the commits of one branch into another. People review it and automation checks it before it is merged.
- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **workflow**: A GitHub Actions automation described in a YAML file under `.github/workflows/`. It names the events that start it and the jobs it runs.
- **runner**: The computer, usually a virtual machine, on which GitHub runs a job. It starts clean for every job.
- **API**: Application programming interface: a set of requests a program can send to another program or service, with documented answers. A web API is called over the internet with HTTP.
- **HTTP**: The protocol (agreed rules) that web browsers and servers use to talk. A request names a **method** (`GET` to read, `POST` to create, `PATCH` to change part, `PUT` to replace, `DELETE` to remove) and an address; the answer carries a **status code** (200 means success, 404 not found, 500 server problem).
- **URL**: A web address such as `https://api.github.com/zen`.
- **JSON**: A plain-text format for structured data: objects `{ "name": "value" }`, lists `[1, 2]`, texts in double quotes, numbers, `true`, `false`, `null`. It has no comments.
- **container**: A running, isolated copy of a program together with its own files, started from an image. Containers are managed by Docker.
- **Docker**: A tool that builds images and runs containers.
- **folder**: A container for files and other folders on disk (also called a directory).
- **test**: A small program that uses your code and checks that the answer is the one you expected.
- **dictionary**: A Python mapping from keys to values, written `{"key": value}`.
- **matrix**: In GitHub Actions, a list of values (for example operating systems and Python versions) from which GitHub starts one job for every combination.

</details>

<!-- /words -->

## Why this repository uses it

CI steps are mostly one-line commands, and a few need real logic: installing a tool safely, running the matrix locally, or calling the GitHub API. Those are small Bash scripts, checked by ShellCheck (see `shellcheck.md`).

## Where it appears

| Path | What it does with Bash |
| --- | --- |
| `pipeline/install-actionlint.sh` | Downloads a pinned `actionlint`, verifies its checksum, unpacks it. Runs in CI. |
| `scripts/act-matrix.sh` | Runs the test job with `act` once per Python version and summarizes. |
| `scripts/protect-main.sh` | Requires the `ci-ok` check on `main` through `gh api`. |
| `Makefile` recipes | Each recipe line is run by the shell. |
| `.github/workflows/*.yml` | `run:` steps with `shell: bash`. |

## How it works underneath

When you run `scripts/act-matrix.sh`, the operating system reads the first line, `#!/usr/bin/env bash` (the **shebang**), and starts Bash with the script as input. Bash reads one line at a time. Each command starts a new **process**; when it ends it leaves an **exit code**: 0 for success, anything else for failure. `$?` holds the last exit code. A **pipe** (`a | b`) connects the output of `a` to the input of `b`. **Standard output** (stdout, file 1) carries results, **standard error** (stderr, file 2) carries messages; `>` redirects stdout to a file, `2>&1` sends stderr to the same place. **Variables** hold text; `"$name"` uses one. Always put quotes around variable uses, or Bash splits the text on spaces.

## Walkthrough of this repository's use

### The safety line

```bash
set -euo pipefail
```

`-e` stops the script at the first command that fails. `-u` makes using an unset variable an error (it catches typos). `-o pipefail` makes a pipeline fail if *any* part fails, not only the last. Together they turn silent mistakes into loud stops. `pipeline/install-actionlint.sh` and `scripts/protect-main.sh` start with it; `scripts/act-matrix.sh` does too.

### `pipeline/install-actionlint.sh`

```bash
VERSION="1.7.12"
declare -A SUMS=(
  [linux_amd64]="8aca8db96f1b9477..."
  [linux_arm64]="325e971b6ba9bfa5..."
)
```

`declare -A` makes an **associative array**: a dictionary from names to values. It needs Bash 4 or newer, fine on Linux CI. The values are SHA-256 checksums of the official downloads.

```bash
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) platform="linux_amd64" ;;
  Linux-aarch64) platform="linux_arm64" ;;
  *) echo "install-actionlint: unsupported platform $(uname -sm); ..." >&2; exit 1 ;;
esac
```

`$( ... )` runs a command and uses its output. `uname -s` prints the system (`Linux`), `uname -m` the processor. `case` compares the text with patterns; `;;` ends each branch; `*)` is "anything else". `>&2` sends the message to stderr. `exit 1` ends the script with failure.

```bash
dest="${TOOLS_DIR:-.tools}/bin"
mkdir -p "$dest"
archive="$(mktemp)"
trap 'rm -f "$archive"' EXIT
```

`${TOOLS_DIR:-.tools}` means "the value of `TOOLS_DIR`, or `.tools` if it is unset". `mkdir -p` creates folders and does not mind if they exist. `mktemp` makes a unique temporary file. `trap '...' EXIT` registers a command to run when the script ends, however it ends, so the temp file is always removed.

```bash
curl --fail --silent --show-error --location --retry 3 "https://github.com/rhysd/actionlint/releases/download/v${VERSION}/actionlint_${VERSION}_${platform}.tar.gz" -o "$archive"
echo "${SUMS[$platform]}  $archive" | sha256sum --check --status || { echo "install-actionlint: checksum mismatch" >&2; exit 1; }
tar -xzf "$archive" -C "$dest" actionlint
```

`curl` downloads. `--fail` makes HTTP errors fail, `--silent --show-error` hides the progress bar but still prints errors, `--location` follows redirects, `--retry 3` tries again on transient failures. `sha256sum --check` compares the file with the expected checksum; `--status` prints nothing and only sets the exit code. `||` runs the group `{ ...; }` only if the left side failed. `tar -xzf` extracts (`x`) a gzip (`z`) archive (`f` names the file), `-C` changes into the destination first, and the last word picks one member to extract.

### `scripts/act-matrix.sh`

```bash
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
```

`$0` is the script's own path; `dirname` gives its folder; `..` goes up one; `pwd` prints the absolute path. This makes the script work from any folder.

```bash
fail_on=""
if [[ "${1:-}" == "--fail-on" ]]; then
  fail_on="${2:?usage: scripts/act-matrix.sh [--fail-on VERSION]}"
fi
```

`$1`, `$2` are the first and second arguments. `[[ ... ]]` is Bash's test. `${2:?message}` stops with the message if `$2` is missing.

```bash
flags=(--concurrent-jobs 1 --local-repository "$upload_artifact=$root/ci/act-stubs/upload-artifact")
if [[ -n "$fail_on" ]]; then
  flags+=(--var "DEMO_FAIL_ON_PYTHON=$fail_on")
fi
```

`flags=( ... )` is an **array**. `+=( )` appends. `"${flags[@]}"` later expands it into separate, correctly quoted words. `-n` tests that a string is not empty.

```bash
for version in "${versions[@]}"; do
  log="$root/build/act/test-$version${fail_on:+-fail-on-$fail_on}.log"
  if act push "${flags[@]}" -W .github/workflows/ci.yml -j test ... >"$log" 2>&1; then
    results+=("$version:green")
  elif grep -q "Job succeeded" "$log" && ! grep -q "Job failed" "$log"; then
    ...
```

`${fail_on:+text}` gives `text` only if `fail_on` is non-empty. `>"$log" 2>&1` sends both streams to the log file. `if command; then` runs the command and tests its exit code. `grep -q` searches quietly and answers through its exit code. `!` negates.

```bash
for entry in "${results[@]}"; do
  version="${entry%%:*}"
  outcome="${entry##*:}"
```

`${entry%%:*}` removes the longest match of `:*` from the end (leaving the part before the first colon); `${entry##*:}` removes the longest match of `*:` from the start (leaving the part after the last colon). The result array holds strings like `3.10:green`.

### `scripts/protect-main.sh`

```bash
if [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
```

`=~` matches a regular expression. The script refuses anything that is not `OWNER/NAME` before it builds a URL from the value.

```bash
if [[ "${DRY_RUN:-0}" == "1" ]]; then
  echo "gh api -X PUT repos/$repo/branches/main/protection --input - <<< '$(tr -s ' \n' ' ' <<<"$body")'"
else
  gh api -X PUT "repos/$repo/branches/main/protection" --input - <<<"$body"
fi
```

`DRY_RUN=1 scripts/protect-main.sh ...` prints the command instead of running it. `<<<"$body"` is a **here-string**: it feeds the text of `$body` to the command's standard input. `--input -` tells `gh` to read the request body from stdin.

### Bash inside the workflow

```yaml
- run: echo "$PWD/.tools/bin" >> "$GITHUB_PATH"
```

`>>` appends to a file. `GITHUB_PATH` names a file; adding a line makes the folder part of `PATH` for later steps.

<!-- walk:scripts/act-matrix.sh -->
### `scripts/act-matrix.sh`, line by line

Lines 1 to 16:

```bash
#!/usr/bin/env bash
# Run the test job of ci.yml with act, one Python version at a time (act cannot run the Windows legs, and three

# containers installing numpy and pandas at once overload a laptop), then summarize which legs were green.

#
#   usage:  scripts/act-matrix.sh                       every Ubuntu leg must be green

#           scripts/act-matrix.sh --fail-on 3.10        lesson step 2: that leg fails on purpose, the others must still

#                                                       run and report; exits 0 only when exactly that leg is red

set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
versions=(3.10 3.11 3.12)
fail_on=""
if [[ "${1:-}" == "--fail-on" ]]; then
  fail_on="${2:?usage: scripts/act-matrix.sh [--fail-on VERSION]}"
fi
```

The header: run the test job of `ci.yml` with `act`, one Python version at a time (act cannot run the Windows cells, and three containers installing numpy and pandas at once overload a laptop), then summarize which cells were green. `--fail-on VERSION` is the lesson's step 2. `set -euo pipefail` makes the script stop on errors, on unset variables and on failed pipeline parts. `root` is the repository root; `versions=(3.10 3.11 3.12)` is an array; `fail_on` is read from the arguments: `${1:-}` is the first argument or empty, and `${2:?usage...}` stops with a message if the second is missing.

Lines 18 to 27:

```bash
# act's artifact service cannot be reached from a runner container when Docker runs in a VM, so the pinned

# upload-artifact action is replaced by a stand-in that lists the files and checks the missing-file rule. The cache

# service has the same problem: setup-python warns that it cannot restore or save and carries on.

upload_artifact="$(grep -o 'actions/upload-artifact@[0-9a-f]\{40\}' .github/workflows/ci.yml | head -1)"
flags=(--concurrent-jobs 1 --local-repository "$upload_artifact=$root/ci/act-stubs/upload-artifact")
if [[ -n "$fail_on" ]]; then
  flags+=(--var "DEMO_FAIL_ON_PYTHON=$fail_on")
fi

mkdir -p "$root/build/act"
```

The comment explains why `upload-artifact` is replaced: `act`'s artifact service cannot be reached from a runner container when Docker runs in a VM. `upload_artifact` is the exact pinned reference found with `grep -o` (print only the matching part) in `ci.yml`. `flags` is an array: run one job at a time, and use the stand-in folder for that action (`--local-repository`). If `fail_on` is not empty (`-n`), `--var DEMO_FAIL_ON_PYTHON=...` is appended with `flags+=(...)`. `mkdir -p` creates the log folder, `results=()` starts an empty array.

Lines 28 to 42:

```bash
results=()
for version in "${versions[@]}"; do
  log="$root/build/act/test-$version${fail_on:+-fail-on-$fail_on}.log"
  echo "== Python $version"
  if act push "${flags[@]}" -W .github/workflows/ci.yml -j test --matrix os:ubuntu-latest --matrix "python:$version" >"$log" 2>&1; then
    results+=("$version:green")
  elif grep -q "Job succeeded" "$log" && ! grep -q "Job failed" "$log"; then
    # A busy Docker daemon can time out while act removes the job's volumes, after the job itself succeeded.
    echo "   (act reported a Docker cleanup error after the job succeeded; see $log)"
    results+=("$version:green")
  else
    results+=("$version:red")
  fi
  grep -E "Cache (restored|not found|hit)|pip cache is not found|passed|failed|skipped|deliberate|\| artifact reports-|Failure - Main" "$log" | sed 's/^/   /' | cut -c1-200 || true
done
```

The loop over the versions. `log="...${fail_on:+-fail-on-$fail_on}.log"`: `${var:+text}` expands to the text only if the variable is set and non-empty. `act push "${flags[@]}" -W .github/workflows/ci.yml -j test --matrix os:ubuntu-latest --matrix "python:$version"` runs the `test` job for the event `push` with the matrix restricted to one cell; its output goes to the log (`>"$log" 2>&1`). If `act` succeeds the result is `green`. Otherwise, if the log contains `Job succeeded` and not `Job failed`, a Docker clean-up error after a good job is tolerated and counted green; else `red`. The `grep -E ... | sed 's/^/   /' | cut ...` line prints the interesting log lines indented.

Lines 44 to 61:

```bash
echo
printf '%-8s %s\n' "python" "result"
bad=0
for entry in "${results[@]}"; do
  version="${entry%%:*}"
  outcome="${entry##*:}"
  printf '%-8s %s\n' "$version" "$outcome"
  if [[ "$version" == "$fail_on" ]]; then
    [[ "$outcome" == "red" ]] || bad=1
  else
    [[ "$outcome" == "green" ]] || bad=1
  fi
done

if [[ -n "$fail_on" ]]; then
  echo "expected: $fail_on red, the others green and still reporting"
fi
exit "$bad"
```

The summary. `printf '%-8s %s\n'` prints two aligned columns. For each result `"$version:green"`, `${entry%%:*}` removes everything from the first `:` on (the version) and `${entry##*:}` removes everything up to the last `:` (the outcome). A cell named by `--fail-on` must be red; every other must be green; otherwise `bad=1`. The script exits with `bad`, so it succeeds only when exactly the expected cells are red.

<!-- /walk:scripts/act-matrix.sh -->

<!-- walk:scripts/protect-main.sh -->
### `scripts/protect-main.sh`, line by line

Lines 1 to 16:

```bash
#!/usr/bin/env bash
# Lesson step 6: make the `ci-ok` check required for main, so a pull request cannot merge while it is red.

#
#   usage:  scripts/protect-main.sh OWNER/REPO

#           DRY_RUN=1 scripts/protect-main.sh OWNER/REPO    print the command, change nothing

#
# Needs the gh CLI signed in with admin rights on the repository. Run it once, by hand, after the first push: it

# changes a repository setting. `ci-ok` (not the six matrix names) is required because it survives changes to the

# matrix, and ci-docs-only.yml reports the same name for documentation-only changes.

set -euo pipefail

repo="${1:?usage: scripts/protect-main.sh OWNER/REPO}"
if [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  echo "protect-main: '$repo' is not OWNER/REPO" >&2
  exit 2
fi
```

The header: make the check `ci-ok` required for `main`, so a pull request cannot merge while it is red. It needs the `gh` CLI signed in with admin rights; `DRY_RUN=1` prints the command only. `ci-ok` is required instead of the six matrix names because it survives changes to the matrix. The script requires `OWNER/REPO` as its first argument and checks it against a regular expression (letters, digits, `_`, `.`, `-`, one `/`), exiting with 2 otherwise.

Lines 18 to 29:

```bash
body='{
  "required_status_checks": { "strict": true, "contexts": ["ci-ok"] },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}'

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  echo "gh api -X PUT repos/$repo/branches/main/protection --input - <<< '$(tr -s ' \n' ' ' <<<"$body")'"
else
  gh api -X PUT "repos/$repo/branches/main/protection" --input - <<<"$body"
fi
```

`body` is a multi-line text holding JSON: `required_status_checks` with `strict: true` (the branch must be up to date with `main` before merging) and the one required context `ci-ok`; `enforce_admins: false`; no required reviews; no push restrictions. In dry-run mode the command is printed (`tr -s ' \n' ' '` squeezes whitespace into single spaces so the JSON fits on a line). Otherwise `gh api -X PUT repos/$repo/branches/main/protection --input - <<<"$body"` sends it: `-X PUT` chooses the HTTP method, `--input -` reads the request body from standard input and `<<<` feeds the text of `body` into it (a *here-string*).

<!-- /walk:scripts/protect-main.sh -->

<!-- walk:pipeline/install-actionlint.sh -->
### `pipeline/install-actionlint.sh`, line by line

Lines 1 to 10:

```bash
#!/usr/bin/env bash
# Install a pinned actionlint into ./.tools/bin and verify its SHA-256 before unpacking.

# Usage: pipeline/install-actionlint.sh   (Linux amd64 or arm64; on a Mac use `brew install actionlint`)

set -euo pipefail

VERSION="1.7.12"
declare -A SUMS=(
  [linux_amd64]="8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8"
  [linux_arm64]="325e971b6ba9bfa504672e29be93c24981eeb1c07576d730e9f7c8805afff0c6"
)
```

Shebang, comments, `set -euo pipefail`, the version `1.7.12` and an associative array `SUMS` holding the expected SHA-256 checksum of the download for each platform (`declare -A` makes a dictionary, `[key]="value"` an entry; Bash 4 or newer).

Lines 12 to 16:

```bash
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) platform="linux_amd64" ;;
  Linux-aarch64) platform="linux_arm64" ;;
  *) echo "install-actionlint: unsupported platform $(uname -sm); install actionlint $VERSION yourself" >&2; exit 1 ;;
esac
```

`case "$(uname -s)-$(uname -m)" in ... esac` chooses the platform from the operating system and CPU names printed by `uname` (`Linux-x86_64`, `Linux-aarch64`); anything else prints a message to standard error (`>&2`) and exits with 1.

Lines 18 to 26:

```bash
dest="${TOOLS_DIR:-.tools}/bin"
mkdir -p "$dest"
archive="$(mktemp)"
trap 'rm -f "$archive"' EXIT
curl --fail --silent --show-error --location --retry 3 \
  "https://github.com/rhysd/actionlint/releases/download/v${VERSION}/actionlint_${VERSION}_${platform}.tar.gz" -o "$archive"
echo "${SUMS[$platform]}  $archive" | sha256sum --check --status || { echo "install-actionlint: checksum mismatch" >&2; exit 1; }
tar -xzf "$archive" -C "$dest" actionlint
echo "installed actionlint ${VERSION} to $dest/actionlint"
```

`dest` is `${TOOLS_DIR:-.tools}/bin` (the variable, or `.tools` when unset); `mkdir -p` creates it; `mktemp` makes a temporary file and `trap 'rm -f "$archive"' EXIT` deletes it however the script ends. `curl --fail --silent --show-error --location --retry 3 URL -o file` downloads (fail on HTTP errors, quiet except for errors, follow redirects, retry three times). `echo "${SUMS[$platform]}  $archive" | sha256sum --check --status` compares the file's checksum with the expected one; on a mismatch the `||` branch prints `checksum mismatch` and exits 1. Only then `tar -xzf "$archive" -C "$dest" actionlint` unpacks the single file `actionlint` (`-x` extract, `-z` gunzip, `-f` file, `-C` change folder first). The last line reports the install.

<!-- /walk:pipeline/install-actionlint.sh -->

## Try it yourself

1. Check the scripts: `shellcheck scripts/*.sh pipeline/*.sh`. No output means no findings.
2. Dry-run the branch rule: `DRY_RUN=1 scripts/protect-main.sh sumitsr/mathkit` prints the `gh api -X PUT ...` command and changes nothing.
3. See exit codes: `scripts/protect-main.sh bad; echo "exit $?"` prints `protect-main: 'bad' is not OWNER/REPO` and `exit 2`.
4. See the safety line work: `bash -c 'set -e; false; echo not reached'; echo "exit $?"` prints `exit 1` only.
5. See quoting: `bash -c 'f="a b"; printf "%s\n" $f; printf "%s\n" "$f"'` prints two lines, then one.

## Mistakes people make

- Leaving variables unquoted, so a path with a space becomes two words.
- No `set -e`, so a failed download is ignored and the script goes on.
- Using `[ ... ]` with `==` or `&&` inside; `[[ ... ]]` is safer in Bash.
- Pasting untrusted text into a command line (injection). The workflows here pass such text through environment variables.
- Writing Bash 4 features and running on macOS's old `/bin/bash` 3.2. The scripts here avoid associative arrays except the Linux-only installer.

## Check yourself

1. What do `-e`, `-u` and `pipefail` each do? *(Stop on error; error on unset variable; fail a pipeline if any part fails.)*
2. What does `trap '...' EXIT` guarantee? *(The command runs when the script ends, success or failure.)*
3. What does `${2:?usage}` do? *(Stops with the message if the second argument is missing.)*
4. Why `"${flags[@]}"` with quotes? *(Each array element stays one word, even with spaces.)*
5. What does `>"$log" 2>&1` do? *(Sends standard output to the file, then sends standard error to the same place.)*

## Further reading

- GNU Bash manual (the CI and Linux runners have Bash 5): https://www.gnu.org/software/bash/manual/bash.html
- ShellCheck wiki, explaining each warning: https://www.shellcheck.net/wiki/
