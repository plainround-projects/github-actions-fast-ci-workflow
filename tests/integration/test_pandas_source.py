"""The pandas adapter against the real pandas and numpy, the dependencies the CI cache exists for."""

import pytest

from mathkit.application.summarize import SummarizeTable
from mathkit.domain.errors import InvalidTableError
from mathkit.infrastructure.pandas_source import PandasColumnSource

CSV = "name,price,qty\nwidget,2.5,4\ngadget,3.5,\nthing,4.5,6\n"


def test_numeric_columns_are_read_and_text_columns_are_left_out():
    columns = PandasColumnSource().numeric_columns(CSV)
    assert list(columns) == ["price", "qty"]


def test_missing_values_are_dropped_per_column():
    assert PandasColumnSource().numeric_columns(CSV)["qty"] == (4.0, 6.0)


def test_text_that_is_not_a_table_is_rejected():
    with pytest.raises(InvalidTableError):
        PandasColumnSource().numeric_columns("")


def test_the_use_case_summarizes_through_the_real_adapter():
    price = SummarizeTable(PandasColumnSource())(CSV)[0]
    assert (price.name, price.count, price.mean, price.median) == ("price", 3, 3.5, 3.5)
