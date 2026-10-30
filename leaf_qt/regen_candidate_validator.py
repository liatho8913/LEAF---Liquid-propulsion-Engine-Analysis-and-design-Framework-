from leaf_qt.structured_status_access import highest_severity as solver_highest_severity, is_pass
"""
LEAF Regen Candidate Validator
==============================

PHASE 11B.1B

Validates generated regen candidates conservatively.

This module DOES:
- evaluate each generated candidate
- record pass/fail reasons
- store validation metrics
- count passing/failing candidates

This module DOES NOT:
- rank candidates
- select best candidate
- apply candidate geometry
"""

import math




def _leaf_48m_attach_feasibility_robust_contract(results):
    """Classify existing regen engineering evidence by qualification level.

    This helper introduces no new engineering equations or numerical
    safety margins.

    FEASIBILITY contains only the absolute boundary evidence established
    by Programme 48H:

    - geometry fits the available circumference,
    - coolant flow is above the existing Reynolds flow-regime floor,
    - wall temperature does not exceed the available material limit.

    ROBUSTNESS reuses the existing full candidate validator as the
    nominal engineering-envelope gate. That validator already owns the
    Reynolds engineering target, coolant-velocity envelope,
    channel-aspect-ratio envelope, wall-thickness envelope,
    material-temperature comparison and pressure-drop budget.

    The existing manufacturability and geometry-realism owners remain
    specialist hard gates.

    Thermal robustness additionally requires authoritative sourced
    material-temperature validation. No 10 %, 25 %, melting-point
    fraction or other universal thermal derating is introduced here.
    """

    def first_number(*keys):
        for key in keys:
            value = results.get(key)

            if value is None:
                continue

            try:
                return float(value)
            except (TypeError, ValueError):
                continue

        return None

    def first_boolean(*keys):
        for key in keys:
            if key not in results:
                continue

            value = results.get(key)

            if isinstance(value, bool):
                return value

            if isinstance(value, (int, float)):
                return bool(value)

            if isinstance(value, str):
                normalised = value.strip().upper()

                if normalised in {
                    "TRUE",
                    "PASS",
                    "PASSED",
                    "READY",
                    "VALID",
                    "ACCEPT",
                    "ACCEPTED",
                    "1",
                }:
                    return True

                if normalised in {
                    "FALSE",
                    "FAIL",
                    "FAILED",
                    "BLOCKED",
                    "INVALID",
                    "REJECT",
                    "REJECTED",
                    "0",
                }:
                    return False

        return None

    # ------------------------------------------------------------
    # ABSOLUTE FEASIBILITY EVIDENCE
    # ------------------------------------------------------------

    fit_ratio = first_number(
        "fit_ratio",
        "regen_geometry_fit_ratio",
        "channel_fit_ratio",
        "regen_channel_fit_ratio",
    )

    reynolds = first_number(
        "regen_axial_min_reynolds_number",
        "coolant_reynolds_preview",
        "coolant_reynolds_number",
        "regen_min_reynolds_number",
        "full_engine_regen_min_reynolds",
        "minimum_coolant_reynolds_number",
    )

    wall_temperature = first_number(
        "regen_axial_max_hot_wall_temperature",
        "Twg",
        "hot_gas_side_wall_temperature",
        "hot_gas_wall_temperature",
        "max_hot_gas_wall_temperature",
        "regen_axial_max_hot_gas_wall_temperature",
    )

    feasibility_temperature_limit = first_number(
        "selected_material_max_temperature",
        "material_max_temperature",
        "regen_material_temperature_limit",
        "material_temperature_limit",
        "effective_material_temperature_limit",
        "material_max_wall_temperature",
    )

    geometry_fit_pass = (
        fit_ratio is not None
        and
        fit_ratio >= 1.0
    )

    reynolds_flow_regime_pass = (
        reynolds is not None
        and
        reynolds >= 2300.0
    )

    material_temperature_feasibility_pass = (
        wall_temperature is not None
        and
        feasibility_temperature_limit is not None
        and
        wall_temperature <= feasibility_temperature_limit
    )

    feasibility_components = {
        "geometry_fit":
            geometry_fit_pass,

        "reynolds_flow_regime":
            reynolds_flow_regime_pass,

        "material_temperature":
            material_temperature_feasibility_pass,
    }

    feasibility_blockers = []

    if fit_ratio is None:
        feasibility_blockers.append(
            "Geometry fit ratio is unavailable."
        )
    elif not geometry_fit_pass:
        feasibility_blockers.append(
            "Geometry does not satisfy absolute circumference fit."
        )

    if reynolds is None:
        feasibility_blockers.append(
            "Coolant Reynolds number is unavailable."
        )
    elif not reynolds_flow_regime_pass:
        feasibility_blockers.append(
            "Coolant Reynolds number is below the established flow-regime floor."
        )

    if wall_temperature is None:
        feasibility_blockers.append(
            "Hot-gas wall temperature is unavailable."
        )
    elif feasibility_temperature_limit is None:
        feasibility_blockers.append(
            "Material temperature limit is unavailable."
        )
    elif not material_temperature_feasibility_pass:
        feasibility_blockers.append(
            "Hot-gas wall temperature exceeds the available material limit."
        )

    feasibility_pass = all(
        feasibility_components.values()
    )

    results[
        "regen_feasibility_pass"
    ] = feasibility_pass

    results[
        "regen_feasibility_blockers"
    ] = feasibility_blockers

    results[
        "regen_feasibility_component_state"
    ] = feasibility_components

    results[
        "regen_feasibility_evidence"
    ] = {
        "fit_ratio":
            fit_ratio,

        "coolant_reynolds":
            reynolds,

        "hot_gas_wall_temperature":
            wall_temperature,

        "material_temperature_limit":
            feasibility_temperature_limit,
    }

    # ------------------------------------------------------------
    # EXISTING NOMINAL ENGINEERING ENVELOPE
    # ------------------------------------------------------------

    status_candidates = (
        results.get("regen_candidate_validator_status"),
        results.get("regen_candidate_validation_status"),
        results.get("candidate_validator_status"),
    )

    legacy_status = next(
        (
            str(value).strip().upper()
            for value in status_candidates
            if value not in (
                None,
                "",
            )
        ),
        "",
    )

    fail_count_raw = (
        results.get(
            "regen_candidate_validator_fail_count"
        )
    )

    if fail_count_raw is None:
        fail_count_raw = (
            results.get(
                "regen_candidate_validation_fail_count"
            )
        )

    try:
        legacy_fail_count = int(
            fail_count_raw or 0
        )
    except (TypeError, ValueError):
        legacy_fail_count = 1

    legacy_engineering_envelope_pass = (
        legacy_status.startswith(
            "PASS"
        )
        and
        legacy_fail_count == 0
    )

    # ------------------------------------------------------------
    # SPECIALIST NOMINAL HARD GATES
    # ------------------------------------------------------------

    manufacturability_pass = first_boolean(
        "phase_16q3_manufacturability_pass",
        "manufacturability_pass",
        "regen_manufacturability_pass",
        "geometry_manufacturability_pass",
    )

    geometry_realism_pass = first_boolean(
        "phase_16q8_geometry_realism_pass",
        "geometry_realism_pass",
        "regen_geometry_realism_pass",
    )

    # If specialist results are genuinely unavailable, qualification
    # remains unproven rather than assuming PASS.
    nominal_manufacturability_pass = (
        manufacturability_pass is True
    )

    nominal_geometry_realism_pass = (
        geometry_realism_pass is True
    )

    # ------------------------------------------------------------
    # SOURCED THERMAL ROBUSTNESS
    # ------------------------------------------------------------

    material_mode = str(
        results.get("material_source_validation_mode")
        or
        results.get("material_property_interpolation_mode")
        or
        results.get("material_temperature_validation_mode")
        or
        ""
    ).upper()

    authoritative_thermal_source = (
        "SOURCED_VALIDATION"
        in
        material_mode
    )

    robust_temperature_limit = first_number(
        "effective_material_temperature_limit",
        "material_max_wall_temperature",
        "material_max_service_temperature",
        "sourced_material_temperature_limit",
        "material_temperature_limit",
    )

    thermal_robust_pass = (
        authoritative_thermal_source
        and
        wall_temperature is not None
        and
        robust_temperature_limit is not None
        and
        wall_temperature <= robust_temperature_limit
    )

    # ------------------------------------------------------------
    # ROBUST COMPONENT CONTRACT
    # ------------------------------------------------------------

    robust_components = {
        "feasibility":
            feasibility_pass,

        # Existing validator owns:
        # Reynolds engineering target,
        # coolant velocity envelope,
        # aspect-ratio envelope,
        # structural wall envelope,
        # material-temperature comparison,
        # pressure-drop budget.
        "existing_engineering_envelope":
            legacy_engineering_envelope_pass,

        "nominal_manufacturability":
            nominal_manufacturability_pass,

        "nominal_geometry_realism":
            nominal_geometry_realism_pass,

        "sourced_material_temperature":
            thermal_robust_pass,
    }

    robust_blockers = []

    if not feasibility_pass:
        robust_blockers.append(
            "Absolute regen feasibility has not passed."
        )

    if not legacy_engineering_envelope_pass:
        robust_blockers.append(
            "Existing regen engineering-envelope validation has not passed."
        )

    if not nominal_manufacturability_pass:
        robust_blockers.append(
            "Nominal manufacturability gate has not passed."
        )

    if not nominal_geometry_realism_pass:
        robust_blockers.append(
            "Nominal geometry-realism gate has not passed."
        )

    if not authoritative_thermal_source:
        robust_blockers.append(
            "Authoritative sourced material-temperature validation is unavailable."
        )

    elif wall_temperature is None:
        robust_blockers.append(
            "Hot-gas wall temperature is unavailable for robust thermal qualification."
        )

    elif robust_temperature_limit is None:
        robust_blockers.append(
            "Sourced material-specific service/recommended temperature limit is unavailable."
        )

    elif not thermal_robust_pass:
        robust_blockers.append(
            "Hot-gas wall temperature exceeds the sourced material-specific robust limit."
        )

    robust_pass = all(
        robust_components.values()
    )

    results[
        "regen_robust_qualification_pass"
    ] = robust_pass

    results[
        "regen_robust_qualification_blockers"
    ] = robust_blockers

    results[
        "regen_robust_qualification_component_state"
    ] = robust_components

    results[
        "regen_robust_qualification_evidence"
    ] = {
        "legacy_validator_status":
            legacy_status,

        "legacy_validator_fail_count":
            legacy_fail_count,

        "manufacturability_pass":
            manufacturability_pass,

        "geometry_realism_pass":
            geometry_realism_pass,

        "material_source_validation_mode":
            material_mode,

        "hot_gas_wall_temperature":
            wall_temperature,

        "robust_material_temperature_limit":
            robust_temperature_limit,
    }

    return results



