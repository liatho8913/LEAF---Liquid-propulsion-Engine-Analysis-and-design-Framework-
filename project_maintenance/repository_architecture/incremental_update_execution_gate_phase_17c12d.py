from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12d"
OUT.mkdir(parents=True, exist_ok=True)

PLAN_JSON = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12c" / "incremental_update_execution_plan_phase_17c12c.json"

SCHEMA = "LEAF_INCREMENTAL_UPDATE_EXECUTION_GATE_PHASE_17C12D_V1"


def load_plan() -> dict:
    if not PLAN_JSON.exists():
        return {}
    return json.loads(PLAN_JSON.read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    plan = load_plan()

    if not plan:
        failures.append("missing_incremental_execution_plan")

    summary = plan.get("summary", {})
    planned_steps = plan.get("planned_steps", [])

    if not summary.get("plan_only", False):
        failures.append("source_plan_not_plan_only")

    if summary.get("consumer_execution_started", True):
        failures.append("consumer_execution_already_started")

    if summary.get("delete_allowed", True):
        failures.append("delete_allowed_true")

    if summary.get("automatic_delete_allowed", True):
        failures.append("automatic_delete_allowed_true")

    execution_gate = {
        "can_execute_incremental_consumers": not failures,
        "execution_mode": "GATED_READY_BUT_NOT_EXECUTED",
        "planned_steps_ready": len(planned_steps),
        "requires_next_phase_to_execute": True,
    }

    result = {
        "schema": SCHEMA,
        "phase": "17C.12D",
        "feature": "INCREMENTAL_UPDATE_EXECUTION_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "summary": {
            "planned_consumer_count": len(planned_steps),
            "can_execute_incremental_consumers": execution_gate["can_execute_incremental_consumers"],
            "execution_started": False,
            "execution_mode": execution_gate["execution_mode"],
            "delete_allowed": False,
            "automatic_delete_allowed": False,
        },
        "execution_gate": execution_gate,
        "planned_steps": planned_steps,
        "failures": failures,
        "deletion_status": {
            "deletion_started": False,
            "automatic_deletion_possible": False,
            "reason": "Incremental execution gating is not connected to file deletion.",
        },
        "completion_notice": (
            "PHASE_17C12D_COMPLETE_INCREMENTAL_UPDATE_EXECUTION_GATE_ESTABLISHED"
            if not failures else "PHASE_17C12D_BLOCKED"
        ),
        "next_phase": "17C.12E_INCREMENTAL_UPDATE_EXECUTOR",
    }

    json_path = OUT / "incremental_update_execution_gate_phase_17c12d.json"
    txt_path = OUT / "incremental_update_execution_gate_phase_17c12d.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    s = result["summary"]
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.12D INCREMENTAL UPDATE EXECUTION GATE",
            "=====================================================",
            f"passed={result['passed']}",
            f"planned_consumer_count={s['planned_consumer_count']}",
            f"can_execute_incremental_consumers={s['can_execute_incremental_consumers']}",
            f"execution_started={s['execution_started']}",
            f"execution_mode={s['execution_mode']}",
            f"delete_allowed={s['delete_allowed']}",
            f"automatic_delete_allowed={s['automatic_delete_allowed']}",
            "deletion_started=False",
            f"failures={len(failures)}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C12D_INCREMENTAL_UPDATE_EXECUTION_GATE" if result["passed"] else "FAIL_PHASE_17C12D_INCREMENTAL_UPDATE_EXECUTION_GATE")
    print(f"planned_consumer_count={s['planned_consumer_count']}")
    print(f"can_execute_incremental_consumers={s['can_execute_incremental_consumers']}")
    print(f"execution_started={s['execution_started']}")
    print(f"execution_mode={s['execution_mode']}")
    print(f"delete_allowed={s['delete_allowed']}")
    print(f"automatic_delete_allowed={s['automatic_delete_allowed']}")
    print("deletion_started=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
