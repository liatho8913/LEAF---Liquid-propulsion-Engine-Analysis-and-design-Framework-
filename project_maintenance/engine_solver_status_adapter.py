"""Maintenance-owned engine-solver status adapter.

Transferred from leaf_qt.engine_solver by Programme 46Z.
Production runtime does not depend on this maintenance validation surface.
"""

_ENGINE_SOLVER_STATUS_ADAPTER_OWNER = "Engine Solver"


def _leaf_engine_solver_make_finding(message, category, evidence=None):
    if _leaf_status_make_finding is not None:
        return _leaf_status_make_finding(
            message=str(message),
            category=str(category),
            owner=_ENGINE_SOLVER_STATUS_ADAPTER_OWNER,
            evidence=evidence or {},
        )

    return {
        "message": str(message),
        "category": str(category),
        "owner": _ENGINE_SOLVER_STATUS_ADAPTER_OWNER,
        "evidence": evidence or {},
    }


def _leaf_engine_solver_classify(findings):
    if _leaf_status_classify_status is not None:
        return _leaf_status_classify_status(
            findings,
            production_gate=True,
        )

    has_fail = any(
        str(f.get("category", "")).upper() in {
            "PHYSICS_INVALID",
            "VALIDATION_FAILURE",
            "SOLVER_FAILURE",
        }
        for f in findings
    )

    has_block = any(
        str(f.get("category", "")).upper() in {
            "VALIDATION_INCOMPLETE",
            "MANUAL_REVIEW_REQUIRED",
            "PLACEHOLDER_USED_FOR_PASS",
            "PLACEHOLDER_DATA",
        }
        for f in findings
    )

    status = "FAIL" if has_fail else "BLOCKED" if has_block else "PASS"

    return {
        "status": status,
        "passed": status == "PASS",
        "blocked": status == "BLOCKED",
        "failed": status == "FAIL",
        "finding_count": len(findings),
    }


