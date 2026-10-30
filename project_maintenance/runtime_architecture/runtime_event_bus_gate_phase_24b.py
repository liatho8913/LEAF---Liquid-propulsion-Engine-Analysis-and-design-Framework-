from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
    ROOT / "leaf_qt" / "runtime" / "event_bus.py",
]

from leaf_qt.runtime.event_bus import SCHEMA, RuntimeEventBus


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    bus = RuntimeEventBus(max_history=3)

    received_specific: list[str] = []
    received_global: list[str] = []

    def specific_handler(event):
        received_specific.append(event.event_id)

    def global_handler(event):
        received_global.append(event.event_type)

    specific_id = bus.subscribe("design.changed", specific_handler, "test_specific")
    global_id = bus.subscribe("*", global_handler, "test_global")

    if specific_id != "test_specific":
        failures.append("specific_subscriber_id_not_retained")

    if global_id != "test_global":
        failures.append("global_subscriber_id_not_retained")

    event = bus.emit(
        "design.changed",
        source="phase_24b_gate",
        payload={"design": "LEAF_Designs/test_design.leaf_design.json"},
    )

    if not event.event_id.startswith("event_"):
        failures.append("event_id_invalid")

    if event.event_type != "design.changed":
        failures.append("event_type_not_retained")

    if event.source != "phase_24b_gate":
        failures.append("event_source_not_retained")

    if event.payload.get("design") != "LEAF_Designs/test_design.leaf_design.json":
        failures.append("event_payload_not_retained")

    if received_specific != [event.event_id]:
        failures.append("specific_subscriber_not_called")

    if received_global != ["design.changed"]:
        failures.append("global_subscriber_not_called")

    if bus.subscriber_count("design.changed") != 1:
        failures.append("specific_subscriber_count_invalid")

    if bus.subscriber_count("*") != 1:
        failures.append("global_subscriber_count_invalid")

    if bus.subscriber_count() != 2:
        failures.append("total_subscriber_count_invalid")

    unsubscribed = bus.unsubscribe("design.changed", "test_specific")

    if unsubscribed is not True:
        failures.append("unsubscribe_returned_false_for_existing_subscriber")

    bus.emit("design.changed", source="phase_24b_gate", payload={"design": "second"})

    if len(received_specific) != 1:
        failures.append("unsubscribed_handler_was_called")

    for index in range(5):
        bus.emit("history.test", source="phase_24b_gate", payload={"index": index})

    history = bus.history()

    if len(history) != 3:
        failures.append("event_history_limit_not_enforced")

    if history[-1].get("payload", {}).get("index") != 4:
        failures.append("event_history_latest_event_missing")

    snapshot = bus.snapshot()

    required_snapshot_keys = [
        "schema",
        "subscriber_groups",
        "subscriber_count",
        "retain_history",
        "max_history",
        "history_count",
        "qt_owns_event_bus",
        "direct_tool_to_tool_calls_required",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("qt_owns_event_bus") is not False:
        failures.append("qt_ownership_boundary_invalid")

    if snapshot.get("direct_tool_to_tool_calls_required") is not False:
        failures.append("direct_tool_coupling_boundary_invalid")

    bus.clear_history()

    if bus.history():
        failures.append("event_history_not_cleared")

    result = {
        "phase": "24B",
        "programme": "24",
        "feature": "RUNTIME_EVENT_BUS",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_RUNTIME_EVENT_BUS_GATE_PHASE_24B_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/runtime/event_bus.py",
            "project_maintenance/runtime_architecture/runtime_event_bus_gate_phase_24b.py",
        ],
        "files_replaced": [
            "leaf_qt/runtime/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "runtime_event_model": True,
            "specific_event_subscription": True,
            "global_event_subscription": True,
            "event_payload_delivery": True,
            "unsubscribe": True,
            "bounded_event_history": True,
            "qt_does_not_own_event_bus": True,
            "direct_tool_to_tool_calls_not_required": True,
        },
        "completion_notice": (
            "PHASE_24B_COMPLETE_RUNTIME_EVENT_BUS_ESTABLISHED"
            if not failures
            else "PHASE_24B_BLOCKED"
        ),
        "next_phase": "24C_RUNTIME_STATE_REGISTRY",
    }

    json_path = OUT / "runtime_event_bus_gate_phase_24b.json"
    txt_path = OUT / "runtime_event_bus_gate_phase_24b.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24B RUNTIME EVENT BUS GATE",
                "=========================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "runtime_event_model=True",
                "specific_event_subscription=True",
                "global_event_subscription=True",
                "event_payload_delivery=True",
                "unsubscribe=True",
                "bounded_event_history=True",
                "qt_does_not_own_event_bus=True",
                "direct_tool_to_tool_calls_not_required=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24B_RUNTIME_EVENT_BUS")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24B_RUNTIME_EVENT_BUS")
    print(f"runtime_schema={SCHEMA}")
    print("runtime_event_model=True")
    print("specific_event_subscription=True")
    print("global_event_subscription=True")
    print("event_payload_delivery=True")
    print("unsubscribe=True")
    print("bounded_event_history=True")
    print("qt_does_not_own_event_bus=True")
    print("direct_tool_to_tool_calls_not_required=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
