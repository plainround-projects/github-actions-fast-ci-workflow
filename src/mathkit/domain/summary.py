"""The summary of one numeric column, as an immutable value."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from mathkit.domain import statistics


@dataclass(frozen=True, slots=True)
class ColumnSummary:
    """Count, mean, median and range of one column."""

    name: str
    count: int
    mean: float
    median: float
    minimum: float
    maximum: float

    @classmethod
    def of(cls, name: str, values: Sequence[float]) -> ColumnSummary:
        """Summarize ``values``; raise :class:`~mathkit.domain.errors.EmptyInputError` when there are none."""
        return cls(
            name=name,
            count=len(values),
            mean=statistics.mean(values),
            median=statistics.median(values),
            minimum=min(values),
            maximum=max(values),
        )
