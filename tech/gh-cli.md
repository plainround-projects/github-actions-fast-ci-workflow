# GitHub CLI (`gh`)

## What it is

`gh` is GitHub's official command-line program. It signs in to your GitHub account once and then lets you call GitHub from the terminal: start workflows, list runs, and send any request to GitHub's REST API with `gh api`.

## Why this repository uses it

Two parts of the lesson need data from GitHub that only exists after real runs: the duration and billable minutes of each run, and the branch rule that makes `ci-ok` required. `gh` fetches the first and sets the second.

## Where it appears

| Path | What it does with `gh` |
| --- | --- |
| `Makefile` target `measure` | Downloads the job list of each run with `gh api`, then calls `pipeline/billing.py`. |
| `scripts/protect-main.sh` | `gh api -X PUT repos/$repo/branches/main/protection` to require the `ci-ok` check. |
| `README.md` | `gh workflow run measure-1-plain.yml`, `gh variable set DEMO_FAIL_ON_PYTHON`. |

## How it works underneath

`gh` stores a token after `gh auth login`. Each command turns into an HTTPS request to `api.github.com` with that token. `gh api PATH` sends a request to the path you give; `-X METHOD` sets the HTTP method (GET to read, PUT to replace, POST to create); `--input FILE` sends a file as the request body (`-` means standard input); `--paginate` follows "next page" links and joins the results.

## Walkthrough of this repository's use

```make
gh api repos/$${GH_REPO:-$$(gh repo view --json nameWithOwner -q .nameWithOwner)}/actions/runs/$$id/jobs --paginate > build/run-$$id.json
```

For each run id, ask for `repos/OWNER/NAME/actions/runs/ID/jobs`: the list of jobs with their start and end times and runner labels. The repository name comes from the environment variable `GH_REPO` if set, otherwise from `gh repo view --json nameWithOwner -q .nameWithOwner` (`-q` filters the JSON). The shell doubles `$` because Make would otherwise swallow it (see `make.md`).

```bash
body='{
  "required_status_checks": { "strict": true, "contexts": ["ci-ok"] },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}'
gh api -X PUT "repos/$repo/branches/main/protection" --input - <<<"$body"
```

This is the branch protection payload: the branch `main` may be merged only when the check named `ci-ok` is green and the branch is up to date (`strict`). The other three keys are required by the API and set to "off". `DRY_RUN=1` prints the call instead of sending it.

## Try it yourself

1. `gh --version` prints the version.
2. `DRY_RUN=1 scripts/protect-main.sh sumitsr/mathkit` prints the `gh api -X PUT ...` line and sends nothing.
3. After publishing: `gh run list --workflow measure-1-plain.yml` lists runs and their ids.
4. After publishing: `make measure STAGE="1 plain (1 job)" RUNS="id1 id2 id3"` prints a table row.
5. `gh api --help` explains every flag used above.

## Mistakes people make

- Running a write call (`-X PUT`) against the wrong repository; the script validates the `OWNER/REPO` shape and has a dry-run mode.
- Forgetting `--paginate` and getting only the first 30 items.
- Pasting a token into a command instead of using `gh auth login`.

## Check yourself

1. What does `gh api -X PUT` do? *(Sends an HTTP PUT, replacing a resource.)*
2. What does `--paginate` do? *(Follows pages and joins the results.)*
3. Where does `gh` get the repository name in `measure`? *(`GH_REPO`, or `gh repo view`.)*
4. What does `contexts: ["ci-ok"]` require? *(That the check named `ci-ok` passes before merging.)*
5. How do you preview the protection call? *(`DRY_RUN=1`.)*

## Further reading

- GitHub CLI manual: https://cli.github.com/manual/
- Branch protection API: https://docs.github.com/en/rest/branches/branch-protection
