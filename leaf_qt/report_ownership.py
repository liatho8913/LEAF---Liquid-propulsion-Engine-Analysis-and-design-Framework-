"""
Canonical LEAF report-content owner.

This module owns:
- selection of engineering results exposed through reports
- report text composition and formatting
- report-viewer content bundles

It does not own:
- runtime event routing
- notification delivery
- engineering physics
- validation execution
- report persistence/export transport

Runtime report-message routing is owned separately by
leaf_qt.runtime.report_router as part of the LEAF runtime layer.
"""

from station_report_builder import (
    build_station_table_text,
    build_station_validation_table_text,
    build_station_diagnostic_table_text,
)
from variable_registry import (
    get_scalar_output_keys,
    get_validation_output_keys,
    get_diagnostic_output_keys,
    get_recommendation_output_keys,
    get_axial_report_keys,
    get_internal_output_keys,
    get_label,
    get_symbol,
    get_unit,
)


def _safe_results(results):
    return results if isinstance(results, dict) else {}


def _filter_results(results, keys):
    results = _safe_results(results)
    key_set = set(keys)

    return {
        key: value
        for key, value in results.items()
        if key in key_set and value is not None
    }


def get_main_output_results(results):
    return _filter_results(results, get_scalar_output_keys())


def get_validation_results(results):
    return _filter_results(results, get_validation_output_keys())


def get_diagnostic_results(results):
    return _filter_results(results, get_diagnostic_output_keys())


def get_recommendation_results(results):
    return _filter_results(results, get_recommendation_output_keys())


def get_axial_report_results(results):
    return _filter_results(results, get_axial_report_keys())


def get_internal_results(results):
    return _filter_results(results, get_internal_output_keys())


def format_value(value):
    if isinstance(value, float):
        return f"{value:.6g}"

    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)

    if isinstance(value, dict):
        return "\n".join(f"{key}: {val}" for key, val in value.items())

    return str(value)


def format_result_line(key, value):
    label = get_label(key)
    symbol = get_symbol(key)
    unit = get_unit(key)
    value_text = format_value(value)

    name = label

    if symbol:
        name += f" ({symbol})"

    if unit:
        return f"{name}: {value_text} {unit}"

    return f"{name}: {value_text}"


def build_named_report(title, results):
    lines = []
    lines.append(title)
    lines.append("=" * len(title))
    lines.append("")

    if not results:
        lines.append("No entries available.")
        return "\n".join(lines)

    for key, value in results.items():
        lines.append(format_result_line(key, value))

    return "\n".join(lines)


def build_foundation_attachment_audit_report(results):
    results = _safe_results(results)

    lines = []
    lines.append("LEAF FOUNDATION ATTACHMENT AUDIT")
    lines.append("================================")
    lines.append("")

    pipeline_status = results.get(
        "foundation_attachment_pipeline_status",
        "UNKNOWN",
    )

    benchmark_case = results.get(
        "foundation_attachment_benchmark_case",
        "UNKNOWN",
    )

    started_at = results.get("foundation_attachment_pipeline_started_at", "N/A")
    completed_at = results.get("foundation_attachment_pipeline_completed_at", "N/A")

    lines.append(f"Pipeline status: {pipeline_status}")
    lines.append(f"Benchmark case: {benchmark_case}")
    lines.append(f"Started at: {started_at}")
    lines.append(f"Completed at: {completed_at}")
    lines.append("")

    summary = results.get("foundation_attachment_summary", {})

    if summary:
        lines.append("Summary:")
        lines.append(f"- Total layers: {summary.get('total', 0)}")
        lines.append(f"- Passed: {summary.get('passed', 0)}")
        lines.append(f"- Skipped: {summary.get('skipped', 0)}")
        lines.append(f"- Returned None: {summary.get('returned_none', 0)}")
        lines.append(
            f"- Failed non-blocking: {summary.get('failed_non_blocking', 0)}"
        )
        lines.append("")
    else:
        lines.append("No attachment summary is available.")
        lines.append("")

    audit_rows = results.get("foundation_attachment_audit", [])

    if not audit_rows:
        lines.append("No attachment audit rows are available.")
        return "\n".join(lines)

    lines.append("Layer Events:")
    lines.append("")

    for row in audit_rows:
        if not isinstance(row, dict):
            continue

        layer = row.get("layer", "unknown_layer")
        status = row.get("status", "UNKNOWN")
        message = row.get("message", "")
        error_type = row.get("error_type", "")
        timestamp = row.get("timestamp", "")

        lines.append(f"[{status}] {layer}")

        if timestamp:
            lines.append(f"  Time: {timestamp}")

        if message:
            lines.append(f"  Message: {message}")

        if error_type:
            lines.append(f"  Error type: {error_type}")

        lines.append("")

    failed_rows = [
        row for row in audit_rows
        if isinstance(row, dict)
        and row.get("status") == "FAILED_NON_BLOCKING"
    ]

    if failed_rows:
        lines.append("Non-Blocking Failure Explanation:")
        lines.append(
            "- The core calculation completed, but one or more optional "
            "foundation/report layers failed."
        )
        lines.append(
            "- These failures should be fixed, but they do not invalidate "
            "the numerical engine solve by themselves."
        )
        lines.append(
            "- Treat affected reports as incomplete until the failed layer is repaired."
        )
        lines.append("")

    return "\n".join(lines)


def build_main_output_report(results):
    return build_named_report(
        "LEAF MAIN OUTPUT REPORT",
        get_main_output_results(results),
    )


def build_validation_report(results):
    return build_named_report(
        "LEAF VALIDATION REPORT",
        get_validation_results(results),
    )


def build_diagnostics_report(results):
    return build_named_report(
        "LEAF DIAGNOSTICS REPORT",
        get_diagnostic_results(results),
    )


def build_recommendation_report(results):
    return build_named_report(
        "LEAF RECOMMENDED DESIGN REPORT",
        get_recommendation_results(results),
    )


def build_axial_report(results):
    results = _safe_results(results)

    lines = []
    lines.append("LEAF AXIAL THERMAL REPORT")
    lines.append("=========================")
    lines.append("")

    axial_results = get_axial_report_results(results)

    if axial_results:
        for key, value in axial_results.items():
            if key in (
                "design_iteration_narrative",
                "design_iteration_narrative_text",
                "regen_optimisation_proof_text",
                "regen_optimisation_proof_lines",
                "failure_root_cause_text",
                "failure_root_cause_items",
                "before_after_comparison_text",
                "before_after_comparison_rows",
            ):
                continue

            lines.append(format_result_line(key, value))
    else:
        lines.append("No axial/report-only scalar entries available.")

    narrative_text = results.get("design_iteration_narrative_text")
    proof_text = (
            results.get("optimisation_proof_text")
            or results.get("regen_optimisation_proof_text")
    )

    candidate_ranking_text = results.get("optimisation_candidate_ranking_text")
    score_evidence_text = results.get("optimisation_score_evidence_text")
    root_cause_text = (
            results.get("root_cause_ownership_report_text")
            or results.get("failure_root_cause_owner_text")
            or results.get("failure_root_cause_text")
    )
    before_after_text = results.get("before_after_comparison_text")

    if narrative_text:
        lines.append("")
        lines.append("")
        lines.append(narrative_text)

    if proof_text:
        lines.append("")
        lines.append("")
        lines.append(proof_text)

    if candidate_ranking_text:
        lines.append("")
        lines.append("")
        lines.append(candidate_ranking_text)

    if score_evidence_text:
        lines.append("")
        lines.append("")
        lines.append(score_evidence_text)

    if root_cause_text:
        lines.append("")
        lines.append("")
        lines.append(root_cause_text)

    if before_after_text:
        lines.append("")
        lines.append("")
        lines.append(before_after_text)

    thermal_station_table_text = build_station_table_text(results)
    validation_station_table_text = build_station_validation_table_text(results)
    diagnostic_station_table_text = build_station_diagnostic_table_text(results)

    if thermal_station_table_text:
        lines.append("")
        lines.append("")
        lines.append(thermal_station_table_text)

    if validation_station_table_text:
        lines.append("")
        lines.append("")
        lines.append(validation_station_table_text)

    if diagnostic_station_table_text:
        lines.append("")
        lines.append("")
        lines.append(diagnostic_station_table_text)

    return "\n".join(lines)


