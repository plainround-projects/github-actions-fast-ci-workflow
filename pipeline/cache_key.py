"""Model of the cache key ``actions/setup-python`` builds, so a change to the lock file can be shown to miss.

The key is ``setup-python-<OS>-<arch>-python-<version>-pip-<hash>``. The hash is what ``hashFiles()`` computes:
the SHA-256 of the concatenated SHA-256 digests of the matched files.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path


def hash_files(paths: Iterable[Path]) -> str:
    """Return the ``hashFiles()`` value of ``paths``, taken in the order given."""
    outer = hashlib.sha256()
    for path in paths:
        outer.update(hashlib.sha256(path.read_bytes()).digest())
    return outer.hexdigest()


def setup_python_key(runner_os: str, arch: str, python_version: str, dependency_file: Path) -> str:
    """Return the primary cache key for one matrix job."""
    return f"setup-python-{runner_os}-{arch}-python-{python_version}-pip-{hash_files([dependency_file])}"


def main(argv: Sequence[str] | None = None) -> int:
    """Print the key for the given runner OS, Python version and dependency file."""
    parser = argparse.ArgumentParser(prog="pipeline.cache_key")
    parser.add_argument("--os", default="Linux")
    parser.add_argument("--arch", default="x64")
    parser.add_argument("--python", default="3.12.7", dest="python_version")
    parser.add_argument("--file", type=Path, default=Path("requirements.txt"))
    args = parser.parse_args(argv)
    print(setup_python_key(args.os, args.arch, args.python_version, args.file))
    return 0


if __name__ == "__main__":
    sys.exit(main())
