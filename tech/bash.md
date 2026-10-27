# Bash

## What it is

Bash is a **shell**: a program that reads commands you type (or write in a file) and runs them. A file of such commands is a **shell script**. On macOS and Linux, Bash is the usual shell. Windows does not have it by default, but the Windows runners GitHub provides include it (Git Bash), which is why workflow steps here set `shell: bash`.

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