def build_development_evidence_report(results):
    results = _safe_results(results)

    lines = []
    lines.append("LEAF DEVELOPMENT EVIDENCE REPORT")
    lines.append("================================")
    lines.append("")

    dashboard_text = results.get("report_dashboard_text")

    if dashboard_text:
        lines.append(dashboard_text)
        lines.append("")

    lines.append("Purpose:")
    lines.append("- Show what LEAF calculated.")
    lines.append("- Show what failed and why.")
    lines.append("- Show what improved.")
    lines.append("- Show what LEAF recommends next.")
    lines.append("- Show foundation/report attachment integrity.")
    lines.append("- Preserve a controlled raw appendix without polluting Main Outputs.")
    lines.append("")

    lines.append(build_main_output_report(results))
    lines.append("")
    lines.append(build_validation_report(results))
    lines.append("")
    lines.append(build_diagnostics_report(results))
    lines.append("")
    lines.append(build_foundation_attachment_audit_report(results))
    lines.append("")

    narrative_text = results.get("design_iteration_narrative_text")
    history_narrative_text = results.get("design_history_narrative_text")

    proof_text = (
            results.get("optimisation_proof_text")
            or results.get("regen_optimisation_proof_text")
    )

    candidate_ranking_text = results.get("optimisation_candidate_ranking_text")
    score_evidence_text = results.get("optimisation_score_evidence_text")
    best_candidate_reason = results.get("optimisation_best_candidate_reason")
    regression_gate_reason = results.get("optimisation_regression_gate_reason")
    optimisation_ownership_report_text = results.get(
        "optimisation_ownership_report_text"
    )
    root_cause_text = (
            results.get("failure_root_cause_owner_text")
            or results.get("failure_root_cause_text")
    )
    corrective_action_text = results.get("corrective_action_priority_text")
    root_cause_ownership_text = results.get("root_cause_ownership_report_text")
    recommendation_text = (
            results.get("recommendation_owner_text")
            or results.get("recommendation_explanation_text")
    )
    before_after_text = results.get("before_after_comparison_text")
    regression_text = results.get("foundation_regression_text")
    result_key_audit_text = results.get("foundation_result_key_audit_text")
    output_ownership_audit_text = results.get("output_ownership_audit_text")
    benchmark_text = results.get("benchmark_report_text")
    reproduction_text = results.get("engine_reproduction_report_text")

    thermal_station_table_text = build_station_table_text(results)
    validation_station_table_text = build_station_validation_table_text(results)
    diagnostic_station_table_text = build_station_diagnostic_table_text(results)

    for section_text in (
            narrative_text,
            history_narrative_text,
            optimisation_ownership_report_text,
            proof_text,
            candidate_ranking_text,
            score_evidence_text,
            best_candidate_reason,
            regression_gate_reason,
            root_cause_ownership_text,
            root_cause_text,
            corrective_action_text,
            recommendation_text,
            before_after_text,
            thermal_station_table_text,
            regression_text,
            output_ownership_audit_text,
            result_key_audit_text,
            benchmark_text,
            reproduction_text,
            validation_station_table_text,
            diagnostic_station_table_text,
    ):
        if section_text:
            lines.append(section_text)
            lines.append("")

    lines.append("CONTROLLED RAW APPENDIX")
    lines.append("======================")
    lines.append("")

    for key in sorted(results.keys()):
        value = results.get(key)

        if value is None:
            continue

        if key.endswith("_text"):
            continue

        lines.append(format_result_line(key, value))

    return "\n".join(lines)


