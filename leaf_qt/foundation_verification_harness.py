from copy import deepcopy

try:
    from foundation_save_load_verification import verify_foundation_save_load_roundtrip
except Exception:
    verify_foundation_save_load_roundtrip = None

try:
    from foundation_ui_launch_verification import verify_foundation_ui_launch
except Exception:
    verify_foundation_ui_launch = None

try:
    from foundation_final_signoff_controller import evaluate_foundation_final_signoff
except Exception:
    evaluate_foundation_final_signoff = None

try:
    from foundation_completion_handover import build_foundation_completion_handover
except Exception:
    build_foundation_completion_handover = None

EXPECTED_REPORTS = (
    "Dashboard",
    "Main Output Report",
    "Validation Report",
    "Diagnostics Report",
    "Foundation Attachment Audit",
    "Foundation Regression Report",
    "Foundation Result Key Audit",
    "Stage U Regen Completion Audit",
    "Stage V.5 Regen Scalability Completion Audit",
    "Stage W.6 Real Engine Benchmark Completion Audit",
    "Phase 10A Solver Integration Planning",
    "Phase 10B.1 Material Property Consumption Audit",
    "Phase 10B.2 Material Thermal Conductivity Integration",
    "Phase 10B.3 Material Specific Heat Integration",
    "Phase 10B.4 Material Density Integration",
    "Phase 10B.5 Material Temperature Limit Integration",
    "Phase 10B.6 Material Strength Limit Integration",
    "Phase 10B.7 Material Integration Validation",
    "Phase 10B.8 Material Integration Completion Audit",
    "Phase 10C.1 Coating Property Consumption Audit",
    "Phase 10C.2 Coating Thermal Conductivity Integration",
    "Phase 10C.3 Coating Thickness Integration",
    "Phase 10C.4 Coating Thermal Resistance Integration",
    "Phase 10C.5 Coating Temperature Limit Integration",
    "Phase 10C.6 Bond Coat Integration",
    "Phase 10C.7 Coating Integration Validation",
    "Phase 10C.8 Coating Integration Completion Audit",
    "Phase 10D.1 Temperature Dependency Discovery Audit",
    "Phase 10D.2 Material Conductivity Consumption Audit",
    "Phase 10D.3 Specific Heat Consumption Audit",
    "Phase 10D.4 Density and Coolant Property Consumption Audit",
    "Phase 10D.5 Coating Thermal Consumption Audit",
    "Phase 10D.6 Bond-Coat Consumption Audit",
    "Phase 10D.7 Temperature-Dependent Solver Completion Audit",
    "Phase 11A.1 Regen Geometry Constraint Discovery Audit",
    "Phase 11A.2 Regen Geometry Constraint Validation",
    "Phase 11A.3 Regen Geometry Failure Explanation",
    "Phase 11A.4 Regen Geometry Recommendation Engine V1",
    "Phase 11A.5 Apply Recommended Geometry",
    "Phase 11A.6 Regen Geometry Output Architecture",
    "Phase 11A.8 Regen Geometry Candidate Acceptance",
)



# ---------------------------------------------------------------------------
# PHASE 16T.3W.1 — FOUNDATION VERIFICATION HARNESS STATUS ADAPTER
# ---------------------------------------------------------------------------
# Additive reporting wrapper only.
# Does not change verification logic, test ordering, pass/fail decisions,
# public entry points, or legacy PASS/FAIL strings.

try:
    from leaf_qt.global_status_classification_engine import (
        classify_status as _leaf_16t3w1_classify_status,
        make_finding as _leaf_16t3w1_make_finding,
    )
except Exception:
    def _leaf_16t3w1_make_finding(message, category, owner, evidence=None):
        return {
            "message": message,
            "category": category,
            "owner": owner,
            "evidence": evidence or {},
        }

    def _leaf_16t3w1_classify_status(findings, production_gate=True):
        categories = {
            str(finding.get("category", "")).upper()
            for finding in findings
            if isinstance(finding, dict)
        }
        if "VALIDATION_FAILURE" in categories:
            status = "FAIL"
        elif "BLOCKED" in categories:
            status = "BLOCKED"
        elif "MANUAL_REVIEW_REQUIRED" in categories:
            status = "REVIEW_REQUIRED"
        else:
            status = "PASS"
        return {
            "status": status,
            "production_gate": bool(production_gate),
            "finding_count": len(findings),
            "findings": findings,
        }


_PHASE_16T3W1_OWNER = "Foundation Verification Harness"
_PHASE_16T3W1_ADAPTER_STATUS = "PASS_PHASE_16T3W1_STATUS_ADAPTER"


def _leaf_16t3w1_build_foundation_verification_findings(result):
    findings = []

    status = result.get("foundation_verification_status")
    failed_count = int(result.get("foundation_verification_failed_count", 0) or 0)
    passed_count = int(result.get("foundation_verification_passed_count", 0) or 0)

    if status == "PASS_FOUNDATION_VERIFICATION" and failed_count == 0:
        findings.append(
            _leaf_16t3w1_make_finding(
                message="Foundation verification harness passed with legacy output preserved.",
                category="COMPLETE",
                owner=_PHASE_16T3W1_OWNER,
                evidence={
                    "foundation_verification_status": status,
                    "passed_count": passed_count,
                    "failed_count": failed_count,
                },
            )
        )
    else:
        findings.append(
            _leaf_16t3w1_make_finding(
                message="Foundation verification harness reported failing legacy verification output.",
                category="VALIDATION_FAILURE",
                owner=_PHASE_16T3W1_OWNER,
                evidence={
                    "foundation_verification_status": status,
                    "passed_count": passed_count,
                    "failed_count": failed_count,
                },
            )
        )

    if "foundation_verification_text" not in result:
        findings.append(
            _leaf_16t3w1_make_finding(
                message="Foundation verification text report is missing.",
                category="VALIDATION_FAILURE",
                owner=_PHASE_16T3W1_OWNER,
            )
        )

    if "foundation_verification_tests" not in result:
        findings.append(
            _leaf_16t3w1_make_finding(
                message="Foundation verification test list is missing.",
                category="VALIDATION_FAILURE",
                owner=_PHASE_16T3W1_OWNER,
            )
        )

    return findings


def _leaf_16t3w1_build_adapter_report(findings, global_status_payload, legacy_status):
    lines = [
        "LEAF PHASE 16T.3W.1",
        "FOUNDATION VERIFICATION HARNESS STATUS ADAPTER",
        "================================================",
        "",
        f"Legacy Status: {legacy_status}",
        f"Canonical Global Status: {global_status_payload.get('status')}",
        f"Structured Findings: {len(findings)}",
        "",
        "Adapter Scope:",
        "- Add structured findings.",
        "- Add canonical global status payload.",
        "- Preserve legacy verification status strings.",
        "- Preserve public API and existing verification behaviour.",
        "",
        "Findings:",
    ]

    for finding in findings:
        lines.append(
            f"- [{finding.get('category')}] {finding.get('message')}"
        )

    return "\n".join(lines)


