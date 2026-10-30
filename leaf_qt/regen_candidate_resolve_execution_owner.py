"""
PHASE 11B.1H
Regen Candidate Re-Solve Execution Owner

Executes a controlled re-solve on the cloned patched regen candidate state.

Safety:
- Does not mutate live engine geometry.
- Does not overwrite user inputs.
- Does not apply candidate to active design.
- Does not recursively call the full solver unless explicitly provided.
"""


def attach_regen_candidate_resolve_execution_owner(results, solver_callable=None):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_resolve_execution_owner(
        results=results,
        solver_callable=solver_callable,
    )
    results.update(payload)
    return results


def build_regen_candidate_resolve_execution_owner(results, solver_callable=None):
    resolve_ready = bool(results.get("regen_candidate_resolve_ready", False))
    resolve_state = results.get("regen_candidate_resolve_cloned_state") or {}

    blocking_reasons = []

    if not resolve_ready:
        blocking_reasons.append("Resolve preparation owner did not mark the cloned state ready.")

    if not isinstance(resolve_state, dict) or not resolve_state:
        blocking_reasons.append("No cloned resolve state is available.")

    patched_clone = resolve_state.get("patched_clone") if isinstance(resolve_state, dict) else None

    if not isinstance(patched_clone, dict) or not patched_clone:
        blocking_reasons.append("No patched clone input dictionary is available.")

    executed = False
    solve_result = None

    if not blocking_reasons:
        if solver_callable is None:
            blocking_reasons.append(
                "No solver callable was supplied. Re-solve execution is structurally ready "
                "but not executed inside the main solver to avoid recursion."
            )
            status = "WARN_REGEN_CANDIDATE_RESOLVE_EXECUTION_READY_NO_SOLVER_CALLABLE"
        else:
            try:
                solve_result = solver_callable(dict(patched_clone))
                executed = True
                status = "PASS_REGEN_CANDIDATE_RESOLVE_EXECUTED"
            except Exception as exc:
                blocking_reasons.append(f"Solver callable failed: {exc}")
                status = "FAIL_REGEN_CANDIDATE_RESOLVE_EXECUTION_FAILED"
    else:
        status = "FAIL_REGEN_CANDIDATE_RESOLVE_EXECUTION_BLOCKED"

    report = build_resolve_execution_report(
        status=status,
        executed=executed,
        blocking_reasons=blocking_reasons,
        resolve_state=resolve_state,
        solve_result=solve_result,
    )

    return {
        "regen_candidate_resolve_execution_owner_complete": True,
        "phase_11b_1h_regen_candidate_resolve_execution_owner_complete": True,
        "regen_candidate_resolve_execution_owner_status": status,
        "regen_candidate_resolve_execution_executed": executed,
        "regen_candidate_resolve_execution_blocking_reasons": blocking_reasons,
        "regen_candidate_resolve_execution_result": solve_result,
        "regen_candidate_resolve_execution_report": report,

        # Safety locks.
        "regen_candidate_resolve_live_geometry_modified": False,
        "regen_candidate_resolve_original_state_mutated": False,
        "regen_candidate_resolve_candidate_committed": False,

        # Compatibility aliases.
        "recommended_regen_resolve_execution_status": status,
        "recommended_regen_resolve_execution_result": solve_result,
        "recommended_regen_resolve_execution_report": report,
    }


def build_resolve_execution_report(
        status,
        executed,
        blocking_reasons,
        resolve_state,
        solve_result,
):
    lines = [
        "LEAF PHASE 11B.1H REGEN CANDIDATE RE-SOLVE EXECUTION OWNER",
        "===========================================================",
        "",
        f"Status: {status}",
        f"Solver executed: {executed}",
        f"Candidate ID: {resolve_state.get('candidate_id') if isinstance(resolve_state, dict) else None}",
        "",
        "Scope:",
        "- Executes or prepares execution of a re-solve on a cloned patched state.",
        "- Does not mutate the original engine state.",
        "- Does not overwrite live geometry.",
        "- Does not commit the candidate.",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Safety State:",
        "- Live geometry modified: False",
        "- Original state mutated: False",
        "- Candidate committed: False",
    ])

    if solve_result is not None:
        lines.extend([
            "",
            "Solve Result:",
            f"- Type: {type(solve_result).__name__}",
        ])

    return "\n".join(lines)