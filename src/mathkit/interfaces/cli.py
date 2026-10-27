"""Command-line program: ``python -m mathkit add 2 3`` and ``python -m mathkit summarize data.csv``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from mathkit.application.summarize import SummarizeTable
from mathkit.domain import arithmetic
from mathkit.domain.errors import MathkitError
from mathkit.infrastructure.pandas_source import PandasColumnSource

_OPERATIONS = {
    "add": arithmetic.add,
    "subtract": arithmetic.subtract,
    "multiply": arithmetic.multiply,
    "divide": arithmetic.divide,
}


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser; one sub-command per operation plus ``summarize``."""
    parser = argparse.ArgumentParser(prog="mathkit", description="Small math helpers.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in _OPERATIONS:
        command = commands.add_parser(name, help=f"{name} two numbers")
        command.add_argument("left", type=float)
        command.add_argument("right", type=float)
    summarize = commands.add_parser("summarize", help="summarize the numeric columns of a CSV file")
    summarize.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the program; return the exit code (0 success, 1 a mathkit error, 2 a usage error)."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "summarize":
            summaries = SummarizeTable(PandasColumnSource())(args.path.read_text(encoding="utf-8"))
            for item in summaries:
                print(
                    f"{item.name}: count={item.count} mean={item.mean:g} median={item.median:g} "
                    f"min={item.minimum:g} max={item.maximum:g}"
                )
        else:
            print(f"{_OPERATIONS[args.command](args.left, args.right):g}")
    except MathkitError as error:
        print(f"mathkit: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"mathkit: cannot read the file: {error}", file=sys.stderr)
        return 1
    return 0
