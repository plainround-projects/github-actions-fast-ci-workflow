"""Use case: summarize every numeric column of a table."""

from __future__ import annotations

from mathkit.application.ports import ColumnSource
from mathkit.domain.errors import InvalidTableError
from mathkit.domain.summary import ColumnSummary


class SummarizeTable:
    """Summarize the numeric columns of a table, in the order they appear."""

    def __init__(self, source: ColumnSource) -> None:
        self._source = source

    def __call__(self, table_text: str) -> tuple[ColumnSummary, ...]:
        """Return one summary per numeric column; raise ``InvalidTableError`` when there is none."""
        columns = self._source.numeric_columns(table_text)
        if not columns:
            raise InvalidTableError("the table has no numeric column")
        return tuple(ColumnSummary.of(name, values) for name, values in columns.items())