def _leaf_48p_attach_manufacturing_tolerance_qualification(results):
    """Attach manufacturing-tolerance qualification from its canonical owner."""

    try:
        try:
            from .regen_manufacturability_geometry_gate_phase_16q3 import (
                evaluate_manufacturing_tolerance_qualification,
            )
        except ImportError:
            from regen_manufacturability_geometry_gate_phase_16q3 import (
                evaluate_manufacturing_tolerance_qualification,
            )

        report = evaluate_manufacturing_tolerance_qualification(
            results,
            geometry=results,
            engineering_validator=validate_single_candidate,
        )

    except Exception as exc:
        report = {
            "passed":
                False,

            "status":
                "FAIL_REGEN_MANUFACTURING_TOLERANCE_QUALIFICATION_INTERNAL_ERROR",

            "blockers":
                [
                    "Manufacturing tolerance qualification could not be evaluated."
                ],

            "case_count":
                0,

            "failed_case_count":
                0,

            "cases":
                [],

            "error":
                repr(
                    exc
                ),
        }

    results[
        "regen_manufacturing_tolerance_qualification_pass"
    ] = bool(
        report.get(
            "passed",
            False,
        )
    )

    results[
        "regen_manufacturing_tolerance_qualification_status"
    ] = report.get(
        "status"
    )

    results[
        "regen_manufacturing_tolerance_qualification_blockers"
    ] = list(
        report.get(
            "blockers"
        )
        or
        []
    )

    results[
        "regen_manufacturing_tolerance_qualification_evidence"
    ] = report

    return results



