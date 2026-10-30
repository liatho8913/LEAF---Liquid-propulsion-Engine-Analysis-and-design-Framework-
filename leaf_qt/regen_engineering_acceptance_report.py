"""
PHASE 16L.2 — Engineering Acceptance Report

Purpose:
- Convert acceptance criteria results into an engineering acceptance report.
- Summarise readiness, evidence, limits, and next actions.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_ENGINEERING_ACCEPTANCE_REPORT_PHASE_16L2"
FAIL_STATUS = "FAIL_REGEN_ENGINEERING_ACCEPTANCE_REPORT_PHASE_16L2"


def attach_regen_engineering_acceptance_report(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16l1_complete") is not True:
        blockers.append("Phase 16L.1 acceptance criteria owner has not passed.")

    criteria_payload = results.get("regen_acceptance_criteria_payload")
    viewer_payload = results.get("regen_viewer_completion_gate_payload")
    optimisation_payload = results.get("regen_optimisation_completion_gate_payload")
    proof_payload = results.get("regen_optimisation_proof_payload")

    for name, payload in (
        ("acceptance criteria payload", criteria_payload),
        ("viewer completion payload", viewer_payload),
        ("optimisation completion payload", optimisation_payload),
        ("optimisation proof payload", proof_payload),
    ):
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing {name}.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report_payload = None
    if status == PASS_STATUS:
        report_payload = {
            "status": status,
            "source_phase": "16L.2",
            "visibility": "REPORT_ONLY",
            "candidate_id": _candidate_id(
                criteria_payload,
                viewer_payload,
                optimisation_payload,
                proof_payload,
            ),
            "readiness": "ENGINEERING_ACCEPTANCE_READY",
            "acceptance_summary": {
                "criteria_count": criteria_payload.get("criteria_count"),
                "passed_count": criteria_payload.get("passed_count"),
                "failed_count": criteria_payload.get("failed_count"),
                "viewer_complete": True,
                "optimisation_complete": True,
                "proof_state": proof_payload.get("proof_state"),
                "trust_score": proof_payload.get("trust_score"),
            },
            "evidence": {
                "acceptance_criteria": criteria_payload,
                "viewer_completion": viewer_payload,
                "optimisation_completion": optimisation_payload,
                "optimisation_proof": proof_payload,
            },
            "limits": [
                "Engineering acceptance confirms the software pipeline, evidence chain, and report visibility.",
                "This does not replace physical hot-fire validation.",
                "This does not certify manufacturability or flight readiness.",
                "This remains dependent on the quality of upstream solver models and material data.",
            ],
            "next_actions": [
                "Run acceptance audit ownership.",
                "Run acceptance master gate.",
                "Proceed to final regen sign-off only after acceptance gate passes.",
            ],
        }

    report = _build_report(status, blockers, report_payload)

    results["regen_engineering_acceptance_report_complete"] = True
    results["phase_16l2_complete"] = status == PASS_STATUS
    results["regen_engineering_acceptance_report_status"] = status
    results["phase_16l2_status"] = status
    results["regen_engineering_acceptance_report_blockers"] = blockers
    results["regen_engineering_acceptance_report_payload"] = report_payload
    results["regen_engineering_acceptance_report"] = report
    results["regen_engineering_acceptance_visibility"] = "REPORT_ONLY"

    results["phase_16l3_acceptance_audit_allowed"] = status == PASS_STATUS

    return results


def _candidate_id(*payloads):
    for payload in payloads:
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")
    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16L.2 ENGINEERING ACCEPTANCE REPORT",
        "================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Converts acceptance criteria into an engineering report.",
        "- Summarises readiness, evidence, limits, and next actions.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    summary = payload.get("acceptance_summary") or {}

    lines.extend([
        "- None.",
        "",
        "Acceptance Summary:",
        f"- Candidate ID: {payload.get('candidate_id')}",
        f"- Readiness: {payload.get('readiness')}",
        f"- Criteria count: {summary.get('criteria_count')}",
        f"- Passed: {summary.get('passed_count')}",
        f"- Failed: {summary.get('failed_count')}",
        f"- Proof state: {summary.get('proof_state')}",
        f"- Trust score: {summary.get('trust_score')}",
        "",
        "Limits:",
    ])

    for item in payload.get("limits", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Next Actions:")

    for item in payload.get("next_actions", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16L.3 Acceptance Audit.",
    ])

    return "\n".join(lines)
