"""Ports: what the use cases ask of the outside world."""

from __future__ import annotations

from typing import Protocol


class ColumnSource(Protocol):
    """Reads the numeric columns of a table given as text."""

    def numeric_columns(self, table_text: str) -> dict[str, tuple[float, ...]]:
        """Return each numeric column by name; non-numeric columns are left out.

        Raise :class:`~mathkit.domain.errors.InvalidTableError` when the text is not a table.
        """
        ...
