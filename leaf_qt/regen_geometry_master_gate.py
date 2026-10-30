from leaf_qt.structured_status_access import findings_highest_severity, highest_severity as gate_highest_severity, is_pass
REQUIRED_MAPPED_KEYS = [
    "recommended_regen_geometry_solver_status",
    "recommended_regen_geometry_solver_pass",
    "recommended_geometry_constraint_status",
    "recommended_geometry_constraints_pass",
    "recommended_geometry_iteration_history_status",
    "recommended_regen_geometry_report_status",
    "recommended_regen_geometry_failure_owner_status",
    "recommended_number_of_coolant_channels",
    "recommended_coolant_channel_width",
    "recommended_coolant_channel_height",
    "recommended_effective_rib_width",
    "recommended_channel_fit_ratio",
    "recommended_channel_geometry_valid",
    "recommended_coolant_hydraulic_diameter",
    "recommended_coolant_velocity",
    "recommended_coolant_reynolds_number",
]


def evaluate_regen_geometry_master_gate(solver_result):
    failures = []
    warnings = []

    if solver_result is None:
        return {
            "regen_geometry_master_gate_status": "FAIL_REGEN_GEOMETRY_MASTER_GATE",
            "regen_geometry_master_gate_pass": False,
            "regen_geometry_master_gate_failures": ["NO_SOLVER_RESULT"],
            "regen_geometry_master_gate_warnings": [],
        }

    solver_status = solver_result.get("solver_status")
    solver_pass = bool(solver_result.get("solver_pass"))
    best_candidate = solver_result.get("best_candidate")
    candidate_report = solver_result.get("candidate_report", {})
    mapped = solver_result.get("mapped_results", {})
    report = solver_result.get("regen_geometry_report", {})
    failure = solver_result.get("regen_geometry_failure", {})

    if solver_status != "PASS_REGEN_GEOMETRY_SOLVER":
        failures.append("SOLVER_STATUS_NOT_PASS")

    if not solver_pass:
        failures.append("SOLVER_PASS_FALSE")

    if best_candidate is None:
        failures.append("NO_SELECTED_CANDIDATE")

    if not isinstance(candidate_report, dict) or not candidate_report:
        failures.append("MISSING_CANDIDATE_REPORT")

    history = candidate_report.get("iteration_history", {})
    if not isinstance(history, dict) or not history:
        failures.append("MISSING_ITERATION_HISTORY")
    elif history.get("iteration_history_status") != "PASS":
        failures.append("ITERATION_HISTORY_NOT_PASS")

    if not isinstance(mapped, dict) or not mapped:
        failures.append("MISSING_MAPPED_RESULTS")
    else:
        missing_keys = [key for key in REQUIRED_MAPPED_KEYS if key not in mapped]
        if missing_keys:
            failures.append("MISSING_REQUIRED_MAPPED_KEYS")
            warnings.append("Missing mapped keys: " + ", ".join(missing_keys))

        if mapped.get("recommended_geometry_constraints_pass") != 1.0:
            failures.append("CONSTRAINT_OWNER_NOT_PASS")

        if mapped.get("recommended_channel_geometry_valid") != 1.0:
            failures.append("CHANNEL_GEOMETRY_VALID_NOT_TRUE")

        if mapped.get("recommended_regen_geometry_report_status") != "PASS_REGEN_GEOMETRY_REPORT_OWNER":
            failures.append("REPORT_OWNER_NOT_PASS")

        if mapped.get("recommended_regen_geometry_failure_owner_status") != "PASS_REGEN_GEOMETRY_FAILURE_OWNER":
            failures.append("FAILURE_OWNER_NOT_PASS")

    if report.get("regen_geometry_report_status") != "PASS_REGEN_GEOMETRY_REPORT_OWNER":
        failures.append("REPORT_OBJECT_NOT_PASS")

    if failure.get("regen_geometry_failure_owner_status") != "PASS_REGEN_GEOMETRY_FAILURE_OWNER":
        failures.append("FAILURE_OBJECT_NOT_PASS")

    passed = len(failures) == 0

    return {
        "regen_geometry_master_gate_status": (
            "PASS_REGEN_GEOMETRY_MASTER_GATE"
            if passed
            else "FAIL_REGEN_GEOMETRY_MASTER_GATE"
        ),
        "regen_geometry_master_gate_pass": passed,
        "regen_geometry_master_gate_failures": failures,
        "regen_geometry_master_gate_warnings": warnings,
    }