def build_report_viewer_bundle(results):
    results = _safe_results(results)

    return {
        "Dashboard": results.get("report_dashboard_text", "No dashboard available."),
        "Main Output Report": build_main_output_report(results),
        "Validation Report": build_validation_report(results),
        "Regen Source Validation Gate": build_regen_source_validation_gate_report(results),
        "Regen Provenance Report": build_regen_provenance_report(results),
        "Regen Property Table Report": build_regen_property_table_report(results),
        "Regen Validation Master Gate": build_regen_validation_master_gate_report(results),
        "Diagnostics Report": build_diagnostics_report(results),
        "Recommendation Report": build_recommendation_report(results),
        "Recommendation Owner Report": build_recommendation_owner_report(results),
        "Recommendation Ownership Final Audit": build_recommendation_ownership_final_audit_report(results),
        "Axial Thermal Report": build_axial_report(results),
        "Development Evidence Report": build_development_evidence_report(results),
        "Design History": build_design_history_report(results),
        "Optimisation Ownership Report": build_optimisation_ownership_report(results),
        "Failure Root Cause Owner Report": build_failure_root_cause_owner_report(results),
        "Corrective Action Priority Report": build_corrective_action_priority_report(results),
        "Root Cause Ownership Report": build_root_cause_ownership_report(results),
        "Foundation Attachment Audit": build_foundation_attachment_audit_report(results),
        "Foundation Regression Report": build_regression_report(results),
        "Output Ownership Audit": build_output_ownership_audit_report(results),
        "Output Visibility Architecture Audit": build_output_visibility_architecture_report(results),
        "Foundation Result Key Audit": build_result_key_audit_report(results),
        "Benchmark Comparison Report": build_benchmark_report(results),
        "Engine Reproduction Report": build_engine_reproduction_report(results),
        "Stage U Regen Completion Audit": build_regen_completion_audit_report(results),
        "Stage V.1 Regen Scalability Framework": build_regen_scalability_report(results),
        "Stage V.2 Regen Scalability Report Ownership": build_regen_scalability_report_owner_report(results),
        "Stage V.3 Regen Scalability Failure Ownership": build_regen_scalability_failure_owner_report(results),
        "Stage V.4 Regen Scalability Master Gate": build_regen_scalability_master_gate_report(results),
        "Stage V.5 Regen Scalability Completion Audit": build_regen_scalability_completion_audit_report(results),
        "Stage W.1 Real Engine Benchmarking Framework": build_real_engine_benchmarking_framework_report(results),
        "Stage W.2 Public Benchmark Source Ownership": build_real_engine_benchmark_source_owner_report(results),
        "Stage W.3 Numeric Benchmark Band Ownership": build_real_engine_benchmark_band_owner_report(results),
        "Stage W.4 Real Engine Benchmark Failure Ownership": build_real_engine_benchmark_failure_owner_report(results),
        "Stage W.5 Real Engine Benchmark Master Gate": build_real_engine_benchmark_master_gate_report(results),
        "Stage W.6 Real Engine Benchmark Completion Audit": build_real_engine_benchmark_completion_audit_report(
            results),
        "Phase 10A Solver Integration Planning": build_phase_10a_solver_integration_planning_report(results),
        "Phase 10B.1 Material Property Consumption Audit": build_phase_10b1_material_property_consumption_audit_report(results),
        "Phase 10B.2 Material Thermal Conductivity Integration": build_phase_10b2_material_thermal_conductivity_integration_report(results),
        "Phase 10B.3 Material Specific Heat Integration": build_phase_10b3_material_specific_heat_integration_report(results),
        "Phase 10B.4 Material Density Integration": build_phase_10b4_material_density_integration_report(results),
        "Phase 10B.5 Material Temperature Limit Integration": build_phase_10b5_material_temperature_limit_integration_report(results),
        "Phase 10B.6 Material Strength Limit Integration": build_phase_10b6_material_strength_limit_integration_report(results),
        "Phase 10B.7 Material Integration Validation": build_phase_10b7_material_integration_validation_report(results),
        "Phase 10B.8 Material Integration Completion Audit": build_phase_10b8_material_integration_completion_audit_report(results),
        "Phase 10C.1 Coating Property Consumption Audit": build_phase_10c1_coating_property_consumption_audit_report(results),
        "Phase 10C.2 Coating Thermal Conductivity Integration": build_phase_10c2_coating_thermal_conductivity_integration_report(results),
        "Phase 10C.3 Coating Thickness Integration": build_phase_10c3_coating_thickness_integration_report(results),
        "Phase 10C.4 Coating Thermal Resistance Integration": build_phase_10c4_coating_thermal_resistance_integration_report(results),
        "Phase 10C.5 Coating Temperature Limit Integration": build_phase_10c5_coating_temperature_limit_integration_report(results),
        "Phase 10C.6 Bond Coat Integration": build_phase_10c6_bond_coat_integration_report(results),
        "Phase 10C.7 Coating Integration Validation": build_phase_10c7_coating_integration_validation_report(results),
        "Phase 10C.8 Coating Integration Completion Audit": build_phase_10c8_coating_integration_completion_audit_report(results),
        "Phase 10D.1 Temperature Dependency Discovery Audit": build_phase_10d1_temperature_dependency_discovery_audit_report(results),
        "Phase 10D.2 Material Conductivity Consumption Audit": build_phase_10d2_material_conductivity_consumption_audit_report(results),
        "Phase 10D.3 Specific Heat Consumption Audit": build_phase_10d3_specific_heat_consumption_audit_report(results),
        "Phase 10D.4 Density and Coolant Property Consumption Audit": build_phase_10d4_density_coolant_property_consumption_audit_report(results),
        "Phase 10D.5 Coating Thermal Consumption Audit": build_phase_10d5_coating_thermal_consumption_audit_report(results),
        "Foundation Verification Harness": build_foundation_verification_report(results),
        "Foundation Save/Load Verification": build_foundation_save_load_report(results),
        "Foundation UI Launch Verification": build_foundation_ui_launch_report(results),
        "Foundation Final Sign-Off": build_foundation_final_signoff_report(results),
        "Foundation Completion Handover": build_foundation_completion_handover_report(results),
        "Phase 10D.6 Bond-Coat Consumption Audit": build_phase_10d6_bond_coat_consumption_audit_report(results),
        "Phase 10D.7 Temperature-Dependent Solver Completion Audit": build_phase_10d7_temperature_dependent_solver_completion_audit_report(
            results),
        "Phase 11A.1 Regen Geometry Constraint Discovery Audit": build_phase_11a1_regen_geometry_constraint_discovery_audit_report(
            results),
        "Phase 11A.2 Regen Geometry Constraint Validation": build_phase_11a2_regen_geometry_constraint_validation_report(
            results),
        "Phase 11A.3 Regen Geometry Failure Explanation": build_phase_11a3_regen_geometry_failure_explanation_report(
            results),
        "Phase 11A.4 Regen Geometry Recommendation Engine V1": build_phase_11a4_regen_geometry_recommendation_engine_report(
            results),
        "Phase 11A.5 Apply Recommended Geometry": build_phase_11a5_regen_geometry_apply_recommendation_report(results),
        "Phase 11A.6 Regen Geometry Output Architecture": build_phase_11a6_regen_geometry_output_architecture_report(
            results),
        "Phase 11A.8 Regen Geometry Candidate Acceptance": build_phase_11a8_regen_geometry_candidate_acceptance_report(
            results),
    }

def _u_value(results, *keys):
    for key in keys:
        value = results.get(key)
        if value is not None:
            return value
    return None


def _u_short(value, limit=240):
    if value is None:
        return "Not available"

    text = " ".join(
        str(value).split()
    )

    return (
        text
        if len(text) <= limit
        else text[:limit - 3] + "..."
    )


def _u_num(value, unit=None):
    if value is None:
        text = "Not available"

    elif isinstance(value, bool):
        text = (
            "Yes"
            if value
            else "No"
        )

    elif isinstance(
        value,
        (int, float),
    ):
        text = f"{value:.6g}"

    else:
        text = _u_short(value)

    return (
        f"{text} {unit}"
        if unit
        else text
    )


def _u_status(value):
    return (
        "Not evaluated"
        if value is None
        else
        str(value)
        .replace("_", " ")
        .strip()
        .title()
    )


def _u_line(
    label,
    value,
    unit=None,
):
    return (
        f"{label}: "
        f"{_u_num(value, unit)}"
    )


def _u_doc(
    title,
    purpose,
    sections,
):
    lines = [
        title,
        "=" * len(title),
        purpose,
    ]

    for (
        section,
        rows,
    ) in sections:

        rows = [
            str(row)

            for row in rows

            if (
                row is not None
                and
                str(row).strip()
            )
        ]

        if not rows:
            continue

        lines += [
            "",
            section,
            "-" * len(section),
            *rows,
        ]

    return (
        "\n".join(lines).rstrip()
        +
        "\n"
    )


