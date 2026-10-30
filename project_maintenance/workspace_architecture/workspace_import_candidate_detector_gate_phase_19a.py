from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.workspace_runtime_core import (
    IMPORT_CANDIDATE_SCHEMA as SCHEMA,
    build_workspace_import_candidate_detector,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_19a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_architecture_completion_phase_18e.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_import_candidate_detector_gate_phase_19a.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    detector = build_workspace_import_candidate_detector(ROOT)
    summary = detector["summary"]
    policy = detector["execution_policy"]
    activation = detector["activation_status"]

    if detector.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if activation.get("sorting_foundation_complete") is not True:
        failures.append("sorting_foundation_not_complete")

    if activation.get("controlled_detection_active") is not True:
        failures.append("controlled_detection_not_active")

    if activation.get("automatic_import_active") is not False:
        failures.append("automatic_import_active_must_be_false")

    if activation.get("gui_activation_active") is not False:
        failures.append("gui_activation_active_must_be_false")

    for key in [
        "read_only_detector",
        "requires_manual_review",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "moves_existing_files",
        "deletes_files",
        "archives_files",
        "imports_files",
        "rewrites_existing_user_assets",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    if summary.get("automatic_actions_created") != 0:
        failures.append("automatic_actions_created_nonzero")

    for path, item in detector.get("candidates", {}).items():
        if item.get("manual_review_required") is not True:
            failures.append(f"candidate_missing_manual_review={path}")
        for key in ["execution_allowed", "delete_allowed", "archive_allowed", "move_allowed", "import_allowed_without_review"]:
            if item.get(key) is not False:
                failures.append(f"candidate_unsafe_flag_not_false={path}:{key}")

    detector_path = OUT / "workspace_import_candidate_detector_phase_19a.json"
    gate_json = OUT / "workspace_import_candidate_detector_gate_phase_19a.json"
    gate_txt = OUT / "workspace_import_candidate_detector_gate_phase_19a.txt"

    detector_path.write_text(json.dumps(detector, indent=2), encoding="utf-8")

    result = {
        "phase": "19A",
        "feature": "WORKSPACE_IMPORT_CANDIDATE_DETECTOR",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": detector.get("schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "detector_json": detector_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_19A_COMPLETE_WORKSPACE_IMPORT_CANDIDATE_DETECTOR_ESTABLISHED" if not failures else "PHASE_19A_BLOCKED",
        "next_phase": "19B_IMPORT_REVIEW_REGISTRY",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 19A WORKSPACE IMPORT CANDIDATE DETECTOR",
        "====================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"non_authoritative_roots_present={summary.get('non_authoritative_roots_present')}",
        f"scanned_files={summary.get('scanned_files')}",
        f"import_candidates={summary.get('import_candidates')}",
        f"design_import_candidates={summary.get('design_import_candidates')}",
        f"workspace_resource_review_candidates={summary.get('workspace_resource_review_candidates')}",
        f"manual_review_required={summary.get('manual_review_required')}",
        f"automatic_actions_created={summary.get('automatic_actions_created')}",
        f"controlled_detection_active={activation.get('controlled_detection_active')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"gui_activation_active={activation.get('gui_activation_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"detector_json={result['detector_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_19A_WORKSPACE_IMPORT_CANDIDATE_DETECTOR" if result["passed"] else "FAIL_PHASE_19A_WORKSPACE_IMPORT_CANDIDATE_DETECTOR")
    print(f"schema={result['schema']}")
    print(f"non_authoritative_roots_present={summary.get('non_authoritative_roots_present')}")
    print(f"scanned_files={summary.get('scanned_files')}")
    print(f"import_candidates={summary.get('import_candidates')}")
    print(f"design_import_candidates={summary.get('design_import_candidates')}")
    print(f"manual_review_required={summary.get('manual_review_required')}")
    print(f"automatic_actions_created={summary.get('automatic_actions_created')}")
    print(f"controlled_detection_active={activation.get('controlled_detection_active')}")
    print(f"automatic_import_active={activation.get('automatic_import_active')}")
    print(f"gui_activation_active={activation.get('gui_activation_active')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"detector_json={result['detector_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
