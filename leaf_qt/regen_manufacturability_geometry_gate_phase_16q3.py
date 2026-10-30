from __future__ import annotations

from typing import Any


MIN_CHANNEL_WIDTH = 0.00075
WARN_CHANNEL_WIDTH = 0.00100
MIN_EFFECTIVE_RIB_WIDTH = 0.00025
MAX_ASPECT_RATIO = 4.0
MIN_ASPECT_RATIO = 0.5
MAX_COOLING_COVERAGE = 0.90


def _num(value: Any, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def evaluate_manufacturability_geometry(geometry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(geometry, dict):
        geometry = {}

    width = _num(geometry.get("coolant_channel_width", geometry.get("channel_width")), None)
    height = _num(geometry.get("coolant_channel_height", geometry.get("channel_height")), None)
    rib = _num(geometry.get("rib_width", geometry.get("effective_rib_width")), None)
    effective_rib = _num(geometry.get("effective_rib_width"), rib)
    coverage = _num(geometry.get("cooling_coverage"), None)

    blockers = []
    warnings = []

    if width is None or width <= 0:
        blockers.append("Channel width is missing or non-positive.")
    elif width < MIN_CHANNEL_WIDTH:
        blockers.append(f"Channel width is below manufacturable minimum: {width:.6g} m.")
    elif width < WARN_CHANNEL_WIDTH:
        warnings.append(f"Channel width is very small: {width:.6g} m.")

    if height is None or height <= 0:
        blockers.append("Channel height is missing or non-positive.")

    aspect_ratio = None
    if width is not None and width > 0 and height is not None and height > 0:
        aspect_ratio = height / width
        if aspect_ratio > MAX_ASPECT_RATIO:
            blockers.append(f"Channel aspect ratio is too high: {aspect_ratio:.3f}.")
        if aspect_ratio < MIN_ASPECT_RATIO:
            blockers.append(f"Channel aspect ratio is too low: {aspect_ratio:.3f}.")

    if effective_rib is None:
        blockers.append("Effective rib width is missing.")
    elif effective_rib < MIN_EFFECTIVE_RIB_WIDTH:
        blockers.append(f"Effective rib width is below minimum: {effective_rib:.6g} m.")

    if coverage is not None and coverage > MAX_COOLING_COVERAGE:
        blockers.append(f"Cooling coverage is above structural margin limit: {coverage:.6g}.")
    elif coverage is None:
        warnings.append("Cooling coverage is missing; manufacturability gate could not check coverage.")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_MANUFACTURABILITY_GEOMETRY_GATE_PHASE_16Q3"
            if passed
            else "FAIL_REGEN_MANUFACTURABILITY_GEOMETRY_GATE_PHASE_16Q3"
        ),
        "passed": passed,
        "blockers": blockers,
        "warnings": warnings,
        "channel_width": width,
        "channel_height": height,
        "aspect_ratio": aspect_ratio,
        "effective_rib_width": effective_rib,
        "cooling_coverage": coverage,
    }



