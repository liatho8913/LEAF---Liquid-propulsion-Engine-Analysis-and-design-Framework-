"""
PHASE 16K.3 — Viewer Navigation System

Purpose:
- Build a navigation model for rendered regen viewer sections.
- Allow UI to select summary/recommendation/comparison/explanation/root-cause/proof/history.
- Produce default selected section.
- Does not alter geometry.
- Does not rerun solver.
- Does not alter Qt layout yet.
"""

PASS_STATUS = "PASS_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3"
FAIL_STATUS = "FAIL_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3"

SECTION_ORDER = (
    "summary",
    "recommendation",
    "comparison",
    "explanation",
    "root_cause",
    "proof",
    "history",
)

SECTION_LABELS = {
    "summary": "Summary",
    "recommendation": "Recommendation",
    "comparison": "Before / After",
    "explanation": "Explanation",
    "root_cause": "Root Cause",
    "proof": "Proof",
    "history": "History",
}


def attach_regen_viewer_navigation_system(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k2_complete") is not True:
        blockers.append("Phase 16K.2 viewer report renderer has not passed.")

    rendered_sections = results.get("regen_viewer_rendered_sections")
    viewer_payload = results.get("regen_viewer_payload")

    if not isinstance(rendered_sections, dict) or not rendered_sections:
        blockers.append("Rendered viewer sections are missing.")

    if not isinstance(viewer_payload, dict) or not viewer_payload:
        blockers.append("Viewer payload is missing.")

    navigation_items = []
    selected_section = None

    if isinstance(rendered_sections, dict):
        for index, section_key in enumerate(SECTION_ORDER):
            section_text = rendered_sections.get(section_key)
            if not isinstance(section_text, str) or not section_text.strip():
                blockers.append(f"Rendered section missing or empty: {section_key}")
            else:
                navigation_items.append({
                    "index": index,
                    "key": section_key,
                    "label": SECTION_LABELS.get(section_key, section_key),
                    "enabled": True,
                    "has_content": True,
                })

    status = PASS_STATUS if not blockers else FAIL_STATUS

    navigation_payload = None

    if status == PASS_STATUS:
        default_key = "summary"
        selected_section = {
            "key": default_key,
            "label": SECTION_LABELS[default_key],
            "content": rendered_sections[default_key],
            "index": 0,
        }

        navigation_payload = {
            "status": status,
            "source_phase": "16K.3",
            "visibility": "UI_REPORT_VIEW",
            "candidate_id": viewer_payload.get("candidate_id"),
            "navigation_items": navigation_items,
            "default_section_key": default_key,
            "selected_section": selected_section,
            "section_count": len(navigation_items),
            "read_only": True,
        }

    report = _build_report(status, blockers, navigation_payload)

    results["regen_viewer_navigation_system_complete"] = True
    results["phase_16k3_complete"] = status == PASS_STATUS
    results["regen_viewer_navigation_system_status"] = status
    results["phase_16k3_status"] = status
    results["regen_viewer_navigation_system_blockers"] = blockers
    results["regen_viewer_navigation_payload"] = navigation_payload
    results["regen_viewer_selected_section"] = selected_section
    results["regen_viewer_navigation_report"] = report
    results["regen_viewer_navigation_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k4_viewer_ownership_architecture_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, navigation_payload):
    lines = [
        "LEAF PHASE 16K.3 VIEWER NAVIGATION SYSTEM",
        "==========================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Builds navigation model for regen viewer sections.",
        "- Produces default selected section.",
        "- Keeps viewer read-only.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "- Does not alter Qt layout yet.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Navigation:",
        f"- Created: {bool(navigation_payload)}",
        f"- Section count: {(navigation_payload or {}).get('section_count')}",
        f"- Default section: {(navigation_payload or {}).get('default_section_key')}",
        "- Visibility: UI_REPORT_VIEW",
        "",
        "Next Required Phase:",
        "- 16K.4 Viewer Ownership Architecture.",
    ])

    return "\n".join(lines)
