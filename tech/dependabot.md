# Dependabot

## What it is

Dependabot is a GitHub service that opens pull requests to update your dependencies when new versions come out. You configure it with a YAML file. It can watch GitHub Actions versions, Python packages and many other kinds.

<!-- words -->

<details>
<summary><b>Words this note uses, in case they are new to you</b> (click to open)</summary>

- **commit**: A saved snapshot of a project's files in Git, with a message and an author. Every commit has a unique 40-character name (its SHA).
- **pull request**: A proposal on GitHub to merge the commits of one branch into another. People review it and automation checks it before it is merged.
- **repository**: A project's folder of files together with its complete history of changes. On GitHub, a repository is a page with those files, issues and pull requests.
- **CI**: Continuous integration: running checks (build, tests, linters) automatically every time code changes.
- **YAML**: A plain-text format for structured data that uses indentation instead of braces. GitHub workflows are YAML files.
- **dependency**: A package that your project needs in order to work.

</details>

<!-- /words -->

## Why this repository uses it

Every action is pinned to a 40-character commit SHA, and Python packages are pinned with hashes. Pins are safe but they go stale. Dependabot proposes the update as a pull request, and the CI runs on it, so keeping current is a review instead of a chore.

## Where it appears

| Path | What it does with Dependabot |
| --- | --- |
| `.github/dependabot.yml` | Two update jobs: `github-actions` and `pip`, both weekly. |

## How it works underneath

On the schedule, Dependabot reads your files, looks up newer versions, and for a pinned action reads the `# v7.0.1` comment to learn which version the SHA stands for. It opens a pull request that changes both the SHA and the comment. Pull requests from Dependabot run your normal CI.

## Walkthrough of this repository's use

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    groups:
      actions:
        patterns: ["*"]
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
```

`version: 2` is the file format version. Each item in `updates` is one job. `package-ecosystem` names the kind of dependency. `directory: /` means look at the repository root (for `github-actions`, Dependabot reads `.github/workflows` from there). `schedule.interval: weekly` runs it once a week. `groups` with `patterns: ["*"]` bundles all action updates into one pull request instead of one per action. The `pip` entry watches `requirements.txt` and friends.

## Try it yourself

1. `.venv/bin/python -c "import yaml; print(yaml.safe_load(open('.github/dependabot.yml'))['updates'][0]['package-ecosystem'])"` prints `github-actions`.
2. On GitHub, after you push: the repository's Insights, Dependency graph, Dependabot tab shows the last check.
3. Dependabot does not run locally; its first pull request appears after the first scheduled run.

## Mistakes people make

- Pinning to SHAs without the version comment, so the bot cannot tell what to bump to.
- Letting the bot open one pull request per dependency and drowning in them; `groups` helps.
- Editing the lock files by hand next to the bot.

## Check yourself

1. What does `package-ecosystem` choose? *(The kind of dependency to watch.)*
2. How does it know the version of a pinned action? *(From the `# vX.Y.Z` comment next to the SHA.)*
3. What does `groups` do? *(Combines several updates into one pull request.)*
4. Does it run on your laptop? *(No, it is a GitHub service.)*
5. Why does this repository need it? *(Pins go stale; the bot proposes the new SHAs.)*

## Further reading

- Dependabot options reference: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference
