from __future__ import annotations

from typing import Any


def _fmt(value: Any) -> str:
    if value in (None, "", "N/A"):
        return "N/A"
    return str(value)


def build_topology_panel_payload(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    station_pass = results.get("phase_16q16_station_pipeline_pass") is True
    fallback_applied = results.get("phase_16q17_station_fallback_applied") is True
    station_tab_pass = results.get("phase_16q18_station_tab_pass") is True

    row_count = (
        results.get("phase_16q17_station_fallback_row_count")
        or results.get("phase_16q16_station_pipeline_row_count")
        or 0
    )

    if station_pass and fallback_applied:
        status = "TOPOLOGY_FALLBACK_PROFILE_AVAILABLE"
        severity = "INFO"
        reason = f"{row_count} viewer fallback station rows available. This is not full solver station topology."
        passed = True
    elif station_pass:
        status = "TOPOLOGY_STATION_DATA_AVAILABLE"
        severity = "INFO"
        reason = f"{row_count} solver station rows available."
        passed = True
    else:
        status = "TOPOLOGY_UNKNOWN"
        severity = "WARN"
        reason = "No usable station payload is available."
        passed = False

    payload = {
        "status": status,
        "severity": severity,
        "passed": passed,
        "reason": reason,
        "row_count": row_count,
        "station_pipeline_pass": station_pass,
        "fallback_applied": fallback_applied,
        "station_tab_pass": station_tab_pass,
        "selected_station_index": results.get("selected_station_index"),
        "selected_station_x": results.get("selected_station_x"),
        "nearest_station_x": results.get("nearest_station_x"),
        "transition_count": max(0, int(row_count or 0) - 1),
    }

    return payload


def build_topology_panel_text(results: dict[str, Any]) -> str:
    payload = build_topology_panel_payload(results)

    lines = [
        "TOPOLOGY / STATION PROFILE",
        "==========================",
        f"Status: {payload['status']}",
        f"Severity: {payload['severity']}",
        f"Passed: {payload['passed']}",
        f"Reason: {payload['reason']}",
        "",
        "PROFILE",
        "-------",
        f"Row Count: {_fmt(payload['row_count'])}",
        f"Transition Count: {_fmt(payload['transition_count'])}",
        f"Fallback Applied: {_fmt(payload['fallback_applied'])}",
        f"Station Pipeline Pass: {_fmt(payload['station_pipeline_pass'])}",
        f"Station Tab Pass: {_fmt(payload['station_tab_pass'])}",
        "",
        "SELECTED STATION",
        "----------------",
        f"Selected Index: {_fmt(payload['selected_station_index'])}",
        f"Selected x: {_fmt(payload['selected_station_x'])}",
        f"Nearest x: {_fmt(payload['nearest_station_x'])}",
    ]

    if payload["fallback_applied"]:
        lines.extend([
            "",
            "IMPORTANT",
            "---------",
            "Fallback topology is viewer-only. It is suitable for UI navigation and geometry inspection,",
            "but it is not a full solver axial thermal/hydraulic solution.",
        ])

    return "\n".join(lines)


def attach_topology_panel_payload(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    payload = build_topology_panel_payload(results)
    text = build_topology_panel_text(results)

    results["phase_16q19_topology_panel_payload"] = payload
    results["phase_16q19_topology_panel_text"] = text
    results["phase_16q19_topology_panel_status"] = (
        "PASS_REGEN_VIEWER_TOPOLOGY_PANEL_PHASE_16Q19"
        if payload["passed"]
        else "WARN_REGEN_VIEWER_TOPOLOGY_PANEL_NO_STATION_PROFILE_PHASE_16Q19"
    )
    results["phase_16q19_topology_panel_pass"] = payload["passed"]

    results["channel_topology_status"] = payload["status"]
    results["channel_topology_severity"] = payload["severity"]
    results["channel_topology_reason"] = payload["reason"]
    results["channel_topology_transition_count"] = payload["transition_count"]

    return results
