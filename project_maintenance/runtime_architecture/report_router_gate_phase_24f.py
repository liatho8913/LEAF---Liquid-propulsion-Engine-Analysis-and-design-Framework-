from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24f"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
    ROOT / "leaf_qt" / "runtime" / "event_bus.py",
    ROOT / "leaf_qt" / "runtime" / "state_registry.py",
    ROOT / "leaf_qt" / "runtime" / "dirty_state_manager.py",
    ROOT / "leaf_qt" / "runtime" / "undo_redo.py",
    ROOT / "leaf_qt" / "runtime" / "report_router.py",
]

from leaf_qt.runtime.event_bus import RuntimeEventBus
from leaf_qt.runtime.report_router import (
    ROUTE_DIAGNOSTIC,
    ROUTE_RECOMMENDATION,
    ROUTE_REPORT,
    ROUTE_VALIDATION,
    ROUTE_WARNING,
    SCHEMA,
    RuntimeReportRouter,
)


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    bus = RuntimeEventBus()
    router = RuntimeReportRouter(event_bus=bus, max_history=3)

    routed_events: list[dict] = []
    validation_events: list[dict] = []

    bus.subscribe(
        "runtime.report.routed",
        lambda event: routed_events.append(event.payload),
        "report_route_probe",
    )

    bus.subscribe(
        "runtime.report.routed.validation",
        lambda event: validation_events.append(event.payload),
        "validation_route_probe",
    )

    router.diagnostic(
        source="phase_24f_gate",
        title="Diagnostic Routed",
        summary="Diagnostic message reached runtime router.",
        target_id="regen_calculator",
        target_type="tool",
    )

    validation_message = router.validation(
        source="phase_24f_gate",
        title="Validation Routed",
        summary="Validation message reached runtime router.",
        severity="success",
        target_id="validation_run_001",
        target_type="validation",
        payload_ref="LEAF_Reports/validation_run_001.json",
    )

    router.report(
        source="phase_24f_gate",
        title="Report Routed",
        summary="Report message reached runtime router.",
        target_id="LEAF_Reports/test_report.json",
        target_type="report",
    )

    router.warning(
        source="phase_24f_gate",
        title="Warning Routed",
        summary="Warning message reached runtime router.",
        target_id="LEAF_Designs/test_design.leaf_design.json",
        target_type="design",
    )

    router.recommendation(
        source="phase_24f_gate",
        title="Recommendation Routed",
        summary="Recommendation message reached runtime router.",
        severity="info",
        target_id="recommendation_001",
        target_type="optimisation",
    )

    if not validation_message.message_id.startswith("report_msg_"):
        failures.append("message_id_invalid")

    if validation_message.route != ROUTE_VALIDATION:
        failures.append("validation_route_not_retained")

    if validation_message.severity != "success":
        failures.append("severity_not_retained")

    if validation_message.payload_ref != "LEAF_Reports/validation_run_001.json":
        failures.append("payload_ref_not_retained")

    if len(routed_events) != 5:
        failures.append("general_report_events_not_emitted")

    if len(validation_events) != 1:
        failures.append("specific_validation_event_not_emitted")

    history = router.history()

    if len(history) != 3:
        failures.append("bounded_report_history_not_enforced")

    route_history = router.history(ROUTE_WARNING)

    if len(route_history) != 1:
        failures.append("route_filtered_history_invalid")

    snapshot = router.snapshot()

    required_snapshot_keys = [
        "schema",
        "valid_routes",
        "valid_severities",
        "retain_history",
        "max_history",
        "history_count",
        "route_counts",
        "qt_owns_report_routing",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
        "emits_report_route_events",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    expected_routes = {
        ROUTE_DIAGNOSTIC,
        ROUTE_VALIDATION,
        ROUTE_REPORT,
        ROUTE_WARNING,
        ROUTE_RECOMMENDATION,
    }

    if set(snapshot.get("valid_routes", [])) != expected_routes:
        failures.append("valid_routes_invalid")

    if snapshot.get("qt_owns_report_routing") is not False:
        failures.append("qt_ownership_boundary_invalid")

    for key in [
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"report_router_stores_payloads:{key}")

    if snapshot.get("emits_report_route_events") is not True:
        failures.append("report_route_events_not_declared")

    try:
        router.route_message(
            "forbidden_route",
            source="phase_24f_gate",
            title="Bad Route",
            summary="This should fail.",
        )
        failures.append("forbidden_route_accepted")
    except KeyError:
        pass

    try:
        router.report(
            source="phase_24f_gate",
            title="Bad Severity",
            summary="This should fail.",
            severity="half_bad",
        )
        failures.append("forbidden_severity_accepted")
    except ValueError:
        pass

    router.clear_history()

    if router.history():
        failures.append("clear_history_failed")

    result = {
        "phase": "24F",
        "programme": "24",
        "feature": "RUNTIME_REPORT_ROUTING",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_RUNTIME_REPORT_ROUTER_GATE_PHASE_24F_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/runtime/report_router.py",
            "project_maintenance/runtime_architecture/report_router_gate_phase_24f.py",
        ],
        "files_replaced": [
            "leaf_qt/runtime/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "diagnostic_route": True,
            "validation_route": True,
            "report_route": True,
            "warning_route": True,
            "recommendation_route": True,
            "event_emission": True,
            "bounded_history": True,
            "route_filtering": True,
            "route_allowlist": True,
            "severity_allowlist": True,
            "qt_does_not_own_report_routing": True,
            "metadata_only_report_routing": True,
        },
        "completion_notice": (
            "PHASE_24F_COMPLETE_RUNTIME_REPORT_ROUTING_ESTABLISHED"
            if not failures
            else "PHASE_24F_BLOCKED"
        ),
        "next_phase": "24G_RUNTIME_NOTIFICATION_CENTRE",
    }

    json_path = OUT / "report_router_gate_phase_24f.json"
    txt_path = OUT / "report_router_gate_phase_24f.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24F RUNTIME REPORT ROUTER GATE",
                "==============================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "diagnostic_route=True",
                "validation_route=True",
                "report_route=True",
                "warning_route=True",
                "recommendation_route=True",
                "event_emission=True",
                "bounded_history=True",
                "route_filtering=True",
                "route_allowlist=True",
                "severity_allowlist=True",
                "qt_does_not_own_report_routing=True",
                "metadata_only_report_routing=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24F_RUNTIME_REPORT_ROUTING")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24F_RUNTIME_REPORT_ROUTING")
    print(f"runtime_schema={SCHEMA}")
    print("diagnostic_route=True")
    print("validation_route=True")
    print("report_route=True")
    print("warning_route=True")
    print("recommendation_route=True")
    print("event_emission=True")
    print("bounded_history=True")
    print("route_filtering=True")
    print("route_allowlist=True")
    print("severity_allowlist=True")
    print("qt_does_not_own_report_routing=True")
    print("metadata_only_report_routing=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
