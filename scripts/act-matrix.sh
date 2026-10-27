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

# act's artifact service cannot be reached from a runner container when Docker runs in a VM, so the pinned
# upload-artifact action is replaced by a stand-in that lists the files and checks the missing-file rule. The cache
# service has the same problem: setup-python warns that it cannot restore or save and carries on.
upload_artifact="$(grep -o 'actions/upload-artifact@[0-9a-f]\{40\}' .github/workflows/ci.yml | head -1)"
flags=(--concurrent-jobs 1 --local-repository "$upload_artifact=$root/ci/act-stubs/upload-artifact")
if [[ -n "$fail_on" ]]; then
  flags+=(--var "DEMO_FAIL_ON_PYTHON=$fail_on")
fi

mkdir -p "$root/build/act"
results=()
for version in "${versions[@]}"; do
  log="$root/build/act/test-$version${fail_on:+-fail-on-$fail_on}.log"
  echo "== Python $version"
  if act push "${flags[@]}" -W .github/workflows/ci.yml -j test --matrix os:ubuntu-latest --matrix "python:$version" >"$log" 2>&1; then
    results+=("$version:green")
  else
    results+=("$version:red")
  fi
  grep -E "Cache (restored|not found|hit)|pip cache is not found|passed|failed|skipped|DELIBERATE|deliberate|Success - Main actions/upload|Failure - Main" "$log" | sed 's/^/   /' | cut -c1-200 || true
done

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
