import json

from pipeline import gate


def test_all_success_passes():
    assert gate.failed_jobs({"lint": {"result": "success"}, "test": {"result": "success"}}) == []


def test_a_skipped_job_passes():
    assert gate.failed_jobs({"test": {"result": "skipped"}}) == []


def test_failure_and_cancellation_are_named_in_order():
    needs = {"test": {"result": "failure"}, "lint": {"result": "success"}, "audit": {"result": "cancelled"}}
    assert gate.failed_jobs(needs) == ["audit", "test"]


def test_main_exits_1_and_names_the_failed_job(monkeypatch, capsys):
    monkeypatch.setenv("NEEDS", json.dumps({"test": {"result": "failure"}}))
    assert gate.main() == 1
    assert "test" in capsys.readouterr().err


def test_main_exits_0_when_everything_passed(monkeypatch, capsys):
    monkeypatch.setenv("NEEDS", json.dumps({"lint": {"result": "success"}, "test": {"result": "success"}}))
    assert gate.main() == 0
    assert "2 jobs green" in capsys.readouterr().out
