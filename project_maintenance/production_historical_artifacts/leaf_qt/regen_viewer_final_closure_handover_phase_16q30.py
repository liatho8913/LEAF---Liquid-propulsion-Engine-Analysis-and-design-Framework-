from __future__ import annotations

from typing import Any


def _truthy(value: Any) -> bool:
    return value is True or value == 1 or value == 1.0 or str(value).upper() == "TRUE"


def evaluate_final_closure_handover(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    required = {
        "Final runtime consistency": "phase_16q20_final_runtime_consistency_pass",
        "Panel cleanup": "phase_16q21_panel_cleanup_pass",
        "Real button toggle": "phase_16q24_real_button_toggle_pass",
        "Automatic cache": "phase_16q25_auto_geometry_cache_available",
        "Cache audit": "phase_16q26_toggle_cache_audit_pass",
        "Toggle UX": "phase_16q27_toggle_ux_pass",
        "GUI runtime acceptance": "phase_16q28_gui_runtime_acceptance_pass",
    }

    blockers = []
    checks = {}

    for label, key in required.items():
        passed = _truthy(results.get(key))
        checks[label] = {"key": key, "passed": passed, "value": results.get(key)}
        if not passed:
            blockers.append(f"{label} missing/failing: {key}")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_FINAL_CLOSURE_HANDOVER_PHASE_16Q30"
            if passed
            else "FAIL_REGEN_VIEWER_FINAL_CLOSURE_HANDOVER_PHASE_16Q30"
        ),
        "passed": passed,
        "checks": checks,
        "blockers": blockers,
    }


def build_final_closure_handover(results: dict[str, Any]) -> str:
    verdict = evaluate_final_closure_handover(results)

    lines = [
        "# LEAF REGEN VIEWER FINAL CLOSURE HANDOVER",
        "",
        "## Phase",
        "",
        "```text",
        "PHASE 16Q.30 — Final Regen Viewer Closure Handover",
        "```",
        "",
        "## Status",
        "",
        "```text",
        f"Status: {verdict['status']}",
        f"Passed: {verdict['passed']}",
        "```",
        "",
        "## Completed Regen Viewer Systems",
        "",
        "```text",
        "16Q.15 Data synchronisation",
        "16Q.16 Authoritative station pipeline",
        "16Q.17 Station row fallback",
        "16Q.18 Station tab population",
        "16Q.19 Topology panel population",
        "16Q.20 Final runtime consistency gate",
        "16Q.21 Panel cleanup and control meaning owner",
        "16Q.22/23/24 Geometry toggle highlight repair",
        "16Q.25 Automatic geometry cache",
        "16Q.26 Cache runtime audit",
        "16Q.27 Toggle UX cleanup",
        "16Q.28 GUI runtime acceptance gate",
        "16Q.29 Copy final GUI acceptance report",
        "```",
        "",
        "## Current Viewer Behaviour",
        "",
        "```text",
        "Recommended/Automatic geometry switching is owned by the exclusive toggle system.",
        "Automatic geometry can be cached after first generation.",
        "Station fallback rows prevent all-N/A station panels when solver station rows are missing.",
        "Topology panel now reports station/fallback availability instead of remaining permanently unknown.",
        "Final GUI acceptance report can be copied from the viewer.",
        "```",
        "",
        "## Checks",
        "",
        "```text",
    ]

    for label, item in verdict["checks"].items():
        state = "PASS" if item["passed"] else "FAIL"
        lines.append(f"{state} | {label} | {item['key']} = {item['value']}")

    lines.extend([
        "```",
        "",
        "## Blockers",
        "",
        "```text",
    ])

    if verdict["blockers"]:
        for blocker in verdict["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None")

    lines.extend([
        "```",
        "",
        "## Next Development Direction",
        "",
        "```text",
        "Do not move into new physics until the live GUI has been visually checked.",
        "If GUI acceptance report passes, the next structural stage should be post-regen viewer cleanup/audit or Phase 17 planning.",
        "```",
    ])

    return "\n".join(lines)


def attach_final_closure_handover(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_final_closure_handover(results)
    handover = build_final_closure_handover(results)

    results["phase_16q30_final_closure_handover_status"] = verdict["status"]
    results["phase_16q30_final_closure_handover_pass"] = verdict["passed"]
    results["phase_16q30_final_closure_handover_blockers"] = verdict["blockers"]
    results["phase_16q30_final_closure_handover"] = handover

    if verdict["passed"]:
        results["regen_viewer_closure_handover_ready"] = True
    else:
        results["regen_viewer_closure_handover_ready"] = False

    return results
