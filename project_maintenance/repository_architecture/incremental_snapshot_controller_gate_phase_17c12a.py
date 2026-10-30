from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.incremental_snapshot_controller_phase_17c12a import write_report

ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "incremental_snapshot_controller_phase_17c12a.py"
OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12a"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(ENGINE), doraise=True)
    except Exception as exc:
        failures.append(f"compile_failure={exc!r}")

    result = write_report()
    s = result["summary"]

    if s["baseline_files"] <= 0:
        failures.append("missing_or_empty_baseline_snapshot")

    if s["current_files"] <= 0:
        failures.append("empty_current_snapshot")

    if not s["incremental_update_available"]:
        failures.append("incremental_update_not_available")

    if s["delete_allowed"]:
        failures.append("delete_allowed_true")

    if s["automatic_delete_allowed"]:
        failures.append("automatic_delete_allowed_true")

    if s["added_count"] + s["removed_count"] + s["changed_count"] != s["affected_count"]:
        failures.append("affected_count_mismatch")

    passed = not failures

    gate = {
        "phase": "17C.12A",
        "feature": "INCREMENTAL_SNAPSHOT_CONTROLLER_FOUNDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": passed,
        "summary": s,
        "failures": failures,
        "deletion_status": {
            "system_has_controlled_removal_engine": True,
            "deletion_started": False,
            "automatic_deletion_possible": False,
            "reason": "No file can be deleted unless 17C.10D proves delete eligibility. Latest chain had delete_eligible_count=0.",
        },
        "completion_notice": (
            "PHASE_17C12A_COMPLETE_INCREMENTAL_SNAPSHOT_CONTROLLER_FOUNDATION_ESTABLISHED"
            if passed else "PHASE_17C12A_BLOCKED"
        ),
        "next_phase": "17C.12B_INCREMENTAL_CONSUMER_INVALIDATION_MAP",
        "source_report": result["artefacts"],
    }

    json_path = OUT / "incremental_snapshot_controller_gate_phase_17c12a.json"
    txt_path = OUT / "incremental_snapshot_controller_gate_phase_17c12a.txt"

    json_path.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.12A INCREMENTAL SNAPSHOT CONTROLLER GATE",
            "=========================================================",
            f"passed={passed}",
            f"baseline_files={s['baseline_files']}",
            f"current_files={s['current_files']}",
            f"added_count={s['added_count']}",
            f"removed_count={s['removed_count']}",
            f"changed_count={s['changed_count']}",
            f"unchanged_count={s['unchanged_count']}",
            f"affected_count={s['affected_count']}",
            f"incremental_update_available={s['incremental_update_available']}",
            f"delete_allowed={s['delete_allowed']}",
            f"automatic_delete_allowed={s['automatic_delete_allowed']}",
            "deletion_started=False",
            "deletion_requires=17C.10D_DELETE_ELIGIBILITY_GATE_AND_17C.10E_CONTROLLED_REMOVAL_ENGINE",
            f"failures={len(failures)}",
            f"completion_notice={gate['completion_notice']}",
            f"next_phase={gate['next_phase']}",
            f"report={txt_path.relative_to(ROOT)}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C12A_INCREMENTAL_SNAPSHOT_CONTROLLER" if passed else "FAIL_PHASE_17C12A_INCREMENTAL_SNAPSHOT_CONTROLLER")
    print(f"baseline_files={s['baseline_files']}")
    print(f"current_files={s['current_files']}")
    print(f"added_count={s['added_count']}")
    print(f"removed_count={s['removed_count']}")
    print(f"changed_count={s['changed_count']}")
    print(f"unchanged_count={s['unchanged_count']}")
    print(f"affected_count={s['affected_count']}")
    print(f"incremental_update_available={s['incremental_update_available']}")
    print(f"delete_allowed={s['delete_allowed']}")
    print(f"automatic_delete_allowed={s['automatic_delete_allowed']}")
    print("deletion_started=False")
    print("deletion_requires=17C.10D_DELETE_ELIGIBILITY_GATE_AND_17C.10E_CONTROLLED_REMOVAL_ENGINE")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