def _leaf_48u_attach_regen_qualification_report(results):
    """Attach the canonical per-constraint regen qualification report.

    This is reporting only.  It introduces no new universal safety
    factor, manufacturing tolerance, or off-nominal magnitude.
    """

    import math

    def number(*keys):
        for key in keys:
            value = results.get(
                key
            )

            if value is None:
                continue

            try:
                value = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            if math.isfinite(
                value
            ):
                return value

        return None

    def minimum_reserve(
        predicted,
        limit,
    ):
        if (
            predicted is None
            or
            limit is None
        ):
            return None

        return (
            predicted
            -
            limit
        )

    def maximum_reserve(
        predicted,
        limit,
    ):
        if (
            predicted is None
            or
            limit is None
        ):
            return None

        return (
            limit
            -
            predicted
        )

    def status(
        reserve,
        explicit_pass=None,
    ):
        if explicit_pass is True:
            return "PASS"

        if explicit_pass is False:
            return "FAIL"

        if reserve is None:
            return "UNPROVEN"

        return (
            "PASS"
            if reserve >= 0.0
            else
            "FAIL"
        )

    constraints = {}

    def add(
        name,
        predicted_value,
        qualified_limit,
        absolute_limit,
        reserve,
        explicit_pass=None,
    ):
        constraints[
            name
        ] = {
            "predicted_value":
                predicted_value,

            "qualified_limit":
                qualified_limit,

            "absolute_limit":
                absolute_limit,

            "reserve":
                reserve,

            "status":
                status(
                    reserve,
                    explicit_pass,
                ),
        }

    fit_ratio = number(
        "fit_ratio",
        "channel_fit_ratio",
        "viewer_channel_fit_ratio",
        "candidate_channel_fit_ratio",
        "regen_geometry_fit_ratio",
    )

    add(
        "geometry_fit",
        fit_ratio,
        1.0,
        1.0,
        minimum_reserve(
            fit_ratio,
            1.0,
        ),
    )

    reynolds = number(
        "regen_axial_min_reynolds_number",
        "coolant_reynolds_preview",
        "coolant_reynolds_number",
        "regen_min_reynolds_number",
        "full_engine_regen_min_reynolds",
    )

    reynolds_target = number(
        "regen_target_reynolds_number",
        "regen_derived_target_reynolds_number",
        "target_reynolds_number",
    )

    reynolds_absolute = 2300.0

    add(
        "coolant_reynolds",
        reynolds,
        reynolds_target,
        reynolds_absolute,
        minimum_reserve(
            reynolds,
            (
                reynolds_target
                if reynolds_target is not None
                else
                reynolds_absolute
            ),
        ),
    )

    velocity = number(
        "regen_axial_max_coolant_velocity",
        "coolant_velocity_preview",
        "coolant_velocity",
        "regen_coolant_velocity",
    )

    velocity_limit = number(
        "regen_derived_maximum_coolant_velocity",
        "regen_max_coolant_velocity",
        "full_engine_regen_max_velocity",
        "maximum_allowed_coolant_velocity",
    )

    add(
        "coolant_velocity",
        velocity,
        velocity_limit,
        velocity_limit,
        maximum_reserve(
            velocity,
            velocity_limit,
        ),
    )

    aspect_ratio = number(
        "channel_aspect_ratio",
        "regen_channel_aspect_ratio",
    )

    aspect_min = number(
        "regen_min_channel_aspect_ratio",
        "minimum_channel_aspect_ratio",
    )

    aspect_max = number(
        "regen_max_channel_aspect_ratio",
        "maximum_channel_aspect_ratio",
    )

    aspect_reserve = None

    if (
        aspect_ratio is not None
        and
        aspect_min is not None
        and
        aspect_max is not None
    ):
        aspect_reserve = min(
            aspect_ratio
            -
            aspect_min,

            aspect_max
            -
            aspect_ratio,
        )

    add(
        "channel_aspect_ratio",
        aspect_ratio,
        {
            "minimum":
                aspect_min,

            "maximum":
                aspect_max,
        },
        None,
        aspect_reserve,
    )

    wall = number(
        "hot_gas_wall_thickness"
    )

    wall_requirements = [
        value

        for value in (
            number(
                "pressure_required_wall_thickness"
            ),

            number(
                "conduction_required_wall_thickness"
            ),

            number(
                "minimum_wall_thickness"
            ),
        )

        if value is not None
    ]

    governing_wall = (
        max(
            wall_requirements
        )
        if wall_requirements
        else
        None
    )

    add(
        "hot_gas_wall_thickness",
        wall,
        governing_wall,
        governing_wall,
        minimum_reserve(
            wall,
            governing_wall,
        ),
    )

    wall_temperature = number(
        "hot_gas_side_wall_temperature",
        "hot_gas_wall_temperature",
        "max_hot_gas_wall_temperature",
        "regen_axial_max_hot_wall_temperature",
        "Twg",
    )

    qualified_temperature = number(
        "effective_material_temperature_limit",
        "material_max_wall_temperature",
        "material_max_service_temperature",
        "sourced_material_temperature_limit",
    )

    absolute_temperature = number(
        "selected_material_max_temperature",
        "material_max_temperature",
        "regen_material_temperature_limit",
        "material_temperature_limit",
    )

    add(
        "material_temperature",
        wall_temperature,
        qualified_temperature,
        absolute_temperature,
        maximum_reserve(
            wall_temperature,
            qualified_temperature,
        ),
    )

    pressure_drop = number(
        "recommended_regen_axial_total_pressure_drop",
        "regen_axial_total_pressure_drop",
        "coolant_pressure_drop_total",
        "coolant_pressure_drop",
    )

    pressure_limit = number(
        "regen_derived_pressure_drop_limit",
        "regen_pressure_drop_limit",
        "full_engine_regen_pressure_drop_limit",
    )

    add(
        "coolant_pressure_drop",
        pressure_drop,
        pressure_limit,
        pressure_limit,
        maximum_reserve(
            pressure_drop,
            pressure_limit,
        ),
    )

    robust_components = results.get(
        "regen_robust_qualification_component_state"
    )

    if isinstance(
        robust_components,
        dict,
    ):
        for name, payload in (
            robust_components.items()
        ):
            component_pass = None

            if payload is True:
                component_pass = True

            elif payload is False:
                component_pass = False

            elif isinstance(
                payload,
                dict,
            ):
                for key in (
                    "passed",
                    "pass",
                    "valid",
                    "qualified",
                ):
                    if payload.get(
                        key
                    ) is True:
                        component_pass = True
                        break

                    if payload.get(
                        key
                    ) is False:
                        component_pass = False
                        break

            add(
                "robust_component:"
                +
                str(
                    name
                ),

                component_pass,

                True,

                None,

                (
                    1.0
                    if component_pass is True
                    else
                    -1.0
                    if component_pass is False
                    else
                    None
                ),

                component_pass,
            )

    tolerance_evidence = results.get(
        "regen_manufacturing_tolerance_qualification_evidence"
    )

    tolerance_failed = None

    if isinstance(
        tolerance_evidence,
        dict,
    ):
        try:
            tolerance_failed = int(
                tolerance_evidence.get(
                    "failed_case_count"
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            tolerance_failed = None

    add(
        "manufacturing_tolerance_envelope",
        tolerance_failed,
        0,
        0,
        (
            -float(
                tolerance_failed
            )
            if tolerance_failed is not None
            else
            None
        ),
        results.get(
            "regen_manufacturing_tolerance_qualification_pass"
        ),
    )

    offnom_evidence = results.get(
        "regen_off_nominal_qualification_evidence"
    )

    offnom_failed = None

    if isinstance(
        offnom_evidence,
        dict,
    ):
        try:
            offnom_failed = int(
                offnom_evidence.get(
                    "failed_scenario_count"
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            offnom_failed = None

    add(
        "off_nominal_operating_envelope",
        offnom_failed,
        0,
        0,
        (
            -float(
                offnom_failed
            )
            if offnom_failed is not None
            else
            None
        ),
        results.get(
            "regen_off_nominal_qualification_pass"
        ),
    )

    report = {
        "state":
            results.get(
                "regen_qualification_state"
            ),

        "passed":
            results.get(
                "regen_qualification_pass"
            )
            is True,

        "enforcement_ready":
            results.get(
                "regen_qualification_enforcement_ready"
            )
            is True,

        "blockers":
            list(
                results.get(
                    "regen_qualification_blockers"
                )
                or
                []
            ),

        "constraints":
            constraints,
    }

    results[
        "regen_qualification_report"
    ] = report

    results[
        "regen_qualification_margins"
    ] = {
        name:
            payload.get(
                "reserve"
            )

        for name, payload
        in constraints.items()
    }

    return results


def _leaf_48f_attach_regen_qualification_contract(results):
    """Attach the canonical staged regen qualification state.

    No new engineering limits are introduced here.

    FAILED:
        Existing absolute candidate validation failed.

    FEASIBLE:
        Existing absolute candidate validation passed.

    ROBUST:
        FEASIBLE plus nominal robustness qualification passed.

    QUALIFIED:
        ROBUST plus manufacturing-tolerance and off-nominal
        qualification passed.

    Hard automatic enforcement activates only after all three
    qualification components exist.
    """

    status_candidates = (
        results.get("regen_candidate_validator_status"),
        results.get("regen_candidate_validation_status"),
        results.get("candidate_validator_status"),
    )

    status = next(
        (
            str(value).upper()
            for value in status_candidates
            if value not in (None, "")
        ),
        "",
    )

    raw_fail_count = (
        results.get(
            "regen_candidate_validator_fail_count"
        )
    )

    if raw_fail_count is None:
        raw_fail_count = (
            results.get(
                "regen_candidate_validation_fail_count"
            )
        )

    try:
        fail_count = int(
            raw_fail_count or 0
        )
    except Exception:
        fail_count = 1

    failures = []

    for key in (
        "regen_candidate_validation_failures",
        "regen_candidate_validator_failures",
        "candidate_validator_failures",
        "failure_reasons",
    ):

        value = results.get(
            key
        )

        if isinstance(
            value,
            (
                list,
                tuple,
            ),
        ):
            failures.extend(
                str(item)
                for item in value
                if item not in (
                    None,
                    "",
                )
            )

    dedicated_feasibility_pass = (
        results.get(
            "regen_feasibility_pass"
        )
    )

    if dedicated_feasibility_pass is None:
        absolute_feasibility_pass = (
            status.startswith(
                "PASS"
            )
            and
            fail_count == 0
        )
    else:
        absolute_feasibility_pass = (
            dedicated_feasibility_pass
            is True
        )

    robust_pass = (
        results.get(
            "regen_robust_qualification_pass"
        )
    )

    manufacturing_tolerance_pass = (
        results.get(
            "regen_manufacturing_tolerance_qualification_pass"
        )
    )

    off_nominal_pass = (
        results.get(
            "regen_off_nominal_qualification_pass"
        )
    )

    component_keys = (
        "regen_robust_qualification_pass",
        "regen_manufacturing_tolerance_qualification_pass",
        "regen_off_nominal_qualification_pass",
    )

    enforcement_ready = all(
        key in results
        for key in component_keys
    )

    blockers = []

    if not absolute_feasibility_pass:

        state = "FAILED"

        blockers.extend(
            failures
            or
            [
                "Existing absolute regen candidate validation did not pass."
            ]
        )

    elif (
        robust_pass is True
        and
        manufacturing_tolerance_pass is True
        and
        off_nominal_pass is True
    ):

        state = "QUALIFIED"

    elif robust_pass is True:

        state = "ROBUST"

    else:

        state = "FEASIBLE"

    if enforcement_ready:

        if robust_pass is not True:

            blockers.append(
                "Nominal robustness qualification did not pass."
            )

        if manufacturing_tolerance_pass is not True:

            blockers.append(
                "Manufacturing-tolerance qualification did not pass."
            )

        if off_nominal_pass is not True:

            blockers.append(
                "Off-nominal qualification did not pass."
            )

    results[
        "regen_qualification_state"
    ] = state

    results[
        "regen_qualification_pass"
    ] = (
        state == "QUALIFIED"
    )

    results[
        "regen_qualification_blockers"
    ] = blockers

    results.setdefault(
        "regen_qualification_margins",
        {},
    )

    results[
        "regen_qualification_enforcement_ready"
    ] = enforcement_ready

    results[
        "regen_qualification_component_state"
    ] = {
        "absolute_feasibility":
            absolute_feasibility_pass,

        "robust":
            robust_pass,

        "manufacturing_tolerance":
            manufacturing_tolerance_pass,

        "off_nominal":
            off_nominal_pass,
    }

    return results


def attach_regen_candidate_validator(results):
    if not isinstance(results, dict):
        _leaf_48m_attach_feasibility_robust_contract(results)
        _leaf_48p_attach_manufacturing_tolerance_qualification(results)
        _leaf_48f_attach_regen_qualification_contract(results)
        _leaf_48u_attach_regen_qualification_report(results)
        return results

    payload = build_regen_candidate_validator(results)
    results.update(payload)
    _leaf_48m_attach_feasibility_robust_contract(results)
    _leaf_48p_attach_manufacturing_tolerance_qualification(results)
    _leaf_48f_attach_regen_qualification_contract(results)
    _leaf_48u_attach_regen_qualification_report(results)
    return results


def _leaf_16t3q8_original_build_regen_candidate_validator(results):
    candidates = results.get("regen_candidate_generator_candidates") or []

    validated = []
    pass_count = 0
    fail_count = 0

    for candidate in candidates:
        checked = validate_single_candidate(candidate, results)
        validated.append(checked)

        if checked.get("validation_status") == "PASS_CANDIDATE_VALIDATION":
            pass_count += 1
        else:
            fail_count += 1

    if not candidates:
        status = "FAIL_NO_CANDIDATES_TO_VALIDATE"
    elif pass_count > 0:
        status = "PASS_VALIDATED_CANDIDATES_FOUND"
    else:
        status = "FAIL_NO_VALIDATED_PASSING_CANDIDATES"

    text = build_regen_candidate_validator_text(
        status=status,
        pass_count=pass_count,
        fail_count=fail_count,
        validated=validated,
    )

    return {
        "regen_candidate_validator_complete": True,
        "phase_11b_1b_regen_candidate_validator_complete": True,
        "regen_candidate_validator_status": status,
        "regen_candidate_validator_pass_count": pass_count,
        "regen_candidate_validator_fail_count": fail_count,
        "regen_candidate_validator_validated_candidates": validated,
        "regen_candidate_validator_text": text,

        # Still locked until ranker and selector exist.
        "regen_candidate_ranking_allowed": pass_count > 0,
        "regen_candidate_automatic_selection_allowed": False,
        "regen_candidate_geometry_application_allowed": False,
    }


def validate_single_candidate(candidate, results):
    candidate = dict(candidate)
    metrics = candidate.get("preview_metrics") or {}
    inputs = candidate.get("inputs") or {}

    failure_reasons = []
    pass_reasons = []

    _validate_geometry_fit(metrics, failure_reasons, pass_reasons)
    _validate_reynolds(metrics, results, failure_reasons, pass_reasons)
    _validate_velocity(metrics, results, failure_reasons, pass_reasons)
    _validate_aspect_ratio(metrics, results, failure_reasons, pass_reasons)
    _validate_wall_thickness(inputs, results, failure_reasons, pass_reasons)
    _validate_material_temperature(results, failure_reasons, pass_reasons)
    _validate_pressure_drop(results, failure_reasons, pass_reasons)
    _validate_source_quality(results, failure_reasons, pass_reasons)

    if failure_reasons:
        validation_status = "FAIL_CANDIDATE_VALIDATION"
    else:
        validation_status = "PASS_CANDIDATE_VALIDATION"

    candidate["validation_status"] = validation_status
    candidate["candidate_status"] = validation_status
    candidate["failure_reasons"] = failure_reasons
    candidate["pass_reasons"] = pass_reasons
    candidate["validation_metrics"] = {
        "fit_ratio": metrics.get("fit_ratio"),
        "coolant_reynolds_preview": metrics.get("coolant_reynolds_preview"),
        "coolant_velocity_preview": metrics.get("coolant_velocity_preview"),
        "aspect_ratio": metrics.get("aspect_ratio"),
        "hot_gas_wall_thickness": inputs.get("hot_gas_wall_thickness"),
    }

    return candidate


def _validate_geometry_fit(metrics, failures, passes):
    fit_ratio = _num(metrics.get("fit_ratio"))

    if fit_ratio is None:
        failures.append("Geometry fit ratio unavailable.")
    elif fit_ratio < 1.0:
        failures.append(
            f"Candidate does not fit circumference. fit_ratio={fit_ratio:.3f}"
        )
    else:
        passes.append(
            f"Candidate channel pitch fits circumference. fit_ratio={fit_ratio:.3f}"
        )


def _validate_reynolds(metrics, results, failures, passes):
    reynolds = _num(metrics.get("coolant_reynolds_preview"))
    target = _num(results.get("regen_target_reynolds_number"), 10000.0)

    if reynolds is None:
        failures.append("Coolant Reynolds number unavailable.")
    elif reynolds < 2300.0:
        failures.append(
            f"Coolant flow is laminar. Re={reynolds:.1f}"
        )
    elif reynolds < target:
        failures.append(
            f"Coolant Reynolds below target. Re={reynolds:.1f}, target={target:.1f}"
        )
    else:
        passes.append(
            f"Coolant Reynolds passes target. Re={reynolds:.1f}"
        )


def _validate_velocity(metrics, results, failures, passes):
    velocity = _num(metrics.get("coolant_velocity_preview"))
    max_velocity = _num(results.get("regen_derived_maximum_coolant_velocity"), 40.0)
    min_velocity = _num(results.get("regen_derived_minimum_coolant_velocity"), 2.0)

    if velocity is None:
        failures.append("Coolant velocity unavailable.")
    elif velocity < min_velocity:
        failures.append(
            f"Coolant velocity too low. v={velocity:.3f} m/s"
        )
    elif velocity > max_velocity:
        failures.append(
            f"Coolant velocity too high. v={velocity:.3f} m/s"
        )
    else:
        passes.append(
            f"Coolant velocity within bounds. v={velocity:.3f} m/s"
        )


def _validate_aspect_ratio(metrics, results, failures, passes):
    aspect_ratio = _num(metrics.get("aspect_ratio"))
    min_ar = _num(results.get("regen_min_channel_aspect_ratio"), 0.5)
    max_ar = _num(results.get("regen_max_channel_aspect_ratio"), 8.0)

    if aspect_ratio is None:
        failures.append("Channel aspect ratio unavailable.")
    elif aspect_ratio < min_ar or aspect_ratio > max_ar:
        failures.append(
            f"Channel aspect ratio outside bounds. AR={aspect_ratio:.3f}"
        )
    else:
        passes.append(
            f"Channel aspect ratio acceptable. AR={aspect_ratio:.3f}"
        )


def _validate_wall_thickness(inputs, results, failures, passes):
    wall = _num(inputs.get("hot_gas_wall_thickness"))
    min_wall = _num(results.get("minimum_hot_gas_wall_thickness"), 0.00075)
    max_wall = _num(results.get("maximum_hot_gas_wall_thickness"), 0.006)

    if wall is None:
        failures.append("Hot-gas wall thickness unavailable.")
    elif wall < min_wall:
        failures.append(
            f"Hot-gas wall too thin. wall={wall:.6f} m, min={min_wall:.6f} m"
        )
    elif wall > max_wall:
        failures.append(
            f"Hot-gas wall too thick for regen efficiency. wall={wall:.6f} m"
        )
    else:
        passes.append(
            f"Hot-gas wall thickness acceptable. wall={wall:.6f} m"
        )


def _validate_material_temperature(results, failures, passes):
    twg = _num(
        results.get("hot_gas_side_wall_temperature")
        or results.get("Twg")
        or results.get("max_hot_gas_wall_temperature")
    )

    limit = _num(
        results.get("selected_material_max_temperature")
        or results.get("material_max_temperature")
        or results.get("regen_material_temperature_limit")
    )

    if twg is None or limit is None:
        passes.append("Material temperature check deferred; values unavailable.")
        return

    if twg > limit:
        failures.append(
            f"Wall temperature exceeds material limit. Twg={twg:.1f} K, limit={limit:.1f} K"
        )
    else:
        passes.append(
            f"Wall temperature below material limit. Twg={twg:.1f} K"
        )


def _validate_pressure_drop(results, failures, passes):
    dp = _num(
        results.get("regen_pressure_drop")
        or results.get("coolant_pressure_drop")
        or results.get("axial_coolant_pressure_drop")
    )

    max_dp = _num(results.get("regen_max_pressure_drop"), None)

    if dp is None or max_dp is None:
        passes.append("Pressure drop check deferred; limit unavailable.")
        return

    if dp > max_dp:
        failures.append(
            f"Coolant pressure drop too high. dp={dp:.1f} Pa, limit={max_dp:.1f} Pa"
        )
    else:
        passes.append(
            f"Coolant pressure drop acceptable. dp={dp:.1f} Pa"
        )


def _validate_source_quality(results, failures, passes):
    material_mode = str(results.get("material_validation_mode", "")).upper()
    coating_mode = str(results.get("coating_validation_mode", "")).upper()

    blocked_tokens = [
        "PLACEHOLDER",
        "UNSOURCED",
        "MISSING",
    ]

    combined = f"{material_mode} {coating_mode}"

    if any(token in combined for token in blocked_tokens):
        failures.append(
            "Candidate blocked by conservative material/coating source-quality gate."
        )
    else:
        passes.append("Material/coating source-quality gate did not block candidate.")


def build_regen_candidate_validator_text(status, pass_count, fail_count, validated):
    lines = [
        "LEAF PHASE 11B.1B REGEN CANDIDATE VALIDATOR",
        "============================================",
        "",
        f"Status: {status}",
        f"Passing candidates: {pass_count}",
        f"Failing candidates: {fail_count}",
        "",
        "Scope:",
        "- Validates generated candidates.",
        "- Records pass/fail reasons.",
        "- Does not rank candidates.",
        "- Does not apply geometry.",
        "",
        "Candidate Results:",
    ]

    if not validated:
        lines.append("- No candidates validated.")
    else:
        for candidate in validated[:25]:
            lines.append(
                f"- {candidate.get('candidate_id')}: "
                f"{candidate.get('validation_status')}; "
                f"failures={len(candidate.get('failure_reasons') or [])}"
            )

        if len(validated) > 25:
            lines.append(f"- ... {len(validated) - 25} additional candidates hidden.")

    return "\n".join(lines)


def _num(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


# ---------------------------------------------------------------------------
# PHASE 16T.3Q.8 — WAVE 2 STATUS ADAPTER
# REGEN CANDIDATE VALIDATOR
# ---------------------------------------------------------------------------

PHASE_16T3Q8_STATUS_ADAPTER_COMPLETE = True
PHASE_16T3Q8_STATUS_ADAPTER_STATUS = (
    "PASS_REGEN_CANDIDATE_VALIDATOR_STATUS_ADAPTER_PHASE_16T3Q8"
)


def _leaf_16t3q8_make_finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3Q.8",
        "owner": "regen_candidate_validator",
    }


def _leaf_16t3q8_get_first(payload, keys, default=None):
    if not isinstance(payload, dict):
        return default

    for key in keys:
        if key in payload:
            return payload.get(key)

    return default


def _leaf_16t3q8_canonical_status_from_findings(findings, ready):
    severities = {str(f.get("severity", "")).upper() for f in findings}

    if solver_highest_severity(severities) == "FAIL":
        return "FAIL"

    if "BLOCKED" in severities:
        return "BLOCKED"

    if "REVIEW_REQUIRED" in severities:
        return "REVIEW_REQUIRED"

    if ready is True:
        return "PASS"

    return "FAIL"


def _leaf_16t3q8_classify_candidate_validator_findings(payload):
    findings = []

    if not isinstance(payload, dict):
        return [
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_PAYLOAD_INVALID",
                "FAIL",
                "Candidate validator did not return a dictionary payload.",
                {"payload_type": type(payload).__name__},
            )
        ]

    validated = bool(
        _leaf_16t3q8_get_first(
            payload,
            [
                "regen_candidate_validator_validated",
                "regen_candidate_validation_validated",
                "candidate_validator_validated",
                "validated",
            ],
            False,
        )
    )

    status = str(
        _leaf_16t3q8_get_first(
            payload,
            [
                "regen_candidate_validator_status",
                "regen_candidate_validation_status",
                "candidate_validator_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    fail_count = _leaf_16t3q8_get_first(
        payload,
        [
            "regen_candidate_validator_fail_count",
            "regen_candidate_validation_fail_count",
            "candidate_validator_fail_count",
            "fail_count",
        ],
        None,
    )

    pass_count = _leaf_16t3q8_get_first(
        payload,
        [
            "regen_candidate_validator_pass_count",
            "regen_candidate_validation_pass_count",
            "candidate_validator_pass_count",
            "pass_count",
        ],
        None,
    )

    failures = _leaf_16t3q8_get_first(
        payload,
        [
            "regen_candidate_validator_failures",
            "regen_candidate_validation_failures",
            "candidate_validator_failures",
            "failures",
        ],
        [],
    )

    passes = _leaf_16t3q8_get_first(
        payload,
        [
            "regen_candidate_validator_passes",
            "regen_candidate_validation_passes",
            "candidate_validator_passes",
            "passes",
        ],
        [],
    )

    if validated:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_VALIDATED",
                "INFO",
                "Candidate validator reports validated.",
                {"legacy_status": status},
            )
        )
    else:
        severity = "FAIL" if "FAIL" in status.upper() else "REVIEW_REQUIRED"
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_NOT_VALIDATED",
                severity,
                "Candidate validator does not report validated.",
                {"legacy_status": status},
            )
        )

    try:
        fail_count_int = int(fail_count)
    except Exception:
        fail_count_int = None

    if fail_count_int is None:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_FAIL_COUNT_MISSING",
                "REVIEW_REQUIRED",
                "Candidate validator fail count is missing.",
                {"fail_count": fail_count},
            )
        )
    elif fail_count_int > 0:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_FAILURES_PRESENT",
                "FAIL",
                "Candidate validator reports one or more failures.",
                {"fail_count": fail_count_int},
            )
        )
    else:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_NO_FAILURES",
                "INFO",
                "Candidate validator reports no failures.",
                {"fail_count": fail_count_int},
            )
        )

    try:
        pass_count_int = int(pass_count)
    except Exception:
        pass_count_int = None

    if pass_count_int is None:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_PASS_COUNT_MISSING",
                "REVIEW_REQUIRED",
                "Candidate validator pass count is missing.",
                {"pass_count": pass_count},
            )
        )
    elif pass_count_int <= 0 and validated:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_ZERO_PASSES",
                "REVIEW_REQUIRED",
                "Candidate validator reports validated but has zero passes.",
                {"pass_count": pass_count_int},
            )
        )
    else:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATOR_PASS_COUNT_PRESENT",
                "INFO",
                "Candidate validator pass count is present.",
                {"pass_count": pass_count_int},
            )
        )

    if isinstance(failures, list) and failures:
        for index, failure in enumerate(failures):
            findings.append(
                _leaf_16t3q8_make_finding(
                    f"CANDIDATE_VALIDATION_FAILURE_{index}",
                    "FAIL",
                    "Candidate validator contains a failure reason.",
                    {"failure": failure},
                )
            )
    elif isinstance(failures, list):
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATION_FAILURE_LIST_EMPTY",
                "INFO",
                "Candidate validator failure list is empty.",
                {},
            )
        )
    else:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATION_FAILURE_LIST_INVALID",
                "REVIEW_REQUIRED",
                "Candidate validator failure list is not a list.",
                {"failures_type": type(failures).__name__},
            )
        )

    if isinstance(passes, list):
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATION_PASS_LIST_PRESENT",
                "INFO",
                "Candidate validator pass list is present.",
                {"pass_list_count": len(passes)},
            )
        )
    else:
        findings.append(
            _leaf_16t3q8_make_finding(
                "CANDIDATE_VALIDATION_PASS_LIST_INVALID",
                "REVIEW_REQUIRED",
                "Candidate validator pass list is not a list.",
                {"passes_type": type(passes).__name__},
            )
        )

    return findings