def _u_limits(results):
    limitations = []

    material_mode = _u_value(
        results,
        "material_source_provenance_mode",
        "material_aware_combined_source_mode",
    )

    coating_mode = _u_value(
        results,
        "coating_source_provenance_mode",
        "active_coating_source_mode",
    )

    coating_mode_upper = str(
        coating_mode
        or
        ""
    ).upper()

    thermal_margin = _u_value(
        results,
        "regen_axial_material_temperature_margin",
        "best_full_engine_regen_thermal_margin",
    )

    if (
        material_mode is not None

        and

        "SOURCED_VALIDATION"
        not in
        str(material_mode).upper()
    ):
        limitations.append(
            "Material validation does not yet have a complete "
            "sourced-validation dataset."
        )

    if (
        coating_mode is not None

        and

        coating_mode_upper
        not in (
            "NO_COATING_MODE",
            "NOT_APPLICABLE",
            "SOURCED_VALIDATION_MODE",
        )
    ):
        limitations.append(
            "Coating validation relies on incomplete or "
            "placeholder source data."
        )

    if (
        results.get(
            "material_source_has_citation"
        )
        is False
    ):
        limitations.append(
            "The active material record does not provide a "
            "complete source citation."
        )

    if (
        results.get(
            "material_source_has_temperature_table"
        )
        is False
    ):
        limitations.append(
            "The active material record does not provide a "
            "complete temperature-dependent property table."
        )

    if (
        results.get(
            "coating_source_has_citation"
        )
        is False

        and

        coating_mode_upper
        not in (
            "NO_COATING_MODE",
            "NOT_APPLICABLE",
        )
    ):
        limitations.append(
            "The active coating record does not provide a "
            "complete source citation."
        )

    if (
        results.get(
            "coating_source_has_temperature_table"
        )
        is False

        and

        coating_mode_upper
        not in (
            "NO_COATING_MODE",
            "NOT_APPLICABLE",
        )
    ):
        limitations.append(
            "The active coating record does not provide a "
            "complete temperature-dependent property table."
        )

    if (
        isinstance(
            thermal_margin,
            (int, float),
        )

        and

        thermal_margin < 0
    ):
        limitations.append(
            "The calculated material temperature margin is "
            f"negative ({thermal_margin:.3f} K)."
        )

    return (
        limitations
        or
        [
            "No additional high-level evidence limitation "
            "was identified for the current result state."
        ]
    )


def _build_user_overview_report(results):
    return _u_doc(
        "LEAF ENGINEERING OVERVIEW",
        (
            "A concise summary of the solved engine, its principal "
            "engineering results, and the limitations that affect "
            "their interpretation."
        ),
        [
            (
                "Engine configuration",
                [
                    _u_line(
                        "Chamber pressure",
                        results.get(
                            "chamber_pressure"
                        ),
                        "Pa",
                    ),
                    _u_line(
                        "Total mass flow",
                        results.get(
                            "mass_flow_rate"
                        ),
                        "kg/s",
                    ),
                    _u_line(
                        "Mixture ratio",
                        results.get(
                            "mixture_ratio"
                        ),
                    ),
                    _u_line(
                        "Expansion ratio",
                        results.get(
                            "expansion_ratio"
                        ),
                    ),
                ],
            ),
            (
                "Headline performance",
                [
                    _u_line(
                        "Thrust",
                        results.get(
                            "thrust"
                        ),
                        "N",
                    ),
                    _u_line(
                        "Specific impulse",
                        results.get(
                            "specific_impulse"
                        ),
                        "s",
                    ),
                    _u_line(
                        "Characteristic velocity",
                        results.get(
                            "characteristic_velocity"
                        ),
                        "m/s",
                    ),
                ],
            ),
            (
                "Engineering state",
                [
                    (
                        "Chamber geometry: "
                        +
                        _u_status(
                            results.get(
                                "chamber_geometry_status"
                            )
                        )
                    ),
                    (
                        "Nozzle geometry: "
                        +
                        _u_status(
                            _u_value(
                                results,
                                "rao_nozzle_status",
                                "nozzle_geometry_status",
                            )
                        )
                    ),
                    (
                        "Regenerative cooling: "
                        +
                        _u_status(
                            _u_value(
                                results,
                                "regen_overall_status",
                                "best_full_engine_regen_status",
                            )
                        )
                    ),
                ],
            ),
            (
                "Evidence limitations",
                [
                    f"- {item}"
                    for item in _u_limits(
                        results
                    )
                ],
            ),
        ],
    )


def _build_user_performance_geometry_report(results):
    return _u_doc(
        "LEAF PERFORMANCE & GEOMETRY",
        (
            "Principal propulsion performance and canonical "
            "chamber/nozzle geometry for the solved design."
        ),
        [
            (
                "Performance",
                [
                    _u_line(
                        "Thrust",
                        results.get(
                            "thrust"
                        ),
                        "N",
                    ),
                    _u_line(
                        "Specific impulse",
                        results.get(
                            "specific_impulse"
                        ),
                        "s",
                    ),
                    _u_line(
                        "Effective exhaust velocity",
                        _u_value(
                            results,
                            "effective_exhaust_velocity",
                            "exhaust_velocity",
                        ),
                        "m/s",
                    ),
                    _u_line(
                        "Characteristic velocity",
                        results.get(
                            "characteristic_velocity"
                        ),
                        "m/s",
                    ),
                    _u_line(
                        "Total mass flow",
                        results.get(
                            "mass_flow_rate"
                        ),
                        "kg/s",
                    ),
                    _u_line(
                        "Fuel mass flow",
                        results.get(
                            "fuel_mass_flow_rate"
                        ),
                        "kg/s",
                    ),
                    _u_line(
                        "Oxidizer mass flow",
                        results.get(
                            "oxidizer_mass_flow_rate"
                        ),
                        "kg/s",
                    ),
                    _u_line(
                        "Mixture ratio",
                        results.get(
                            "mixture_ratio"
                        ),
                    ),
                ],
            ),
            (
                "Chamber geometry",
                [
                    _u_line(
                        "Chamber diameter",
                        results.get(
                            "chamber_diameter"
                        ),
                        "m",
                    ),
                    _u_line(
                        "Chamber radius",
                        results.get(
                            "chamber_radius"
                        ),
                        "m",
                    ),
                    _u_line(
                        "Chamber total length",
                        results.get(
                            "chamber_total_length"
                        ),
                        "m",
                    ),
                    _u_line(
                        "Chamber volume",
                        results.get(
                            "chamber_volume"
                        ),
                        "m³",
                    ),
                    _u_line(
                        "Contraction ratio",
                        results.get(
                            "chamber_contraction_ratio"
                        ),
                    ),
                    _u_line(
                        "Converging half-angle",
                        results.get(
                            "chamber_converging_half_angle_deg"
                        ),
                        "deg",
                    ),
                ],
            ),
            (
                "Nozzle geometry",
                [
                    _u_line(
                        "Throat area",
                        results.get(
                            "throat_area"
                        ),
                        "m²",
                    ),
                    _u_line(
                        "Exit area",
                        results.get(
                            "exit_area"
                        ),
                        "m²",
                    ),
                    _u_line(
                        "Exit radius",
                        results.get(
                            "exit_radius"
                        ),
                        "m",
                    ),
                    _u_line(
                        "Expansion ratio",
                        results.get(
                            "expansion_ratio"
                        ),
                    ),
                    _u_line(
                        "Exit pressure",
                        results.get(
                            "exit_pressure"
                        ),
                        "Pa",
                    ),
                ],
            ),
        ],
    )


