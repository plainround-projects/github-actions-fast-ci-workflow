import pytest

import mathkit
from mathkit.domain.arithmetic import divide, multiply, subtract
from mathkit.domain.errors import DivisionByZeroError


def test_add_returns_the_sum_of_two_numbers():
    assert mathkit.add(2, 3) == 5


def test_add_keeps_floats_exact_enough_for_a_sum_of_tenths():
    assert mathkit.add(0.5, 0.25) == pytest.approx(0.75)


def test_subtract_returns_the_difference():
    assert subtract(2, 5) == -3


def test_multiply_returns_the_product():
    assert multiply(4, 2.5) == 10


def test_divide_returns_the_quotient_as_a_float():
    assert divide(7, 2) == 3.5


def test_divide_by_zero_raises_a_named_error():
    with pytest.raises(DivisionByZeroError, match="zero"):
        divide(1, 0)


def test_the_package_exposes_the_documented_names():
    assert sorted(mathkit.__all__) == ["add", "divide", "mean", "median", "multiply", "subtract"]
