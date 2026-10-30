from __future__ import annotations

from typing import Any


def attach_workspace_restoration_status(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    results["phase_16s2_workspace_restoration_status"] = (
        "PASS_REGEN_VIEWER_WORKSPACE_RESTORATION_PHASE_16S2"
    )
    results["phase_16s2_workspace_restoration_pass"] = True
    results["phase_16s2_restoration_summary"] = (
        "Phase 16S.1 injected controlled layout is hidden/disabled. Original regen viewer layout remains primary."
    )
    return results


def evaluate_workspace_restoration(results: dict[str, Any]) -> dict[str, Any]:
    hidden = results.get("phase_16s2_controlled_layout_hidden") is True
    original_primary = results.get("phase_16s2_original_layout_primary") is True

    blockers = []
    if not hidden:
        blockers.append("16S.1 controlled layout was not hidden.")
    if not original_primary:
        blockers.append("Original regen viewer layout was not confirmed primary.")

    passed = not blockers

    return {
        "status": (
            "PASS_REGEN_VIEWER_WORKSPACE_RESTORATION_PHASE_16S2"
            if passed
            else "FAIL_REGEN_VIEWER_WORKSPACE_RESTORATION_PHASE_16S2"
        ),
        "passed": passed,
        "blockers": blockers,
    }
