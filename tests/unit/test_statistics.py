import pytest

from mathkit.domain.errors import EmptyInputError
from mathkit.domain.statistics import mean, median
from mathkit.domain.summary import ColumnSummary


def test_mean_sums_exactly():
    assert mean([0.1] * 10) == 0.1


def test_mean_of_nothing_is_an_error():
    with pytest.raises(EmptyInputError):
        mean([])


def test_median_of_an_odd_count_is_the_middle_value():
    assert median([9, 1, 5]) == 5


def test_median_of_an_even_count_averages_the_middle_two():
    assert median([4, 1, 3, 2]) == 2.5


def test_median_of_nothing_is_an_error():
    with pytest.raises(EmptyInputError):
        median([])


def test_a_column_summary_describes_its_values():
    summary = ColumnSummary.of("price", [3.0, 1.0, 2.0])
    assert (summary.count, summary.mean, summary.median, summary.minimum, summary.maximum) == (3, 2.0, 2.0, 1.0, 3.0)


def test_a_column_summary_is_immutable():
    summary = ColumnSummary.of("price", [1.0])
    with pytest.raises(AttributeError):
        summary.count = 2  # type: ignore[misc]
