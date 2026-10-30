from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.incremental_consumer_invalidation_map_phase_17c12b import write_report

ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "incremental_consumer_invalidation_map_phase_17c12b.py"
OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12b"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(ENGINE), doraise=True)
    except Exception as exc:
        failures.append(f"compile_failure={exc!r}")

    result = write_report()
    s = result["summary"]

    if s["consumer_count"] <= 0:
        failures.append("no_consumers_defined")

    if s["affected_count"] != s["added_count"] + s["removed_count"] + s["changed_count"]:
        failures.append("affected_count_mismatch")

    if s["delete_allowed"]:
        failures.append("delete_allowed_true")

    if s["automatic_delete_allowed"]:
        failures.append("automatic_delete_allowed_true")

    passed = not failures

    gate = {
        "phase": "17C.12B",
        "feature": "INCREMENTAL_CONSUMER_INVALIDATION_MAP",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": passed,
        "summary": s,
        "failures": failures,
        "completion_notice": (
            "PHASE_17C12B_COMPLETE_INCREMENTAL_CONSUMER_INVALIDATION_MAP_ESTABLISHED"
            if passed else "PHASE_17C12B_BLOCKED"
        ),
        "next_phase": "17C.12C_INCREMENTAL_UPDATE_EXECUTION_PLAN",
        "source_report": result["artefacts"],
    }

    json_path = OUT / "incremental_consumer_invalidation_map_gate_phase_17c12b.json"
    txt_path = OUT / "incremental_consumer_invalidation_map_gate_phase_17c12b.txt"

    json_path.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.12B INCREMENTAL CONSUMER INVALIDATION MAP GATE",
            "================================================================",
            f"passed={passed}",
            f"added_count={s['added_count']}",
            f"removed_count={s['removed_count']}",
            f"changed_count={s['changed_count']}",
            f"affected_count={s['affected_count']}",
            f"python_added_count={s['python_added_count']}",
            f"python_removed_count={s['python_removed_count']}",
            f"python_changed_count={s['python_changed_count']}",
            f"consumer_count={s['consumer_count']}",
            f"invalidated_consumer_count={s['invalidated_consumer_count']}",
            f"delete_allowed={s['delete_allowed']}",
            f"automatic_delete_allowed={s['automatic_delete_allowed']}",
            "deletion_started=False",
            f"failures={len(failures)}",
            f"completion_notice={gate['completion_notice']}",
            f"next_phase={gate['next_phase']}",
            f"report={txt_path.relative_to(ROOT)}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C12B_INCREMENTAL_CONSUMER_INVALIDATION_MAP" if passed else "FAIL_PHASE_17C12B_INCREMENTAL_CONSUMER_INVALIDATION_MAP")
    print(f"added_count={s['added_count']}")
    print(f"removed_count={s['removed_count']}")
    print(f"changed_count={s['changed_count']}")
    print(f"affected_count={s['affected_count']}")
    print(f"python_added_count={s['python_added_count']}")
    print(f"python_removed_count={s['python_removed_count']}")
    print(f"python_changed_count={s['python_changed_count']}")
    print(f"consumer_count={s['consumer_count']}")
    print(f"invalidated_consumer_count={s['invalidated_consumer_count']}")
    print(f"delete_allowed={s['delete_allowed']}")
    print(f"automatic_delete_allowed={s['automatic_delete_allowed']}")
    print("deletion_started=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