def _build_user_thermal_cooling_report(results):
    margin = _u_value(
        results,
        "regen_axial_material_temperature_margin",
        "best_full_engine_regen_thermal_margin",
    )

    min_re = _u_value(
        results,
        "regen_axial_min_reynolds_number",
        "best_full_engine_regen_min_reynolds",
        "coolant_reynolds_number",
    )

    interpretation = []

    if isinstance(
        margin,
        (int, float),
    ):
        interpretation.append(
            (
                "- Material temperature margin is negative; "
                "the current thermal design does not satisfy "
                "this criterion."
            )
            if margin < 0
            else
            (
                "- Material temperature margin is positive for "
                "the reported criterion."
            )
        )

    if min_re is not None:
        interpretation.append(
            "- Minimum reported coolant Reynolds number: "
            f"{_u_num(min_re)}."
        )

    return _u_doc(
        "LEAF THERMAL & COOLING ANALYSIS",
        (
            "High-level regenerative-cooling and thermal results. "
            "The complete station-by-station dataset remains in "
            "the dedicated Station Table tool."
        ),
        [
            (
                "Thermal summary",
                [
                    _u_line(
                        "Maximum hot-wall temperature",
                        _u_value(
                            results,
                            "regen_axial_max_hot_wall_temperature",
                            "combined_axial_max_hot_wall_temperature",
                            "best_full_engine_regen_max_hot_wall_temperature",
                        ),
                        "K",
                    ),
                    _u_line(
                        "Maximum coolant-wall temperature",
                        results.get(
                            "regen_axial_max_coolant_wall_temperature"
                        ),
                        "K",
                    ),
                    _u_line(
                        "Maximum heat flux",
                        results.get(
                            "regen_axial_max_heat_flux"
                        ),
                        "W/m²",
                    ),
                    _u_line(
                        "Material temperature margin",
                        margin,
                        "K",
                    ),
                ],
            ),
            (
                "Coolant hydraulics",
                [
                    _u_line(
                        "Coolant outlet temperature",
                        _u_value(
                            results,
                            "regen_axial_coolant_outlet_temperature",
                            "coolant_outlet_temperature",
                        ),
                        "K",
                    ),
                    _u_line(
                        "Total coolant pressure drop",
                        _u_value(
                            results,
                            "regen_axial_total_pressure_drop",
                            "coolant_pressure_drop",
                        ),
                        "Pa",
                    ),
                    _u_line(
                        "Minimum Reynolds number",
                        min_re,
                    ),
                    _u_line(
                        "Coolant velocity",
                        results.get(
                            "coolant_velocity"
                        ),
                        "m/s",
                    ),
                ],
            ),
            (
                "Channel geometry",
                [
                    _u_line(
                        "Channel count",
                        _u_value(
                            results,
                            "number_of_coolant_channels",
                            "coolant_channel_count",
                        ),
                    ),
                    _u_line(
                        "Channel width",
                        results.get(
                            "coolant_channel_width"
                        ),
                        "m",
                    ),
                    _u_line(
                        "Channel height",
                        results.get(
                            "coolant_channel_height"
                        ),
                        "m",
                    ),
                    _u_line(
                        "Rib width",
                        results.get(
                            "rib_width"
                        ),
                        "m",
                    ),
                ],
            ),
            (
                "Interpretation",
                (
                    interpretation
                    or
                    [
                        "- No additional thermal interpretation "
                        "is available from the current high-level "
                        "result contract."
                    ]
                ),
            ),
        ],
    )


def _build_user_materials_sources_report(results):
    material = _u_value(
        results,
        "material_source_provenance_material",
        "hot_gas_liner_material",
        "selected_material",
    )

    material_mode = _u_value(
        results,
        "material_source_provenance_mode",
        "material_aware_combined_source_mode",
    )

    material_quality = _u_value(
        results,
        "material_source_quality",
        "material_property_interpolation_source_quality",
        "material_aware_combined_best_material_source_quality",
    )

    coating = _u_value(
        results,
        "active_coating_material",
        "coating_source_provenance_coating",
    )

    coating_mode = _u_value(
        results,
        "coating_source_provenance_mode",
        "active_coating_source_mode",
    )

    coating_quality = _u_value(
        results,
        "active_coating_source_quality",
        "coating_source_quality",
    )

    return _u_doc(
        "LEAF MATERIALS & SOURCES",
        (
            "Selected materials and coatings together with the "
            "evidence quality currently available to support "
            "their engineering use."
        ),
        [
            (
                "Primary hot-gas material",
                [
                    (
                        "Material: "
                        +
                        (
                            str(material)
                            if material is not None
                            else "Not available"
                        )
                    ),
                    (
                        "Source mode: "
                        +
                        _u_status(
                            material_mode
                        )
                    ),
                    (
                        "Source quality: "
                        +
                        _u_short(
                            material_quality
                        )
                    ),
                    _u_line(
                        "Source records",
                        results.get(
                            "material_source_provenance_source_count"
                        ),
                    ),
                    _u_line(
                        "Average source confidence",
                        results.get(
                            "material_source_provenance_average_confidence"
                        ),
                    ),
                    (
                        "Citation available: "
                        +
                        _u_num(
                            results.get(
                                "material_source_has_citation"
                            )
                        )
                    ),
                    (
                        "Temperature-dependent table available: "
                        +
                        _u_num(
                            results.get(
                                "material_source_has_temperature_table"
                            )
                        )
                    ),
                ],
            ),
            (
                "Coating",
                [
                    (
                        "Coating: "
                        +
                        (
                            str(coating)
                            if coating is not None
                            else "None selected"
                        )
                    ),
                    (
                        "Source mode: "
                        +
                        _u_status(
                            coating_mode
                        )
                    ),
                    (
                        "Source quality: "
                        +
                        _u_short(
                            coating_quality
                        )
                    ),
                    _u_line(
                        "Source records",
                        results.get(
                            "coating_source_provenance_source_count"
                        ),
                    ),
                    _u_line(
                        "Average source confidence",
                        results.get(
                            "coating_source_provenance_average_confidence"
                        ),
                    ),
                    (
                        "Citation available: "
                        +
                        _u_num(
                            results.get(
                                "coating_source_has_citation"
                            )
                        )
                    ),
                    (
                        "Temperature-dependent table available: "
                        +
                        _u_num(
                            results.get(
                                "coating_source_has_temperature_table"
                            )
                        )
                    ),
                ],
            ),
            (
                "Evidence limitations",
                [
                    f"- {item}"
                    for item in _u_limits(
                        results
                    )
                ],
            ),
        ],
    )


def _build_user_validation_limitations_report(results):
    checks = [
        (
            "Chamber geometry",
            results.get(
                "chamber_geometry_status"
            ),
        ),
        (
            "Nozzle geometry",
            _u_value(
                results,
                "rao_nozzle_status",
                "nozzle_geometry_status",
            ),
        ),
        (
            "Cooling geometry",
            results.get(
                "regen_geometry_status"
            ),
        ),
        (
            "Thermal result",
            results.get(
                "regen_thermal_status"
            ),
        ),
        (
            "Coolant result",
            results.get(
                "regen_coolant_status"
            ),
        ),
        (
            "Material result",
            results.get(
                "regen_material_status"
            ),
        ),
        (
            "Overall regenerative-cooling result",
            _u_value(
                results,
                "regen_overall_status",
                "best_full_engine_regen_status",
            ),
        ),
    ]

    return _u_doc(
        "LEAF VALIDATION & LIMITATIONS",
        (
            "Engineering validity and known limitations for "
            "the current solved design."
        ),
        [
            (
                "Engineering checks",
                [
                    (
                        f"{label}: "
                        f"{_u_status(value)}"
                    )

                    for (
                        label,
                        value,
                    ) in checks
                ],
            ),
            (
                "Evidence limitations",
                [
                    f"- {item}"
                    for item in _u_limits(
                        results
                    )
                ],
            ),
            (
                "Interpretation rule",
                [
                    (
                        "- A calculated result is not promoted "
                        "to validated engineering evidence when "
                        "its required material or source basis "
                        "is missing, placeholder, or incomplete."
                    ),
                ],
            ),
        ],
    )


