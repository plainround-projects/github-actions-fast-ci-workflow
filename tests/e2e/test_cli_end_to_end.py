"""The command-line program run as a separate process, the way a user starts it."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "mathkit", *args], capture_output=True, text=True, env=env, check=False
    )


def test_add_prints_five():
    result = run("add", "2", "3")
    assert (result.returncode, result.stdout.strip()) == (0, "5")


def test_summarize_prints_one_line_per_numeric_column(tmp_path):
    table = tmp_path / "t.csv"
    table.write_text("x,y\n1,10\n3,20\n", encoding="utf-8")
    result = run("summarize", str(table))
    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "x: count=2 mean=2 median=2 min=1 max=3",
        "y: count=2 mean=15 median=15 min=10 max=20",
    ]


def test_a_failure_has_a_nonzero_exit_code():
    assert run("divide", "1", "0").returncode == 1


def test_the_break_on_purpose_switch_fails_only_on_the_named_version():
    """Lesson step 2: set the repository variable DEMO_FAIL_ON_PYTHON=3.10 to turn one matrix cell red."""
    target = os.environ.get("MATHKIT_DEMO_FAIL_ON_PYTHON", "")
    if target != f"{sys.version_info.major}.{sys.version_info.minor}":
        pytest.skip("MATHKIT_DEMO_FAIL_ON_PYTHON does not name this interpreter")
    pytest.fail(f"deliberate failure on Python {target} (MATHKIT_DEMO_FAIL_ON_PYTHON)")
