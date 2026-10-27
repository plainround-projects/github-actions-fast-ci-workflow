"""Named errors the library raises, so callers can tell a bad input from a bug."""

from __future__ import annotations


class MathkitError(Exception):
    """Base class of every error mathkit raises on purpose."""


class DivisionByZeroError(MathkitError):
    """The divisor was zero."""


class EmptyInputError(MathkitError):
    """A statistic was asked of an empty sequence."""


class InvalidTableError(MathkitError):
    """The table text could not be read as numeric columns."""
