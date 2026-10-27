"""Descriptive statistics on sequences of floats."""

from __future__ import annotations

import math
from collections.abc import Sequence

from mathkit.domain.errors import EmptyInputError


def _require_values(values: Sequence[float]) -> None:
    if len(values) == 0:
        raise EmptyInputError("at least one value is required")


def mean(values: Sequence[float]) -> float:
    """Return the arithmetic mean, summed exactly with :func:`math.fsum`."""
    _require_values(values)
    return math.fsum(values) / len(values)


def median(values: Sequence[float]) -> float:
    """Return the middle value, or the mean of the two middle values for an even count."""
    _require_values(values)
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
