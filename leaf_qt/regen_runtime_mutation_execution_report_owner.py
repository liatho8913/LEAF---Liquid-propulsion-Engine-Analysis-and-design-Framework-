OWNER_NAME = "REGEN_RUNTIME_MUTATION_EXECUTION_REPORT_OWNER"
PHASE = "14A"

PASS_STATUS = "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_REPORT_OWNER_PHASE_14A"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_REPORT_OWNER_PHASE_14A"


def attach_regen_runtime_mutation_execution_report_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_runtime_mutation_execution_report_owner(results)
    results.update(payload)
    return results


def build_regen_runtime_mutation_execution_report_owner(results):
    blockers = []

    registry = results.get("regen_runtime_mutation_execution_registry")
    records = results.get("regen_runtime_mutation_execution_records", [])
    history = results.get("regen_runtime_mutation_execution_history")

    if not isinstance(registry, dict):
        blockers.append("Runtime mutation execution registry is missing.")

    if not isinstance(records, list) or not records:
        blockers.append("Runtime mutation execution records are missing.")

    if not isinstance(history, dict):
        blockers.append("Runtime mutation execution history is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(
        status=status,
        registry=registry,
        records=records,
        history=history,
    )

    return {
        "regen_runtime_mutation_execution_report_owner_complete": True,
        "phase_14a_runtime_mutation_execution_report_owner_complete": True,
        "regen_runtime_mutation_execution_report_owner_ready": ready,
        "regen_runtime_mutation_execution_report_owner_status": status,
        "regen_runtime_mutation_execution_report_owner_blockers": blockers,
        "regen_runtime_mutation_execution_report": report,
    }


def _ready_report(status, registry, records, history):
    lines = [
        "PHASE 14A RUNTIME MUTATION EXECUTION ENGINE",
        f"Status: {status}",
        "",
        "Runtime Mutation State:",
        f"- Registry ready: {registry.get('ready')}",
        f"- Runtime candidates created: {len(records)}",
        f"- History state: {history.get('history_state')}",
        "",
        "Runtime Candidate Records:",
    ]

    for record in records[:20]:
        lines.append(
            f"- {record.get('runtime_candidate_id')} "
            f"from {record.get('source_mutation_package_id')} "
            f"parent={record.get('parent_candidate_id')}"
        )

    lines.extend([
        "",
        "Execution Lock State:",
        "- Solver execution: LOCKED",
        "- Runtime candidate evaluation: LOCKED UNTIL 14B",
        "- Candidate acceptance: LOCKED",
        "- Generation advance: LOCKED",
        "- Live geometry commit: LOCKED",
        "",
        "Meaning:",
        "Mutation packages have been translated into runtime candidate records only.",
        "No regen solver evaluation or live design change has occurred.",
    ])

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 14A RUNTIME MUTATION EXECUTION ENGINE",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]

    for blocker in blockers:
        lines.append(f"- {blocker}")

    return "\n".join(lines)
