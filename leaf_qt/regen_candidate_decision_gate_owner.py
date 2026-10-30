"""
PHASE 11B.1J
Regen Candidate Improvement Decision Gate Owner

Turns post-re-solve validation into a candidate decision.

Decision states:
- REJECTED
- ACCEPTABLE
- PROMISING
- BEST_SO_FAR

This owner does not commit candidate geometry.
"""


def attach_regen_candidate_decision_gate_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_decision_gate_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_decision_gate_owner(results):
    post_status = results.get("regen_candidate_post_validation_status")
    post_complete = bool(results.get("regen_candidate_post_validation_complete", False))
    score = _num(results.get("regen_candidate_post_validation_score"))

    blocking_reasons = []

    if not post_complete:
        blocking_reasons.append("Post-re-solve validation owner has not completed.")

    if score is None:
        blocking_reasons.append("No numeric post-validation score is available.")

    if blocking_reasons:
        decision = "BLOCKED"
        status = "FAIL_REGEN_CANDIDATE_DECISION_BLOCKED"
        reason = "Candidate decision gate blocked."
    else:
        decision, status, reason = classify_candidate_decision(score)

    report = build_candidate_decision_report(
        status=status,
        decision=decision,
        score=score,
        post_status=post_status,
        reason=reason,
        blocking_reasons=blocking_reasons,
    )

    return {
        "regen_candidate_decision_complete": True,
        "phase_11b_1j_regen_candidate_decision_gate_complete": True,
        "regen_candidate_decision_status": status,
        "regen_candidate_decision": decision,
        "regen_candidate_decision_score": score,
        "regen_candidate_decision_reason": reason,
        "regen_candidate_decision_blocking_reasons": blocking_reasons,
        "regen_candidate_decision_report": report,

        # Safety locks.
        "regen_candidate_decision_committed": False,
        "regen_candidate_decision_live_geometry_modified": False,
    }


def classify_candidate_decision(score):
    if score < 0.0:
        return (
            "REJECTED",
            "PASS_REGEN_CANDIDATE_DECISION_REJECTED",
            "Candidate made the design worse and should be rejected.",
        )

    if score == 0.0:
        return (
            "ACCEPTABLE",
            "PASS_REGEN_CANDIDATE_DECISION_ACCEPTABLE",
            "Candidate is equivalent to baseline and may be retained only for traceability.",
        )

    if score < 0.25:
        return (
            "PROMISING",
            "PASS_REGEN_CANDIDATE_DECISION_PROMISING",
            "Candidate improves the design and should remain in the candidate pool.",
        )

    return (
        "BEST_SO_FAR",
        "PASS_REGEN_CANDIDATE_DECISION_BEST_SO_FAR",
        "Candidate has strong improvement score and should be promoted as best-so-far.",
    )


def build_candidate_decision_report(
        status,
        decision,
        score,
        post_status,
        reason,
        blocking_reasons,
):
    lines = [
        "LEAF PHASE 11B.1J REGEN CANDIDATE DECISION GATE OWNER",
        "======================================================",
        "",
        f"Status: {status}",
        f"Decision: {decision}",
        f"Score: {score}",
        f"Post-validation status: {post_status}",
        "",
        "Reason:",
        f"- {reason}",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for item in blocking_reasons:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Safety State:",
        "- Candidate committed: False",
        "- Live geometry modified: False",
    ])

    return "\n".join(lines)


def _num(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None