def _u_recommendations(results):
    source_keys = (
        "final_regen_design_recommendations",
        "final_regen_design_review_recommendations",
        "combined_cooling_allocation_recommendations",
        "combined_cooling_prediction_recommendations",
        "cooling_trade_recommendations",
        "film_cooling_recommendations",
        "coating_liner_recommendation",
        "coating_material_recommendation",
        "material_candidate_recommendation",
        "coupled_auto_material_recommendation",
        "coupled_auto_rebalance_recommendation",
    )

    blocked = (
        "foundation",
        "audit",
        "owner",
        "ownership",
        "phase ",
        "stage ",
        "repository",
        "result key",
        "output visibility",
        "open the relevant",
    )

    rows = []

    def collect(value):
        if value is None:
            return

        if isinstance(
            value,
            dict,
        ):
            for key in (
                "recommendation",
                "reason",
                "expected_outcome",
                "tradeoff",
                "risk",
                "confidence",
            ):
                if value.get(key):
                    collect(
                        value[key]
                    )

            return

        if isinstance(
            value,
            (list, tuple, set),
        ):
            for item in value:
                collect(item)

            return

        text = " ".join(
            str(value).split()
        )

        if (
            not text

            or

            any(
                term in text.lower()
                for term in blocked
            )
        ):
            return

        text = _u_short(
            text,
            320,
        )

        if text not in rows:
            rows.append(text)

    for key in source_keys:
        collect(
            results.get(key)
        )

    return rows[:10]


def _build_user_design_recommendations_report(results):
    recs = _u_recommendations(
        results
    )

    geometry = []

    for (
        label,
        keys,
        unit,
    ) in (
        (
            "Recommended channel count",
            (
                "recommended_channel_count",
                "recommended_number_of_coolant_channels",
            ),
            None,
        ),
        (
            "Recommended channel width",
            (
                "recommended_channel_width",
            ),
            "m",
        ),
        (
            "Recommended channel height",
            (
                "recommended_channel_height",
            ),
            "m",
        ),
        (
            "Recommended rib width",
            (
                "recommended_rib_width",
            ),
            "m",
        ),
    ):
        value = _u_value(
            results,
            *keys,
        )

        if value is not None:
            geometry.append(
                _u_line(
                    label,
                    value,
                    unit,
                )
            )

    return _u_doc(
        "LEAF DESIGN RECOMMENDATIONS",
        (
            "Engineering recommendations derived from the "
            "current solved design."
        ),
        [
            (
                "Recommended design values",
                geometry,
            ),
            (
                "Engineering recommendations",
                (
                    [
                        f"{index}. {text}"

                        for (
                            index,
                            text,
                        ) in enumerate(
                            recs,
                            1,
                        )
                    ]

                    if recs

                    else
                    [
                        "No engineering recommendation is "
                        "available for the current result state."
                    ]
                ),
            ),
            (
                "Use",
                [
                    (
                        "- Recommendations remain advisory until "
                        "the relevant validation and source "
                        "requirements are satisfied."
                    ),
                ],
            ),
        ],
    )


def _build_user_design_history_report(results):
    narrative = _u_value(
        results,
        "design_history_narrative_text",
        "design_history_text",
    )

    blocked = (
        "foundation",
        "ownership",
        "audit",
        "phase ",
        "stage ",
    )

    rows = []

    if narrative:
        for line in str(
            narrative
        ).splitlines():

            clean = " ".join(
                line.split()
            )

            if (
                not clean

                or

                any(
                    term in clean.lower()
                    for term in blocked
                )
            ):
                continue

            rows.append(
                _u_short(clean)
            )

            if len(rows) >= 20:
                break

    return _u_doc(
        "LEAF DESIGN HISTORY",
        (
            "Chronological design-iteration information recorded "
            "by the canonical Design History system."
        ),
        [
            (
                "History state",
                [
                    _u_line(
                        "Recorded iterations",
                        results.get(
                            "design_history_count"
                        ),
                    ),
                    _u_line(
                        "Current iteration",
                        results.get(
                            "design_history_iteration_number"
                        ),
                    ),
                    (
                        "Latest summary: "
                        +
                        _u_short(
                            results.get(
                                "design_history_latest_summary"
                            )
                        )
                    ),
                ],
            ),
            (
                "Narrative",
                (
                    rows
                    or
                    [
                        "No design-history narrative is "
                        "currently available."
                    ]
                ),
            ),
        ],
    )


def _u_propellants(results):
    return (
        _u_value(
            results,
            "selected_fuel",
            "fuel_name",
            "fuel",
            "cea_fuel",
            "propellant_fuel",
        ),
        _u_value(
            results,
            "selected_oxidizer",
            "oxidizer_name",
            "oxidizer",
            "cea_oxidizer",
            "propellant_oxidizer",
        ),
    )


def _build_user_benchmark_reproduction_report(results):
    evaluation = results.get(
        "benchmark_evaluation"
    )

    evaluation = (
        evaluation
        if isinstance(
            evaluation,
            dict,
        )
        else {}
    )

    benchmark_name = (
        evaluation.get(
            "display_name"
        )
        or
        results.get(
            "benchmark_selected_case"
        )
        or
        "No benchmark selected"
    )

    family = (
        evaluation.get(
            "engine_family"
        )
        or
        "Unknown"
    )

    source = (
        evaluation.get(
            "source_status"
        )
        or
        "Unknown"
    )

    fuel, oxidizer = _u_propellants(
        results
    )

    family_lower = str(
        family
    ).lower()

    fuel_lower = str(
        fuel
        or
        ""
    ).lower()

    comparability = (
        "NOT COMPARABLE"
    )

    reason = (
        "The current result contract does not provide enough "
        "propellant and cycle metadata to establish a like-for-like "
        "comparison with this reference engine."
    )

    if "hydrolox" in family_lower:
        if (
            "hydrogen"
            in fuel_lower

            or

            "h2"
            in fuel_lower
        ):
            comparability = (
                "PARTIALLY COMPARABLE"
            )

            reason = (
                "The propellant family appears compatible, but "
                "complete cycle and design similarity have not "
                "been established."
            )

        elif fuel:
            reason = (
                "The selected fuel does not match the hydrolox "
                "reference-engine propellant family."
            )

    comparison_rows = []

    comparisons = evaluation.get(
        "comparisons"
    )

    if isinstance(
        comparisons,
        list,
    ):
        for item in comparisons[:8]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            label = (
                item.get(
                    "target_key"
                )
                or
                item.get(
                    "key"
                )
                or
                "Comparison"
            )

            leaf_value = item.get(
                "leaf_value",
                item.get(
                    "actual"
                ),
            )

            target = item.get(
                "target_range",
                item.get(
                    "public_target_range"
                ),
            )

            comparison_rows.append(
                (
                    f"- {label}: "
                    f"LEAF={leaf_value!r}; "
                    f"reference={target!r}"
                )
            )

    verdict = [
        (
            "Comparability: "
            f"{comparability}"
        ),
        (
            "Reason: "
            f"{reason}"
        ),
    ]

    if (
        comparability
        ==
        "PARTIALLY COMPARABLE"
    ):
        verdict += [
            (
                "Reference comparison status: "
                +
                _u_status(
                    results.get(
                        "benchmark_status"
                    )
                )
            ),
            _u_line(
                "Stored reproduction score",
                results.get(
                    "engine_reproduction_score"
                ),
            ),
        ]

    else:
        verdict.append(
            (
                "Reproduction verdict: NOT EVALUATED — "
                "no engineering reproduction verdict is promoted "
                "without established comparability."
            )
        )

    return _u_doc(
        "LEAF BENCHMARK & REPRODUCTION",
        (
            "Comparison against public reference-engine data "
            "with an explicit comparability decision before any "
            "reproduction result is interpreted."
        ),
        [
            (
                "Reference engine",
                [
                    f"Case: {benchmark_name}",
                    f"Engine family: {family}",
                    f"Source status: {source}",
                    (
                        "Current fuel metadata: "
                        +
                        (
                            str(fuel)
                            if fuel is not None
                            else "Not available"
                        )
                    ),
                    (
                        "Current oxidizer metadata: "
                        +
                        (
                            str(oxidizer)
                            if oxidizer is not None
                            else "Not available"
                        )
                    ),
                ],
            ),
            (
                "Comparability decision",
                verdict,
            ),
            (
                "Reference comparisons",
                (
                    comparison_rows
                    or
                    [
                        "No structured reference-comparison "
                        "rows are available."
                    ]
                ),
            ),
        ],
    )


