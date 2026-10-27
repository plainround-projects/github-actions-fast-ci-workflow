"""The ``ci-ok`` gate: one job to require for ``main`` that fails when any job it needs did not succeed.

Reads the ``needs`` context as JSON from the ``NEEDS`` environment variable, so no job output is ever pasted
into a shell command.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from typing import Any

PASSING = frozenset({"success", "skipped"})


def failed_jobs(needs: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """Return the names of the needed jobs whose result is neither ``success`` nor ``skipped``."""
    return sorted(name for name, job in needs.items() if job.get("result") not in PASSING)


def main() -> int:
    """Exit 0 when every needed job passed, 1 otherwise, naming the jobs that did not."""
    needs = json.loads(os.environ["NEEDS"])
    failed = failed_jobs(needs)
    if failed:
        print(f"ci-ok: not green: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"ci-ok: {len(needs)} jobs green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
