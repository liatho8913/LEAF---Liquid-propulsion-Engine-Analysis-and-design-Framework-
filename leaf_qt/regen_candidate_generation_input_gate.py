from leaf_qt.status_presentation import status_severity
"""
PHASE 11F.1
Candidate Generation Architecture Input Gate

Controls whether candidate generation architecture may begin.

Does NOT:
- mutate geometry
- score candidates
- rank candidates
- accept candidates
- commit geometry
- execute solvers
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

OWNER_NAME = "REGEN_CANDIDATE_GENERATION_INPUT_GATE"
PHASE = "11F.1"

PASS_STATUS = "PASS_REGEN_CANDIDATE_GENERATION_INPUT_GATE_PHASE_11F1"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_GENERATION_INPUT_GATE_PHASE_11F1"


def attach_regen_candidate_generation_input_gate(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_generation_input_gate(results))
    return results


def build_regen_candidate_generation_input_gate(results):
    execution_session = results.get("regen_runtime_execution_session", {})
    execution_registry = results.get("regen_runtime_execution_registry", {})

    checks = [
        _check(
            "phase_11e_complete",
            results.get("phase_11e_complete") is True
            and results.get("regen_runtime_execution_architecture_complete") is True,
            "11E runtime execution architecture is complete.",
            "11E runtime execution architecture is not complete.",
        ),
        _check(
            "candidate_generation_architecture_allowed",
            results.get("phase_11f_candidate_generation_architecture_allowed") is True
            and results.get("regen_candidate_generation_architecture_allowed") is True,
            "11F candidate generation architecture may begin.",
            "11F candidate generation architecture is not allowed.",
        ),
        _check(
            "execution_session_exists",
            isinstance(execution_session, dict)
            and bool(execution_session.get("execution_session_id")),
            "Execution session exists.",
            "Execution session missing.",
        ),
        _check(
            "execution_registry_exists",
            isinstance(execution_registry, dict)
            and bool(execution_registry.get("execution_registry_id")),
            "Execution registry exists.",
            "Execution registry missing.",
        ),
        _check(
            "objective_available",
            bool(execution_session.get("objective_mode")),
            "Objective mode is available for future candidates.",
            "Objective mode missing.",
        ),
        _check(
            "population_size_valid",
            isinstance(execution_session.get("population_size"), int)
            and execution_session.get("population_size") >= 4,
            "Population size is valid.",
            "Population size invalid.",
        ),
        _check(
            "generation_limit_valid",
            isinstance(execution_session.get("generation_limit"), int)
            and execution_session.get("generation_limit") >= 1,
            "Generation limit is valid.",
            "Generation limit invalid.",
        ),
        _check(
            "candidate_generation_not_started",
            execution_session.get("current_candidate_id") is None
            and execution_session.get("current_population_id") is None,
            "Candidate generation has not started.",
            "Candidate generation state should be clean before 11F.1.",
        ),
        _check(
            "solver_execution_locked",
            results.get("regen_optimisation_runtime_execution_allowed") is False,
            "Solver/runtime execution remains locked.",
            "Solver/runtime execution must remain locked in 11F.1.",
        ),
        _check(
            "geometry_commit_locked",
            results.get("regen_optimisation_live_geometry_commit_allowed") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11F.1.",
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
        "execution_session_id": execution_session.get("execution_session_id"),
        "execution_registry_id": execution_registry.get("execution_registry_id"),
        "objective_mode": execution_session.get("objective_mode"),
        "candidate_generation_state": "INPUT_GATE_READY_GENERATION_LOCKED" if ready else "BLOCKED",
        "candidate_type_scope": [
            "regen_channel_geometry_candidate",
            "regen_wall_thickness_candidate",
            "regen_cooling_margin_candidate",
            "regen_pressure_drop_candidate",
        ],
        "next_phase": "11F.2_CANDIDATE_GENERATION_SESSION_OWNER" if ready else None,
    }

    return {
        "regen_candidate_generation_input_gate_complete": True,
        "phase_11f_1_regen_candidate_generation_input_gate_complete": True,
        "regen_candidate_generation_input_gate_ready": ready,
        "regen_candidate_generation_input_gate_status": status,
        "regen_candidate_generation_input_gate": gate,
        "regen_candidate_generation_input_gate_checks": checks,
        "regen_candidate_generation_input_gate_failed_checks": failed,
        "regen_candidate_generation_input_gate_report": build_report(status, ready, gate, checks, failed),
        "phase_11f_2_candidate_generation_session_owner_allowed": ready,
        "regen_candidate_generation_session_owner_allowed": ready,
        "regen_candidate_generation_input_gate_passed": ready,
        "regen_candidate_generation_execution_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, gate, checks, failed):
    lines = [
        "PHASE 11F.1 REGEN CANDIDATE GENERATION INPUT GATE",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11F.2 Candidate Generation Session Owner: {ready}",
        "",
        "CANDIDATE GENERATION GATE SNAPSHOT",
        f"Execution Session ID: {gate.get('execution_session_id')}",
        f"Execution Registry ID: {gate.get('execution_registry_id')}",
        f"Objective Mode: {gate.get('objective_mode')}",
        f"Candidate Generation State: {gate.get('candidate_generation_state')}",
        f"Candidate Type Scope: {', '.join(gate.get('candidate_type_scope', []))}",
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
        lines.append("11F.1 candidate generation input gate is complete.")
        lines.append("11F.2 candidate generation session ownership may begin.")
        lines.append("Candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
