import math
def autosize_wall_thickness(params):
    pressure_required = params.get("pressure_required_wall_thickness")
    minimum_wall = params.get("minimum_wall_thickness")
    current_wall = params.get("hot_gas_wall_thickness")
    corrosion_allowance = params.get("corrosion_allowance") or 0.0

    candidates = [
        pressure_required,
        minimum_wall,
    ]

    valid_candidates = [
        value for value in candidates
        if isinstance(value, (int, float)) and value > 0
    ]

    if not valid_candidates:
        return params

    required_wall = max(valid_candidates) + corrosion_allowance

    params["autosized_hot_gas_wall_thickness"] = required_wall
    params["wall_thickness_margin"] = None

    if current_wall is not None and current_wall > 0:
        params["wall_thickness_margin"] = current_wall - required_wall

        if current_wall < required_wall:
            params["hot_gas_wall_thickness"] = required_wall
            params["wall_autosized"] = True
        else:
            params["wall_autosized"] = False
    else:
        params["hot_gas_wall_thickness"] = required_wall
        params["wall_autosized"] = True

    return params


def analyse_warnings(params):
    if not isinstance(params, dict):
        return [{
            "type": "Invalid Input",
            "variable": "params",
            "message": "Warning analysis input must be a dictionary.",
        }]

    warnings = []

    def add_warning(kind, variable, message):
        warnings.append({
            "type": kind,
            "variable": variable,
            "message": message,
        })

    def value(name):
        return params.get(name)

    def numeric_state(value):
        if value is None:
            return "missing"

        try:
            finite = math.isfinite(value)
        except (TypeError, ValueError):
            return "invalid"

        if not finite:
            return "invalid"

        return "valid"

    def add_invalid_numeric(name):
        add_warning(
            "Invalid",
            name,
            f"{name} must be a finite numeric value.",
        )

    chamber_pressure = value("chamber_pressure")
    chamber_temperature = value("chamber_temperature")
    expansion_ratio = value("expansion_ratio")
    thrust = value("thrust")
    specific_impulse = value("specific_impulse")
    throat_radius = value("throat_radius")
    exit_radius = value("exit_radius")
    selected_length = value("selected_length")
    nozzle_length = value("nozzle_length")

    hot_wall_temp = value("selected_gas_side_recovery_temperature")
    max_wall_temp = value("material_max_wall_temperature")
    wall_thickness = value("hot_gas_wall_thickness")
    pressure_wall = value("pressure_required_wall_thickness")
    conduction_wall = value("conduction_required_wall_thickness")

    channel_fit = value("channel_fit_ratio")
    channel_valid = value("channel_geometry_valid")

    chamber_pressure_state = numeric_state(chamber_pressure)
    chamber_temperature_state = numeric_state(chamber_temperature)
    expansion_ratio_state = numeric_state(expansion_ratio)
    thrust_state = numeric_state(thrust)
    specific_impulse_state = numeric_state(specific_impulse)
    throat_radius_state = numeric_state(throat_radius)
    exit_radius_state = numeric_state(exit_radius)
    selected_length_state = numeric_state(selected_length)
    nozzle_length_state = numeric_state(nozzle_length)
    max_wall_temp_state = numeric_state(max_wall_temp)
    wall_thickness_state = numeric_state(wall_thickness)
    pressure_wall_state = numeric_state(pressure_wall)
    conduction_wall_state = numeric_state(conduction_wall)

    if chamber_pressure_state == "missing":
        add_warning(
            "Missing",
            "chamber_pressure",
            "Chamber pressure is missing."
        )
    elif chamber_pressure_state == "invalid":
        add_invalid_numeric("chamber_pressure")
    elif chamber_pressure <= 0:
        add_warning(
            "Invalid",
            "chamber_pressure",
            "Chamber pressure must be positive."
        )

    if chamber_temperature_state == "missing":
        add_warning(
            "Missing",
            "chamber_temperature",
            "Chamber temperature is missing."
        )
    elif chamber_temperature_state == "invalid":
        add_invalid_numeric("chamber_temperature")
    elif chamber_temperature <= 0:
        add_warning(
            "Invalid",
            "chamber_temperature",
            "Chamber temperature must be positive."
        )

    if expansion_ratio_state == "invalid":
        add_invalid_numeric("expansion_ratio")
    elif expansion_ratio_state == "valid" and expansion_ratio < 1:
        add_warning(
            "Invalid",
            "expansion_ratio",
            "Expansion ratio should be at least 1."
        )

    if thrust_state == "invalid":
        add_invalid_numeric("thrust")
    elif thrust_state == "valid" and thrust <= 0:
        add_warning(
            "Invalid",
            "thrust",
            "Calculated thrust is zero or negative."
        )

    if specific_impulse_state == "invalid":
        add_invalid_numeric("specific_impulse")
    elif specific_impulse_state == "valid" and specific_impulse <= 0:
        add_warning(
            "Invalid",
            "specific_impulse",
            "Specific impulse is zero or negative."
        )

    if throat_radius_state == "invalid":
        add_invalid_numeric("throat_radius")

    if exit_radius_state == "invalid":
        add_invalid_numeric("exit_radius")

    if (
        throat_radius_state == "valid"
        and
        exit_radius_state == "valid"
    ):
        if exit_radius <= throat_radius:
            add_warning(
                "Geometry",
                "exit_radius",
                "Exit radius is not larger than throat radius."
            )

    if selected_length_state == "invalid":
        add_invalid_numeric("selected_length")

    if nozzle_length_state == "invalid":
        add_invalid_numeric("nozzle_length")

    if (
        selected_length_state == "valid"
        and
        nozzle_length_state == "valid"
    ):
        if selected_length < 0:
            add_warning(
                "Geometry",
                "selected_length",
                "Selected length is negative."
            )
        elif selected_length > nozzle_length:
            add_warning(
                "Geometry",
                "selected_length",
                "Selected length is greater than nozzle length."
            )

    hot_wall_actual = value("hot_gas_side_wall_temperature")
    hot_wall_actual_state = numeric_state(hot_wall_actual)

    if hot_wall_actual_state == "invalid":
        add_invalid_numeric(
            "hot_gas_side_wall_temperature"
        )

    if max_wall_temp_state == "invalid":
        add_invalid_numeric(
            "material_max_wall_temperature"
        )

    if (
        hot_wall_actual_state == "valid"
        and
        max_wall_temp_state == "valid"
    ):
        if hot_wall_actual > max_wall_temp:
            add_warning(
                "Thermal",
                "hot_gas_side_wall_temperature",
                "Calculated gas-side metal wall temperature exceeds the selected material limit."
            )

    bartz_hg = value(
        "bartz_gas_side_heat_transfer_coefficient"
    )

    manual_hg = value(
        "hot_gas_heat_transfer_coefficient"
    )

    bartz_hg_state = numeric_state(
        bartz_hg
    )

    if bartz_hg is None and manual_hg is None:
        add_warning(
            "Thermal Model",
            "bartz_gas_side_heat_transfer_coefficient",
            "Gas-side heat-transfer coefficient is missing. Bartz could not be calculated and no manual fallback was supplied."
        )

    if bartz_hg_state == "invalid":
        add_invalid_numeric(
            "bartz_gas_side_heat_transfer_coefficient"
        )
    elif bartz_hg_state == "valid" and bartz_hg <= 0:
        add_warning(
            "Thermal Model",
            "bartz_gas_side_heat_transfer_coefficient",
            "Calculated Bartz gas-side heat-transfer coefficient is invalid."
        )

    coolant_re = value(
        "coolant_reynolds_number"
    )

    coolant_dp = value(
        "coolant_pressure_drop"
    )

    chamber_pressure = value(
        "chamber_pressure"
    )

    coolant_re_state = numeric_state(
        coolant_re
    )

    coolant_dp_state = numeric_state(
        coolant_dp
    )

    if coolant_re_state == "invalid":
        add_invalid_numeric(
            "coolant_reynolds_number"
        )
    elif coolant_re_state == "valid" and coolant_re < 10000:
        add_warning(
            "Cooling",
            "coolant_reynolds_number",
            "Coolant Reynolds number is below the preferred turbulent range for Dittus-Boelter."
        )

    if coolant_dp_state == "invalid":
        add_invalid_numeric(
            "coolant_pressure_drop"
        )
    elif (
        coolant_dp_state == "valid"
        and
        chamber_pressure_state == "valid"
    ):
        if coolant_dp > 0.2 * chamber_pressure:
            add_warning(
                "Cooling",
                "coolant_pressure_drop",
                "Coolant pressure drop is very high relative to chamber pressure."
            )

    if wall_thickness_state == "invalid":
        add_invalid_numeric(
            "hot_gas_wall_thickness"
        )
    elif wall_thickness_state == "valid":
        if wall_thickness <= 0:
            add_warning(
                "Invalid",
                "hot_gas_wall_thickness",
                "Wall thickness is zero or negative."
            )

    if pressure_wall_state == "invalid":
        add_invalid_numeric(
            "pressure_required_wall_thickness"
        )
    elif (
        pressure_wall_state == "valid"
        and
        wall_thickness_state == "valid"
    ):
        if wall_thickness < pressure_wall:
            add_warning(
                "Structural",
                "hot_gas_wall_thickness",
                "Wall thickness is below pressure-required wall thickness."
            )

    if params.get("wall_autosized") is True:
        add_warning(
            "Autosized",
            "hot_gas_wall_thickness",
            "Hot-gas wall thickness was automatically sized from pressure/minimum wall constraints."
        )

    if conduction_wall_state == "invalid":
        add_invalid_numeric(
            "conduction_required_wall_thickness"
        )
    elif conduction_wall_state == "valid":
        if conduction_wall > 0.02:
            add_warning(
                "Thermal Model",
                "conduction_required_wall_thickness",
                "Conduction-only wall thickness is unrealistically high. "
                "This value is diagnostic only and is not used for wall autosizing. "
                "Add coolant-side convection before treating thermal wall sizing as final."
            )
        elif (
            wall_thickness_state == "valid"
            and
            wall_thickness < conduction_wall
        ):
            add_warning(
                "Thermal",
                "hot_gas_wall_thickness",
                "Wall thickness is below the simple conduction-only estimate."
            )

    if channel_valid is not None:
        if (
            channel_valid is False
            or
            str(channel_valid).lower()
            in ["false", "invalid", "0"]
        ):
            add_warning(
                "Cooling Geometry",
                "channel_geometry_valid",
                "Cooling channel geometry is marked invalid."
            )

    if channel_fit is not None:
        try:
            channel_fit_numeric = float(
                channel_fit
            )

            if not math.isfinite(
                channel_fit_numeric
            ):
                raise ValueError(
                    "non-finite channel_fit_ratio"
                )

        except (TypeError, ValueError, OverflowError):
            add_warning(
                "Invalid",
                "channel_fit_ratio",
                "channel_fit_ratio must be a finite numeric value."
            )

        else:
            if channel_fit_numeric < 1.0:
                add_warning(
                    "Cooling Geometry",
                    "channel_fit_ratio",
                    "Cooling channel pitch/rib layout exceeds available circumference."
                )

    return warnings
