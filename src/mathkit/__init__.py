"""mathkit: a tiny math library, the test subject of the fast CI workflow."""

from mathkit.domain.arithmetic import add, divide, multiply, subtract
from mathkit.domain.statistics import mean, median

__all__ = ["add", "divide", "mean", "median", "multiply", "subtract"]
__version__ = "0.1.0"