def build_user_facing_report_viewer_bundle(results):
    return {
        "Overview":
            _build_user_overview_report(
                results
            ),

        "Performance & Geometry":
            _build_user_performance_geometry_report(
                results
            ),

        "Thermal & Cooling":
            _build_user_thermal_cooling_report(
                results
            ),

        "Materials & Sources":
            _build_user_materials_sources_report(
                results
            ),

        "Validation & Limitations":
            _build_user_validation_limitations_report(
                results
            ),

        "Design Recommendations":
            _build_user_design_recommendations_report(
                results
            ),

        "Design History":
            _build_user_design_history_report(
                results
            ),

        "Benchmark & Reproduction":
            _build_user_benchmark_reproduction_report(
                results
            ),
    }



def build_foundation_bundle_report(results):
    sections = [
        build_main_output_report(results),
        "",
        build_validation_report(results),
        "",
        build_diagnostics_report(results),
        "",
        build_recommendation_report(results),
        "",
        build_recommendation_owner_report(results),
        "",
        build_optimisation_ownership_report(results),
        "",
        build_root_cause_ownership_report(results),
        "",
        build_foundation_attachment_audit_report(results),
        "",
        build_axial_report(results),
    ]

    return "\n\n".join(sections)


def build_regression_report(results):
    results = _safe_results(results)

    return results.get(
        "foundation_regression_text",
        "No foundation regression test report available.",
    )


def build_benchmark_report(results):
    results = _safe_results(results)

    return results.get(
        "benchmark_report_text",
        "No benchmark comparison report available.",
    )


def build_engine_reproduction_report(results):
    results = _safe_results(results)

    return results.get(
        "engine_reproduction_report_text",
        "No engine reproduction validation report available.",
    )


def build_startup_health_report(results):
    results = _safe_results(results)

    return results.get(
        "startup_health_text",
        "Startup health report is only available from the main window before calculation.",
    )

def build_phase_10a_solver_integration_planning_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10a_solver_integration_planning_owner_text",
        "No Phase 10A solver integration planning report available.",
    )

def build_phase_10b1_material_property_consumption_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b1_material_property_consumption_audit_owner_text",
        "No Phase 10B.1 material property consumption audit report available.",
    )

def build_phase_10b2_material_thermal_conductivity_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b2_material_thermal_conductivity_integration_owner_text",
        "No Phase 10B.2 material thermal conductivity integration report available.",
    )

def build_phase_10b3_material_specific_heat_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b3_material_specific_heat_integration_owner_text",
        "No Phase 10B.3 material specific heat integration report available.",
    )

def build_phase_10b4_material_density_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b4_material_density_integration_owner_text",
        "No Phase 10B.4 material density integration report available.",
    )

def build_phase_10b5_material_temperature_limit_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b5_material_temperature_limit_integration_owner_text",
        "No Phase 10B.5 material temperature limit integration report available.",
    )

def build_phase_10b6_material_strength_limit_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b6_material_strength_limit_integration_owner_text",
        "No Phase 10B.6 material strength limit integration report available.",
    )

def build_phase_10b7_material_integration_validation_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b7_material_integration_validation_owner_text",
        "No Phase 10B.7 material integration validation report available.",
    )

def build_phase_10b8_material_integration_completion_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10b8_material_integration_completion_audit_text",
        "No Phase 10B.8 material integration completion audit report available.",
    )

def build_phase_10c1_coating_property_consumption_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c1_coating_property_consumption_audit_owner_text",
        "No Phase 10C.1 coating property consumption audit report available.",
    )

def build_phase_10c2_coating_thermal_conductivity_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c2_coating_thermal_conductivity_integration_owner_text",
        "No Phase 10C.2 coating thermal conductivity integration report available.",
    )

def build_phase_10c3_coating_thickness_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c3_coating_thickness_integration_owner_text",
        "No Phase 10C.3 coating thickness integration report available.",
    )

def build_phase_10c4_coating_thermal_resistance_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c4_coating_thermal_resistance_integration_owner_text",
        "No Phase 10C.4 coating thermal resistance integration report available.",
    )

def build_phase_10c5_coating_temperature_limit_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c5_coating_temperature_limit_integration_owner_text",
        "No Phase 10C.5 coating temperature limit integration report available.",
    )

def build_phase_10c6_bond_coat_integration_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c6_bond_coat_integration_owner_text",
        "No Phase 10C.6 bond coat integration report available.",
    )

def build_phase_10c7_coating_integration_validation_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c7_coating_integration_validation_owner_text",
        "No Phase 10C.7 coating integration validation report available.",
    )

def build_phase_10c8_coating_integration_completion_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10c8_coating_integration_completion_audit_text",
        "No Phase 10C.8 coating integration completion audit report available.",
    )

def build_phase_10d1_temperature_dependency_discovery_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10d1_temperature_dependency_discovery_audit_owner_text",
        "No Phase 10D.1 temperature dependency discovery audit report available.",
    )


def build_phase_10d2_material_conductivity_consumption_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10d2_material_conductivity_consumption_audit_owner_text",
        "No Phase 10D.2 material conductivity consumption audit report available.",
    )

def build_phase_10d3_specific_heat_consumption_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10d3_specific_heat_consumption_audit_owner_text",
        "No Phase 10D.3 specific heat consumption audit report available.",
    )

def build_phase_10d4_density_coolant_property_consumption_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10d4_density_coolant_property_consumption_audit_owner_text",
        "No Phase 10D.4 density and coolant property consumption audit report available.",
    )

def build_phase_10d5_coating_thermal_consumption_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10d5_coating_thermal_consumption_audit_owner_text",
        "No Phase 10D.5 coating thermal consumption audit report available.",
    )

def build_phase_10d6_bond_coat_consumption_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10d6_bond_coat_consumption_audit_owner_text",
        "No Phase 10D.6 bond-coat consumption audit report available.",
    )

def build_phase_10d7_temperature_dependent_solver_completion_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_text",
        "No Phase 10D.7 temperature-dependent solver completion audit report available.",
    )

