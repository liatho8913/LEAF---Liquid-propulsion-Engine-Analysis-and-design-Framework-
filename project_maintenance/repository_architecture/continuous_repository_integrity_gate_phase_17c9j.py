from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_architecture_synchronisation_engine import (
    synchronise_repository_architecture,
)
from project_maintenance.repository_architecture.incremental_repository_intelligence_updates_phase_17c9i import (
    detect_changes,
    load_json,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9j"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SYNC_ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "repository_architecture_synchronisation_engine.py"
INCREMENTAL_ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "incremental_repository_intelligence_updates_phase_17c9i.py"
BASELINE_METADATA = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9i" / "current_synchronised" / "repository_metadata_v1.json"

SCHEMA = "LEAF_CONTINUOUS_REPOSITORY_INTEGRITY_GATE_V1"


def main() -> None:
    failures: list[str] = []
    warnings: list[str] = []

    for script in [SYNC_ENGINE, INCREMENTAL_ENGINE]:
        try:
            py_compile.compile(str(script), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure={script.relative_to(ROOT)}:{exc!r}")

    if not BASELINE_METADATA.exists():
        failures.append("phase_17c9i_baseline_metadata_missing")
        baseline_metadata = {}
    else:
        baseline_metadata = load_json(BASELINE_METADATA)

    sync = synchronise_repository_architecture(
        ROOT,
        "_leaf_artifacts/repository_architecture/phase_17c9j/current_integrity_sync",
    )

    current_metadata = load_json(ROOT / sync["artefacts"]["metadata"]) if sync.get("artefacts") else {}
    changes = detect_changes(baseline_metadata, current_metadata) if baseline_metadata and current_metadata else {
        "summary": {
            "previous_file_count": 0,
            "current_file_count": 0,
            "added_count": 0,
            "removed_count": 0,
            "changed_count": 0,
            "unchanged_count": 0,
            "incremental_candidate_count": 0,
        },
        "added_files": [],
        "removed_files": [],
        "changed_files": [],
    }

    architecture_errors = sync["summary"]["architecture_errors"]
    architecture_warnings = sync["summary"]["architecture_warnings"]
    incremental_candidates = changes["summary"]["incremental_candidate_count"]

    if architecture_errors != 0:
        failures.append("architecture_errors_present")

    if sync["summary"]["supported_files"] <= 0:
        failures.append("no_supported_files")

    if sync["summary"]["resolved_dependency_edges"] <= 0:
        failures.append("no_dependency_edges")

    if incremental_candidates > 25:
        warnings.append(f"large_incremental_change_set={incremental_candidates}")

    readiness = {
        "safe_for_next_sorter_batch": not failures and architecture_errors == 0,
        "safe_for_duplicate_detection": not failures and architecture_errors == 0,
        "safe_for_removal_detection": not failures and architecture_errors == 0,
        "safe_for_automatic_delete": False,
        "automatic_delete_reason": "Deletion requires duplicate proof, unused-file proof, archive-first retirement, and delete eligibility gates.",
    }

    result = {
        "phase": "17C.9J",
        "feature": "CONTINUOUS_REPOSITORY_INTEGRITY_GATE",
        "schema": SCHEMA,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "sync_summary": sync["summary"],
        "change_summary": changes["summary"],
        "added_files_preview": changes["added_files"][:25],
        "removed_files_preview": changes["removed_files"][:25],
        "changed_files_preview": changes["changed_files"][:25],
        "readiness": readiness,
        "warnings": warnings,
        "failures": failures,
        "completion_notice": (
            "PHASE_17C9J_COMPLETE_CONTINUOUS_REPOSITORY_INTEGRITY_GATE_ESTABLISHED"
            if not failures
            else "PHASE_17C9J_BLOCKED"
        ),
        "next_phase": "17C.10A_DUPLICATE_FUNCTIONALITY_DETECTION",
    }

    json_path = OUT_DIR / "continuous_repository_integrity_gate_phase_17c9j.json"
    txt_path = OUT_DIR / "continuous_repository_integrity_gate_phase_17c9j.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.9J CONTINUOUS REPOSITORY INTEGRITY GATE",
            "=======================================================",
            f"passed={result['passed']}",
            f"supported_files={sync['summary']['supported_files']}",
            f"python_files={sync['summary']['python_files']}",
            f"file_nodes={sync['summary']['file_nodes']}",
            f"owner_nodes={sync['summary']['owner_nodes']}",
            f"subsystem_nodes={sync['summary']['subsystem_nodes']}",
            f"resolved_dependency_edges={sync['summary']['resolved_dependency_edges']}",
            f"architecture_errors={architecture_errors}",
            f"architecture_warnings={architecture_warnings}",
            f"added_count={changes['summary']['added_count']}",
            f"removed_count={changes['summary']['removed_count']}",
            f"changed_count={changes['summary']['changed_count']}",
            f"incremental_candidate_count={incremental_candidates}",
            f"safe_for_next_sorter_batch={readiness['safe_for_next_sorter_batch']}",
            f"safe_for_duplicate_detection={readiness['safe_for_duplicate_detection']}",
            f"safe_for_removal_detection={readiness['safe_for_removal_detection']}",
            f"safe_for_automatic_delete={readiness['safe_for_automatic_delete']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9J_CONTINUOUS_REPOSITORY_INTEGRITY_GATE" if result["passed"] else "FAIL_PHASE_17C9J_CONTINUOUS_REPOSITORY_INTEGRITY_GATE")
    print(f"supported_files={sync['summary']['supported_files']}")
    print(f"python_files={sync['summary']['python_files']}")
    print(f"resolved_dependency_edges={sync['summary']['resolved_dependency_edges']}")
    print(f"architecture_errors={architecture_errors}")
    print(f"architecture_warnings={architecture_warnings}")
    print(f"added_count={changes['summary']['added_count']}")
    print(f"removed_count={changes['summary']['removed_count']}")
    print(f"changed_count={changes['summary']['changed_count']}")
    print(f"incremental_candidate_count={incremental_candidates}")
    print(f"safe_for_duplicate_detection={readiness['safe_for_duplicate_detection']}")
    print(f"safe_for_removal_detection={readiness['safe_for_removal_detection']}")
    print(f"safe_for_automatic_delete={readiness['safe_for_automatic_delete']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
