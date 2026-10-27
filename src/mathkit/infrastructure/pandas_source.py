"""Adapter: read numeric columns from CSV text with pandas.

pandas and numpy are the heavy dependencies the CI cache exists for; nothing outside this module imports them.
"""

from __future__ import annotations

import io

import numpy as np
import pandas as pd

from mathkit.domain.errors import InvalidTableError


class PandasColumnSource:
    """:class:`~mathkit.application.ports.ColumnSource` backed by ``pandas.read_csv``."""

    def numeric_columns(self, table_text: str) -> dict[str, tuple[float, ...]]:
        """Parse ``table_text`` as CSV and return its numeric columns, dropping rows with a missing value."""
        try:
            frame = pd.read_csv(io.StringIO(table_text))
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
            raise InvalidTableError(f"not a CSV table: {error}") from error
        numeric = frame.select_dtypes(include=[np.number])
        return {
            str(name): tuple(float(value) for value in numeric[name].dropna().to_numpy()) for name in numeric.columns
        }