def flatten_regen_geometry_master_gate_result(result, prefix="recommended"):
    failures = result.get("regen_geometry_master_gate_failures", [])
    warnings = result.get("regen_geometry_master_gate_warnings", [])

    return {
        f"{prefix}_regen_geometry_master_gate_status": result.get(
            "regen_geometry_master_gate_status",
            "FAIL_REGEN_GEOMETRY_MASTER_GATE",
        ),
        f"{prefix}_regen_geometry_master_gate_pass": 1.0
        if result.get("regen_geometry_master_gate_pass")
        else 0.0,
        f"{prefix}_regen_geometry_master_gate_failure_count": float(len(failures)),
        f"{prefix}_regen_geometry_master_gate_warning_count": float(len(warnings)),
        f"{prefix}_regen_geometry_master_gate_failures": "; ".join(failures),
        f"{prefix}_regen_geometry_master_gate_warnings": "; ".join(warnings),
    }

# ============================================================
# PHASE 16T.3Q.1 — REGEN GEOMETRY MASTER GATE STATUS ADAPTER
# ============================================================
#
# Non-destructive Wave 2 adapter.
#
# This does not rewrite the existing geometry master gate. It adds a reusable
# status-adapter layer that can be attached to geometry gate result payloads
# while preserving legacy PASS/WARN/FAIL strings.

from typing import Any as _LeafAny_16t3q1

from leaf_qt.global_status_classification_engine import (
    classify_status as _leaf_16t3q1_classify_status,
    make_finding as _leaf_16t3q1_make_finding,
)


_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1 = "Regen Geometry Master Gate"


def _leaf_16t3q1_first_present(results: dict, keys: tuple[str, ...]):
    for key in keys:
        if key in results:
            return results.get(key)
    return None


def _leaf_16t3q1_float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _leaf_16t3q1_bool_or_none(value):
    if value is None:
        return None
    return bool(value)


def _leaf_16t3q1_geometry_master_gate_findings(results: dict) -> list[dict[str, _LeafAny_16t3q1]]:
    findings: list[dict[str, _LeafAny_16t3q1]] = []

    status_keys = (
        "regen_geometry_master_gate_status",
        "regen_geometry_status",
        "regen_geometry_constraint_validation_owner_status",
        "regen_axial_geometry_master_gate_status",
        "regen_variable_geometry_master_gate_status",
        "regen_overall_status",
    )

    evidence = {
        "status_values": {
            key: results.get(key)
            for key in status_keys
            if key in results
        },
        "geometry_valid": _leaf_16t3q1_first_present(
            results,
            (
                "regen_geometry_master_gate_pass",
                "regen_geometry_valid",
                "viewer_channel_geometry_valid",
                "geometry_valid",
            ),
        ),
        "channel_fit_ratio": _leaf_16t3q1_float_or_none(
            _leaf_16t3q1_first_present(
                results,
                (
                    "viewer_channel_fit_ratio",
                    "channel_fit_ratio",
                    "regen_channel_fit_ratio",
                ),
            )
        ),
        "cooling_coverage": _leaf_16t3q1_float_or_none(
            _leaf_16t3q1_first_present(
                results,
                (
                    "viewer_cooling_coverage",
                    "cooling_coverage",
                    "regen_cooling_coverage",
                ),
            )
        ),
        "wall_thickness": _leaf_16t3q1_float_or_none(
            _leaf_16t3q1_first_present(
                results,
                (
                    "hot_gas_wall_thickness",
                    "wall_thickness",
                    "regen_wall_thickness",
                ),
            )
        ),
        "channel_width": _leaf_16t3q1_float_or_none(
            _leaf_16t3q1_first_present(
                results,
                (
                    "coolant_channel_width",
                    "channel_width",
                    "regen_channel_width",
                ),
            )
        ),
        "channel_height": _leaf_16t3q1_float_or_none(
            _leaf_16t3q1_first_present(
                results,
                (
                    "coolant_channel_height",
                    "channel_height",
                    "regen_channel_height",
                ),
            )
        ),
        "channel_count": _leaf_16t3q1_float_or_none(
            _leaf_16t3q1_first_present(
                results,
                (
                    "number_of_coolant_channels",
                    "channel_count",
                    "n_channels",
                ),
            )
        ),
    }

    for key, value in evidence["status_values"].items():
        text = str(value).upper()

        if "FAIL" in text or "INVALID" in text:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"{key} reports failing geometry state: {value}",
                    category="PHYSICS_INVALID",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence={"key": key, "value": value},
                )
            )

        elif "WARN" in text or "REVIEW" in text or "PLACEHOLDER" in text:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"{key} requires geometry review: {value}",
                    category="MANUAL_REVIEW_REQUIRED",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence={"key": key, "value": value},
                )
            )

    geometry_valid = _leaf_16t3q1_bool_or_none(evidence["geometry_valid"])

    if geometry_valid is False:
        findings.append(
            _leaf_16t3q1_make_finding(
                message="Geometry validity flag is false.",
                category="PHYSICS_INVALID",
                owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                evidence=evidence,
            )
        )

    for key in ("wall_thickness", "channel_width", "channel_height"):
        value = evidence[key]

        if value is None:
            continue

        if value <= 0:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"{key} must be positive for geometry master-gate sign-off; got {value}.",
                    category="PHYSICS_INVALID",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence={**evidence, "invalid_key": key, "invalid_value": value},
                )
            )

    channel_count = evidence["channel_count"]

    if channel_count is not None:
        if channel_count <= 0:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"channel_count must be positive; got {channel_count}.",
                    category="PHYSICS_INVALID",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence=evidence,
                )
            )
        elif abs(channel_count - round(channel_count)) > 1e-9:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"channel_count must be integer-like; got {channel_count}.",
                    category="PHYSICS_INVALID",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence=evidence,
                )
            )

    fit_ratio = evidence["channel_fit_ratio"]

    if fit_ratio is not None:
        if fit_ratio > 1.0:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"channel_fit_ratio exceeds available envelope: {fit_ratio}.",
                    category="PHYSICS_INVALID",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence=evidence,
                )
            )
        elif fit_ratio < 0.25:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"channel_fit_ratio is very low and requires review: {fit_ratio}.",
                    category="MANUAL_REVIEW_REQUIRED",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence=evidence,
                )
            )

    coverage = evidence["cooling_coverage"]

    if coverage is not None:
        if coverage < 0.0 or coverage > 1.0:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"cooling_coverage must be between 0 and 1; got {coverage}.",
                    category="PHYSICS_INVALID",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence=evidence,
                )
            )
        elif coverage < 0.5:
            findings.append(
                _leaf_16t3q1_make_finding(
                    message=f"cooling_coverage is below review threshold: {coverage}.",
                    category="MANUAL_REVIEW_REQUIRED",
                    owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                    evidence=evidence,
                )
            )

    if not findings:
        findings.append(
            _leaf_16t3q1_make_finding(
                message="Regen geometry master gate status-adapter checks passed.",
                category="COMPLETE",
                owner=_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_OWNER_16T3Q1,
                evidence=evidence,
            )
        )

    return findings