def _leaf_16t3q8_build_global_status_payload(
    canonical_status,
    legacy_status,
    findings,
    ready,
):
    severity_counts = {}

    for finding in findings:
        severity = str(finding.get("severity", "UNKNOWN")).upper()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "owner": "regen_candidate_validator",
        "phase": "16T.3Q.8",
        "canonical_status": canonical_status,
        "global_status": canonical_status,
        "legacy_status": legacy_status,
        "ready": bool(ready),
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "findings": findings,
        "adapter": "wave_2_status_adapter",
        "adapter_phase": "16T.3Q.8",
    }


def _leaf_16t3q8_build_adapter_report(
    canonical_status,
    legacy_status,
    findings,
):
    lines = [
        "LEAF PHASE 16T.3Q.8 STATUS ADAPTER",
        "====================================",
        "",
        "Owner: regen_candidate_validator",
        "Target: Regen Candidate Validator",
        f"Canonical Status: {canonical_status}",
        f"Legacy Status: {legacy_status}",
        f"Structured Findings: {len(findings)}",
        "",
        "Findings:",
    ]

    if findings:
        for finding in findings:
            lines.append(
                f"- [{finding.get('severity')}] "
                f"{finding.get('code')}: {finding.get('message')}"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "Compatibility:",
            "- Existing public function name is preserved.",
            "- Existing payload fields are preserved.",
            "- Existing legacy status strings are preserved.",
            "- Structured status fields are additive only.",
            "- validate_single_candidate remains untouched.",
        ]
    )

    return "\n".join(lines)


