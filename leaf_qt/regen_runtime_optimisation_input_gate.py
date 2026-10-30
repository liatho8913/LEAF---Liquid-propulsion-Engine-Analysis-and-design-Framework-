from leaf_qt.status_presentation import status_severity
"""
PHASE 11D.1
Runtime Regen Optimisation Input Gate

This owner decides whether runtime optimisation architecture may begin.

It DOES NOT:
- run optimisation
- advance generations
- execute mutation
- execute solver sweeps
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

OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_INPUT_GATE"
PHASE = "11D.1"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_INPUT_GATE_PHASE_11D1"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_INPUT_GATE_PHASE_11D1"


def attach_regen_runtime_optimisation_input_gate(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_optimisation_input_gate(results))
    return results


def build_regen_runtime_optimisation_input_gate(results):
    session = results.get("regen_optimisation_session", {})
    registry = results.get("regen_optimisation_registry", {})

    checks = [
        _check(
            "phase_11c_complete",
            results.get("phase_11c_complete") is True
            and results.get("regen_optimisation_architecture_complete") is True,
            "11C optimisation ownership architecture is complete.",
            "11C optimisation ownership architecture is not complete.",
        ),
        _check(
            "runtime_architecture_allowed",
            results.get("phase_11d_runtime_optimisation_architecture_allowed") is True
            and results.get("regen_runtime_optimisation_architecture_allowed") is True,
            "11D runtime architecture may begin.",
            "11D runtime architecture is not allowed.",
        ),
        _check(
            "valid_session_exists",
            isinstance(session, dict) and bool(session.get("session_id")),
            "Valid optimisation session exists.",
            "Valid optimisation session missing.",
        ),
        _check(
            "valid_registry_exists",
            isinstance(registry, dict) and bool(registry.get("registry_id")),
            "Valid optimisation registry exists.",
            "Valid optimisation registry missing.",
        ),
        _check(
            "objective_exists",
            bool(session.get("objective_mode")),
            "Objective mode exists.",
            "Objective mode missing.",
        ),
        _check(
            "population_size_valid",
            isinstance(session.get("population_size"), int)
            and session.get("population_size") >= 4,
            "Population size is valid.",
            "Population size invalid.",
        ),
        _check(
            "generation_limit_valid",
            isinstance(session.get("generation_limit"), int)
            and session.get("generation_limit") >= 1,
            "Generation limit is valid.",
            "Generation limit invalid.",
        ),
        _check(
            "generation_count_zero",
            session.get("generation_count") == 0,
            "Generation count is still zero before runtime execution.",
            "Generation count should not advance before runtime execution.",
        ),
        _check(
            "runtime_execution_still_locked",
            results.get("regen_optimisation_runtime_execution_allowed") is False,
            "Runtime execution remains locked by 11D.1.",
            "Runtime execution must remain locked in 11D.1.",
        ),
        _check(
            "live_commit_still_locked",
            results.get("regen_optimisation_live_geometry_commit_allowed") is False,
            "Live geometry commit remains locked by 11D.1.",
            "Live geometry commit must remain locked in 11D.1.",
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
        "session_id": session.get("session_id"),
        "registry_id": registry.get("registry_id"),
        "objective_mode": session.get("objective_mode"),
        "runtime_architecture_state": "INPUT_GATE_READY_RUNTIME_STILL_LOCKED" if ready else "BLOCKED",
        "runtime_execution_state": "LOCKED_UNTIL_11D_RUNTIME_OWNER",
        "next_phase": "11D.2_RUNTIME_OPTIMISATION_SESSION_RUNTIME_OWNER" if ready else None,
    }

    return {
        "regen_runtime_optimisation_input_gate_complete": True,
        "phase_11d_1_regen_runtime_optimisation_input_gate_complete": True,
        "regen_runtime_optimisation_input_gate_ready": ready,
        "regen_runtime_optimisation_input_gate_status": status,
        "regen_runtime_optimisation_input_gate": gate,
        "regen_runtime_optimisation_input_gate_checks": checks,
        "regen_runtime_optimisation_input_gate_failed_checks": failed,
        "regen_runtime_optimisation_input_gate_report": build_report(status, ready, gate, checks, failed),
        "phase_11d_2_runtime_owner_allowed": ready,
        "regen_runtime_optimisation_runtime_owner_allowed": ready,
        "regen_runtime_optimisation_architecture_gate_passed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, gate, checks, failed):
    lines = [
        "PHASE 11D.1 RUNTIME REGEN OPTIMISATION INPUT GATE",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11D.2 Runtime Owner: {ready}",
        "",
        "GATE SNAPSHOT",
        f"Session ID: {gate.get('session_id')}",
        f"Registry ID: {gate.get('registry_id')}",
        f"Objective Mode: {gate.get('objective_mode')}",
        f"Architecture State: {gate.get('runtime_architecture_state')}",
        f"Runtime Execution State: {gate.get('runtime_execution_state')}",
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
        lines.append("11D.1 runtime optimisation input gate is complete.")
        lines.append("11D.2 runtime owner may begin.")
        lines.append("Runtime optimisation remains locked until a later runtime execution owner explicitly unlocks it.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
