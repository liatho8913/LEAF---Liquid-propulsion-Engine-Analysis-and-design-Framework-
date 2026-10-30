"""
PHASE 16M.3 — Final Regen Sign-Off Report

Purpose:
- Produce the final regen sign-off report.
- Summarise completion, verification, acceptance, viewer, optimisation, evidence, limits, and next actions.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_FINAL_SIGNOFF_REPORT_PHASE_16M3"
FAIL_STATUS = "FAIL_REGEN_FINAL_SIGNOFF_REPORT_PHASE_16M3"


def attach_regen_final_signoff_report(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16m2_complete") is not True:
        blockers.append("Phase 16M.2 final regen verification audit has not passed.")

    completion = results.get("regen_final_completion_audit_payload")
    verification = results.get("regen_final_verification_audit_payload")
    acceptance = results.get("regen_acceptance_master_gate_payload")
    viewer = results.get("regen_viewer_completion_gate_payload")
    optimisation = results.get("regen_optimisation_completion_gate_payload")
    engineering = results.get("regen_engineering_acceptance_report_payload")

    required = {
        "completion audit": completion,
        "verification audit": verification,
        "acceptance gate": acceptance,
        "viewer gate": viewer,
        "optimisation gate": optimisation,
        "engineering acceptance report": engineering,
    }

    for name, payload in required.items():
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing {name} payload.")

    candidate_id = _candidate_id(*required.values())

    if not candidate_id:
        blockers.append("Could not resolve candidate ID for final sign-off report.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16M.3",
            "visibility": "REPORT_ONLY",
            "candidate_id": candidate_id,
            "signoff_report_state": "FINAL_REGEN_SIGNOFF_REPORT_READY",
            "completion_summary": {
                "optimisation_complete": True,
                "viewer_complete": True,
                "acceptance_complete": True,
                "completion_audit_passed": True,
                "verification_audit_passed": True,
            },
            "evidence": required,
            "engineering_limits": engineering.get("limits", []),
            "final_statement": (
                "The LEAF regenerative cooling software pipeline has completed "
                "optimisation, viewer integration, acceptance, completion audit, "
                "and verification audit. This is software-system sign-off evidence, "
                "not physical hot-fire certification."
            ),
            "next_actions": [
                "Run final regen master sign-off gate.",
                "Preserve all report-only payloads for UI/export.",
                "Do not start new physics until final master gate passes.",
            ],
        }

    report = _build_report(status, blockers, payload)

    results["regen_final_signoff_report_complete"] = True
    results["phase_16m3_complete"] = status == PASS_STATUS
    results["regen_final_signoff_report_status"] = status
    results["phase_16m3_status"] = status
    results["regen_final_signoff_report_blockers"] = blockers
    results["regen_final_signoff_report_payload"] = payload
    results["regen_final_signoff_report_text"] = report

    results["phase_16m4_final_regen_master_gate_allowed"] = status == PASS_STATUS

    return results


def _candidate_id(*payloads):
    for payload in payloads:
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")
    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16M.3 FINAL REGEN SIGN-OFF REPORT",
        "==============================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Produces final regen sign-off report.",
        "- Summarises completion, verification, acceptance, viewer, optimisation, and limits.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    lines.extend([
        "- None.",
        "",
        "Final Sign-Off Report:",
        f"- Candidate ID: {payload.get('candidate_id')}",
        f"- Report state: {payload.get('signoff_report_state')}",
        "",
        "Completion Summary:",
    ])

    for key, value in payload.get("completion_summary", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "Final Statement:",
        payload.get("final_statement"),
        "",
        "Engineering Limits:",
    ])

    for item in payload.get("engineering_limits", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Next Actions:")

    for item in payload.get("next_actions", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16M.4 Final Regen Master Gate.",
    ])

    return "\n".join(lines)
