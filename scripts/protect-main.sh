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
