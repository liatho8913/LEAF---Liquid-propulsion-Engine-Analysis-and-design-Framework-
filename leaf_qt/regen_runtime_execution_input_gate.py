from leaf_qt.status_presentation import status_severity
"""
PHASE 11E.1
Runtime Regen Optimisation Execution Input Gate

Controls whether execution architecture may begin.

Does NOT:
- run optimisation
- generate candidates
- mutate geometry
- score candidates
- rank candidates
- accept candidates
- commit geometry
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

OWNER_NAME = "REGEN_RUNTIME_EXECUTION_INPUT_GATE"
PHASE = "11E.1"

PASS_STATUS = "PASS_REGEN_RUNTIME_EXECUTION_INPUT_GATE_PHASE_11E1"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EXECUTION_INPUT_GATE_PHASE_11E1"


def attach_regen_runtime_execution_input_gate(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_execution_input_gate(results))
    return results


def build_regen_runtime_execution_input_gate(results):
    runtime_session = results.get("regen_runtime_optimisation_session", {})
    runtime_registry = results.get("regen_runtime_optimisation_registry", {})

    checks = [
        _check(
            "phase_11d_complete",
            results.get("phase_11d_complete") is True
            and results.get("regen_runtime_optimisation_architecture_complete") is True,
            "11D runtime ownership architecture is complete.",
            "11D runtime ownership architecture is not complete.",
        ),
        _check(
            "execution_architecture_allowed",
            results.get("phase_11e_runtime_execution_architecture_allowed") is True
            and results.get("regen_runtime_execution_architecture_allowed") is True,
            "11E runtime execution architecture may begin.",
            "11E runtime execution architecture is not allowed.",
        ),
        _check(
            "runtime_session_exists",
            isinstance(runtime_session, dict)
            and bool(runtime_session.get("runtime_session_id")),
            "Runtime session exists.",
            "Runtime session missing.",
        ),
        _check(
            "runtime_registry_exists",
            isinstance(runtime_registry, dict)
            and bool(runtime_registry.get("runtime_registry_id")),
            "Runtime registry exists.",
            "Runtime registry missing.",
        ),
        _check(
            "runtime_registry_has_session",
            runtime_registry.get("runtime_session_registry", {}).get("runtime_session_count") == 1,
            "Runtime registry contains the runtime session.",
            "Runtime registry does not contain the runtime session.",
        ),
        _check(
            "runtime_registry_has_reports",
            runtime_registry.get("runtime_report_registry", {}).get("runtime_report_count") == 5,
            "Runtime registry contains all runtime reports.",
            "Runtime registry does not contain all runtime reports.",
        ),
        _check(
            "objective_available",
            bool(runtime_session.get("objective_mode")),
            "Runtime objective is available.",
            "Runtime objective missing.",
        ),
        _check(
            "population_size_valid",
            isinstance(runtime_session.get("population_size"), int)
            and runtime_session.get("population_size") >= 4,
            "Runtime population size is valid.",
            "Runtime population size invalid.",
        ),
        _check(
            "generation_limit_valid",
            isinstance(runtime_session.get("generation_limit"), int)
            and runtime_session.get("generation_limit") >= 1,
            "Runtime generation limit is valid.",
            "Runtime generation limit invalid.",
        ),
        _check(
            "execution_not_yet_started",
            runtime_session.get("current_generation_index") == 0
            and runtime_session.get("current_population_id") is None
            and runtime_session.get("current_candidate_id") is None,
            "Execution has not started yet.",
            "Execution state should be clean before 11E.1.",
        ),
        _check(
            "optimisation_execution_still_locked",
            results.get("regen_optimisation_runtime_execution_allowed") is False,
            "Runtime optimisation execution remains locked.",
            "Runtime optimisation execution must remain locked in 11E.1.",
        ),
        _check(
            "geometry_commit_still_locked",
            results.get("regen_optimisation_live_geometry_commit_allowed") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11E.1.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    gate = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "runtime_session_id": runtime_session.get("runtime_session_id"),
        "runtime_registry_id": runtime_registry.get("runtime_registry_id"),
        "objective_mode": runtime_session.get("objective_mode"),
        "execution_architecture_state": "INPUT_GATE_READY_EXECUTION_LOCKED" if ready else "BLOCKED",
        "execution_state": "LOCKED_UNTIL_11E_EXECUTION_SESSION_OWNER",
        "next_phase": "11E.2_RUNTIME_EXECUTION_SESSION_OWNER" if ready else None,
    }

    return {
        "regen_runtime_execution_input_gate_complete": True,
        "phase_11e_1_regen_runtime_execution_input_gate_complete": True,
        "regen_runtime_execution_input_gate_ready": ready,
        "regen_runtime_execution_input_gate_status": status,
        "regen_runtime_execution_input_gate": gate,
        "regen_runtime_execution_input_gate_checks": checks,
        "regen_runtime_execution_input_gate_failed_checks": failed,
        "regen_runtime_execution_input_gate_report": build_report(status, ready, gate, checks, failed),
        "phase_11e_2_runtime_execution_session_owner_allowed": ready,
        "regen_runtime_execution_session_owner_allowed": ready,
        "regen_runtime_execution_input_gate_passed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, gate, checks, failed):
    lines = [
        "PHASE 11E.1 RUNTIME REGEN OPTIMISATION EXECUTION INPUT GATE",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11E.2 Execution Session Owner: {ready}",
        "",
        "EXECUTION GATE SNAPSHOT",
        f"Runtime Session ID: {gate.get('runtime_session_id')}",
        f"Runtime Registry ID: {gate.get('runtime_registry_id')}",
        f"Objective Mode: {gate.get('objective_mode')}",
        f"Execution Architecture State: {gate.get('execution_architecture_state')}",
        f"Execution State: {gate.get('execution_state')}",
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
        lines.append("11E.1 runtime execution input gate is complete.")
        lines.append("11E.2 runtime execution session ownership may begin.")
        lines.append("Execution remains locked until later execution systems explicitly enable it.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
