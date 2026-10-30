from leaf_qt.status_presentation import status_severity
"""
PHASE 16K.2 — Regen Viewer Report Renderer

Purpose:
- Render the unified regen viewer payload from 16K.1.
- Produce UI-ready section text.
- Preserve read-only/report-only behaviour.
- Does not modify geometry.
- Does not rerun solver.
- Does not alter Qt layout yet.
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

PASS_STATUS = "PASS_REGEN_VIEWER_REPORT_RENDERER_PHASE_16K2"
FAIL_STATUS = "FAIL_REGEN_VIEWER_REPORT_RENDERER_PHASE_16K2"


SECTION_ORDER = (
    "summary",
    "recommendation",
    "comparison",
    "explanation",
    "root_cause",
    "proof",
    "history",
)


def attach_regen_viewer_report_renderer(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k1_complete") is not True:
        blockers.append("Phase 16K.1 viewer data adapter has not passed.")

    payload = results.get("regen_viewer_payload")

    if not isinstance(payload, dict) or not payload:
        blockers.append("Unified regen viewer payload is missing.")

    rendered_sections = {}
    full_report = None

    if isinstance(payload, dict):
        sections = payload.get("sections") or {}
        for section_name in SECTION_ORDER:
            section = sections.get(section_name)
            if not isinstance(section, dict) or not section:
                blockers.append(f"Viewer section missing or invalid: {section_name}")
            else:
                rendered_sections[section_name] = _render_section(section_name, section)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    if status == PASS_STATUS:
        full_report = _build_full_report(payload, rendered_sections)

    results["regen_viewer_report_renderer_complete"] = True
    results["phase_16k2_complete"] = status == PASS_STATUS
    results["regen_viewer_report_renderer_status"] = status
    results["phase_16k2_status"] = status
    results["regen_viewer_report_renderer_blockers"] = blockers
    results["regen_viewer_rendered_sections"] = rendered_sections
    results["regen_viewer_rendered_report"] = full_report
    results["regen_viewer_report_renderer_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k3_viewer_navigation_system_allowed"] = status == PASS_STATUS

    return results


def _render_section(section_name, section):
    heading = section.get("heading", section_name.replace("_", " ").title())
    lines = [heading, "=" * len(heading), ""]

    if section_name == "summary":
        lines.extend([
            f"Candidate ID: {section.get('candidate_id')}",
            f"Completion State: {section.get('completion_state')}",
            f"Trust Score: {section.get('trust_score')}",
            f"Status: {section.get('status')}",
        ])

    elif section_name == "recommendation":
        lines.extend([
            f"Candidate ID: {section.get('candidate_id')}",
            f"Rank: {section.get('rank')}",
            f"Score: {section.get('score')}",
            "",
            "Reasoning:",
            str(section.get("reasoning")),
            "",
            "Advantages:",
        ])
        lines.extend(_bullet_list(section.get("advantages")))
        lines.append("")
        lines.append("Penalties:")
        lines.extend(_bullet_list(section.get("penalties")))

    elif section_name == "comparison":
        summary = section.get("summary") or {}
        lines.extend([
            f"Compared Outputs: {summary.get('total_compared')}",
            f"Changed Outputs: {summary.get('changed')}",
            f"Improved: {summary.get('improved')}",
            f"Regressed: {summary.get('regressed')}",
            f"Neutral Changed: {summary.get('neutral_changed')}",
            "",
            "Classified Changes:",
        ])
        changes = section.get("classified_changes") or []
        if changes:
            for change in changes:
                lines.append(
                    f"- {change.get('key')}: {change.get('before')} -> "
                    f"{change.get('after')} [{change.get('classification')}]"
                )
        else:
            lines.append("- None.")

    elif section_name == "explanation":
        lines.extend([
            "Headline:",
            str(section.get("headline")),
            "",
            "Why Chosen:",
        ])
        lines.extend(_bullet_list(section.get("why_chosen")))
        trust = section.get("trust_assessment") or {}
        lines.extend([
            "",
            "Trust Assessment:",
            f"- Level: {trust.get('level')}",
            f"- Reason: {trust.get('reason')}",
            "",
            "Remaining Risks:",
        ])
        lines.extend(_bullet_list(section.get("remaining_risks")))
        lines.append("")
        lines.append("Next Actions:")
        lines.extend(_bullet_list(section.get("next_actions")))

    elif section_name == "root_cause":
        summary = section.get("summary") or {}
        lines.extend([
            f"Total Root Causes: {summary.get('total')}",
            f"High Severity: {summary.get('high')}",
            f"Medium Severity: {summary.get('medium')}",
            f"Low Severity: {summary.get('low')}",
            "",
            "Root Causes:",
        ])
        causes = section.get("root_causes") or []
        if causes:
            for cause in causes:
                lines.append(
                    f"- [{cause.get('severity')}] {cause.get('category')}: "
                    f"{cause.get('message')}"
                )
        else:
            lines.append("- None detected.")
        lines.append("")
        lines.append("Next Actions:")
        lines.extend(_bullet_list(section.get("next_actions")))

    elif section_name == "proof":
        lines.extend([
            f"Proof State: {section.get('proof_state')}",
            f"Trust Score: {section.get('trust_score')}",
            "",
            "Proof Ledger:",
        ])
        ledger = section.get("proof_ledger") or []
        if ledger:
            for item in ledger:
                lines.append(
                    f"- {item.get('check')}: "
                    f"{LegacyCompatibilityProducer.marker_from_bool(item.get('passed'))}"
                )
        else:
            lines.append("- None.")

    elif section_name == "history":
        lines.extend([
            f"Event Type: {section.get('event_type')}",
            f"Phase: {section.get('phase')}",
            f"Timestamp UTC: {section.get('timestamp_utc')}",
            "",
            "Chain:",
        ])
        lines.extend(_bullet_list(section.get("chain")))
        lines.append("")
        lines.append("Comparison Summary:")
        summary = section.get("comparison_summary") or {}
        for key, value in summary.items():
            lines.append(f"- {key}: {value}")

    return "\n".join(lines)


def _bullet_list(values):
    if not values:
        return ["- None."]
    if not isinstance(values, list):
        return [f"- {values}"]
    return [f"- {value}" for value in values]


def _build_full_report(payload, rendered_sections):
    lines = [
        "LEAF REGEN VIEWER REPORT",
        "========================",
        "",
        f"Title: {payload.get('title')}",
        f"Candidate ID: {payload.get('candidate_id')}",
        f"Visibility: {payload.get('visibility')}",
        "",
    ]

    ui_state = payload.get("ui_state") or {}
    lines.extend([
        "UI State:",
        f"- Geometry Applied: {ui_state.get('geometry_applied')}",
        f"- Solver Regenerated: {ui_state.get('solver_regenerated')}",
        f"- Report Only: {ui_state.get('report_only')}",
        f"- Editable: {ui_state.get('editable')}",
        "",
    ])

    for section_name in SECTION_ORDER:
        lines.append(rendered_sections[section_name])
        lines.append("")
        lines.append("-" * 72)
        lines.append("")

    return "\n".join(lines)
