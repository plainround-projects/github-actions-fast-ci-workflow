"""Four-function arithmetic on numbers."""

from __future__ import annotations

from mathkit.domain.errors import DivisionByZeroError

Number = int | float


def add(left: Number, right: Number) -> Number:
    """Return ``left + right``."""
    return left + right


def subtract(left: Number, right: Number) -> Number:
    """Return ``left - right``."""
    return left - right


def multiply(left: Number, right: Number) -> Number:
    """Return ``left * right``."""
    return left * right


def divide(left: Number, right: Number) -> float:
    """Return ``left / right``; raise :class:`DivisionByZeroError` when ``right`` is zero."""
    if right == 0:
        raise DivisionByZeroError("cannot divide by zero")
    return left / right
