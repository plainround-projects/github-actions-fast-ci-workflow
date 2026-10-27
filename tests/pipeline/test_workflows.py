"""The lesson's review checklist, asserted against the real workflow files."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from pipeline import pins
from pipeline.pathfilter import starts_workflow

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def load(name: str) -> dict[Any, Any]:
    document: dict[Any, Any] = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    document["on"] = document.pop(True)  # YAML 1.1 reads the key `on` as the boolean True
    return document


@pytest.fixture(scope="module")
def ci() -> dict[Any, Any]:
    return load("ci.yml")


def test_the_workflow_token_starts_read_only(ci):
    assert ci["permissions"] == {"contents": "read"}


def test_every_job_of_every_workflow_states_its_permissions():
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for name, job in load(path.name)["jobs"].items():
            assert "permissions" in job, f"{path.name}: job {name} has no permissions block"
            assert "timeout-minutes" in job, f"{path.name}: job {name} has no timeout"


def test_the_matrix_is_three_quoted_versions_on_two_systems_and_does_not_fail_fast(ci):
    strategy = ci["jobs"]["test"]["strategy"]
    assert strategy["fail-fast"] is False
    assert strategy["matrix"]["python"] == ["3.10", "3.11", "3.12"]
    assert strategy["matrix"]["os"] == ["ubuntu-latest", "windows-latest"]


def test_the_dependency_cache_is_keyed_on_the_lock_file(ci):
    setup = next(s for s in ci["jobs"]["test"]["steps"] if "setup-python" in s.get("uses", ""))
    assert setup["with"]["cache"] == "pip"
    assert setup["with"]["cache-dependency-path"] == "requirements.txt"


def test_the_report_is_uploaded_also_on_failure_with_a_unique_name_and_short_retention(ci):
    upload = next(s for s in ci["jobs"]["test"]["steps"] if "upload-artifact" in s.get("uses", ""))
    assert upload["if"] == "always()"
    assert "${{ matrix.os }}" in upload["with"]["name"]
    assert "${{ matrix.python }}" in upload["with"]["name"]
    assert upload["with"]["retention-days"] == 7
    assert upload["with"]["if-no-files-found"] == "error"


def test_a_newer_push_cancels_the_older_run_on_a_branch_but_never_on_main(ci):
    assert ci["concurrency"]["group"] == "ci-${{ github.ref }}"
    assert ci["concurrency"]["cancel-in-progress"] == "${{ github.ref != 'refs/heads/main' }}"


def test_documentation_only_changes_are_ignored_on_both_events(ci):
    ignore = ["docs/**", "**.md"]
    assert ci["on"]["push"]["paths-ignore"] == ignore
    assert ci["on"]["pull_request"]["paths-ignore"] == ignore


def test_a_docs_only_change_starts_only_the_companion_and_a_source_change_starts_only_ci(ci):
    ignore = ci["on"]["pull_request"]["paths-ignore"]
    companion = load("ci-docs-only.yml")["on"]["pull_request"]["paths"]
    assert not starts_workflow(["docs/index.md"], paths_ignore=ignore)
    assert starts_workflow(["docs/index.md"], paths=companion)
    assert starts_workflow(["src/mathkit/domain/arithmetic.py"], paths_ignore=ignore)
    assert not starts_workflow(["src/mathkit/domain/arithmetic.py"], paths=companion)


def test_the_companion_workflow_reports_the_same_check_name_as_the_gate(ci):
    assert load("ci-docs-only.yml")["jobs"]["ci-ok"]["name"] == ci["jobs"]["ci-ok"]["name"] == "ci-ok"


def test_the_gate_always_runs_and_needs_every_other_job(ci):
    gate = ci["jobs"]["ci-ok"]
    assert gate["if"] == "always()"
    assert sorted(gate["needs"]) == ["lint", "test"]


def test_the_gate_reads_job_results_from_the_environment_not_from_the_shell_text(ci):
    gate = ci["jobs"]["ci-ok"]
    run_step = next(s for s in gate["steps"] if "run" in s)
    assert "${{" not in run_step["run"]
    assert run_step["env"]["NEEDS"] == "${{ toJSON(needs) }}"


def test_the_measurement_workflows_are_started_by_hand_only():
    for name in ("measure-1-plain.yml", "measure-2-matrix.yml", "measure-3-cache.yml"):
        assert load(name)["on"] == "workflow_dispatch"


def test_only_the_cache_stage_uses_the_cache():
    def caches(name: str) -> bool:
        steps = load(name)["jobs"]["test"]["steps"]
        return any(s.get("with", {}).get("cache") == "pip" for s in steps)

    assert [caches(n) for n in ("measure-1-plain.yml", "measure-2-matrix.yml", "measure-3-cache.yml")] == [
        False,
        False,
        True,
    ]


def test_every_action_is_pinned_to_a_full_commit_sha():
    assert pins.violations(ROOT) == []
