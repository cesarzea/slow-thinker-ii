"""Validate explicit coordinator lifetime and admission bounds before constructing owners."""

import math


def require_bounds(preparation: float, shutdown: float, maximum: int) -> None:
    if any(
        isinstance(value, bool) or not math.isfinite(value) or value <= 0
        for value in (preparation, shutdown)
    ):
        raise ValueError("Finite preparation and shutdown bounds are required")
    if type(maximum) is not int or maximum < 1:
        raise ValueError("A positive pending-command bound is required")