def _leaf_16t3w1_apply_status_adapter(result):
    if not isinstance(result, dict):
        return result

    legacy_status = result.get("foundation_verification_status", "UNKNOWN")

    findings = _leaf_16t3w1_build_foundation_verification_findings(result)
    global_status_payload = _leaf_16t3w1_classify_status(
        findings,
        production_gate=True,
    )
    adapter_report = _leaf_16t3w1_build_adapter_report(
        findings,
        global_status_payload,
        legacy_status,
    )

    result.update({
        "phase_16t3w1_status_adapter_complete": True,
        "phase_16t3w1_foundation_verification_harness_status_adapter_complete": True,
        "foundation_verification_harness_status_adapter_complete": True,
        "foundation_verification_harness_status_adapter_status": _PHASE_16T3W1_ADAPTER_STATUS,
        "foundation_verification_harness_structured_findings": findings,
        "foundation_verification_harness_global_status": global_status_payload.get("status"),
        "foundation_verification_harness_global_status_payload": global_status_payload,
        "foundation_verification_harness_adapter_report": adapter_report,
        "foundation_verification_harness_legacy_status": legacy_status,

        # Generic compatibility aliases used by structured-status consumers.
        "structured_findings": findings,
        "global_status": global_status_payload.get("status"),
        "global_status_payload": global_status_payload,
        "adapter_report": adapter_report,
    })

    return result

def build_foundation_verification_seed():
    return {
        "material_name": "GRCop-42",
        "coating_name": "NONE",

        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_validation_score": 95,
        "material_source_is_placeholder": False,

        "coating_source_validation_mode": "NONE",
        "coating_source_validation_score": 0,
        "coating_source_is_placeholder": False,

        "material_temperature_table_status": "PASS_TABLE_AVAILABLE",
        "material_property_interpolation_status": "PASS_INTERPOLATED",
        "material_table_min_temperature": 250,
        "material_table_max_temperature": 1200,

        "hot_gas_side_wall_temperature": 850,
        "material_max_wall_temperature": 900,
        "max_wall_temperature": 900,

        "full_engine_regen_geometry_status": "PASS_VALID_GEOMETRY",
        "regen_validation_status": "PASS_REGEN_VALIDATION",

        "thrust": 845000,
        "mass_flow_rate": 320,
        "specific_impulse": 310,
        "chamber_pressure": 9700000,
        "throat_area": 0.09,

        "regen_coolant_velocity": 25,
        "regen_pressure_drop": 1200000,
        "regen_heat_flux": 18000000,

        "hot_gas_wall_thickness": 0.0005,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "number_of_coolant_channels": 80,
        "phase_10d_verification_thermal_chain_evidence": {
            "material_thermal_conductivity": 300.0,
            "wall_thickness": 0.0012,
            "hot_gas_heat_transfer_coefficient": 8200.0,
            "coolant_heat_transfer_coefficient": 25000.0,
            "adiabatic_wall_temperature": 2800.0,
            "coolant_bulk_temperature": 300.0,
            "coating_thermal_resistance": 0.0,
            "bond_coat_thermal_resistance": 0.0,
        },
        "phase_10d_verification_specific_heat_evidence": {
            "specific_heat_cp": 2000.0,
            "heat_load": 180000.0,
            "coolant_mass_flow": 0.4,
            "coolant_inlet_temperature": 300.0,
        },
        "phase_10d_verification_coolant_property_evidence": {
            "coolant_density": 810.0,
            "coolant_dynamic_viscosity": 0.0016,
            "coolant_mass_flow": 0.4,
            "coolant_flow_area": 0.00002,
            "hydraulic_diameter": 0.002,
            "flow_length": 0.5,
            "coolant_thermal_conductivity": 0.13,
        },

        "phase_10d_verification_coating_thermal_evidence": {
            "coating_thermal_conductivity": 1.5,
            "coating_thickness": 0.00025,
            "hot_gas_heat_transfer_coefficient": 8200.0,
            "coolant_heat_transfer_coefficient": 25000.0,
            "adiabatic_wall_temperature": 2800.0,
            "coolant_bulk_temperature": 300.0,
            "wall_thermal_resistance": 0.000004,
            "coating_temperature_limit": 1600.0,
        },

        "phase_10d_verification_bond_coat_evidence": {
            "bond_coat_thermal_conductivity": 8.0,
            "bond_coat_thickness": 0.000075,
            "coating_thermal_resistance": 0.0001666667,
            "hot_gas_heat_transfer_coefficient": 8200.0,
            "coolant_heat_transfer_coefficient": 25000.0,
            "adiabatic_wall_temperature": 2800.0,
            "coolant_bulk_temperature": 300.0,
            "wall_thermal_resistance": 0.000004,
            "bond_coat_temperature_limit": 1450.0,
        },
        "regen_validation_master_gate_status": "PASS_REGEN_VALIDATION_MASTER_GATE",
        "regen_validation_master_gate_pass_allowed": True,

        "stage_u_regen_validation_complete": True,

        "stage_v1_regen_scalability_framework_complete": False,
        "stage_v2_regen_scalability_report_ownership_complete": False,
        "stage_v3_regen_scalability_failure_ownership_complete": False,
        "stage_v4_regen_scalability_master_gate_complete": False,
        "stage_v_scalability_complete": False,

        "propellant_pair": "RP-1/LOX",
        "cycle_type": "GAS_GENERATOR",
        "benchmark_reference_engine": "Merlin",
    }


