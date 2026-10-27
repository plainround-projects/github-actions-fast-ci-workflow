# ShellCheck

## What it is

ShellCheck is a static analyzer for shell scripts. It reads a script without running it and warns about common mistakes: unquoted variables, commands that may not do what they look like, features that your shell does not have. Each warning has a code such as `SC2086`. This repository uses version 0.11.0.

## Why this repository uses it

Bash is easy to get subtly wrong (see `bash.md`). ShellCheck turns most of those mistakes into build failures. `make lint` runs it on every script, and `actionlint` runs it on `run:` blocks in the workflows.

## Where it appears

| Path | What it does with ShellCheck |
| --- | --- |
| `Makefile` | `lint` runs `shellcheck scripts/*.sh pipeline/*.sh`. |
| `pipeline/install-actionlint.sh`, `scripts/act-matrix.sh`, `scripts/protect-main.sh` | The files it checks. |
| `.github/workflows/*.yml` | Checked indirectly: actionlint calls it for each `run:` step. |

## How it works underneath

ShellCheck parses the script into the same kind of tree that Bash builds, then applies a long list of rules to it. It reads the shebang line (`#!/usr/bin/env bash`) to know which shell to assume. `-e`-style behaviors are not run; it only reasons about the text.

## Walkthrough of this repository's use

```bash
shellcheck scripts/*.sh pipeline/*.sh
```

`scripts/*.sh` expands to all `.sh` files in `scripts/`. A clean run prints nothing and exits 0.

Rules these scripts satisfy, with their codes:

- `SC2086` "double quote to prevent globbing and word splitting": every variable use is quoted, for example `"$log"`.
- `SC2155` "declare and assign separately": `local` declarations and assignments are split where a command's exit code matters.
- `SC2015` "`A && B || C` is not if-then-else": the scripts use `if` / `elif` instead of that chain.

Where a finding is wrong for a line, a comment such as `# shellcheck disable=SC2086` on the line above silences exactly that code; `.github/workflows` uses none here.

## Try it yourself

1. `shellcheck --version` prints a block with `version: 0.11.0`.
2. `shellcheck scripts/*.sh pipeline/*.sh; echo "exit $?"` prints `exit 0`.
3. `printf '#!/bin/bash\necho $1\n' > /tmp/s.sh && shellcheck /tmp/s.sh` reports `SC2086` with an explanation and a suggested fix.
4. `shellcheck -f gcc scripts/act-matrix.sh` prints findings in compiler style (none here).

## Mistakes people make

- Disabling a rule globally to make noise stop.
- Writing `#!/bin/sh` but using Bash-only features; ShellCheck then warns.
- Running it on only some scripts.

## Check yourself

1. What does it analyze? *(The text of shell scripts, without running them.)*
2. What does `SC2086` warn about? *(An unquoted variable that can be split into several words.)*
3. How do you silence one finding? *(A `# shellcheck disable=SCxxxx` comment above the line.)*
4. How does it know which shell to assume? *(From the shebang.)*
5. How is it used on workflows? *(Through actionlint.)*

## Further reading

- ShellCheck wiki (0.11): https://www.shellcheck.net/wiki/
