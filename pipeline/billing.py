"""Wall time and billable minutes of a workflow run, from the job list the GitHub API returns.

GitHub bills each job on its own: the duration rounds up to the next whole minute, and the minutes are multiplied
by the runner's rate (Linux 1, Windows 2, macOS 10). Fetch a run's jobs with::

    gh api repos/OWNER/REPO/actions/runs/RUN_ID/jobs --paginate > run.json
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

RATES = {"linux": 1, "windows": 2, "macos": 10}


@dataclass(frozen=True, slots=True)
class Job:
    """One job that ran: its name, the operating system family of its runner and its start and end."""

    name: str
    family: str
    started_at: datetime
    completed_at: datetime

    @property
    def seconds(self) -> float:
        """Seconds between start and completion."""
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def billable_minutes(self) -> int:
        """Whole minutes, rounded up, times the runner's rate."""
        return math.ceil(self.seconds / 60) * RATES[self.family]


@dataclass(frozen=True, slots=True)
class RunCost:
    """The cost of one run: wall time (first job start to last job end) and billable minutes."""

    wall_seconds: float
    billable_minutes: int


def _timestamp(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _family(labels: Sequence[str]) -> str:
    joined = " ".join(labels).lower()
    for family in ("windows", "macos"):
        if family in joined:
            return family
    return "linux"


def parse_jobs(payload: Mapping[str, Any]) -> tuple[Job, ...]:
    """Read the jobs of a run; jobs that never started (skipped) are left out."""
    jobs = []
    for raw in payload["jobs"]:
        if not raw.get("started_at") or not raw.get("completed_at"):
            continue
        jobs.append(
            Job(
                raw["name"],
                _family(raw.get("labels", [])),
                _timestamp(raw["started_at"]),
                _timestamp(raw["completed_at"]),
            )
        )
    return tuple(jobs)


def run_cost(jobs: Sequence[Job]) -> RunCost:
    """Return the wall time and billable minutes of a run; a run with no job that ran costs nothing."""
    if not jobs:
        return RunCost(0.0, 0)
    wall = (max(job.completed_at for job in jobs) - min(job.started_at for job in jobs)).total_seconds()
    return RunCost(wall, sum(job.billable_minutes for job in jobs))


def format_duration(seconds: float) -> str:
    """Format seconds as ``2m 20s``."""
    whole = round(seconds)
    return f"{whole // 60}m {whole % 60:02d}s"


def stage_row(name: str, runs: Sequence[RunCost]) -> str:
    """One README table row for a stage: the median wall time and median billable minutes of its runs."""
    wall = statistics.median(run.wall_seconds for run in runs)
    minutes = statistics.median(run.billable_minutes for run in runs)
    return f"{name:<34}{format_duration(wall):<12}{minutes:g}   (median of {len(runs)} runs)"


def main(argv: Sequence[str] | None = None) -> int:
    """Print the stage table for ``--stage NAME run.json [run.json ...]`` arguments."""
    parser = argparse.ArgumentParser(prog="pipeline.billing", description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument("--stage", nargs="+", action="append", metavar=("NAME", "RUN_JSON"), required=True)
    args = parser.parse_args(argv)
    print(f"{'stage':<34}{'wall time':<12}billable minutes")
    for name, *files in args.stage:
        if not files:
            parser.error(f"stage {name!r} needs at least one run file")
        runs = [run_cost(parse_jobs(json.loads(Path(file).read_text(encoding="utf-8")))) for file in files]
        print(stage_row(name, runs))
        for number, run in enumerate(runs, start=1):
            print(f"  run {number}: {format_duration(run.wall_seconds)}, {run.billable_minutes} billable minutes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
