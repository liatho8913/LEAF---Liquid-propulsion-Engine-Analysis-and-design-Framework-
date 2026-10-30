OWNER_NAME = "REGEN_OPTIMISATION_FOUNDATION_REPORT_OWNER"
PHASE = "13L"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_FOUNDATION_REPORT_OWNER_PHASE_13L"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_FOUNDATION_REPORT_OWNER_PHASE_13L"


def attach_regen_optimisation_foundation_report_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_foundation_report_owner(results)
    results.update(payload)
    return results


def build_regen_optimisation_foundation_report_owner(results):
    blockers = []

    registry = results.get("regen_optimisation_foundation_registry")
    validation = results.get("regen_optimisation_foundation_validation")
    history = results.get("regen_optimisation_foundation_history")

    if not isinstance(registry, dict):
        blockers.append("Optimisation foundation registry is missing.")

    if not isinstance(validation, dict):
        blockers.append("Optimisation foundation validation is missing.")

    if not isinstance(history, dict):
        blockers.append("Optimisation foundation history is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(
        registry=registry,
        validation=validation,
        history=history,
        status=status,
    )

    return {
        "regen_optimisation_foundation_report_owner_complete": True,
        "phase_13l_optimisation_foundation_report_owner_complete": True,
        "regen_optimisation_foundation_report_owner_ready": ready,
        "regen_optimisation_foundation_report_owner_status": status,
        "regen_optimisation_foundation_report_owner_blockers": blockers,
        "regen_optimisation_foundation_report": report,
    }


def _ready_report(registry, validation, history, status):
    lines = [
        "PHASE 13L OPTIMISATION FOUNDATION COMPLETION FRAMEWORK",
        f"Status: {status}",
        "",
        "Foundation State:",
        f"- Registry ready: {registry.get('ready')}",
        f"- Validation ready: {validation.get('ready')}",
        f"- History state: {history.get('history_state')}",
        "",
        "Completed Foundation Layers:",
    ]

    for layer in registry.get("completed_foundation_layers", []):
        lines.append(f"- {layer}")

    lines.extend([
        "",
        "Runtime Lock State:",
        "- Runtime optimisation execution: LOCKED",
        "- Solver execution: LOCKED",
        "- Candidate acceptance: LOCKED",
        "- Generation advancement: LOCKED",
        "- Live geometry commit: LOCKED",
        "",
        "Phase 14 Unlock State:",
        "- 14A Runtime Mutation Execution Engine: UNLOCKED NEXT",
        "- 14B Runtime Candidate Evaluation Engine: LOCKED",
        "- 14C Runtime Selection Engine: LOCKED",
        "- 14D Runtime Evolution Engine: LOCKED",
        "- 14E Runtime Convergence Engine: LOCKED",
        "",
        "Meaning:",
        "The optimisation foundation is complete, but no real optimisation runtime has executed yet.",
    ])

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 13L OPTIMISATION FOUNDATION COMPLETION FRAMEWORK",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]

    for blocker in blockers:
        lines.append(f"- {blocker}")

    return "\n".join(lines)
