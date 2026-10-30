from leaf_qt.status_presentation import status_severity
"""
PHASE 12A.1
Candidate Blueprint Generation Input Gate
"""

try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_GENERATION_INPUT_GATE"
PHASE = "12A.1"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_GENERATION_INPUT_GATE_PHASE_12A1"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_GENERATION_INPUT_GATE_PHASE_12A1"


def attach_regen_candidate_blueprint_generation_input_gate(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_candidate_blueprint_generation_input_gate(results))
    return results


def build_regen_candidate_blueprint_generation_input_gate(results):
    creation_audit = results.get("regen_candidate_creation_completion_audit", {})
    creation_registry = results.get("regen_candidate_creation_registry", {})
    creation_session = results.get("regen_candidate_creation_session", {})

    checks = [
        _check(
            "phase_11g_complete",
            results.get("phase_11g_complete") is True
            and results.get("regen_candidate_creation_architecture_complete") is True,
            "11G candidate creation ownership architecture is complete.",
            "11G candidate creation ownership architecture is not complete.",
        ),
        _check(
            "phase_12a_allowed",
            results.get("phase_12a_candidate_blueprint_generation_allowed") is True
            and results.get("regen_candidate_blueprint_generation_allowed") is True,
            "12A blueprint generation architecture may begin.",
            "12A blueprint generation architecture is not allowed.",
        ),
        _check(
            "candidate_creation_completion_audit_exists",
            isinstance(creation_audit, dict) and creation_audit.get("complete") is True,
            "11G completion audit exists and is complete.",
            "11G completion audit missing or incomplete.",
        ),
        _check(
            "candidate_creation_registry_exists",
            isinstance(creation_registry, dict)
            and bool(creation_registry.get("candidate_creation_registry_id")),
            "Candidate creation registry exists.",
            "Candidate creation registry missing.",
        ),
        _check(
            "candidate_creation_session_exists",
            isinstance(creation_session, dict)
            and bool(creation_session.get("candidate_creation_session_id")),
            "Candidate creation session exists.",
            "Candidate creation session missing.",
        ),
        _check(
            "blueprint_scope_available",
            _has_any_key(results, [
                "regen_candidate_creation_package_schema",
                "regen_candidate_creation_registry",
                "regen_candidate_generation_registry",
                "regen_candidate_generation_session",
                "regen_optimisation_registration",
            ]),
            "Blueprint source scope exists.",
            "Blueprint source scope missing.",
        ),
        _check(
            "geometry_input_signals_available",
            _has_any_key(results, [
                "channel_geometry_valid",
                "regen_geometry_constraint_validation_status",
                "regen_geometry_output_architecture_status",
                "coolant_channel_width_m",
                "rib_width_m",
                "coolant_channel_height_m",
                "channel_count",
                "wall_thickness_m",
            ]),
            "Geometry input signals exist for future blueprint generation.",
            "Geometry input signals missing.",
        ),
        _check(
            "thermal_validation_signals_available",
            _has_any_key(results, [
                "regen_validation_status",
                "stage_u_regen_validation_complete",
                "stage_v_regen_scalability_complete",
                "stage_w_real_engine_benchmark_complete",
                "hot_gas_side_wall_temperature",
                "regen_heat_flux",
                "regen_pressure_drop",
            ]),
            "Thermal and validation signals exist for future blueprint generation.",
            "Thermal and validation signals missing.",
        ),
        _check(
            "candidate_creation_locked",
            results.get("regen_candidate_creation_create_candidates_allowed") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked in 12A.1.",
        ),
        _check(
            "blueprint_creation_locked",
            results.get("regen_candidate_blueprint_create_blueprints_allowed") is False,
            "Blueprint creation remains locked.",
            "Blueprint creation must remain locked in 12A.1.",
        ),
        _check(
            "mutation_locked",
            results.get("regen_optimisation_mutation_execution_allowed") is False,
            "Mutation remains locked.",
            "Mutation must remain locked in 12A.1.",
        ),
        _check(
            "runtime_execution_locked",
            results.get("regen_optimisation_runtime_execution_allowed") is False,
            "Runtime optimisation execution remains locked.",
            "Runtime optimisation execution must remain locked in 12A.1.",
        ),
        _check(
            "population_evolution_locked",
            results.get("regen_optimisation_generation_advance_allowed") is False,
            "Population evolution remains locked.",
            "Population evolution must remain locked in 12A.1.",
        ),
        _check(
            "candidate_acceptance_locked",
            results.get("regen_optimisation_candidate_acceptance_allowed") is False,
            "Candidate acceptance remains locked.",
            "Candidate acceptance must remain locked in 12A.1.",
        ),
        _check(
            "live_geometry_commit_locked",
            results.get("regen_optimisation_live_geometry_commit_allowed") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 12A.1.",
        ),
    ]

    failed = [check for check in checks if not check["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    gate = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "candidate_creation_completion_status": results.get(
            "regen_candidate_creation_completion_audit_status"
        ),
        "candidate_creation_session_id": creation_session.get(
            "candidate_creation_session_id"
        ),
        "candidate_creation_registry_id": creation_registry.get(
            "candidate_creation_registry_id"
        ),
        "blueprint_generation_state": (
            "INPUT_GATE_READY_BLUEPRINT_CREATION_LOCKED" if ready else "BLOCKED"
        ),
        "required_input_groups": [
            "candidate_creation_architecture",
            "candidate_creation_registry",
            "candidate_creation_session",
            "geometry_inputs",
            "thermal_inputs",
            "validation_inputs",
            "safety_locks",
        ],
        "next_phase": "12A.2_CANDIDATE_BLUEPRINT_SESSION_OWNER" if ready else None,
    }

    return {
        "regen_candidate_blueprint_generation_input_gate_complete": True,
        "phase_12a_1_regen_candidate_blueprint_generation_input_gate_complete": True,
        "regen_candidate_blueprint_generation_input_gate_ready": ready,
        "regen_candidate_blueprint_generation_input_gate_status": status,
        "regen_candidate_blueprint_generation_input_gate": gate,
        "regen_candidate_blueprint_generation_input_gate_checks": checks,
        "regen_candidate_blueprint_generation_input_gate_failed_checks": failed,
        "regen_candidate_blueprint_generation_input_gate_report": build_report(
            status, ready, gate, checks, failed
        ),

        "phase_12a_2_candidate_blueprint_session_owner_allowed": ready,
        "regen_candidate_blueprint_session_owner_allowed": ready,
        "regen_candidate_blueprint_generation_input_gate_passed": ready,

        "regen_candidate_blueprint_generation_execution_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, gate, checks, failed):
    lines = [
        "PHASE 12A.1 REGEN CANDIDATE BLUEPRINT GENERATION INPUT GATE",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12A.2 Candidate Blueprint Session Owner: {ready}",
        "",
        "INPUT GATE SNAPSHOT",
        f"Candidate Creation Completion Status: {gate.get('candidate_creation_completion_status')}",
        f"Candidate Creation Session ID: {gate.get('candidate_creation_session_id')}",
        f"Candidate Creation Registry ID: {gate.get('candidate_creation_registry_id')}",
        f"Blueprint Generation State: {gate.get('blueprint_generation_state')}",
        f"Required Input Groups: {', '.join(gate.get('required_input_groups', []))}",
        "",
        "CHECKS",
    ]

    for check in checks:
        marker = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{marker}] {check['name']} - {message}")

    if failed:
        lines.append("")
        lines.append("BLOCKERS")
        for check in failed:
            lines.append(f"- {check['name']}: {check['fail_message']}")
    else:
        lines.append("")
        lines.append("RESULT")
        lines.append("12A.1 candidate blueprint generation input gate is complete.")
        lines.append("12A.2 candidate blueprint session ownership may begin.")
        lines.append(
            "Blueprint creation, candidate creation, mutation, scoring, "
            "population evolution, solver execution, and geometry commit remain locked."
        )

    return "\n".join(lines)


def _has_any_key(results, keys):
    return any(key in results for key in keys)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
