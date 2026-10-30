from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.incremental_update_execution_plan_phase_17c12c import write_report

ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "incremental_update_execution_plan_phase_17c12c.py"
OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12c"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(ENGINE), doraise=True)
    except Exception as exc:
        failures.append(f"compile_failure={exc!r}")

    result = write_report()
    s = result["summary"]

    if not s["plan_only"]:
        failures.append("plan_only_false")

    if s["consumer_execution_started"]:
        failures.append("consumer_execution_started_true")

    if s["delete_allowed"]:
        failures.append("delete_allowed_true")

    if s["automatic_delete_allowed"]:
        failures.append("automatic_delete_allowed_true")

    if s["available_consumers"] <= 0:
        failures.append("no_available_consumers")

    passed = not failures

    gate = {
        "phase": "17C.12C",
        "feature": "INCREMENTAL_UPDATE_EXECUTION_PLAN",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": passed,
        "summary": s,
        "failures": failures,
        "deletion_status": {
            "deletion_started": False,
            "automatic_deletion_possible": False,
            "reason": "Execution planning is not a deletion path.",
        },
        "completion_notice": (
            "PHASE_17C12C_COMPLETE_INCREMENTAL_UPDATE_EXECUTION_PLAN_ESTABLISHED"
            if passed else "PHASE_17C12C_BLOCKED"
        ),
        "next_phase": "17C.12D_INCREMENTAL_UPDATE_EXECUTION_GATE",
        "source_report": result["artefacts"],
    }

    json_path = OUT / "incremental_update_execution_plan_gate_phase_17c12c.json"
    txt_path = OUT / "incremental_update_execution_plan_gate_phase_17c12c.txt"

    json_path.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.12C INCREMENTAL UPDATE EXECUTION PLAN GATE",
            "==========================================================",
            f"passed={passed}",
            f"available_consumers={s['available_consumers']}",
            f"planned_consumer_count={s['planned_consumer_count']}",
            f"plan_only={s['plan_only']}",
            f"consumer_execution_started={s['consumer_execution_started']}",
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

    print("PASS_PHASE_17C12C_INCREMENTAL_UPDATE_EXECUTION_PLAN" if passed else "FAIL_PHASE_17C12C_INCREMENTAL_UPDATE_EXECUTION_PLAN")
    print(f"available_consumers={s['available_consumers']}")
    print(f"planned_consumer_count={s['planned_consumer_count']}")
    print(f"plan_only={s['plan_only']}")
    print(f"consumer_execution_started={s['consumer_execution_started']}")
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
