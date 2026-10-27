"""Turn a JUnit report into a Markdown table of the slowest tests, for the job summary page.

The report is the one pytest wrote in the same job, so it is trusted input.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from xml.etree import ElementTree


def slowest(report: Path, count: int = 5) -> list[tuple[str, float]]:
    """Return the ``count`` slowest test cases as ``(classname::name, seconds)``, slowest first."""
    cases = [
        (f"{case.get('classname', '')}::{case.get('name', '')}", float(case.get("time", "0")))
        for case in ElementTree.parse(report).getroot().iter("testcase")
    ]
    return sorted(cases, key=lambda item: item[1], reverse=True)[:count]


def markdown(rows: Sequence[tuple[str, float]]) -> str:
    """Render the rows as a GitHub-flavored Markdown table."""
    lines = ["### Slowest tests", "", "| Test | Seconds |", "| --- | ---: |"]
    lines += [f"| `{name}` | {seconds:.3f} |" for name, seconds in rows]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    """Print the table for the report path given as the first argument."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python -m pipeline.slowest_tests REPORT.xml", file=sys.stderr)
        return 2
    print(markdown(slowest(Path(args[0]))), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
