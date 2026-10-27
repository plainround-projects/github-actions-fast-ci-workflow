import json
from pathlib import Path

import pytest

from pipeline import billing

FIXTURES = Path(__file__).parent / "fixtures"


def job(name, labels, start, end):
    return {"name": name, "labels": labels, "started_at": start, "completed_at": end}


def test_each_job_rounds_up_to_the_next_whole_minute():
    jobs = billing.parse_jobs({"jobs": [job("a", ["ubuntu-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:01:01Z")]})
    assert jobs[0].billable_minutes == 2


def test_windows_minutes_count_double_and_macos_ten_times():
    jobs = billing.parse_jobs(
        {
            "jobs": [
                job("w", ["windows-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"),
                job("m", ["macos-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"),
            ]
        }
    )
    assert [j.billable_minutes for j in jobs] == [2, 10]


def test_a_skipped_job_costs_nothing():
    payload = {"jobs": [{"name": "s", "labels": [], "started_at": None, "completed_at": None}]}
    assert billing.parse_jobs(payload) == ()
    assert billing.run_cost(()) == billing.RunCost(0.0, 0)


def test_wall_time_runs_from_the_first_start_to_the_last_end():
    jobs = billing.parse_jobs(
        {
            "jobs": [
                job("a", ["ubuntu-latest"], "2026-01-01T00:00:00Z", "2026-01-01T00:02:00Z"),
                job("b", ["ubuntu-latest"], "2026-01-01T00:00:10Z", "2026-01-01T00:03:05Z"),
            ]
        }
    )
    cost = billing.run_cost(jobs)
    assert (cost.wall_seconds, cost.billable_minutes) == (185.0, 2 + 3)


def test_format_duration_reads_as_minutes_and_seconds():
    assert billing.format_duration(140) == "2m 20s"


def test_the_stage_table_uses_the_median_of_the_runs(capsys):
    plain = [FIXTURES / f"plain-{n}.json" for n in (1, 2, 3)]
    assert billing.main(["--stage", "1 plain (1 job)", *map(str, plain)]) == 0
    out = capsys.readouterr().out
    assert "1 plain (1 job)" in out
    assert "2m 20s" in out
    assert "(median of 3 runs)" in out


def test_the_matrix_fixture_bills_windows_double():
    payload = json.loads((FIXTURES / "matrix-1.json").read_text(encoding="utf-8"))
    cost = billing.run_cost(billing.parse_jobs(payload))
    assert cost.billable_minutes == 3 * 2 + 3 * 3 * 2


def test_a_stage_without_run_files_is_a_usage_error():
    with pytest.raises(SystemExit):
        billing.main(["--stage", "only-a-name"])