def build_regen_candidate_validator(*args, **kwargs):
    payload = _leaf_16t3q8_original_build_regen_candidate_validator(
        *args,
        **kwargs,
    )

    if not isinstance(payload, dict):
        findings = _leaf_16t3q8_classify_candidate_validator_findings(payload)
        canonical_status = "FAIL"
        legacy_status = "UNKNOWN"
        ready = False

        global_status_payload = _leaf_16t3q8_build_global_status_payload(
            canonical_status=canonical_status,
            legacy_status=legacy_status,
            findings=findings,
            ready=ready,
        )

        adapter_report = _leaf_16t3q8_build_adapter_report(
            canonical_status=canonical_status,
            legacy_status=legacy_status,
            findings=findings,
        )

        return {
            "phase_16t3q8_status_adapter_complete": True,
            "phase_16t3q8_regen_candidate_validator_status_adapter_complete": True,
            "regen_candidate_validator_status_adapter_complete": True,
            "regen_candidate_validator_status_adapter_status": (
                PHASE_16T3Q8_STATUS_ADAPTER_STATUS
            ),
            "regen_candidate_validator_structured_findings": findings,
            "regen_candidate_validator_global_status": canonical_status,
            "regen_candidate_validator_global_status_payload": global_status_payload,
            "regen_candidate_validator_adapter_report": adapter_report,
            "regen_candidate_validator_legacy_status": legacy_status,
            "structured_findings": findings,
            "global_status": canonical_status,
            "global_status_payload": global_status_payload,
            "adapter_report": adapter_report,
        }

    ready = bool(
        _leaf_16t3q8_get_first(
            payload,
            [
                "regen_candidate_validator_validated",
                "regen_candidate_validation_validated",
                "candidate_validator_validated",
                "validated",
            ],
            False,
        )
    )

    legacy_status = str(
        _leaf_16t3q8_get_first(
            payload,
            [
                "regen_candidate_validator_status",
                "regen_candidate_validation_status",
                "candidate_validator_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    findings = _leaf_16t3q8_classify_candidate_validator_findings(payload)
    canonical_status = _leaf_16t3q8_canonical_status_from_findings(
        findings=findings,
        ready=ready,
    )

    global_status_payload = _leaf_16t3q8_build_global_status_payload(
        canonical_status=canonical_status,
        legacy_status=legacy_status,
        findings=findings,
        ready=ready,
    )

    adapter_report = _leaf_16t3q8_build_adapter_report(
        canonical_status=canonical_status,
        legacy_status=legacy_status,
        findings=findings,
    )

    payload.update(
        {
            "phase_16t3q8_status_adapter_complete": True,
            "phase_16t3q8_regen_candidate_validator_status_adapter_complete": True,
            "regen_candidate_validator_status_adapter_complete": True,
            "regen_candidate_validator_status_adapter_status": (
                PHASE_16T3Q8_STATUS_ADAPTER_STATUS
            ),
            "regen_candidate_validator_structured_findings": findings,
            "regen_candidate_validator_global_status": canonical_status,
            "regen_candidate_validator_global_status_payload": global_status_payload,
            "regen_candidate_validator_adapter_report": adapter_report,
            "regen_candidate_validator_legacy_status": legacy_status,
            "structured_findings": findings,
            "global_status": canonical_status,
            "global_status_payload": global_status_payload,
            "adapter_report": adapter_report,
        }
    )

    return payload


