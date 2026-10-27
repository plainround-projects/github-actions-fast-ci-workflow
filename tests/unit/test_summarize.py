import pytest

from mathkit.application.summarize import SummarizeTable
from mathkit.domain.errors import InvalidTableError


class FakeSource:
    def __init__(self, columns):
        self._columns = columns

    def numeric_columns(self, table_text):
        return self._columns


def test_each_numeric_column_gets_a_summary_in_order():
    use_case = SummarizeTable(FakeSource({"a": (1.0, 3.0), "b": (10.0,)}))
    summaries = use_case("ignored")
    assert [(s.name, s.mean) for s in summaries] == [("a", 2.0), ("b", 10.0)]


def test_a_table_without_numeric_columns_is_rejected():
    with pytest.raises(InvalidTableError, match="numeric"):
        SummarizeTable(FakeSource({}))("ignored")