def build_regen_geometry_master_gate_status_adapter_report(
    results: dict,
    global_status_payload: dict,
) -> str:
    return "\n".join([
        "LEAF PHASE 16T.3Q.1 — REGEN GEOMETRY MASTER GATE STATUS ADAPTER",
        "=================================================================",
        "",
        f"canonical_status: {global_status_payload.get('status')}",
        f"passed: {global_status_payload.get('passed')}",
        f"blocked: {global_status_payload.get('blocked')}",
        f"failed: {global_status_payload.get('failed')}",
        f"finding_count: {global_status_payload.get('finding_count')}",
        "",
        "Legacy Status Evidence:",
        f"- regen_geometry_master_gate_status: {results.get('regen_geometry_master_gate_status')}",
        f"- regen_geometry_status: {results.get('regen_geometry_status')}",
        f"- regen_overall_status: {results.get('regen_overall_status')}",
        "",
        "Rule:",
        "- The existing geometry master gate still owns geometry decisions.",
        "- This adapter classifies the resulting geometry state.",
        "- Invalid geometry maps to FAIL.",
        "- Warning/review geometry states block production sign-off.",
        "- Legacy status strings remain available.",
    ])


def attach_regen_geometry_master_gate_status_adapter(results):
    if not isinstance(results, dict):
        return results

    findings = _leaf_16t3q1_geometry_master_gate_findings(results)

    global_status_payload = _leaf_16t3q1_classify_status(
        findings,
        production_gate=True,
    )

    canonical = global_status_payload.get("status")

    if is_pass(canonical):
        legacy_status = "PASS_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER"
    elif canonical in {"BLOCKED", "REVIEW_REQUIRED"}:
        legacy_status = "WARN_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_REVIEW_REQUIRED"
    else:
        legacy_status = "FAIL_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER"

    results["regen_geometry_master_gate_status_adapter_status"] = legacy_status
    results["regen_geometry_master_gate_structured_findings"] = findings
    results["regen_geometry_master_gate_global_status"] = canonical
    results["regen_geometry_master_gate_global_status_payload"] = global_status_payload
    results["regen_geometry_master_gate_status_adapter_report"] = (
        build_regen_geometry_master_gate_status_adapter_report(
            results,
            global_status_payload,
        )
    )
    results["phase_16t3q1_status_adapter_complete"] = True

    return results