def build_foundation_verification_cases():
    base = build_foundation_verification_seed()

    cases = []

    cases.append({
        "name": "sourced_valid_no_coating",
        "results": deepcopy(base),
        "expect_stage_u_complete": True,
        "expect_stage_v_complete": True,
        "expect_stage_w_complete": True,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    placeholder = deepcopy(base)
    placeholder["material_source_validation_mode"] = "PLACEHOLDER_MODE"
    placeholder["material_source_is_placeholder"] = True
    cases.append({
        "name": "placeholder_material_blocks_pass",
        "results": placeholder,
        "expect_stage_u_complete": False,
        "expect_stage_v_complete": False,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    partial = deepcopy(base)
    partial["material_source_validation_mode"] = "PARTIAL_SOURCE_MODE"
    partial["material_source_validation_score"] = 65
    cases.append({
        "name": "partial_source_blocks_final_pass",
        "results": partial,
        "expect_stage_u_complete": False,
        "expect_stage_v_complete": False,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    missing_material_table = deepcopy(base)
    missing_material_table["material_temperature_table_status"] = "MISSING"
    cases.append({
        "name": "missing_material_table_blocks_pass",
        "results": missing_material_table,
        "expect_stage_u_complete": False,
        "expect_stage_v_complete": False,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    selected_coating_missing_table = deepcopy(base)
    selected_coating_missing_table["coating_name"] = "TBC"
    selected_coating_missing_table["coating_source_validation_mode"] = "SOURCED_VALIDATION_MODE"
    selected_coating_missing_table["coating_source_validation_score"] = 90
    selected_coating_missing_table["coating_temperature_table_status"] = "MISSING"
    selected_coating_missing_table["coating_property_interpolation_status"] = "UNKNOWN"
    cases.append({
        "name": "selected_coating_missing_table_blocks_pass",
        "results": selected_coating_missing_table,
        "expect_stage_u_complete": False,
        "expect_stage_v_complete": False,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    overheated_wall = deepcopy(base)
    overheated_wall["hot_gas_side_wall_temperature"] = 1100
    overheated_wall["max_wall_temperature"] = 1100
    overheated_wall["material_max_wall_temperature"] = 900
    cases.append({
        "name": "overheated_wall_blocks_pass",
        "results": overheated_wall,
        "expect_stage_u_complete": False,
        "expect_stage_v_complete": False,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    laminar_warning = deepcopy(base)
    laminar_warning["regen_coolant_velocity"] = 0.5
    cases.append({
        "name": "low_coolant_velocity_blocks_scalability_signoff",
        "results": laminar_warning,
        "expect_stage_u_complete": True,
        "expect_stage_v_complete": False,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    low_confidence_benchmark = deepcopy(base)
    low_confidence_benchmark["real_engine_benchmark_source_confidence"] = 0.3
    low_confidence_benchmark["real_engine_benchmark_source_count"] = 1
    low_confidence_benchmark["public_benchmark_data_available"] = True
    low_confidence_benchmark[
        "foundation_verification_low_confidence_public_benchmark_blocks_stage_w"
    ] = True
    low_confidence_benchmark[
        "real_engine_benchmark_source_confidence"
    ] = 0.3

    low_confidence_benchmark[
        "real_engine_benchmark_source_count"
    ] = 1

    low_confidence_benchmark[
        "public_benchmark_data_available"
    ] = True
    low_confidence_benchmark["benchmark_reference_engine"] = "Raptor"
    low_confidence_benchmark["propellant_pair"] = "CH4/LOX"
    low_confidence_benchmark["cycle_type"] = "FULL_FLOW_STAGED_COMBUSTION"
    low_confidence_benchmark["thrust"] = 2_200_000
    low_confidence_benchmark["chamber_pressure"] = 30_000_000
    low_confidence_benchmark["specific_impulse"] = 350
    low_confidence_benchmark["mass_flow_rate"] = 700
    low_confidence_benchmark["throat_area"] = 0.08

    cases.append({
        "name": "low_confidence_public_benchmark_blocks_stage_w",
        "results": low_confidence_benchmark,
        "expect_stage_u_complete": True,
        "expect_stage_v_complete": True,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    out_of_band_benchmark = deepcopy(base)
    out_of_band_benchmark[
        "real_engine_benchmark_tolerance_fraction"
    ] = 0.10

    out_of_band_benchmark[
        "real_engine_benchmark_reference_thrust"
    ] = 200000.0

    out_of_band_benchmark[
        "benchmark_thrust"
    ] = 200000.0

    out_of_band_benchmark[
        "public_benchmark_data_available"
    ] = True

    out_of_band_benchmark[
        "real_engine_benchmark_source_confidence"
    ] = 0.75

    out_of_band_benchmark[
        "real_engine_benchmark_source_count"
    ] = 2
    out_of_band_benchmark["benchmark_reference_engine"] = "Merlin"
    out_of_band_benchmark["thrust"] = 2_500_000
    out_of_band_benchmark["chamber_pressure"] = 30_000_000
    out_of_band_benchmark["specific_impulse"] = 500
    out_of_band_benchmark["mass_flow_rate"] = 900

    cases.append({
        "name": "out_of_band_public_benchmark_blocks_stage_w",
        "results": out_of_band_benchmark,
        "expect_stage_u_complete": True,
        "expect_stage_v_complete": True,
        "expect_stage_w_complete": False,
        "expect_pipeline_pass": True,
        "expect_main_output_clean": True,
    })

    return cases


def run_foundation_verification_harness(
        apply_foundation_layers_callback,
        build_report_viewer_bundle_callback,
        get_main_output_results_callback,
):
    tests = []

    latest_successful_solved = {}

    def add_test(case_name, name, passed, detail=""):
        tests.append({
            "case": case_name,
            "name": name,
            "passed": bool(passed),
            "detail": detail,
        })

    for case in build_foundation_verification_cases():
        case_name = case["name"]
        case_payload = deepcopy(case["results"])
        case_payload["foundation_verification_case"] = case_name

        solved = apply_foundation_layers_callback(case_payload)
        pipeline_status = solved.get("foundation_attachment_pipeline_status")
        stage_u_complete = bool(solved.get("stage_u_regen_validation_complete"))
        stage_v_complete = bool(solved.get("stage_v_scalability_complete"))
        stage_w_complete = bool(solved.get("stage_w_real_engine_benchmarking_complete"))

        add_test(
            case_name,
            "Foundation attachment pipeline status matches expectation",
            (pipeline_status == "PASS") == bool(case["expect_pipeline_pass"]),
            f"pipeline_status={pipeline_status}",
        )

        add_test(
            case_name,
            "Stage U completion matches expectation",
            stage_u_complete == bool(case["expect_stage_u_complete"]),
            f"stage_u_regen_validation_complete={stage_u_complete}",
        )

        main_outputs = get_main_output_results_callback(solved)

        polluted = [
            key for key, value in main_outputs.items()
            if isinstance(value, str) and len(value) > 80
        ]

        add_test(
            case_name,
            "Main scalar outputs are not polluted by long report text",
            not polluted,
            f"polluted_keys={polluted}",
        )

        reports = build_report_viewer_bundle_callback(solved)

        missing_reports = [
            report_name for report_name in EXPECTED_REPORTS
            if report_name not in reports
        ]

        add_test(
            case_name,
            "Report viewer bundle exposes required foundation reports",
            not missing_reports,
            f"missing_reports={missing_reports}",
        )

        expected_stage_v = bool(case.get("expect_stage_v_complete", False))
        expected_stage_w = bool(case.get("expect_stage_w_complete", False))

        add_test(
            case_name,
            "Stage V completion matches expectation",
            stage_v_complete == expected_stage_v,
            (
                f"stage_v_complete={stage_v_complete}; "
                f"stage_v_status={solved.get('regen_scalability_completion_audit_status')}"
            ),
        )

        add_test(
            case_name,
            "Stage W completion matches expectation",
            stage_w_complete == expected_stage_w,
            (
                f"stage_w_complete={stage_w_complete}; "
                f"stage_w_status={solved.get('real_engine_benchmark_completion_audit_status')}"
            ),
        )

        result_key_audit_status = solved.get("foundation_result_key_audit_status")

        add_test(
            case_name,
            "Result key audit exists",
            result_key_audit_status is not None,
            f"status={result_key_audit_status}",
        )

        add_test(
            case_name,
            "Result key audit fully passes",
            result_key_audit_status == "PASS",
            f"status={result_key_audit_status}",
        )

        phase_10a_status = solved.get(
            "phase_10a_solver_integration_planning_owner_status"
        )

        phase_10a_complete = bool(
            solved.get("phase_10a_solver_integration_planning_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10A solver integration planning owner exists",
            phase_10a_complete
            and phase_10a_status == "PASS_PHASE_10A_SOLVER_INTEGRATION_PLANNING_OWNER",
            f"status={phase_10a_status}; complete={phase_10a_complete}",
        )

        phase_10b1_status = solved.get(
            "phase_10b1_material_property_consumption_audit_owner_status"
        )

        phase_10b1_complete = bool(
            solved.get("phase_10b1_material_property_consumption_audit_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10B.1 material property consumption audit owner exists",
            phase_10b1_complete
            and phase_10b1_status == "PASS_PHASE_10B1_MATERIAL_PROPERTY_CONSUMPTION_AUDIT_OWNER",
            f"status={phase_10b1_status}; complete={phase_10b1_complete}",
        )

        phase_10b2_status = solved.get(
            "phase_10b2_material_thermal_conductivity_integration_owner_status"
        )

        phase_10b2_complete = bool(
            solved.get("phase_10b2_material_thermal_conductivity_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10B.2 material thermal conductivity integration owner exists",
            phase_10b2_complete
            and phase_10b2_status == "PASS_PHASE_10B2_MATERIAL_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER",
            f"status={phase_10b2_status}; complete={phase_10b2_complete}",
        )

        phase_10b3_status = solved.get(
            "phase_10b3_material_specific_heat_integration_owner_status"
        )

        phase_10b3_complete = bool(
            solved.get("phase_10b3_material_specific_heat_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10B.3 material specific heat integration owner exists",
            phase_10b3_complete
            and phase_10b3_status == "PASS_PHASE_10B3_MATERIAL_SPECIFIC_HEAT_INTEGRATION_OWNER",
            f"status={phase_10b3_status}; complete={phase_10b3_complete}",
        )

        phase_10b4_status = solved.get(
            "phase_10b4_material_density_integration_owner_status"
        )

        phase_10b4_complete = bool(
            solved.get("phase_10b4_material_density_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10B.4 material density integration owner exists",
            phase_10b4_complete
            and phase_10b4_status == "PASS_PHASE_10B4_MATERIAL_DENSITY_INTEGRATION_OWNER",
            f"status={phase_10b4_status}; complete={phase_10b4_complete}",
        )

        phase_10b5_status = solved.get(
            "phase_10b5_material_temperature_limit_integration_owner_status"
        )

        phase_10b5_complete = bool(
            solved.get("phase_10b5_material_temperature_limit_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10B.5 material temperature limit integration owner exists",
            phase_10b5_complete
            and phase_10b5_status == "PASS_PHASE_10B5_MATERIAL_TEMPERATURE_LIMIT_INTEGRATION_OWNER",
            f"status={phase_10b5_status}; complete={phase_10b5_complete}",
        )

        phase_10b6_status = solved.get(
            "phase_10b6_material_strength_limit_integration_owner_status"
        )

        phase_10b6_complete = bool(
            solved.get("phase_10b6_material_strength_limit_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10B.6 material strength limit integration owner exists",
            phase_10b6_complete
            and phase_10b6_status == "PASS_PHASE_10B6_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER",
            f"status={phase_10b6_status}; complete={phase_10b6_complete}",
        )

        phase_10b7_status = solved.get(
            "phase_10b7_material_integration_validation_owner_status"
        )

        phase_10b7_complete = bool(
            solved.get("phase_10b7_material_integration_validation_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10B.7 material integration validation owner exists",
            phase_10b7_complete
            and phase_10b7_status in (
                "PASS_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER",
                "FAIL_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER",
            ),
            f"status={phase_10b7_status}; complete={phase_10b7_complete}",
        )

        phase_10b8_status = solved.get(
            "phase_10b8_material_integration_completion_audit_status"
        )

        phase_10b8_complete = bool(
            solved.get("phase_10b8_material_integration_completion_audit_complete")
        )

        add_test(
            case_name,
            "Phase 10B.8 material integration completion audit exists",
            phase_10b8_complete
            and phase_10b8_status in (
                "PASS_MATERIAL_INTEGRATION_COMPLETION_AUDIT",
                "FAIL_MATERIAL_INTEGRATION_COMPLETION_AUDIT",
            ),
            f"status={phase_10b8_status}; complete={phase_10b8_complete}",
        )

        phase_10c1_status = solved.get(
            "phase_10c1_coating_property_consumption_audit_owner_status"
        )

        phase_10c1_complete = bool(
            solved.get("phase_10c1_coating_property_consumption_audit_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10C.1 coating property consumption audit owner exists",
            phase_10c1_complete
            and phase_10c1_status == "PASS_PHASE_10C1_COATING_PROPERTY_CONSUMPTION_AUDIT_OWNER",
            f"status={phase_10c1_status}; complete={phase_10c1_complete}",
        )

        phase_10c2_status = solved.get(
            "phase_10c2_coating_thermal_conductivity_integration_owner_status"
        )

        phase_10c2_complete = bool(
            solved.get("phase_10c2_coating_thermal_conductivity_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10C.2 coating thermal conductivity integration owner exists",
            phase_10c2_complete
            and phase_10c2_status == "PASS_PHASE_10C2_COATING_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER",
            f"status={phase_10c2_status}; complete={phase_10c2_complete}",
        )

        phase_10c3_status = solved.get(
            "phase_10c3_coating_thickness_integration_owner_status"
        )

        phase_10c3_complete = bool(
            solved.get("phase_10c3_coating_thickness_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10C.3 coating thickness integration owner exists",
            phase_10c3_complete
            and phase_10c3_status == "PASS_PHASE_10C3_COATING_THICKNESS_INTEGRATION_OWNER",
            f"status={phase_10c3_status}; complete={phase_10c3_complete}",
        )

        phase_10c4_status = solved.get(
            "phase_10c4_coating_thermal_resistance_integration_owner_status"
        )

        phase_10c4_complete = bool(
            solved.get("phase_10c4_coating_thermal_resistance_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10C.4 coating thermal resistance integration owner exists",
            phase_10c4_complete
            and phase_10c4_status == "PASS_PHASE_10C4_COATING_THERMAL_RESISTANCE_INTEGRATION_OWNER",
            f"status={phase_10c4_status}; complete={phase_10c4_complete}",
        )

        phase_10c5_status = solved.get(
            "phase_10c5_coating_temperature_limit_integration_owner_status"
        )

        phase_10c5_complete = bool(
            solved.get("phase_10c5_coating_temperature_limit_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10C.5 coating temperature limit integration owner exists",
            phase_10c5_complete
            and phase_10c5_status == "PASS_PHASE_10C5_COATING_TEMPERATURE_LIMIT_INTEGRATION_OWNER",
            f"status={phase_10c5_status}; complete={phase_10c5_complete}",
        )

        phase_10c6_status = solved.get(
            "phase_10c6_bond_coat_integration_owner_status"
        )

        phase_10c6_complete = bool(
            solved.get("phase_10c6_bond_coat_integration_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10C.6 bond coat integration owner exists",
            phase_10c6_complete
            and phase_10c6_status == "PASS_PHASE_10C6_BOND_COAT_INTEGRATION_OWNER",
            f"status={phase_10c6_status}; complete={phase_10c6_complete}",
        )

        phase_10c7_status = solved.get(
            "phase_10c7_coating_integration_validation_owner_status"
        )

        phase_10c7_complete = bool(
            solved.get("phase_10c7_coating_integration_validation_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10C.7 coating integration validation owner exists",
            phase_10c7_complete
            and phase_10c7_status in (
                "PASS_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER",
                "FAIL_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER",
            ),
            f"status={phase_10c7_status}; complete={phase_10c7_complete}",
        )

        phase_10c8_status = solved.get(
            "phase_10c8_coating_integration_completion_audit_status"
        )

        phase_10c8_complete = bool(
            solved.get("phase_10c8_coating_integration_completion_audit_complete")
        )

        add_test(
            case_name,
            "Phase 10C.8 coating integration completion audit exists",
            phase_10c8_complete
            and phase_10c8_status in (
                "PASS_COATING_INTEGRATION_COMPLETION_AUDIT",
                "FAIL_COATING_INTEGRATION_COMPLETION_AUDIT",
            ),
            f"status={phase_10c8_status}; complete={phase_10c8_complete}",
        )

        phase_10d1_status = solved.get(
            "phase_10d1_temperature_dependency_discovery_audit_owner_status"
        )

        phase_10d1_complete = bool(
            solved.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
        )

        add_test(
            case_name,
            "Phase 10D.1 temperature dependency discovery audit owner exists",
            phase_10d1_complete
            and phase_10d1_status == "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER",
            f"status={phase_10d1_status}; complete={phase_10d1_complete}",
        )

        phase_10d2_status = solved.get(
            "phase_10d2_material_conductivity_consumption_audit_owner_status"
        )

        phase_10d2_complete = bool(
            solved.get("phase_10d2_material_conductivity_consumption_audit_owner_complete")
        )

        phase_10d2_evidence = solved.get(
            "phase_10d_verification_thermal_chain_evidence",
            {},
        )

        phase_10d2_should_pass = bool(
            solved.get("material_source_validation_mode") == "SOURCED_VALIDATION_MODE"
            and solved.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
            and isinstance(phase_10d2_evidence, dict)
            and phase_10d2_evidence.get("material_thermal_conductivity") is not None
            and phase_10d2_evidence.get("wall_thickness") is not None
            and phase_10d2_evidence.get("hot_gas_heat_transfer_coefficient") is not None
            and phase_10d2_evidence.get("coolant_heat_transfer_coefficient") is not None
            and phase_10d2_evidence.get("adiabatic_wall_temperature") is not None
            and phase_10d2_evidence.get("coolant_bulk_temperature") is not None
        )

        if phase_10d2_should_pass:
            phase_10d2_expected_status = (
                "PASS_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
            )
        else:
            phase_10d2_expected_status = (
                "FAIL_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
            )

        add_test(
            case_name,
            "Phase 10D.2 material conductivity consumption audit owner exists",
            phase_10d2_complete and phase_10d2_status == phase_10d2_expected_status,
            (
                f"status={phase_10d2_status}; "
                f"expected={phase_10d2_expected_status}; "
                f"complete={phase_10d2_complete}"
            ),
        )

        phase_10d3_status = solved.get(
            "phase_10d3_specific_heat_consumption_audit_owner_status"
        )

        phase_10d3_complete = bool(
            solved.get("phase_10d3_specific_heat_consumption_audit_owner_complete")
        )

        phase_10d3_evidence = solved.get(
            "phase_10d_verification_specific_heat_evidence",
            {},
        )

        phase_10d3_should_pass = bool(
            solved.get("material_source_validation_mode") == "SOURCED_VALIDATION_MODE"
            and solved.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
            and isinstance(phase_10d3_evidence, dict)
            and phase_10d3_evidence.get("specific_heat_cp") is not None
            and phase_10d3_evidence.get("heat_load") is not None
            and phase_10d3_evidence.get("coolant_mass_flow") is not None
            and phase_10d3_evidence.get("coolant_inlet_temperature") is not None
        )

        if phase_10d3_should_pass:
            phase_10d3_expected_status = (
                "PASS_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
            )
        else:
            phase_10d3_expected_status = (
                "FAIL_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
            )

        add_test(
            case_name,
            "Phase 10D.3 specific heat consumption audit owner exists",
            phase_10d3_complete and phase_10d3_status == phase_10d3_expected_status,
            (
                f"status={phase_10d3_status}; "
                f"expected={phase_10d3_expected_status}; "
                f"complete={phase_10d3_complete}"
            ),
        )

        phase_10d4_status = solved.get(
            "phase_10d4_density_coolant_property_consumption_audit_owner_status"
        )

        phase_10d4_complete = bool(
            solved.get("phase_10d4_density_coolant_property_consumption_audit_owner_complete")
        )

        phase_10d4_evidence = solved.get(
            "phase_10d_verification_coolant_property_evidence",
            {},
        )

        phase_10d4_should_pass = bool(
            solved.get("material_source_validation_mode") == "SOURCED_VALIDATION_MODE"
            and solved.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
            and isinstance(phase_10d4_evidence, dict)
            and phase_10d4_evidence.get("coolant_density") is not None
            and phase_10d4_evidence.get("coolant_dynamic_viscosity") is not None
            and phase_10d4_evidence.get("coolant_mass_flow") is not None
            and phase_10d4_evidence.get("coolant_flow_area") is not None
            and phase_10d4_evidence.get("hydraulic_diameter") is not None
            and phase_10d4_evidence.get("flow_length") is not None
            and phase_10d4_evidence.get("coolant_thermal_conductivity") is not None
        )

        if phase_10d4_should_pass:
            phase_10d4_expected_status = (
                "PASS_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"
            )
        else:
            phase_10d4_expected_status = (
                "FAIL_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"
            )

        add_test(
            case_name,
            "Phase 10D.4 density coolant property consumption audit owner exists",
            phase_10d4_complete and phase_10d4_status == phase_10d4_expected_status,
            (
                f"status={phase_10d4_status}; "
                f"expected={phase_10d4_expected_status}; "
                f"complete={phase_10d4_complete}"
            ),
        )

        phase_10d5_status = solved.get(
            "phase_10d5_coating_thermal_consumption_audit_owner_status"
        )

        phase_10d5_complete = bool(
            solved.get("phase_10d5_coating_thermal_consumption_audit_owner_complete")
        )

        coating_name = str(
            solved.get("coating_name") or solved.get("selected_coating") or "NONE"
        ).strip().upper()

        phase_10d5_coating_selected = coating_name not in (
            "",
            "NONE",
            "NO_COATING",
            "N/A",
            "NA",
            "NULL",
        )

        phase_10d5_evidence = solved.get(
            "phase_10d_verification_coating_thermal_evidence",
            {},
        )

        phase_10d5_should_pass = bool(
            not phase_10d5_coating_selected
            or (
                solved.get("coating_source_validation_mode") == "SOURCED_VALIDATION_MODE"
                and solved.get("coating_temperature_table_status") != "MISSING"
                and solved.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
                and isinstance(phase_10d5_evidence, dict)
                and phase_10d5_evidence.get("coating_thermal_conductivity") is not None
                and phase_10d5_evidence.get("coating_thickness") is not None
                and phase_10d5_evidence.get("hot_gas_heat_transfer_coefficient") is not None
                and phase_10d5_evidence.get("coolant_heat_transfer_coefficient") is not None
                and phase_10d5_evidence.get("adiabatic_wall_temperature") is not None
                and phase_10d5_evidence.get("coolant_bulk_temperature") is not None
                and phase_10d5_evidence.get("wall_thermal_resistance") is not None
                and phase_10d5_evidence.get("coating_temperature_limit") is not None
            )
        )

        if phase_10d5_should_pass:
            phase_10d5_expected_status = (
                "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
            )
        else:
            phase_10d5_expected_status = (
                "FAIL_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
            )

        add_test(
            case_name,
            "Phase 10D.5 coating thermal consumption audit owner exists",
            phase_10d5_complete and phase_10d5_status == phase_10d5_expected_status,
            (
                f"status={phase_10d5_status}; "
                f"expected={phase_10d5_expected_status}; "
                f"complete={phase_10d5_complete}"
            ),
        )

        phase_10d6_status = solved.get(
            "phase_10d6_bond_coat_consumption_audit_owner_status"
        )

        phase_10d6_complete = bool(
            solved.get("phase_10d6_bond_coat_consumption_audit_owner_complete")
        )

        bond_active = bool(solved.get("bond_coat_integration_active"))

        bond_name = str(
            solved.get("bond_coat_name") or solved.get("selected_bond_coat") or "NONE"
        ).strip().upper()

        phase_10d6_bond_selected = bond_active or bond_name not in (
            "",
            "NONE",
            "NO_BOND_COAT",
            "N/A",
            "NA",
            "NULL",
        )

        phase_10d6_evidence = solved.get(
            "phase_10d_verification_bond_coat_evidence",
            {},
        )

        phase_10d6_should_pass = bool(
            not phase_10d6_bond_selected
            or (
                solved.get("bond_coat_source_validation_mode") == "SOURCED_VALIDATION_MODE"
                and solved.get("bond_coat_temperature_table_status") != "MISSING"
                and solved.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
                and isinstance(phase_10d6_evidence, dict)
                and phase_10d6_evidence.get("bond_coat_thermal_conductivity") is not None
                and phase_10d6_evidence.get("bond_coat_thickness") is not None
                and phase_10d6_evidence.get("coating_thermal_resistance") is not None
                and phase_10d6_evidence.get("hot_gas_heat_transfer_coefficient") is not None
                and phase_10d6_evidence.get("coolant_heat_transfer_coefficient") is not None
                and phase_10d6_evidence.get("adiabatic_wall_temperature") is not None
                and phase_10d6_evidence.get("coolant_bulk_temperature") is not None
                and phase_10d6_evidence.get("wall_thermal_resistance") is not None
                and phase_10d6_evidence.get("bond_coat_temperature_limit") is not None
            )
        )

        if phase_10d6_should_pass:
            phase_10d6_expected_status = (
                "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
            )
        else:
            phase_10d6_expected_status = (
                "FAIL_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
            )

        add_test(
            case_name,
            "Phase 10D.6 bond-coat consumption audit owner exists",
            phase_10d6_complete and phase_10d6_status == phase_10d6_expected_status,
            (
                f"status={phase_10d6_status}; "
                f"expected={phase_10d6_expected_status}; "
                f"complete={phase_10d6_complete}"
            ),
        )

        phase_10d7_status = solved.get(
            "phase_10d7_temperature_dependent_solver_completion_audit_owner_status"
        )

        phase_10d7_complete = bool(
            solved.get("phase_10d7_temperature_dependent_solver_completion_audit_owner_complete")
        )

        phase_10d7_required_statuses = [
            solved.get("phase_10d1_temperature_dependency_discovery_audit_owner_status"),
            solved.get("phase_10d2_material_conductivity_consumption_audit_owner_status"),
            solved.get("phase_10d3_specific_heat_consumption_audit_owner_status"),
            solved.get("phase_10d4_density_coolant_property_consumption_audit_owner_status"),
            solved.get("phase_10d5_coating_thermal_consumption_audit_owner_status"),
            solved.get("phase_10d6_bond_coat_consumption_audit_owner_status"),
        ]

        phase_10d7_expected_pass_statuses = [
            "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER",
            "PASS_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER",
            "PASS_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER",
            "PASS_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER",
            "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER",
            "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER",
        ]

        phase_10d7_should_pass = phase_10d7_required_statuses == phase_10d7_expected_pass_statuses

        if phase_10d7_should_pass:
            phase_10d7_expected_status = (
                "PASS_PHASE_10D7_TEMPERATURE_DEPENDENT_SOLVER_COMPLETION_AUDIT_OWNER"
            )
        else:
            phase_10d7_expected_status = (
                "FAIL_PHASE_10D7_TEMPERATURE_DEPENDENT_SOLVER_COMPLETION_AUDIT_OWNER"
            )

        add_test(
            case_name,
            "Phase 10D.7 temperature-dependent solver completion audit owner exists",
            phase_10d7_complete and phase_10d7_status == phase_10d7_expected_status,
            (
                f"status={phase_10d7_status}; "
                f"expected={phase_10d7_expected_status}; "
                f"complete={phase_10d7_complete}"
            ),
        )

        phase_11a1_status = solved.get(
            "phase_11a1_regen_geometry_constraint_discovery_audit_owner_status"
        )

        phase_11a1_complete = bool(
            solved.get("phase_11a1_regen_geometry_constraint_discovery_audit_owner_complete")
        )

        phase_11a1_constraints = solved.get(
            "phase_11a1_regen_geometry_constraint_discovery_audit_owner_constraints",
            [],
        )

        phase_11a1_discovered_count = solved.get(
            "phase_11a1_regen_geometry_constraint_discovery_audit_owner_discovered_count",
            0,
        )

        add_test(
            case_name,
            "Phase 11A.1 regen geometry constraint discovery audit owner exists",
            (
                phase_11a1_complete
                and phase_11a1_status
                == "PASS_PHASE_11A1_REGEN_GEOMETRY_CONSTRAINT_DISCOVERY_AUDIT_OWNER"
                and isinstance(phase_11a1_constraints, list)
                and len(phase_11a1_constraints) > 0
                and phase_11a1_discovered_count >= 0
            ),
            (
                f"status={phase_11a1_status}; "
                f"complete={phase_11a1_complete}; "
                f"constraints={len(phase_11a1_constraints)}; "
                f"discovered={phase_11a1_discovered_count}"
            ),
        )

        phase_11a2_status = solved.get(
            "regen_geometry_constraint_validation_owner_status"
        )

        phase_11a2_complete = bool(
            solved.get("regen_geometry_constraint_validation_owner_complete")
        )

        phase_11a2_results = solved.get(
            "regen_geometry_constraint_validation_rules",
            [],
        )

        phase_11a2_engineering_status = solved.get(
            "regen_geometry_constraint_validation_global_status"
        )

        add_test(
            case_name,
            "Phase 11A.2 regen geometry constraint validation owner exists",
            (
                phase_11a2_complete
                and phase_11a2_status
                in (
                    "PASS_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER",
                    "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER",
                )
                and isinstance(phase_11a2_results, list)
                and phase_11a2_engineering_status
                in (
                    "PASS",
                    "BLOCKED",
                    "REVIEW_REQUIRED",
                    "FAIL",
                )
            ),
            (
                f"status={phase_11a2_status}; "
                f"complete={phase_11a2_complete}; "
                f"results={len(phase_11a2_results)}; "
                f"engineering_status={phase_11a2_engineering_status}"
            ),
        )

        phase_11a3_status = solved.get(
            "phase_11a3_regen_geometry_failure_explanation_owner_status"
        )

        phase_11a3_complete = bool(
            solved.get("phase_11a3_regen_geometry_failure_explanation_owner_complete")
        )

        phase_11a3_explanations = solved.get(
            "phase_11a3_regen_geometry_failure_explanation_owner_explanations",
            [],
        )

        phase_11a3_engineering_status = solved.get(
            "phase_11a3_regen_geometry_failure_explanation_owner_engineering_status"
        )

        add_test(
            case_name,
            "Phase 11A.3 regen geometry failure explanation owner exists",
            (
                phase_11a3_complete
                and phase_11a3_status
                == "PASS_PHASE_11A3_REGEN_GEOMETRY_FAILURE_EXPLANATION_OWNER"
                and isinstance(phase_11a3_explanations, list)
                and phase_11a3_engineering_status
                in (
                    "PASS_REGEN_GEOMETRY_FAILURE_EXPLANATION",
                    "WARN_REGEN_GEOMETRY_FAILURE_EXPLANATION",
                    "FAIL_REGEN_GEOMETRY_FAILURE_EXPLANATION",
                )
            ),
            (
                f"status={phase_11a3_status}; "
                f"complete={phase_11a3_complete}; "
                f"explanations={len(phase_11a3_explanations)}; "
                f"engineering_status={phase_11a3_engineering_status}"
            ),
        )

        phase_11a4_status = solved.get(
            "phase_11a4_regen_geometry_recommendation_engine_owner_status"
        )

        phase_11a4_complete = bool(
            solved.get("phase_11a4_regen_geometry_recommendation_engine_owner_complete")
        )

        phase_11a4_recommendations = solved.get(
            "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations",
            [],
        )

        phase_11a4_engineering_status = solved.get(
            "phase_11a4_regen_geometry_recommendation_engine_owner_engineering_status"
        )

        add_test(
            case_name,
            "Phase 11A.4 regen geometry recommendation engine owner exists",
            (
                phase_11a4_complete
                and phase_11a4_status
                == "PASS_PHASE_11A4_REGEN_GEOMETRY_RECOMMENDATION_ENGINE_OWNER"
                and isinstance(phase_11a4_recommendations, list)
                and phase_11a4_engineering_status
                in (
                    "PASS_REGEN_GEOMETRY_RECOMMENDATION_ENGINE",
                    "WARN_REGEN_GEOMETRY_RECOMMENDATION_ENGINE",
                )
            ),
            (
                f"status={phase_11a4_status}; "
                f"complete={phase_11a4_complete}; "
                f"recommendations={len(phase_11a4_recommendations)}; "
                f"engineering_status={phase_11a4_engineering_status}"
            ),
        )

        phase_11a5_status = solved.get(
            "phase_11a5_regen_geometry_apply_recommendation_owner_status"
        )

        phase_11a5_complete = bool(
            solved.get("phase_11a5_regen_geometry_apply_recommendation_owner_complete")
        )

        phase_11a5_candidate = solved.get(
            "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry",
            {},
        )

        phase_11a5_improvement = solved.get(
            "phase_11a5_regen_geometry_apply_recommendation_owner_improvement",
            {},
        )

        phase_11a5_engineering_status = solved.get(
            "phase_11a5_regen_geometry_apply_recommendation_owner_engineering_status"
        )

        add_test(
            case_name,
            "Phase 11A.5 apply recommended geometry owner exists",
            (
                phase_11a5_complete
                and phase_11a5_status
                == "PASS_PHASE_11A5_REGEN_GEOMETRY_APPLY_RECOMMENDATION_OWNER"
                and isinstance(phase_11a5_candidate, dict)
                and isinstance(phase_11a5_improvement, dict)
                and phase_11a5_engineering_status
                in (
                    "PASS_REGEN_GEOMETRY_APPLY_RECOMMENDATION",
                    "WARN_REGEN_GEOMETRY_APPLY_RECOMMENDATION_CANDIDATE_CREATED",
                )
            ),
            (
                f"status={phase_11a5_status}; "
                f"complete={phase_11a5_complete}; "
                f"candidate_keys={len(phase_11a5_candidate)}; "
                f"engineering_status={phase_11a5_engineering_status}"
            ),
        )

        phase_11a6_status = solved.get(
            "phase_11a6_regen_geometry_output_architecture_owner_status"
        )

        phase_11a6_complete = bool(
            solved.get("phase_11a6_regen_geometry_output_architecture_owner_complete")
        )

        phase_11a6_report = solved.get(
            "phase_11a6_regen_geometry_output_architecture_owner_report",
            {},
        )

        phase_11a6_summary = solved.get(
            "phase_11a6_regen_geometry_output_architecture_owner_summary",
            {},
        )

        phase_11a6_engineering_status = solved.get(
            "phase_11a6_regen_geometry_output_architecture_owner_engineering_status"
        )

        add_test(
            case_name,
            "Phase 11A.6 regen geometry output architecture owner exists",
            (
                phase_11a6_complete
                and phase_11a6_status
                == "PASS_PHASE_11A6_REGEN_GEOMETRY_OUTPUT_ARCHITECTURE_OWNER"
                and isinstance(phase_11a6_report, dict)
                and isinstance(phase_11a6_summary, dict)
                and phase_11a6_engineering_status
                in (
                    "PASS_REGEN_GEOMETRY_OUTPUT_ARCHITECTURE",
                    "WARN_REGEN_GEOMETRY_OUTPUT_ARCHITECTURE_ACTIONABLE",
                )
            ),
            (
                f"status={phase_11a6_status}; "
                f"complete={phase_11a6_complete}; "
                f"summary_keys={len(phase_11a6_summary)}; "
                f"engineering_status={phase_11a6_engineering_status}"
            ),
        )

        try:
            from regen_geometry_output_window import RegenGeometryOutputWindow
            regen_geometry_window_importable = RegenGeometryOutputWindow is not None
        except Exception:
            regen_geometry_window_importable = False

        add_test(
            case_name,
            "Phase 11A.7 regen geometry output window is importable",
            regen_geometry_window_importable,
            f"importable={regen_geometry_window_importable}",
        )

        phase_11a8_status = solved.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_status"
        )

        phase_11a8_complete = bool(
            solved.get("phase_11a8_regen_geometry_candidate_acceptance_owner_complete")
        )

        phase_11a8_patch = solved.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch",
            {},
        )

        phase_11a8_record = solved.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_record",
            {},
        )

        phase_11a8_engineering_status = solved.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_engineering_status"
        )

        add_test(
            case_name,
            "Phase 11A.8 regen geometry candidate acceptance owner exists",
            (
                phase_11a8_complete
                and phase_11a8_status
                == "PASS_PHASE_11A8_REGEN_GEOMETRY_CANDIDATE_ACCEPTANCE_OWNER"
                and isinstance(phase_11a8_patch, dict)
                and isinstance(phase_11a8_record, dict)
                and phase_11a8_engineering_status
                in (
                    "PASS_REGEN_GEOMETRY_NO_CANDIDATE_ACCEPTANCE_REQUIRED",
                    "WARN_REGEN_GEOMETRY_CANDIDATE_READY_FOR_USER_ACCEPTANCE",
                )
            ),
            (
                f"status={phase_11a8_status}; "
                f"complete={phase_11a8_complete}; "
                f"patch_keys={len(phase_11a8_patch)}; "
                f"engineering_status={phase_11a8_engineering_status}"
            ),
        )

        try:
            from PySide6.QtWidgets import QApplication
            from regen_geometry_output_window import RegenGeometryOutputWindow
            import sys

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            sample_window = RegenGeometryOutputWindow(
                results={
                    "phase_11a6_regen_geometry_output_architecture_owner_report": {
                        "summary": {},
                        "validation": {"grouped_results": {}},
                        "recommendations": {"recommendations": []},
                        "candidate": {"comparison_rows": []},
                    },
                    "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch": {
                        "coolant_channel_width": 0.0012,
                    },
                    "phase_11a8_regen_geometry_candidate_acceptance_owner_record": {
                        "acceptance_ready": True,
                        "changed_keys": ["channel_width"],
                    },
                }
            )

            tab_names = [
                sample_window.tabs.tabText(index)
                for index in range(sample_window.tabs.count())
            ]

            phase_11a9_ready = (
                "Acceptance" in tab_names
                and hasattr(sample_window, "acceptance_patch_text")
                and "coolant_channel_width" in sample_window.acceptance_patch_text.toPlainText()
            )

            sample_window.close()

        except Exception:
            phase_11a9_ready = False

        add_test(
            case_name,
            "Phase 11A.9 candidate acceptance UI controls exist",
            phase_11a9_ready,
            f"phase_11a9_ready={phase_11a9_ready}",
        )

        try:
            from PySide6.QtWidgets import QApplication
            from regen_geometry_output_window import RegenGeometryOutputWindow
            import sys

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            sample_window = RegenGeometryOutputWindow(
                results={
                    "phase_11a6_regen_geometry_output_architecture_owner_report": {
                        "summary": {},
                        "validation": {
                            "grouped_results": {
                                "WARN": [
                                    {
                                        "validation_state": "WARN",
                                        "constraint_id": "coolant_velocity",
                                        "reason": "Coolant velocity is low.",
                                    }
                                ]
                            }
                        },
                        "explanations": {
                            "explanations": [
                                {
                                    "constraint_id": "coolant_velocity",
                                    "failure_mode": "COOLANT_VELOCITY_OUT_OF_GUIDANCE",
                                    "engineering_meaning": "Coolant velocity is low.",
                                }
                            ]
                        },
                        "recommendations": {
                            "recommendations": [
                                {
                                    "priority": "MEDIUM",
                                    "title": "Correct coolant velocity",
                                    "source_constraint": "coolant_velocity",
                                    "target_variables": ["channel_width"],
                                    "expected_benefit": "Raises coolant velocity.",
                                    "proposed_direction": "decrease channel area",
                                }
                            ]
                        },
                        "candidate": {
                            "comparison_rows": [
                                {
                                    "variable": "channel_width",
                                    "before": 0.0015,
                                    "after": 0.001275,
                                    "delta": -0.000225,
                                    "changed": True,
                                }
                            ]
                        },
                    },
                    "phase_11a8_regen_geometry_candidate_acceptance_owner_ready": True,
                    "phase_11a8_regen_geometry_candidate_acceptance_owner_engineering_status": (
                        "WARN_REGEN_GEOMETRY_CANDIDATE_READY_FOR_USER_ACCEPTANCE"
                    ),
                    "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch": {
                        "coolant_channel_width": 0.001275,
                    },
                }
            )

            tab_names = [
                sample_window.tabs.tabText(index)
                for index in range(sample_window.tabs.count())
            ]

            detail_text = sample_window.visual_recommendation_detail_text.toPlainText()

            phase_11a10_ready = (
                "Visual Recommendation" in tab_names
                and hasattr(sample_window, "visual_recommendation_table")
                and "Correct coolant velocity" in detail_text
                and "channel_width" in detail_text
                and "coolant_channel_width" in detail_text
            )

            sample_window.close()

        except Exception:
            phase_11a10_ready = False

        add_test(
            case_name,
            "Phase 11A.10 full visual recommendation integration exists",
            phase_11a10_ready,
            f"phase_11a10_ready={phase_11a10_ready}",
        )

        if verify_foundation_save_load_roundtrip is None:
            add_test(
                case_name,
                "Foundation save/load verifier is available",
                False,
                "foundation_save_load_verification.py could not be imported",
            )
        else:
            save_load_result = verify_foundation_save_load_roundtrip(solved)
            solved.update(save_load_result)

            add_test(
                case_name,
                "Foundation save/load roundtrip preserves required state",
                bool(save_load_result.get("foundation_save_load_verified")),
                save_load_result.get(
                    "foundation_save_load_verification_status",
                    "UNKNOWN",
                ),
            )

        if verify_foundation_ui_launch is None:
            add_test(
                case_name,
                "Foundation UI/report verification is available",
                False,
                "foundation_ui_launch_verification.py could not be imported",
            )
        else:
            ui_result = verify_foundation_ui_launch(
                solved,
                report_bundle_callback=build_report_viewer_bundle_callback,
            )
            solved.update(ui_result)

            add_test(
                case_name,
                "Foundation UI/report bundle verification passes",
                bool(ui_result.get("foundation_ui_launch_verified")),
                ui_result.get(
                    "foundation_ui_launch_verification_status",
                    "UNKNOWN",
                ),
            )
        if case.get("name") == "sourced_valid_no_coating":
            latest_successful_solved = dict(solved)

    passed_count = sum(1 for test in tests if test["passed"])
    failed_count = len(tests) - passed_count

    status = "PASS_FOUNDATION_VERIFICATION" if failed_count == 0 else "FAIL_FOUNDATION_VERIFICATION"

    verification_result = dict(latest_successful_solved)

    verification_result.update({
        "foundation_verification_status": status,
        "foundation_verification_passed_count": passed_count,
        "foundation_verification_failed_count": failed_count,
        "foundation_verification_tests": tests,
        "foundation_verification_text": build_foundation_verification_report(
            status,
            passed_count,
            failed_count,
            tests,
        ),
        "foundation_layer_verified": failed_count == 0,
    })

    if evaluate_foundation_final_signoff is not None:
        verification_result.update(
            evaluate_foundation_final_signoff(verification_result)
        )
    else:
        verification_result.update({
            "foundation_final_signoff_status": "FAIL_FINAL_SIGNOFF_UNAVAILABLE",
            "foundation_final_signoff_complete": False,
            "foundation_final_signoff_text": (
                "Foundation final sign-off controller could not be imported."
            ),
        })

    if build_foundation_completion_handover is not None:
        verification_result.update(
            build_foundation_completion_handover(verification_result)
        )
    else:
        verification_result.update({
            "foundation_completion_handover_status": "FAIL_HANDOVER_UNAVAILABLE",
            "foundation_completion_handover_ready_for_regen_geometry": False,
            "foundation_completion_handover_text": (
                "Foundation completion handover module could not be imported."
            ),
        })

    return _leaf_16t3w1_apply_status_adapter(verification_result)

def build_foundation_verification_report(status, passed_count, failed_count, tests):
    lines = [
        "LEAF FOUNDATION VERIFICATION HARNESS",
        "====================================",
        "",
        f"Status: {status}",
        f"Passed: {passed_count}",
        f"Failed: {failed_count}",
        "",
    ]

    grouped = {}

    for test in tests:
        grouped.setdefault(test["case"], []).append(test)

    for case_name, case_tests in grouped.items():
        lines.append(f"CASE: {case_name}")
        lines.append("-" * (6 + len(case_name)))

        for test in case_tests:
            marker = "PASS" if test["passed"] else "FAIL"
            lines.append(f"[{marker}] {test['name']}")

            if test.get("detail"):
                lines.append(f"  {test['detail']}")

        lines.append("")

    lines.append("Completion Rule:")
    lines.append("- LEAF Foundation Layer Verified only when every verification case passes.")
    lines.append("- Verification passing means the foundation is ready for regen geometry development.")
    lines.append("- Verification failing means fix the foundation before adding new physics.")

    return "\n".join(lines)


def attach_foundation_verification_harness(results):
    return results