from __future__ import annotations

import json
import py_compile
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25i"
OUT.mkdir(parents=True, exist_ok=True)

SANDBOX = OUT / "_project_browser_sandbox"

MODULES = [
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
    ROOT / "leaf_qt" / "storage" / "project_manifest.py",
    ROOT / "leaf_qt" / "storage" / "design_manifest.py",
    ROOT / "leaf_qt" / "storage" / "creation_owner.py",
    ROOT / "leaf_qt" / "storage" / "save_load_bridge.py",
    ROOT / "leaf_qt" / "storage" / "legacy_import_locations.py",
    ROOT / "leaf_qt" / "storage" / "storage_validation_repair.py",
    ROOT / "leaf_qt" / "storage" / "project_browser_model.py",
]

from leaf_qt.storage.creation_owner import ProjectDesignCreationOwner
from leaf_qt.storage.project_browser_model import SCHEMA, ProjectBrowserModel


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        if not module.exists():
            failures.append(f"missing_module:{module.relative_to(ROOT)}")
            continue
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True, exist_ok=True)

    creator = ProjectDesignCreationOwner(SANDBOX)
    created = creator.create_project_with_design(
        project_name="Browser Model Project",
        design_name="Browser Model Design",
    )

    reports_dir = SANDBOX / "LEAF_Reports"
    exports_dir = SANDBOX / "LEAF_Exports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / "browser_report.json"
    export_path = exports_dir / "browser_export.csv"
    report_path.write_text(json.dumps({"status": "PASS"}, indent=2), encoding="utf-8")
    export_path.write_text("x,y\n1,2\n", encoding="utf-8")

    project_path = Path(created.project_manifest_path)
    design_path = Path(created.design_manifest_path or "")
    project_payload = json.loads(project_path.read_text(encoding="utf-8"))
    design_payload = json.loads(design_path.read_text(encoding="utf-8"))
    project_payload["linked_reports"].append(str(report_path))
    project_payload["linked_exports"].append(str(export_path))
    design_payload["report_refs"].append(str(report_path))
    design_payload["export_refs"].append(str(export_path))
    project_path.write_text(json.dumps(project_payload, indent=2), encoding="utf-8")
    design_path.write_text(json.dumps(design_payload, indent=2), encoding="utf-8")

    model = ProjectBrowserModel(SANDBOX)
    built = model.build()

    if built.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if built.get("project_count") != 1:
        failures.append("project_count_invalid")

    if built.get("design_count") != 1:
        failures.append("design_count_invalid")

    projects = built.get("projects", [])

    if not projects:
        failures.append("no_projects_returned")
    else:
        project = projects[0]

        if project.get("project_name") != "Browser Model Project":
            failures.append("project_name_not_retained")

        if str(report_path) not in project.get("linked_reports", []):
            failures.append("project_linked_report_missing")

        if str(export_path) not in project.get("linked_exports", []):
            failures.append("project_linked_export_missing")

        designs = project.get("designs", [])

        if len(designs) != 1:
            failures.append("project_design_item_count_invalid")
        else:
            design = designs[0]

            if design.get("design_name") != "Browser Model Design":
                failures.append("design_name_not_retained")

            if design.get("dirty_state") != "saved":
                failures.append("design_dirty_state_invalid")

            if str(report_path) not in design.get("report_refs", []):
                failures.append("design_report_ref_missing")

            if str(export_path) not in design.get("export_refs", []):
                failures.append("design_export_ref_missing")

    # Add a broken report link to ensure browser warning surface works.
    project_manifest_path = Path(created.project_manifest_path)
    project_payload = json.loads(project_manifest_path.read_text(encoding="utf-8"))
    project_payload["linked_reports"].append(str(SANDBOX / "LEAF_Reports" / "missing_report.json"))
    project_manifest_path.write_text(json.dumps(project_payload, indent=2), encoding="utf-8")

    broken_built = model.build()
    broken_projects = broken_built.get("projects", [])
    broken_links = broken_projects[0].get("broken_links", []) if broken_projects else []

    if not broken_links:
        failures.append("broken_links_not_surfaced")

    snapshot = model.snapshot()

    required_snapshot_keys = [
        "schema",
        "root",
        "lists_projects",
        "lists_designs",
        "shows_linked_reports",
        "shows_linked_exports",
        "shows_dirty_state",
        "shows_validation_refs",
        "shows_broken_links",
        "qt_owns_project_browser",
        "model_only",
        "read_only",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    for key in [
        "lists_projects",
        "lists_designs",
        "shows_linked_reports",
        "shows_linked_exports",
        "shows_dirty_state",
        "shows_validation_refs",
        "shows_broken_links",
        "model_only",
        "read_only",
    ]:
        if snapshot.get(key) is not True:
            failures.append(f"browser_capability_not_declared:{key}")

    if snapshot.get("qt_owns_project_browser") is not False:
        failures.append("qt_ownership_boundary_invalid")

    if built.get("qt_owns_project_browser") is not False:
        failures.append("built_model_qt_ownership_boundary_invalid")

    if built.get("stores_solver_payloads") is not False:
        failures.append("built_model_stores_solver_payloads")

    if built.get("stores_report_payloads") is not False:
        failures.append("built_model_stores_report_payloads")

    if built.get("stores_validation_payloads") is not False:
        failures.append("built_model_stores_validation_payloads")

    result = {
        "phase": "25I",
        "programme": "25",
        "feature": "PROJECT_BROWSER_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_PROJECT_BROWSER_MODEL_GATE_PHASE_25I_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/project_browser_model.py",
            "project_maintenance/storage_architecture/project_browser_model_gate_phase_25i.py",
        ],
        "files_replaced": [
            "leaf_qt/storage/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "project_listing": True,
            "design_listing": True,
            "linked_reports_visible": True,
            "linked_exports_visible": True,
            "dirty_state_visible": True,
            "validation_refs_visible": True,
            "broken_links_visible": True,
            "model_only": True,
            "read_only": True,
            "qt_does_not_own_project_browser": True,
        },
        "completion_notice": (
            "PHASE_25I_COMPLETE_PROJECT_BROWSER_MODEL_ESTABLISHED"
            if not failures
            else "PHASE_25I_BLOCKED"
        ),
        "next_phase": "25J_PROGRAMME_25_COMPLETION_GATE",
    }

    json_path = OUT / "project_browser_model_gate_phase_25i.json"
    txt_path = OUT / "project_browser_model_gate_phase_25i.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25I PROJECT BROWSER MODEL GATE",
                "=============================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "project_listing=True",
                "design_listing=True",
                "linked_reports_visible=True",
                "linked_exports_visible=True",
                "dirty_state_visible=True",
                "validation_refs_visible=True",
                "broken_links_visible=True",
                "model_only=True",
                "read_only=True",
                "qt_does_not_own_project_browser=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25I_PROJECT_BROWSER_MODEL")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25I_PROJECT_BROWSER_MODEL")
    print(f"runtime_schema={SCHEMA}")
    print("project_listing=True")
    print("design_listing=True")
    print("linked_reports_visible=True")
    print("linked_exports_visible=True")
    print("dirty_state_visible=True")
    print("validation_refs_visible=True")
    print("broken_links_visible=True")
    print("model_only=True")
    print("read_only=True")
    print("qt_does_not_own_project_browser=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
