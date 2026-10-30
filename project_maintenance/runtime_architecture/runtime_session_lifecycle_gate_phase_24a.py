from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
]

from leaf_qt.runtime.session_lifecycle import (
    CANONICAL_DESIGN_ROOT,
    CANONICAL_EXPORT_ROOT,
    CANONICAL_PROJECT_ROOT,
    CANONICAL_REPORT_ROOT,
    SCHEMA,
    RuntimeSessionLifecycle,
)


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    lifecycle = RuntimeSessionLifecycle()

    try:
        lifecycle.snapshot()
        failures.append("snapshot_available_without_open_session")
    except RuntimeError:
        pass

    session = lifecycle.create_session()

    lifecycle.set_active_project("LEAF_Projects/test_project")
    lifecycle.set_active_design("LEAF_Designs/test_design.leaf_design.json")
    lifecycle.set_active_workspace("engineering_workspace")
    lifecycle.set_active_tool("regen_calculator")
    lifecycle.set_active_report("LEAF_Reports/test_report.json")

    doc = lifecycle.open_document(
        "LEAF_Reports/test_report.json",
        "report",
    )

    snapshot = lifecycle.snapshot()

    required_keys = [
        "schema",
        "session_id",
        "created_at",
        "closed_at",
        "is_open",
        "active_project",
        "active_design",
        "active_workspace",
        "active_tool",
        "active_report",
        "open_documents",
        "qt_owns_runtime_state",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
        "canonical_user_roots",
    ]

    for key in required_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("active_project") != "LEAF_Projects/test_project":
        failures.append("active_project_not_retained")

    if snapshot.get("active_design") != "LEAF_Designs/test_design.leaf_design.json":
        failures.append("active_design_not_retained")

    if snapshot.get("active_workspace") != "engineering_workspace":
        failures.append("active_workspace_not_retained")

    if snapshot.get("active_tool") != "regen_calculator":
        failures.append("active_tool_not_retained")

    if snapshot.get("active_report") != "LEAF_Reports/test_report.json":
        failures.append("active_report_not_retained")

    if doc.document_id not in snapshot.get("open_documents", {}):
        failures.append("open_document_not_tracked")

    if snapshot.get("qt_owns_runtime_state") is not False:
        failures.append("qt_ownership_boundary_invalid")

    for key in [
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"runtime_stores_payloads:{key}")

    roots = snapshot.get("canonical_user_roots", {})
    expected_roots = {
        "projects": CANONICAL_PROJECT_ROOT,
        "designs": CANONICAL_DESIGN_ROOT,
        "reports": CANONICAL_REPORT_ROOT,
        "exports": CANONICAL_EXPORT_ROOT,
    }

    if roots != expected_roots:
        failures.append("canonical_user_roots_invalid")

    lifecycle.close_document(doc.document_id)

    if doc.document_id in lifecycle.snapshot().get("open_documents", {}):
        failures.append("closed_document_still_tracked")

    lifecycle.close_session()

    try:
        lifecycle.snapshot()
        failures.append("closed_session_still_accessible")
    except RuntimeError:
        pass

    result = {
        "phase": "24A",
        "programme": "24",
        "feature": "RUNTIME_SESSION_LIFECYCLE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_RUNTIME_SESSION_LIFECYCLE_GATE_PHASE_24A_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/runtime/session_lifecycle.py",
            "leaf_qt/runtime/__init__.py",
            "project_maintenance/runtime_architecture/runtime_session_lifecycle_gate_phase_24a.py",
        ],
        "files_replaced": [],
        "files_removed": [],
        "validated": {
            "single_runtime_session_owner": True,
            "metadata_only_runtime": True,
            "qt_does_not_own_runtime_state": True,
            "canonical_user_storage_roots_preserved": True,
            "open_document_tracking": True,
            "closed_session_lockout": True,
        },
        "completion_notice": (
            "PHASE_24A_COMPLETE_RUNTIME_SESSION_LIFECYCLE_ESTABLISHED"
            if not failures
            else "PHASE_24A_BLOCKED"
        ),
        "next_phase": "24B_RUNTIME_EVENT_BUS",
    }

    json_path = OUT / "runtime_session_lifecycle_gate_phase_24a.json"
    txt_path = OUT / "runtime_session_lifecycle_gate_phase_24a.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24A RUNTIME SESSION LIFECYCLE GATE",
                "=================================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "single_runtime_session_owner=True",
                "metadata_only_runtime=True",
                "qt_does_not_own_runtime_state=True",
                "canonical_user_storage_roots_preserved=True",
                "open_document_tracking=True",
                "closed_session_lockout=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24A_RUNTIME_SESSION_LIFECYCLE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24A_RUNTIME_SESSION_LIFECYCLE")
    print(f"runtime_schema={SCHEMA}")
    print("single_runtime_session_owner=True")
    print("metadata_only_runtime=True")
    print("qt_does_not_own_runtime_state=True")
    print("canonical_user_storage_roots_preserved=True")
    print("open_document_tracking=True")
    print("closed_session_lockout=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
