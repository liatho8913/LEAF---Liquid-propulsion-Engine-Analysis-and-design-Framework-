from __future__ import annotations

from typing import Any


REQUIRED_LAYOUT_REGIONS = (
    "toolbar",
    "main_cross_section",
    "side_profile",
    "engineering_summary",
    "status_strip",
)


def build_viewer_architecture_spec() -> dict[str, Any]:
    return {
        "phase": "16S.1",
        "name": "Regen Viewer Layout Architecture Refactor",
        "regions": list(REQUIRED_LAYOUT_REGIONS),
        "purpose": {
            "toolbar": "Contains only active controls: Recommended, Automatic, Generate/Refresh, Rollback, Full/Fit.",
            "main_cross_section": "Front/rear cross-section canvas.",
            "side_profile": "Side nozzle profile with moving station marker.",
            "engineering_summary": "Clean populated data table; no useless N/A clutter.",
            "status_strip": "Short pass/fail/warning state.",
        },
    }


def evaluate_viewer_architecture(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    blockers = []

    for region in REQUIRED_LAYOUT_REGIONS:
        key = f"phase_16s1_region_{region}_available"
        if results.get(key) is not True:
            blockers.append(f"Missing viewer architecture region: {region}")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_ARCHITECTURE_REFACTOR_PHASE_16S1"
            if passed
            else "FAIL_REGEN_VIEWER_ARCHITECTURE_REFACTOR_PHASE_16S1"
        ),
        "passed": passed,
        "blockers": blockers,
    }


def attach_viewer_architecture_status(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    spec = build_viewer_architecture_spec()
    verdict = evaluate_viewer_architecture(results)

    results["phase_16s1_architecture_spec"] = spec
    results["phase_16s1_architecture_status"] = verdict["status"]
    results["phase_16s1_architecture_pass"] = verdict["passed"]
    results["phase_16s1_architecture_blockers"] = verdict["blockers"]

    return results
