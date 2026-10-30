"""
LEAF Regen Scalability Report Owner
===================================

Stage V.2 owner for regen scalability report ownership.

This module does not perform scalability pass/fail logic.
That belongs to:

- regen_scalability_constraint_owner.py

This module owns the readable report explaining:

- scale class
- Stage V.0 profile result
- Stage V.1 constraint result
- missing inputs
- blocking reasons
- warning reasons
- evidence
- next required action
"""


def attach_regen_scalability_report_owner(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_regen_scalability_report_owner(results)
    results.update(audit)
    return results


def evaluate_regen_scalability_report_owner(results):
    results = results if isinstance(results, dict) else {}

    constraint_status = str(
        results.get("regen_scalability_constraint_owner_status")
        or results.get("regen_scalability_framework_status")
        or "UNKNOWN"
    )

    profile_status = str(
        results.get("regen_scalability_profile_status", "UNKNOWN")
    )

    profile_complete = bool(
        results.get("stage_v0_regen_scalability_profile_complete", False)
    )

    constraint_complete = bool(
        results.get("stage_v1_regen_scalability_constraint_owner_complete")
        or results.get("stage_v1_regen_scalability_framework_complete")
        or False
    )

    constraint_text = (
        results.get("regen_scalability_constraint_owner_text")
        or results.get("regen_scalability_text")
    )

    blocking_reasons = _as_list(
        results.get("regen_scalability_constraint_owner_blocking_reasons")
        or results.get("regen_scalability_blocking_reasons")
    )

    warning_reasons = _as_list(
        results.get("regen_scalability_constraint_owner_warning_reasons")
        or results.get("regen_scalability_warning_reasons")
    )

    missing_inputs = _as_list(
        results.get("regen_scalability_constraint_owner_missing_inputs")
    )

    evidence = _as_list(
        results.get("regen_scalability_constraint_owner_evidence")
    )

    blocking = []

    if not profile_complete:
        blocking.append(
            "Stage V.0 scalability profile is incomplete or missing."
        )

    if constraint_status.upper() in {"UNKNOWN", "", "NONE", "N/A"}:
        blocking.append(
            "Stage V.1 scalability constraint owner status is missing."
        )

    if not constraint_text:
        blocking.append(
            "Stage V.1 scalability constraint owner text is missing."
        )

    if blocking:
        status = "FAIL_REGEN_SCALABILITY_REPORT_OWNER"
        complete = False
    else:
        status = "PASS_REGEN_SCALABILITY_REPORT_OWNER"
        complete = True

    text = build_regen_scalability_report_owner_text(
        status=status,
        complete=complete,
        profile_status=profile_status,
        profile_complete=profile_complete,
        constraint_status=constraint_status,
        constraint_complete=constraint_complete,
        engine_class=results.get(
            "regen_scalability_constraint_owner_engine_class",
            results.get(
                "regen_scalability_profile_scale_class",
                results.get("regen_scalability_engine_class", "N/A"),
            ),
        ),
        blocking=blocking,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        missing_inputs=missing_inputs,
        evidence=evidence,
        constraint_text=constraint_text,
    )

    return {
        "regen_scalability_report_owner_status": status,
        "regen_scalability_report_owner_complete": complete,
        "regen_scalability_report_owner_text": text,
        "regen_scalability_report_owner_blocking_reasons": blocking,
        "stage_v2_regen_scalability_report_owner_complete": complete,

        # Backward-compatible existing key from earlier Stage V files.
        "stage_v2_regen_scalability_report_ownership_complete": complete,
    }


def build_regen_scalability_report_owner_text(
    status,
    complete,
    profile_status,
    profile_complete,
    constraint_status,
    constraint_complete,
    engine_class,
    blocking,
    blocking_reasons,
    warning_reasons,
    missing_inputs,
    evidence,
    constraint_text,
):
    lines = [
        "LEAF STAGE V.2 REGEN SCALABILITY REPORT OWNER",
        "================================================",
        "",
        f"Status: {status}",
        f"Complete: {complete}",
        f"Engine scale class: {engine_class}",
        "",
        "Owned By:",
        "- regen_scalability_report_owner.py",
        "",
        "Scope:",
        "- Owns the readable Stage V scalability report.",
        "- Does not classify engine scale.",
        "- Does not perform scalability pass/fail logic.",
        "- Does not benchmark against real engines.",
        "- Does not optimise geometry.",
        "",
        "Architecture Ownership:",
        "- Stage V.0 profile owner: regen_scalability_profile.py",
        "- Stage V.1 constraint owner: regen_scalability_constraint_owner.py",
        "- Stage V.2 report owner: regen_scalability_report_owner.py",
        "",
        "Profile Evidence:",
        f"- Profile status: {profile_status}",
        f"- Profile complete: {profile_complete}",
        "",
        "Constraint Evidence:",
        f"- Constraint owner status: {constraint_status}",
        f"- Constraint owner complete: {constraint_complete}",
        "",
        "Report Owner Blocking Reasons:",
    ]

    lines.extend([f"- {item}" for item in blocking] or ["- None."])

    lines.append("")
    lines.append("Scalability Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Scalability Warning Reasons:")
    lines.extend([f"- {item}" for item in warning_reasons] or ["- None."])

    lines.append("")
    lines.append("Missing Scalability Inputs:")
    lines.extend([f"- {item}" for item in missing_inputs] or ["- None."])

    lines.append("")
    lines.append("Evidence:")
    lines.extend([f"- {item}" for item in evidence] or ["- None."])

    lines.append("")
    lines.append("Next Required Action:")

    if blocking:
        lines.append(
            "- Fix the report-owner blocking reasons before Stage V reporting can be trusted."
        )
    elif blocking_reasons:
        lines.append(
            "- Resolve scalability blocking reasons before Stage V can pass."
        )
    elif warning_reasons:
        lines.append(
            "- Review or resolve scalability warnings before trusted scalability sign-off."
        )
    else:
        lines.append(
            "- Report ownership is complete. Continue to Stage V.3 failure ownership / validation ownership."
        )

    lines.append("")
    lines.append("Constraint Owner Report:")
    lines.append("------------------------")
    lines.append(
        constraint_text
        or "No Stage V.1 scalability constraint owner report was available."
    )

    lines.append("")
    lines.append("Rule:")
    lines.append("- Reports explain decisions; they do not own pass/fail physics.")
    lines.append("- Constraint decisions must remain owned by Stage V.1.")
    lines.append("- Real-engine comparison remains Stage W.")

    return "\n".join(lines)


def _as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]