def _leaf_engine_solver_is_bad_number(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False

    return numeric != numeric or numeric in (float("inf"), float("-inf"))


def _leaf_engine_solver_numeric_checks(results):
    checks = []

    positive_required = {
        "chamber_pressure": results.get("chamber_pressure"),
        "chamber_temperature": results.get("chamber_temperature"),
        "mass_flow_rate": results.get("mass_flow_rate"),
        "throat_area": results.get("throat_area"),
        "exit_area": results.get("exit_area"),
        "specific_impulse": results.get("specific_impulse"),
        "vacuum_specific_impulse": results.get("vacuum_specific_impulse"),
        "sea_level_specific_impulse": results.get("sea_level_specific_impulse"),
        "characteristic_velocity": results.get("characteristic_velocity"),
        "thrust": results.get("thrust"),
    }

    non_negative_required = {
        "hot_gas_wall_thickness": results.get("hot_gas_wall_thickness"),
        "coolant_channel_width": results.get("coolant_channel_width"),
        "coolant_channel_height": results.get("coolant_channel_height"),
        "rib_width": results.get("rib_width"),
        "material_temperature_margin": results.get("material_temperature_margin"),
        "regen_axial_worst_material_margin": results.get("regen_axial_worst_material_margin"),
    }

    for key, value in positive_required.items():
        if value is None:
            continue

        if _leaf_engine_solver_is_bad_number(value):
            checks.append((key, value, "invalid numeric value"))
            continue

        try:
            if float(value) <= 0:
                checks.append((key, value, "must be positive"))
        except (TypeError, ValueError):
            pass

    for key, value in non_negative_required.items():
        if value is None:
            continue

        if _leaf_engine_solver_is_bad_number(value):
            checks.append((key, value, "invalid numeric value"))
            continue

        try:
            if float(value) < 0:
                checks.append((key, value, "must be non-negative"))
        except (TypeError, ValueError):
            pass

    return checks


def _leaf_engine_solver_status_findings(results):
    findings = []

    if not isinstance(results, dict):
        return [
            _leaf_engine_solver_make_finding(
                "Engine solver status adapter requires a result dictionary.",
                "SOLVER_FAILURE",
            )
        ]

    status_keys = [
        "regen_overall_status",
        "regen_geometry_status",
        "regen_thermal_status",
        "regen_coolant_status",
        "regen_material_status",
        "best_full_engine_regen_status",
        "final_regen_design_verdict",
        "reference_validation_verdict",
    ]

    for key in status_keys:
        value = results.get(key)

        if value is None:
            continue

        text = str(value).upper()

        evidence = {
            "key": key,
            "value": value,
        }

        if "FAIL" in text or "INVALID" in text:
            category = (
                "PHYSICS_INVALID"
                if key in {
                    "regen_geometry_status",
                    "regen_thermal_status",
                    "regen_coolant_status",
                    "regen_material_status",
                    "regen_overall_status",
                }
                else "VALIDATION_FAILURE"
            )

            findings.append(
                _leaf_engine_solver_make_finding(
                    f"{key} reported non-passing status: {value}",
                    category,
                    evidence=evidence,
                )
            )

        elif "WARN" in text or "REVIEW" in text:
            findings.append(
                _leaf_engine_solver_make_finding(
                    f"{key} requires review: {value}",
                    "MANUAL_REVIEW_REQUIRED",
                    evidence=evidence,
                )
            )

        elif "PLACEHOLDER" in text:
            findings.append(
                _leaf_engine_solver_make_finding(
                    f"{key} contains placeholder status: {value}",
                    "PLACEHOLDER_DATA",
                    evidence=evidence,
                )
            )

    for key, value, reason in _leaf_engine_solver_numeric_checks(results):
        findings.append(
            _leaf_engine_solver_make_finding(
                f"{key} has invalid physics value {value}: {reason}.",
                "PHYSICS_INVALID",
                evidence={
                    "key": key,
                    "value": value,
                    "reason": reason,
                },
            )
        )

    if results.get("thermo_r_error_percent") is not None:
        try:
            thermo_error = abs(float(results.get("thermo_r_error_percent")))
            if thermo_error > 5.0:
                findings.append(
                    _leaf_engine_solver_make_finding(
                        f"Thermodynamic consistency error is high: {thermo_error} percent.",
                        "MANUAL_REVIEW_REQUIRED",
                        evidence={
                            "thermo_r_error_percent": thermo_error,
                        },
                    )
                )
        except (TypeError, ValueError):
            findings.append(
                _leaf_engine_solver_make_finding(
                    "Thermodynamic consistency error is not numeric.",
                    "VALIDATION_INCOMPLETE",
                    evidence={
                        "thermo_r_error_percent": results.get("thermo_r_error_percent"),
                    },
                )
            )

    if not findings:
        findings.append(
            _leaf_engine_solver_make_finding(
                "Engine solver output passed status-adapter checks.",
                "COMPLETE",
                evidence={
                    "has_thrust": results.get("thrust") is not None,
                    "has_specific_impulse": results.get("specific_impulse") is not None,
                    "has_regen_overall_status": results.get("regen_overall_status") is not None,
                },
            )
        )

    return findings


def build_engine_solver_status_adapter_report(results, global_status_payload):
    lines = [
        "LEAF PHASE 16T.3K.9 — ENGINE SOLVER STATUS ADAPTER",
        "===================================================",
        "",
        f"canonical_status: {global_status_payload.get('status')}",
        f"passed: {global_status_payload.get('passed')}",
        f"blocked: {global_status_payload.get('blocked')}",
        f"failed: {global_status_payload.get('failed')}",
        f"finding_count: {global_status_payload.get('finding_count')}",
        "",
        "Key Solver Outputs:",
        f"- thrust: {results.get('thrust') if isinstance(results, dict) else None}",
        f"- specific_impulse: {results.get('specific_impulse') if isinstance(results, dict) else None}",
        f"- chamber_pressure: {results.get('chamber_pressure') if isinstance(results, dict) else None}",
        f"- chamber_temperature: {results.get('chamber_temperature') if isinstance(results, dict) else None}",
        f"- regen_overall_status: {results.get('regen_overall_status') if isinstance(results, dict) else None}",
        "",
        "Rule:",
        "- The physics solver still owns calculations.",
        "- The status adapter only classifies solver output health.",
        "- FAIL/INVALID physics values map to canonical FAIL.",
        "- WARN/REVIEW states block production sign-off until reviewed.",
        "- Legacy solver outputs remain available.",
    ]

    return "\n".join(lines)


def attach_engine_solver_status_adapter(results):
    """
    Phase 16T.3W.2 additive structured-status adapter.

    Reporting wrapper only.
    Does not alter solver calculations, legacy values, or public solver API.
    """
    if not isinstance(results, dict):
        return results

    findings = _leaf_engine_solver_status_findings(results)
    global_status_payload = _leaf_engine_solver_classify(findings)
    adapter_report = build_engine_solver_status_adapter_report(
        findings,
        global_status_payload,
    )

    results.update({
        "engine_solver_status_adapter_complete": True,
        "phase_16t3w2_status_adapter_complete": True,
        "phase_16t3w2_engine_solver_status_adapter_complete": True,
        "engine_solver_structured_findings": findings,
        "engine_solver_global_status": global_status_payload.get("status"),
        "engine_solver_global_status_payload": global_status_payload,
        "engine_solver_adapter_report": adapter_report,
    })

    results.setdefault("structured_findings", findings)
    results.setdefault("global_status", global_status_payload.get("status"))
    results.setdefault("global_status_payload", global_status_payload)
    results.setdefault("adapter_report", adapter_report)

    return results

