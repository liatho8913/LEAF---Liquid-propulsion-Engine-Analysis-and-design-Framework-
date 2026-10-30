from leaf_qt.status_presentation import status_severity
"""
PHASE 11C.1
Autonomous Regen Optimisation Input Audit

Architecture-only audit. Does NOT run optimisation, mutation, solver
execution, candidate acceptance, or live geometry commit.
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

OWNER_NAME = "REGEN_AUTONOMOUS_OPTIMISATION_INPUT_AUDIT"
PHASE = "11C.1"

PASS_STATUS = "PASS_REGEN_AUTONOMOUS_OPTIMISATION_INPUT_AUDIT_PHASE_11C1"
FAIL_STATUS = "FAIL_REGEN_AUTONOMOUS_OPTIMISATION_INPUT_AUDIT_PHASE_11C1"

DEFAULT_SETTINGS = {
    "objective_mode": "balanced_regen_geometry",
    "population_size": 16,
    "generation_limit": 8,
    "elite_count": 2,
    "mutation_rate": 0.06,
    "convergence_tolerance": 1.0e-3,
    "runtime_execution_enabled": False,
    "live_geometry_commit_enabled": False,
    "candidate_auto_accept_enabled": False,
}

ALLOWED_OBJECTIVE_MODES = {
    "balanced_regen_geometry",
    "minimise_wall_temperature",
    "minimise_pressure_drop",
    "maximise_geometry_margin",
    "benchmark_similarity",
}


def attach_regen_autonomous_optimisation_input_audit(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_autonomous_optimisation_input_audit(results))
    return results


def build_regen_autonomous_optimisation_input_audit(results):
    settings = dict(DEFAULT_SETTINGS)

    checks = [
        _check(
            "evolution_loop_master_gate_complete",
            results.get("phase_11b_6f_regen_evolution_loop_master_gate_complete") is True
            or results.get("regen_evolution_loop_master_gate_complete") is True,
            "11B.6F evolution-loop master gate is complete.",
            "11B.6F evolution-loop master gate is missing.",
        ),
        _check(
            "evolution_loop_master_gate_ready",
            results.get("regen_evolution_loop_master_gate_ready") is True,
            "Evolution-loop master gate is ready.",
            "Evolution-loop master gate is not ready.",
        ),
        _check(
            "objective_mode_supported",
            settings["objective_mode"] in ALLOWED_OBJECTIVE_MODES,
            "Objective mode is supported.",
            "Objective mode is unsupported.",
        ),
        _check(
            "population_size_valid",
            4 <= settings["population_size"] <= 512,
            "Population size is safe.",
            "Population size is invalid.",
        ),
        _check(
            "generation_limit_valid",
            1 <= settings["generation_limit"] <= 10000,
            "Generation limit is safe.",
            "Generation limit is invalid.",
        ),
        _check(
            "elite_count_valid",
            1 <= settings["elite_count"] < settings["population_size"],
            "Elite count is safe.",
            "Elite count is invalid.",
        ),
        _check(
            "mutation_rate_valid",
            0.0 < settings["mutation_rate"] <= 0.5,
            "Mutation rate is safe.",
            "Mutation rate is invalid.",
        ),
        _check(
            "convergence_tolerance_valid",
            0.0 < settings["convergence_tolerance"] <= 0.1,
            "Convergence tolerance is safe.",
            "Convergence tolerance is invalid.",
        ),
        _check(
            "runtime_execution_disabled",
            settings["runtime_execution_enabled"] is False,
            "Runtime optimisation remains disabled.",
            "Runtime optimisation must remain disabled in 11C.1.",
        ),
        _check(
            "live_commit_disabled",
            settings["live_geometry_commit_enabled"] is False,
            "Live geometry commit remains disabled.",
            "Live geometry commit must remain disabled in 11C.1.",
        ),
        _check(
            "candidate_auto_accept_disabled",
            settings["candidate_auto_accept_enabled"] is False,
            "Candidate auto-accept remains disabled.",
            "Candidate auto-accept must remain disabled in 11C.1.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    report = build_report(status, ready, settings, checks, failed)

    return {
        "regen_autonomous_optimisation_input_audit_complete": True,
        "phase_11c_1_regen_autonomous_optimisation_input_audit_complete": True,
        "regen_autonomous_optimisation_input_audit_ready": ready,
        "regen_autonomous_optimisation_input_audit_status": status,
        "regen_autonomous_optimisation_input_settings": settings,
        "regen_autonomous_optimisation_input_audit_checks": checks,
        "regen_autonomous_optimisation_input_audit_failed_checks": failed,
        "regen_autonomous_optimisation_input_audit_report": report,
        "phase_11c_2_optimisation_session_owner_allowed": ready,
        "regen_optimisation_session_owner_architecture_allowed": ready,
        "regen_autonomous_optimisation_runtime_allowed": False,
        "regen_autonomous_optimisation_solver_execution_allowed": False,
        "regen_autonomous_optimisation_live_commit_allowed": False,
        "regen_autonomous_optimisation_candidate_acceptance_allowed": False,
    }


def build_report(status, ready, settings, checks, failed):
    lines = [
        "PHASE 11C.1 AUTONOMOUS REGEN OPTIMISATION INPUT AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11C.2 Session Owner: {ready}",
        "",
        "SETTINGS SNAPSHOT",
        f"Objective Mode: {settings['objective_mode']}",
        f"Population Size: {settings['population_size']}",
        f"Generation Limit: {settings['generation_limit']}",
        f"Elite Count: {settings['elite_count']}",
        f"Mutation Rate: {settings['mutation_rate']}",
        f"Convergence Tolerance: {settings['convergence_tolerance']}",
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
        lines.append("11C.1 input audit is complete.")
        lines.append("11C.2 optimisation session ownership may begin.")
        lines.append("Runtime optimisation remains locked until 11D.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
