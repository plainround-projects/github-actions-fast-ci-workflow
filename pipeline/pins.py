"""Check that every ``uses:`` in the workflows and local actions names a full commit SHA.

A tag can be moved by whoever owns it; a 40-character commit hash names one tree of files for ever.
Local actions (``./path``) and Docker images pinned by digest are allowed.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import yaml

_PINNED = re.compile(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}")
_DIGEST = re.compile(r"docker://\S+@sha256:[0-9a-f]{64}")


def uses_values(document: Any) -> Iterator[str]:
    """Yield every ``uses`` value of a parsed workflow or action: job-level and step-level."""
    if not isinstance(document, dict):
        return
    for job in (document.get("jobs") or {}).values():
        if "uses" in job:
            yield str(job["uses"])
        for step in job.get("steps") or []:
            if "uses" in step:
                yield str(step["uses"])
    for step in (document.get("runs") or {}).get("steps") or []:
        if "uses" in step:
            yield str(step["uses"])


def is_pinned(reference: str) -> bool:
    """Return whether a ``uses`` value is local, a digest-pinned image, or a full-SHA reference."""
    return reference.startswith("./") or bool(_DIGEST.fullmatch(reference)) or bool(_PINNED.fullmatch(reference))


def violations(root: Path) -> list[str]:
    """Return ``path: uses-value`` for each unpinned reference under ``root/.github``."""
    found = []
    files = sorted([*root.glob(".github/workflows/*.y*ml"), *root.glob(".github/actions/**/action.y*ml")])
    for file in files:
        document = yaml.safe_load(file.read_text(encoding="utf-8"))
        found += [f"{file.relative_to(root)}: {ref}" for ref in uses_values(document) if not is_pinned(ref)]
    return found


def main(argv: Sequence[str] | None = None) -> int:
    """Exit 1 and list the unpinned references when there are any."""
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]) if args else Path(".")
    found = violations(root)
    for line in found:
        print(f"not pinned to a full commit SHA: {line}", file=sys.stderr)
    if not found:
        print("pins: every uses: is a full commit SHA, a local path or a digest")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
