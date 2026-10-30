from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.workspace_sidebar_shell_phase_21a import build_workspace_sidebar_shell_snapshot

SCHEMA = "LEAF_QT_WORKSPACE_SIDEBAR_SHELL_PHASE_21A_V1"

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_sidebar_shell_phase_21a.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_workspace_sidebar_shell_gate_phase_21a.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    snapshot = build_workspace_sidebar_shell_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if snapshot.get("source_sidebar_schema") != "LEAF_WORKSPACE_SIDEBAR_MODEL_PHASE_20A_V1":
        failures.append("source_sidebar_schema_invalid")

    if summary.get("sidebar_items") != 6:
        failures.append("sidebar_item_count_invalid")

    if summary.get("developer_internal_items_exposed") != 0:
        failures.append("developer_internal_items_exposed")

    if summary.get("items_requiring_internal_path_knowledge") != 0:
        failures.append("items_requiring_internal_path_knowledge")

    if summary.get("presentation_only") is not True:
        failures.append("sidebar_shell_not_presentation_only")

    snapshot_path = OUT / "qt_workspace_sidebar_shell_snapshot_phase_21a.json"
    gate_json = OUT / "qt_workspace_sidebar_shell_gate_phase_21a.json"
    gate_txt = OUT / "qt_workspace_sidebar_shell_gate_phase_21a.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "phase": "21A",
        "feature": "QT_WORKSPACE_SIDEBAR_SHELL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot.get("schema"),
        "source_sidebar_schema": snapshot.get("source_sidebar_schema"),
        "summary": summary,
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_21A_COMPLETE_QT_WORKSPACE_SIDEBAR_SHELL_ESTABLISHED" if not failures else "PHASE_21A_BLOCKED",
        "next_phase": "21B_QT_WORKSPACE_PANEL_SHELL",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21A QT WORKSPACE SIDEBAR SHELL",
        "==========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_sidebar_schema={result['source_sidebar_schema']}",
        f"sidebar_items={summary.get('sidebar_items')}",
        f"visible_items={summary.get('visible_items')}",
        f"enabled_items={summary.get('enabled_items')}",
        f"developer_internal_items_exposed={summary.get('developer_internal_items_exposed')}",
        f"items_requiring_internal_path_knowledge={summary.get('items_requiring_internal_path_knowledge')}",
        f"qt_widget_class={summary.get('qt_widget_class')}",
        f"presentation_only={summary.get('presentation_only')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21A_QT_WORKSPACE_SIDEBAR_SHELL" if result["passed"] else "FAIL_PHASE_21A_QT_WORKSPACE_SIDEBAR_SHELL")
    print(f"schema={result['schema']}")
    print(f"source_sidebar_schema={result['source_sidebar_schema']}")
    print(f"sidebar_items={summary.get('sidebar_items')}")
    print(f"visible_items={summary.get('visible_items')}")
    print(f"enabled_items={summary.get('enabled_items')}")
    print(f"developer_internal_items_exposed={summary.get('developer_internal_items_exposed')}")
    print(f"items_requiring_internal_path_knowledge={summary.get('items_requiring_internal_path_knowledge')}")
    print(f"qt_widget_class={summary.get('qt_widget_class')}")
    print(f"presentation_only={summary.get('presentation_only')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