def build_phase_11a1_regen_geometry_constraint_discovery_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_text",
        "No Phase 11A.1 regen geometry constraint discovery audit report available.",
    )

def build_phase_11a2_regen_geometry_constraint_validation_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_11a2_regen_geometry_constraint_validation_owner_text",
        "No Phase 11A.2 regen geometry constraint validation report available.",
    )

def build_phase_11a3_regen_geometry_failure_explanation_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_11a3_regen_geometry_failure_explanation_owner_text",
        "No Phase 11A.3 regen geometry failure explanation report available.",
    )

def build_phase_11a4_regen_geometry_recommendation_engine_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_11a4_regen_geometry_recommendation_engine_owner_text",
        "No Phase 11A.4 regen geometry recommendation engine report available.",
    )

def build_phase_11a5_regen_geometry_apply_recommendation_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_text",
        "No Phase 11A.5 apply recommended geometry report available.",
    )

def build_phase_11a6_regen_geometry_output_architecture_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_11a6_regen_geometry_output_architecture_owner_text",
        "No Phase 11A.6 regen geometry output architecture report available.",
    )

def build_phase_11a8_regen_geometry_candidate_acceptance_report(results):
    results = _safe_results(results)

    return results.get(
        "phase_11a8_regen_geometry_candidate_acceptance_owner_text",
        "No Phase 11A.8 regen geometry candidate acceptance report available.",
    )

def build_result_key_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "foundation_result_key_audit_text",
        "No foundation result key audit report available.",
    )

def build_output_ownership_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "output_ownership_audit_text",
        "No output ownership audit available. Run a calculation first.",
    )

def build_design_history_report(results):
    results = _safe_results(results)

    sections = []

    history_text = results.get("design_history_text")
    narrative_text = results.get("design_history_narrative_text")

    if history_text:
        sections.append(history_text)

    if narrative_text:
        sections.append(narrative_text)

    if not sections:
        return "No design history available. Run a calculation first."

    return "\n\n".join(sections)

def build_optimisation_ownership_report(results):
    results = _safe_results(results)

    return results.get(
        "optimisation_ownership_report_text",
        "No optimisation ownership report available. Run at least two calculations first.",
    )

def build_failure_root_cause_owner_report(results):
    results = _safe_results(results)

    return results.get(
        "failure_root_cause_owner_text",
        results.get(
            "failure_root_cause_text",
            "No failure root-cause report available. Run a calculation first.",
        ),
    )

def build_corrective_action_priority_report(results):
    results = _safe_results(results)

    return results.get(
        "corrective_action_priority_text",
        "No corrective action priority report available. Run a calculation first.",
    )

def build_root_cause_ownership_report(results):
    results = _safe_results(results)

    return results.get(
        "root_cause_ownership_report_text",
        results.get(
            "failure_root_cause_owner_text",
            results.get(
                "failure_root_cause_text",
                "No root-cause ownership report available. Run a calculation first.",
            ),
        ),
    )

def build_recommendation_owner_report(results):
    results = _safe_results(results)

    return results.get(
        "recommendation_owner_text",
        results.get(
            "recommendation_explanation_text",
            "No recommendation explanation report available. Run a calculation first.",
        ),
    )

def build_output_visibility_architecture_report(results):
    results = _safe_results(results)

    return results.get(
        "output_visibility_architecture_text",
        "No output visibility architecture audit available. Run a calculation first.",
    )

def build_recommendation_ownership_final_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "recommendation_ownership_final_audit_text",
        "No recommendation ownership final audit available. Run a calculation first.",
    )

def build_regen_source_validation_gate_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_source_validation_text",
        "No regen source validation gate report available. Run a calculation first.",
    )

def build_regen_provenance_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_provenance_report_text",
        "No regen provenance report available. Run a calculation first.",
    )

def build_regen_property_table_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_property_table_owner_text",
        "No regen property table report available. Run a calculation first.",
    )

def build_regen_validation_master_gate_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_validation_master_gate_text",
        "No regen validation master gate report available. Run a calculation first.",
    )

def build_regen_completion_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_completion_audit_text",
        "No Stage U regen completion audit available. Run a calculation first.",
    )

def build_regen_scalability_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_scalability_text",
        "No Stage V.1 regen scalability framework report available. Run a calculation first.",
    )

def build_regen_scalability_report_owner_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_scalability_report_owner_text",
        "No Stage V.2 regen scalability report ownership report available. Run a calculation first.",
    )

def build_regen_scalability_failure_owner_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_scalability_failure_owner_text",
        "No Stage V.3 regen scalability failure ownership report available. Run a calculation first.",
    )

def build_regen_scalability_master_gate_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_scalability_master_gate_text",
        "No Stage V.4 regen scalability master gate report available. Run a calculation first.",
    )

def build_regen_scalability_completion_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "regen_scalability_completion_audit_text",
        "No Stage V.5 regen scalability completion audit report available. Run a calculation first.",
    )

def build_real_engine_benchmarking_framework_report(results):
    results = _safe_results(results)

    return results.get(
        "real_engine_benchmarking_framework_text",
        "No Stage W.1 real-engine benchmarking framework report available. Run a calculation first.",
    )

def build_real_engine_benchmark_source_owner_report(results):
    results = _safe_results(results)

    return results.get(
        "real_engine_benchmark_source_owner_text",
        "No Stage W.2 public benchmark source ownership report available. Run a calculation first.",
    )

def build_real_engine_benchmark_band_owner_report(results):
    results = _safe_results(results)

    return results.get(
        "real_engine_benchmark_band_owner_text",
        "No Stage W.3 numeric benchmark band ownership report available. Run a calculation first.",
    )

def build_real_engine_benchmark_failure_owner_report(results):
    results = _safe_results(results)

    return results.get(
        "real_engine_benchmark_failure_owner_text",
        "No Stage W.4 real-engine benchmark failure ownership report available. Run a calculation first.",
    )

def build_real_engine_benchmark_master_gate_report(results):
    results = _safe_results(results)

    return results.get(
        "real_engine_benchmark_master_gate_text",
        "No Stage W.5 real-engine benchmark master gate report available. Run a calculation first.",
    )

def build_real_engine_benchmark_completion_audit_report(results):
    results = _safe_results(results)

    return results.get(
        "real_engine_benchmark_completion_audit_text",
        "No Stage W.6 real-engine benchmark completion audit report available. Run a calculation first.",
    )

def build_foundation_verification_report(results):
    results = _safe_results(results)

    return results.get(
        "foundation_verification_text",
        "No Foundation Verification Harness report available. Run foundation verification first.",
    )

def build_foundation_save_load_report(results):
    results = _safe_results(results)

    return results.get(
        "foundation_save_load_verification_text",
        "No Foundation Save/Load Verification report available.",
    )

def build_foundation_ui_launch_report(results):
    results = _safe_results(results)

    return results.get(
        "foundation_ui_launch_verification_text",
        "No Foundation UI Launch Verification report available.",
    )

def build_foundation_final_signoff_report(results):
    results = _safe_results(results)

    return results.get(
        "foundation_final_signoff_text",
        "No Foundation Final Sign-Off report available.",
    )

def build_foundation_completion_handover_report(results):
    results = _safe_results(results)

    return results.get(
        "foundation_completion_handover_text",
        "No Foundation Completion Handover report available.",
    )