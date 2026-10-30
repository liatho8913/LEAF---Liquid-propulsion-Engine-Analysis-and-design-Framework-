from __future__ import annotations

from typing import Any

try:
    from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_auto_geometry_handover_lock_phase_16q10 import (
        attach_auto_geometry_handover_lock,
    )
except Exception:
    attach_auto_geometry_handover_lock = None


def build_clean_handover_export(results: dict[str, Any]) -> str:
    if not isinstance(results, dict):
        results = {}

    if attach_auto_geometry_handover_lock is not None:
        try:
            attach_auto_geometry_handover_lock(results)
        except Exception as exc:
            results["phase_16q11_handover_lock_attach_error"] = str(exc)

    blockers = (
        results.get("phase_16q10_auto_geometry_handover_lock_blockers")
        or results.get("phase_16q7_final_completion_declaration_blockers")
        or []
    )

    lines = [
        "# LEAF REGEN VIEWER CLEAN HANDOVER EXPORT",
        "",
        "## Current Phase",
        "",
        "```text",
        "PHASE 16Q.11 — Clean Regen Viewer Handover Export",
        "```",
        "",
        "## Status",
        "",
        "```text",
        f"Auto Geometry Handover Status: {results.get('regen_viewer_auto_geometry_handover_status')}",
        f"Auto Geometry Handover Ready: {results.get('regen_viewer_auto_geometry_handover_ready')}",
        f"16Q.10 Lock: {results.get('phase_16q10_auto_geometry_handover_lock_status')}",
        f"16Q.9 Realism Runtime: {results.get('phase_16q9_realism_runtime_status')}",
        f"16Q.8 Realism Score: {results.get('phase_16q9_realism_runtime_score')}",
        "```",
        "",
        "## Confirmed Automatic Geometry",
        "",
        "```text",
        f"Channel Count: {results.get('number_of_coolant_channels')}",
        f"Width: {results.get('phase_16p19_runtime_proof_width')}",
        f"Height: {results.get('phase_16p19_runtime_proof_height')}",
        f"Fit Ratio: {results.get('viewer_channel_fit_ratio')}",
        f"Cooling Coverage: {results.get('viewer_cooling_coverage')}",
        f"Effective Rib Width: {results.get('viewer_effective_rib_width')}",
        f"Geometry Valid: {results.get('viewer_channel_geometry_valid')}",
        "```",
        "",
        "## Key Interpretation",
        "",
        "```text",
        "The regen viewer/automatic geometry stack is considered handover-ready only if:",
        "- fit ratio >= 1.0",
        "- cooling coverage <= 0.90",
        "- effective rib width >= 0.25 mm",
        "- realism runtime report passes",
        "- stale old geometry is not detected",
        "```",
        "",
        "## Blockers",
        "",
        "```text",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None")

    lines.extend([
        "```",
        "",
        "## Next Action",
        "",
        "```text",
        "Relaunch LEAF, generate automatic geometry, accept/apply geometry, then copy/paste the Realism Runtime Report.",
        "If the pasted report matches the confirmed 16Q.8/16Q.9 geometry, regen viewer work can be declared complete.",
        "```",
    ])

    return "\n".join(lines)


def attach_clean_handover_export(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    report = build_clean_handover_export(results)

    results["phase_16q11_clean_handover_export"] = report
    results["phase_16q11_clean_handover_export_available"] = True
    results["phase_16q11_clean_handover_export_status"] = (
        "PASS_REGEN_VIEWER_CLEAN_HANDOVER_EXPORT_PHASE_16Q11"
        if "LEAF REGEN VIEWER CLEAN HANDOVER EXPORT" in report
        else "FAIL_REGEN_VIEWER_CLEAN_HANDOVER_EXPORT_PHASE_16Q11"
    )

    return results
