import math
from leaf_data import LABEL_TO_VAR
from leaf_qt.engine_solver import (
    iterative_solver,
    module_execution_enabled,
)


def none_if_blank(value):
    if value in ("", None):
        return None

    return value

def build_full_parameter_dict(inputs):
    """
    Promethean-style solver input.

    The old Tkinter GUI passed a full dictionary containing both known values
    and unknown values as None. The legacy solver depends on that behaviour.
    """

    full_params = {
        var_name: None
        for var_name in LABEL_TO_VAR.values()
    }

    full_params.update(inputs)

    if full_params.get("ambient_pressure") is None:
        full_params["ambient_pressure"] = 101325.0

    return full_params

def calculate_basic_geometry(params, module_execution_policy=None):
    """
    Recreates the core geometry preparation layer that the old GUI relied on.
    This must happen before/after iterative_solver so geometry values are not lost.
    """

    nozzle_active = module_execution_enabled(
        module_execution_policy, "nozzle"
    )

    mdot = params.get("mass_flow_rate")
    c_star = params.get("characteristic_velocity")
    pc = params.get("chamber_pressure")

    throat_area = params.get("throat_area")
    throat_radius = params.get("throat_radius")

    if nozzle_active:
        if throat_area is None and mdot is not None and c_star is not None and pc:
            throat_area = mdot * c_star / pc
            params["throat_area"] = throat_area

        if throat_radius is None and throat_area is not None and throat_area > 0:
            throat_radius = math.sqrt(throat_area / math.pi)
            params["throat_radius"] = throat_radius

        expansion_ratio = params.get("expansion_ratio")
        exit_area = params.get("exit_area")
        exit_radius = params.get("exit_radius")

        if exit_area is None and expansion_ratio is not None and throat_area is not None:
            exit_area = expansion_ratio * throat_area
            params["exit_area"] = exit_area

        if exit_radius is None and exit_area is not None and exit_area > 0:
            exit_radius = math.sqrt(exit_area / math.pi)
            params["exit_radius"] = exit_radius

        if expansion_ratio is None and exit_area is not None and throat_area is not None and throat_area > 0:
            expansion_ratio = exit_area / throat_area
            params["expansion_ratio"] = expansion_ratio

    if nozzle_active:
        if params.get("radius_2") is None and throat_radius is not None:
            params["radius_2"] = throat_radius * 1.5

        if params.get("radius_3") is None and throat_radius is not None:
            params["radius_3"] = throat_radius * 0.382

        radius_3 = params.get("radius_3")
        nozzle_length = params.get("nozzle_length")

        if nozzle_length is None and throat_radius is not None and exit_radius is not None:
            half_angle = math.radians(15)

            params["nozzle_length"] = (
                math.cos(half_angle) * radius_3
                + (
                    exit_radius
                    - throat_radius
                    - (radius_3 - math.cos(half_angle) * radius_3)
                ) / math.tan(half_angle)
            )

    return params




def calculate_with_full_bridge(
        inputs,
        execution_scope="full",
        module_execution_policy=None,
):
    """
    Main Qt calculation bridge.

    This is the place where old GUI orchestration is rebuilt.
    The GUI should call this instead of directly calling iterative_solver().
    """

    params = build_full_parameter_dict(inputs)

    params = calculate_basic_geometry(
        params, module_execution_policy=module_execution_policy
    )

    # First traversal is an enrichment prepass.
    #
    # Full/regen execution previously entered the deep candidate pipeline
    # here even though geometry/station state is enriched afterwards and
    # the authoritative traversal is then executed again.
    #
    # Reuse iterative_solver's existing "graph" return boundary so this
    # prepass retains the required thermal/regen state while stopping
    # immediately before candidate generation and qualification.
    prepass_execution_scope = (
        "graph"
        if execution_scope in {"full", "regen"}
        else execution_scope
    )

    solved, history = iterative_solver(
        params,
        execution_scope=prepass_execution_scope,
        module_execution_policy=module_execution_policy,
    )

    final_params = dict(params)
    final_params.update(solved)

    final_params = calculate_basic_geometry(
        final_params, module_execution_policy=module_execution_policy
    )

    # Graph core and corrected-performance scopes are complete after the
    # first solver traversal plus the bridge's existing station processing.
    # Deeper engineering graph and full runtime scopes retain the second
    # traversal because they require outputs generated from the enriched state.
    if execution_scope in {"graph_core", "graph_corrected"}:
        final_params = apply_selected_cea_aliases(final_params)
        return final_params, history or {}

    solved_2, history_2 = iterative_solver(
        final_params,
        execution_scope=execution_scope,
        module_execution_policy=module_execution_policy,
    )

    final_params.update(solved_2)
    final_params = calculate_basic_geometry(
        final_params, module_execution_policy=module_execution_policy
    )
    final_params = apply_selected_cea_aliases(final_params)

    combined_history = {}
    combined_history.update(history or {})
    combined_history.update(history_2 or {})

    return final_params, combined_history

def apply_selected_cea_aliases(params):
    """
    Maps chamber CEA values into selected CEA values when no better
    selected-station values exist.
    """

    if params.get("cea_selected_gamma") is None:
        params["cea_selected_gamma"] = (
            params.get("cea_chamber_gamma")
            or params.get("Gamma")
        )

    if params.get("cea_selected_molecular_weight") is None:
        params["cea_selected_molecular_weight"] = (
            params.get("cea_chamber_molecular_weight")
            or params.get("cea_molecular_weight")
        )

    return params