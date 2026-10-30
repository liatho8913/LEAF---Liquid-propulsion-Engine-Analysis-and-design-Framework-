def build_foundation_completion_handover(results):
    if not isinstance(results, dict):
        return {
            "foundation_completion_handover_status": "FAIL_INVALID_RESULTS",
            "foundation_completion_handover_ready_for_regen_geometry": False,
            "foundation_completion_handover_text": (
                "Foundation completion handover requires a result dictionary."
            ),
        }

    complete = bool(results.get("foundation_final_signoff_complete"))

    blocking = []

    if not complete:
        blocking.append("Final foundation sign-off is not complete.")

    required_statuses = {
        "foundation_verification_status": "PASS_FOUNDATION_VERIFICATION",
        "foundation_final_signoff_status": "PASS_FOUNDATION_FINAL_SIGNOFF",
        "foundation_attachment_pipeline_status": "PASS",
        "foundation_result_key_audit_status": "PASS",
        "foundation_save_load_verification_status": "PASS_FOUNDATION_SAVE_LOAD_VERIFICATION",
        "foundation_ui_launch_verification_status": "PASS_FOUNDATION_UI_LAUNCH_VERIFICATION",
    }

    for key, expected in required_statuses.items():
        actual = results.get(key)
        if actual != expected:
            blocking.append(f"{key} expected {expected}, got {actual}")

    if blocking:
        status = "FAIL_FOUNDATION_COMPLETION_HANDOVER"
        ready = False
    else:
        status = "PASS_FOUNDATION_COMPLETION_HANDOVER"
        ready = True

    return {
        "foundation_completion_handover_status": status,
        "foundation_completion_handover_ready_for_regen_geometry": ready,
        "foundation_completion_handover_blocking_reasons": blocking,
        "foundation_completion_handover_text": build_handover_text(
            status=status,
            ready=ready,
            blocking=blocking,
            results=results,
        ),
    }


def build_handover_text(status, ready, blocking, results):
    lines = [
        "LEAF FOUNDATION COMPLETION HANDOVER",
        "==================================",
        "",
        f"Status: {status}",
        f"Ready for Regen Geometry Completion Phase 1: {ready}",
        "",
        "Verified Foundation Evidence:",
        f"- Foundation verification: {results.get('foundation_verification_status')}",
        f"- Passed tests: {results.get('foundation_verification_passed_count')}",
        f"- Failed tests: {results.get('foundation_verification_failed_count')}",
        f"- Final sign-off: {results.get('foundation_final_signoff_status')}",
        f"- Attachment pipeline: {results.get('foundation_attachment_pipeline_status')}",
        f"- Result key audit: {results.get('foundation_result_key_audit_status')}",
        f"- Save/load verification: {results.get('foundation_save_load_verification_status')}",
        f"- UI/report verification: {results.get('foundation_ui_launch_verification_status')}",
        "",
        "Stage Evidence:",
        f"- Stage U valid-case behaviour: {results.get('stage_u_regen_validation_complete')}",
        f"- Stage V valid-case behaviour: {results.get('stage_v_scalability_complete')}",
        f"- Stage W valid-case behaviour: {results.get('stage_w_real_engine_benchmarking_complete')}",
        "",
        "What Is Now Complete:",
        "- Foundation verification harness.",
        "- Strict result-key and visibility ownership.",
        "- Stage U conservative regen validation verification.",
        "- Stage V regen scalability verification.",
        "- Stage W real-engine benchmark verification.",
        "- Save/load foundation state verification.",
        "- UI/report bundle verification.",
        "- Final foundation sign-off controller.",
        "",
        "What This Means:",
        "- LEAF can now distinguish scalar outputs from reports, diagnostics, validation, recommendations, and audit evidence.",
        "- Placeholder and partial-source data are blocked from trusted PASS states.",
        "- Low-confidence benchmark data is blocked from final benchmark sign-off.",
        "- Out-of-band public benchmark comparisons are blocked from Stage W completion.",
        "- Foundation report ownership and result-key visibility are clean.",
        "",
        "Blocking Reasons:",
    ]

    lines.extend([f"- {item}" for item in blocking] or ["- None."])

    lines.extend([
        "",
        "Next Engineering Phase:",
        "Regen Geometry Completion Phase 1 — Automatic Regen Geometry Solver.",
        "",
        "Initial Regen Geometry Scope:",
        "- Automatic channel count selection.",
        "- Automatic channel width sizing.",
        "- Rib width preservation.",
        "- Circumference fit validation at every station.",
        "- Coolant velocity targeting.",
        "- Pressure drop targeting.",
        "- Wall temperature targeting.",
        "- Material/coating margin targeting.",
        "- Manufacturing minimum constraints.",
        "- Manual vs automatic geometry comparison.",
        "- Iteration history and failure explanation.",
        "",
        "Rule:",
        "- Do not add unrelated new physics before Regen Geometry Completion Phase 1 is complete.",
    ])

    return "\n".join(lines)