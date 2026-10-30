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
    IMPORT_REVIEW_REGISTRY_SCHEMA as SCHEMA,
    build_import_review_registry,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_19b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "import_review_registry_gate_phase_19b.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    registry = build_import_review_registry(ROOT)
    summary = registry["summary"]
    policy = registry["execution_policy"]

    if registry.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if registry.get("source_detector_schema") != "LEAF_WORKSPACE_IMPORT_CANDIDATE_DETECTOR_PHASE_19A_V1":
        failures.append("source_detector_schema_invalid")

    if summary.get("detected_candidates") != summary.get("review_records"):
        failures.append("candidate_record_count_mismatch")

    if summary.get("pending_review") != summary.get("review_records"):
        failures.append("not_all_records_pending_review")

    if summary.get("automatic_actions_created") != 0:
        failures.append("automatic_actions_created_nonzero")

    if summary.get("approved_records") != 0:
        failures.append("approved_records_nonzero")

    if summary.get("import_allowed_records") != 0:
        failures.append("import_allowed_records_nonzero")

    for key in [
        "review_registry_is_read_only",
        "creates_review_records_only",
        "manual_review_required",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "imports_files",
        "moves_existing_files",
        "deletes_files",
        "archives_files",
        "rewrites_existing_user_assets",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    for review_id, record in registry.get("review_records", {}).items():
        if record.get("status") != "PENDING_REVIEW":
            failures.append(f"record_not_pending={review_id}")
        if record.get("manual_review_required") is not True:
            failures.append(f"record_manual_review_missing={review_id}")
        for key in [
            "approved",
            "rejected",
            "execution_allowed",
            "import_allowed",
            "move_allowed",
            "delete_allowed",
            "archive_allowed",
        ]:
            if record.get(key) is not False:
                failures.append(f"record_unsafe_flag_not_false={review_id}:{key}")

    registry_path = OUT / "import_review_registry_phase_19b.json"
    gate_json = OUT / "import_review_registry_gate_phase_19b.json"
    gate_txt = OUT / "import_review_registry_gate_phase_19b.txt"

    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    result = {
        "phase": "19B",
        "feature": "IMPORT_REVIEW_REGISTRY",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": registry.get("schema"),
        "source_detector_schema": registry.get("source_detector_schema"),
        "summary": summary,
        "failures": failures,
        "registry_json": registry_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_19B_COMPLETE_IMPORT_REVIEW_REGISTRY_ESTABLISHED" if not failures else "PHASE_19B_BLOCKED",
        "next_phase": "19C_SAFE_IMPORT_PLAN_GENERATOR",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 19B IMPORT REVIEW REGISTRY",
        "======================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_detector_schema={result['source_detector_schema']}",
        f"detected_candidates={summary.get('detected_candidates')}",
        f"review_records={summary.get('review_records')}",
        f"pending_review={summary.get('pending_review')}",
        f"duplicate_groups={summary.get('duplicate_groups')}",
        f"destination_conflict_groups={summary.get('destination_conflict_groups')}",
        f"high_review={summary.get('high_review')}",
        f"duplicate_review={summary.get('duplicate_review')}",
        f"normal_review={summary.get('normal_review')}",
        f"low_confidence_review={summary.get('low_confidence_review')}",
        f"automatic_actions_created={summary.get('automatic_actions_created')}",
        f"approved_records={summary.get('approved_records')}",
        f"import_allowed_records={summary.get('import_allowed_records')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"registry_json={result['registry_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_19B_IMPORT_REVIEW_REGISTRY" if result["passed"] else "FAIL_PHASE_19B_IMPORT_REVIEW_REGISTRY")
    print(f"schema={result['schema']}")
    print(f"source_detector_schema={result['source_detector_schema']}")
    print(f"detected_candidates={summary.get('detected_candidates')}")
    print(f"review_records={summary.get('review_records')}")
    print(f"pending_review={summary.get('pending_review')}")
    print(f"duplicate_groups={summary.get('duplicate_groups')}")
    print(f"destination_conflict_groups={summary.get('destination_conflict_groups')}")
    print(f"high_review={summary.get('high_review')}")
    print(f"duplicate_review={summary.get('duplicate_review')}")
    print(f"normal_review={summary.get('normal_review')}")
    print(f"low_confidence_review={summary.get('low_confidence_review')}")
    print(f"automatic_actions_created={summary.get('automatic_actions_created')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"registry_json={result['registry_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
