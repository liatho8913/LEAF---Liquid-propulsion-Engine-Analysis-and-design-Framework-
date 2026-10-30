from __future__ import annotations

"""Reusable helpers extracted from engine_solver.py.

This module is runtime-authoritative only for helpers explicitly imported by engine_solver.py.
The public solver boundary remains solve_engine().
"""


def calculate_selected_station_length_default(selected_station_length=None):
    if selected_station_length is not None and selected_station_length > 0:
        return selected_station_length

    return 0.001


def calculate_coolant_flow_fraction_default(coolant_flow_fraction=None):
    from math import isfinite
    from numbers import Real

    if (
        not isinstance(coolant_flow_fraction, Real)
        or isinstance(coolant_flow_fraction, bool)
        or not isfinite(float(coolant_flow_fraction))
        or coolant_flow_fraction <= 0
    ):
        return 1.0

    return coolant_flow_fraction