def evaluate_manufacturing_tolerance_qualification(
    results,
    geometry=None,
    engineering_validator=None,
):
    """Evaluate the complete sourced manufacturing-tolerance envelope.

    No tolerance values are invented here.

    Qualification requires an authoritative process-capability or
    verified drawing-tolerance policy. The four current qualification
    dimensions are:

    - coolant channel width
    - coolant channel height
    - rib width
    - hot-gas wall thickness

    All 2**4 dimensional corner combinations are evaluated.

    The existing manufacturability owner evaluates manufacturing
    geometry. The existing candidate validator may be supplied as a
    callback so engineering-envelope checks remain with their current
    owner.
    """

    from itertools import product
    import math

    required_dimensions = (
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
        "hot_gas_wall_thickness",
    )

    authoritative_modes = {
        "SOURCED_PROCESS_CAPABILITY",
        "VERIFIED_DRAWING_TOLERANCE",
    }

    blockers = []
    cases = []

    report = {
        "passed":
            False,

        "status":
            "FAIL_REGEN_MANUFACTURING_TOLERANCE_QUALIFICATION",

        "blockers":
            blockers,

        "case_count":
            0,

        "failed_case_count":
            0,

        "cases":
            cases,

        "required_dimensions":
            list(
                required_dimensions
            ),

        "policy_status":
            None,

        "process":
            None,

        "source":
            None,
    }

    policy = results.get(
        "regen_manufacturing_tolerance_policy"
    )

    if not isinstance(
        policy,
        dict,
    ):

        blockers.append(
            "Authoritative manufacturing tolerance policy is unavailable."
        )

        report[
            "status"
        ] = (
            "UNPROVEN_REGEN_MANUFACTURING_TOLERANCE_QUALIFICATION"
        )

        return report

    policy_status = str(
        policy.get("status")
        or
        ""
    ).strip().upper()

    process_name = str(
        policy.get("process")
        or
        ""
    ).strip()

    source_name = str(
        policy.get("source")
        or
        ""
    ).strip()

    report[
        "policy_status"
    ] = policy_status

    report[
        "process"
    ] = process_name or None

    report[
        "source"
    ] = source_name or None

    if (
        policy_status
        not in
        authoritative_modes
    ):

        blockers.append(
            "Manufacturing tolerance policy is not authoritative."
        )

    if not source_name:

        blockers.append(
            "Manufacturing tolerance policy has no provenance source."
        )

    if (
        policy_status
        ==
        "SOURCED_PROCESS_CAPABILITY"
        and
        not process_name
    ):

        blockers.append(
            "Sourced process capability has no manufacturing process identifier."
        )

    dimensions = policy.get(
        "dimensions"
    )

    if not isinstance(
        dimensions,
        dict,
    ):

        blockers.append(
            "Manufacturing tolerance policy has no dimensional capability map."
        )

        dimensions = {}

    nominal_sources = []

    if isinstance(
        geometry,
        dict,
    ):

        nominal_sources.append(
            geometry
        )

    nominal_sources.append(
        results
    )

    def number_from_sources(
        key,
    ):
        for source_map in nominal_sources:

            value = source_map.get(
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

    nominal = {}
    tolerances = {}

    for dimension in required_dimensions:

        value = number_from_sources(
            dimension
        )

        if (
            value is None
            or
            value <= 0.0
        ):

            blockers.append(
                f"Nominal {dimension} is unavailable or non-positive."
            )

        else:

            nominal[
                dimension
            ] = value

        specification = dimensions.get(
            dimension
        )

        if not isinstance(
            specification,
            dict,
        ):

            blockers.append(
                f"Required dimensional tolerance is unavailable: {dimension}."
            )

            continue

        parsed = {}

        for side in (
            "minus",
            "plus",
        ):

            raw = specification.get(
                side
            )

            try:
                parsed_value = float(
                    raw
                )

            except (
                TypeError,
                ValueError,
            ):

                blockers.append(
                    f"{dimension} {side} tolerance is invalid."
                )

                continue

            if (
                not math.isfinite(
                    parsed_value
                )
                or
                parsed_value < 0.0
            ):

                blockers.append(
                    f"{dimension} {side} tolerance must be a finite non-negative SI value."
                )

                continue

            parsed[
                side
            ] = parsed_value

        if (
            set(
                parsed
            )
            ==
            {
                "minus",
                "plus",
            }
        ):

            tolerances[
                dimension
            ] = parsed

    if blockers:

        return report

    nominal_width = nominal[
        "coolant_channel_width"
    ]

    nominal_rib = nominal[
        "rib_width"
    ]

    nominal_pitch = (
        nominal_width
        +
        nominal_rib
    )

    nominal_fit_ratio = number_from_sources(
        "fit_ratio"
    )

    def engineering_pass(
        validation,
    ):
        if isinstance(
            validation,
            bool,
        ):
            return validation

        if not isinstance(
            validation,
            dict,
        ):
            return False

        for key in (
            "passed",
            "pass",
            "validation_pass",
            "candidate_validation_pass",
            "regen_candidate_validation_pass",
        ):

            if key not in validation:
                continue

            value = validation.get(
                key
            )

            if isinstance(
                value,
                bool,
            ):
                return value

        status = str(
            validation.get("status")
            or
            validation.get(
                "validation_status"
            )
            or
            validation.get(
                "regen_candidate_validator_status"
            )
            or
            ""
        ).strip().upper()

        fail_count = (
            validation.get(
                "fail_count"
            )
        )

        if fail_count is None:
            fail_count = validation.get(
                "validation_fail_count"
            )

        try:
            fail_count = int(
                fail_count or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            fail_count = 1

        return (
            status.startswith(
                "PASS"
            )
            and
            fail_count == 0
        )

    def validation_blockers(
        validation,
    ):
        if not isinstance(
            validation,
            dict,
        ):
            return []

        for key in (
            "blockers",
            "failure_reasons",
            "fail_reasons",
            "reasons",
        ):

            value = validation.get(
                key
            )

            if isinstance(
                value,
                (
                    list,
                    tuple,
                ),
            ):
                return [
                    str(
                        item
                    )
                    for item
                    in value
                ]

        return []

    # ------------------------------------------------------------
    # COMPLETE 4-DIMENSIONAL CORNER ENVELOPE
    # ------------------------------------------------------------

    for signs in product(
        (
            "minus",
            "plus",
        ),
        repeat=len(
            required_dimensions
        ),
    ):

        adverse_geometry = dict(
            geometry
            if isinstance(
                geometry,
                dict,
            )
            else
            {}
        )

        adverse_results = dict(
            results
        )

        applied = {}

        invalid_geometry = False

        for dimension, side in zip(
            required_dimensions,
            signs,
        ):

            magnitude = tolerances[
                dimension
            ][
                side
            ]

            delta = (
                -magnitude
                if side == "minus"
                else magnitude
            )

            actual = (
                nominal[
                    dimension
                ]
                +
                delta
            )

            applied[
                dimension
            ] = {
                "side":
                    side,

                "delta":
                    delta,

                "value":
                    actual,
            }

            adverse_geometry[
                dimension
            ] = actual

            adverse_results[
                dimension
            ] = actual

            if actual <= 0.0:

                invalid_geometry = True

        width = adverse_geometry[
            "coolant_channel_width"
        ]

        height = adverse_geometry[
            "coolant_channel_height"
        ]

        rib = adverse_geometry[
            "rib_width"
        ]

        if (
            width > 0.0
            and
            height > 0.0
        ):

            aspect_ratio = (
                height
                /
                width
            )

            adverse_geometry[
                "channel_aspect_ratio"
            ] = aspect_ratio

            adverse_geometry[
                "aspect_ratio"
            ] = aspect_ratio

            adverse_results[
                "channel_aspect_ratio"
            ] = aspect_ratio

            adverse_results[
                "aspect_ratio"
            ] = aspect_ratio

        if (
            width > 0.0
            and
            rib > 0.0
        ):

            actual_pitch = (
                width
                +
                rib
            )

            cooling_coverage = (
                width
                /
                actual_pitch
            )

            adverse_geometry[
                "effective_rib_width"
            ] = rib

            adverse_geometry[
                "cooling_coverage"
            ] = cooling_coverage

            adverse_geometry[
                "channel_pitch"
            ] = actual_pitch

            adverse_results[
                "effective_rib_width"
            ] = rib

            adverse_results[
                "cooling_coverage"
            ] = cooling_coverage

            adverse_results[
                "channel_pitch"
            ] = actual_pitch

            if (
                nominal_fit_ratio is not None
                and
                nominal_pitch > 0.0
            ):

                adverse_fit_ratio = (
                    nominal_fit_ratio
                    *
                    nominal_pitch
                    /
                    actual_pitch
                )

                adverse_geometry[
                    "fit_ratio"
                ] = adverse_fit_ratio

                adverse_results[
                    "fit_ratio"
                ] = adverse_fit_ratio

        manufacturability = (
            evaluate_manufacturability_geometry(
                adverse_geometry
            )
        )

        manufacturing_pass = bool(
            manufacturability.get(
                "passed",
                False,
            )
        )

        manufacturing_blockers = [
            str(
                item
            )
            for item
            in (
                manufacturability.get(
                    "blockers"
                )
                or
                []
            )
        ]

        if invalid_geometry:

            manufacturing_pass = False

            manufacturing_blockers.append(
                "Tolerance envelope produced a non-positive physical dimension."
            )

        if callable(
            engineering_validator
        ):

            try:

                engineering_validation = (
                    engineering_validator(
                        adverse_geometry,
                        adverse_results,
                    )
                )

                engineering_validation_pass = (
                    engineering_pass(
                        engineering_validation
                    )
                )

                engineering_validation_blockers = (
                    validation_blockers(
                        engineering_validation
                    )
                )


            except Exception as exc:

                engineering_validation = {
                    "status":
                        "FAIL_ENGINEERING_VALIDATOR_EXCEPTION",

                    "error":
                        repr(
                            exc
                        ),
                }

                engineering_validation_pass = False

                engineering_validation_blockers = [
                    "Existing candidate validator could not evaluate a tolerance-envelope case."
                ]


        else:

            engineering_validation = None

            engineering_validation_pass = False

            engineering_validation_blockers = [
                "Existing engineering validator callback is unavailable."
            ]

        case_pass = (
            manufacturing_pass
            and
            engineering_validation_pass
        )

        cases.append(
            {
                "case_index":
                    len(
                        cases
                    )
                    +
                    1,

                "applied_tolerances":
                    applied,

                "geometry":
                    {
                        key:
                            adverse_geometry.get(
                                key
                            )
                        for key in (
                            "coolant_channel_width",
                            "coolant_channel_height",
                            "rib_width",
                            "effective_rib_width",
                            "hot_gas_wall_thickness",
                            "aspect_ratio",
                            "cooling_coverage",
                            "fit_ratio",
                        )
                    },

                "manufacturability_pass":
                    manufacturing_pass,

                "manufacturability_status":
                    manufacturability.get(
                        "status"
                    ),

                "manufacturability_blockers":
                    manufacturing_blockers,

                "engineering_validation_pass":
                    engineering_validation_pass,

                "engineering_validation_blockers":
                    engineering_validation_blockers,

                "passed":
                    case_pass,
            }
        )

    failed_cases = [
        case
        for case in cases
        if not case[
            "passed"
        ]
    ]

    report[
        "case_count"
    ] = len(
        cases
    )

    report[
        "failed_case_count"
    ] = len(
        failed_cases
    )

    if failed_cases:

        blockers.append(
            f"{len(failed_cases)} of {len(cases)} required manufacturing tolerance corner cases failed."
        )

        return report

    report[
        "passed"
    ] = True

    report[
        "status"
    ] = (
        "PASS_REGEN_MANUFACTURING_TOLERANCE_QUALIFICATION"
    )

    return report


def attach_manufacturability_gate(results: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_manufacturability_geometry(geometry)

    results["phase_16q3_manufacturability_status"] = verdict["status"]
    results["phase_16q3_manufacturability_pass"] = verdict["passed"]
    results["phase_16q3_manufacturability_blockers"] = verdict["blockers"]
    results["phase_16q3_manufacturability_warnings"] = verdict["warnings"]
    results["phase_16q3_channel_aspect_ratio"] = verdict["aspect_ratio"]

    if not verdict["passed"]:
        results["regen_geometry_status"] = "FAIL"
        results["geometry_status"] = "FAIL"
        results["final_regen_design_verdict"] = "FAIL_REGEN_MANUFACTURABILITY_GEOMETRY_GATE"

    return results
