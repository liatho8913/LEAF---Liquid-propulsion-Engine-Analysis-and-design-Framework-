from __future__ import annotations
from leaf_qt.status_presentation import status_severity

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

from typing import Any


REQUIRED_PASS_KEYS = {
    "16Q.15 data synchronisation": "phase_16q15_data_sync_pass",
    "16Q.16 station pipeline": "phase_16q16_station_pipeline_pass",
    "16Q.18 station tab": "phase_16q18_station_tab_pass",
    "16Q.19 topology panel": "phase_16q19_topology_panel_pass",
}


def _truthy(value: Any) -> bool:
    return value is True or value == 1 or value == 1.0 or str(value).upper() == "TRUE"


def _num(value: Any, default=None):
    try:
        if value is None or value == "" or value == "N/A":
            return default
        return float(value)
    except Exception:
        return default


def evaluate_final_viewer_runtime_consistency(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    blockers = []
    warnings = []
    checks = {}

    for label, key in REQUIRED_PASS_KEYS.items():
        passed = _truthy(results.get(key))
        checks[label] = {"key": key, "passed": passed, "value": results.get(key)}
        if not passed:
            blockers.append(f"{label} missing/failing: {key}")

    n_main = _num(results.get("number_of_coolant_channels"))
    n_rec = _num(results.get("recommended_geometry_channels"))
    n_station = _num(results.get("viewer_station_number_of_coolant_channels") or results.get("viewer_station_channel_count"))

    if n_main is None:
        blockers.append("Main channel count missing.")
    if n_rec is None:
        blockers.append("Recommended geometry channel count missing.")
    if n_station is None:
        warnings.append("Station channel count missing; station geometry may be partially populated.")

    if n_main is not None and n_rec is not None and int(round(n_main)) != int(round(n_rec)):
        blockers.append(f"Main/recommended channel count mismatch: {n_main} vs {n_rec}")

    w_main = _num(results.get("coolant_channel_width"))
    w_rec = _num(results.get("recommended_geometry_width"))
    w_station = _num(results.get("viewer_station_coolant_channel_width") or results.get("viewer_station_channel_width"))

    if w_main is None or w_rec is None:
        blockers.append("Main/recommended width missing.")
    elif abs(w_main - w_rec) > 1e-12:
        blockers.append(f"Main/recommended width mismatch: {w_main} vs {w_rec}")

    h_main = _num(results.get("coolant_channel_height"))
    h_rec = _num(results.get("recommended_geometry_height"))

    if h_main is None or h_rec is None:
        blockers.append("Main/recommended height missing.")
    elif abs(h_main - h_rec) > 1e-12:
        blockers.append(f"Main/recommended height mismatch: {h_main} vs {h_rec}")

    fit = _num(results.get("viewer_channel_fit_ratio") or results.get("channel_fit_ratio"))
    effective_rib = _num(results.get("viewer_effective_rib_width") or results.get("effective_rib_width"))
    valid = _num(results.get("viewer_channel_geometry_valid") or results.get("channel_geometry_valid"))

    if fit is None or fit < 1.0:
        blockers.append(f"Viewer fit ratio is invalid: {fit}")

    if effective_rib is None or effective_rib <= 0.0:
        blockers.append(f"Viewer effective rib width is invalid: {effective_rib}")

    if valid != 1.0:
        blockers.append(f"Viewer geometry valid flag is not 1.0: {valid}")

    topology_status = str(results.get("channel_topology_status", ""))
    if topology_status in ("", "TOPOLOGY_UNKNOWN"):
        blockers.append("Topology is still unknown.")

    if results.get("phase_16q17_station_fallback_applied") is True:
        warnings.append("Viewer is using fallback station rows, not full solver axial station rows.")

    row_count = _num(results.get("phase_16q16_station_pipeline_row_count") or results.get("phase_16q17_station_fallback_row_count"))
    if row_count is None or row_count <= 0:
        blockers.append("Station row count is missing or zero.")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_FINAL_RUNTIME_CONSISTENCY_GATE_PHASE_16Q20"
            if passed
            else "FAIL_REGEN_VIEWER_FINAL_RUNTIME_CONSISTENCY_GATE_PHASE_16Q20"
        ),
        "passed": passed,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
    }


def build_final_viewer_runtime_consistency_report(results: dict[str, Any]) -> str:
    verdict = evaluate_final_viewer_runtime_consistency(results)

    lines = [
        "LEAF PHASE 16Q.20 — FINAL VIEWER RUNTIME CONSISTENCY GATE",
        "==========================================================",
        f"Status: {verdict['status']}",
        f"Passed: {verdict['passed']}",
        "",
        "CORE CHECKS",
        "-----------",
    ]

    for label, item in verdict["checks"].items():
        state = LegacyCompatibilityProducer.marker_from_bool(item["passed"])
        lines.append(f"{state} | {label} | {item['key']} = {item['value']}")

    lines.extend([
        "",
        "GEOMETRY SNAPSHOT",
        "-----------------",
        f"Channels: {results.get('number_of_coolant_channels')}",
        f"Width: {results.get('coolant_channel_width')}",
        f"Height: {results.get('coolant_channel_height')}",
        f"Rib: {results.get('rib_width')}",
        f"Fit Ratio: {results.get('viewer_channel_fit_ratio', results.get('channel_fit_ratio'))}",
        f"Effective Rib: {results.get('viewer_effective_rib_width', results.get('effective_rib_width'))}",
        f"Geometry Valid: {results.get('viewer_channel_geometry_valid', results.get('channel_geometry_valid'))}",
        "",
        "STATION / TOPOLOGY",
        "------------------",
        f"Station Rows: {results.get('phase_16q16_station_pipeline_row_count', results.get('phase_16q17_station_fallback_row_count'))}",
        f"Selected Station Index: {results.get('selected_station_index')}",
        f"Selected x: {results.get('selected_station_x')}",
        f"Topology Status: {results.get('channel_topology_status')}",
        f"Topology Reason: {results.get('channel_topology_reason')}",
        "",
        "WARNINGS",
        "--------",
    ])

    if verdict["warnings"]:
        for warning in verdict["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")

    lines.extend(["", "BLOCKERS", "--------"])

    if verdict["blockers"]:
        for blocker in verdict["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None")

    return "\n".join(lines)


def attach_final_viewer_runtime_consistency_gate(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_final_viewer_runtime_consistency(results)
    report = build_final_viewer_runtime_consistency_report(results)

    results["phase_16q20_final_runtime_consistency_status"] = verdict["status"]
    results["phase_16q20_final_runtime_consistency_pass"] = verdict["passed"]
    results["phase_16q20_final_runtime_consistency_blockers"] = verdict["blockers"]
    results["phase_16q20_final_runtime_consistency_warnings"] = verdict["warnings"]
    results["phase_16q20_final_runtime_consistency_report"] = report

    if verdict["passed"]:
        results["regen_viewer_runtime_consistent"] = True
        results["regen_viewer_runtime_consistency_status"] = "PASS"
    else:
        results["regen_viewer_runtime_consistent"] = False
        results["regen_viewer_runtime_consistency_status"] = "FAIL"

    return results
