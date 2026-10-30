from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12c"
OUT.mkdir(parents=True, exist_ok=True)

INVALIDATION_JSON = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12b" / "incremental_consumer_invalidation_map_phase_17c12b.json"

SCHEMA = "LEAF_INCREMENTAL_UPDATE_EXECUTION_PLAN_PHASE_17C12C_V1"

EXECUTION_ORDER = [
    "metadata",
    "knowledge_database",
    "dependency_graph",
    "semantic_classification",
    "architecture_validation",
    "duplicate_detection",
    "unused_file_proof",
    "visualisation",
    "sorter",
]


def load_invalidation() -> dict[str, Any]:
    if not INVALIDATION_JSON.exists():
        return {}
    return json.loads(INVALIDATION_JSON.read_text(encoding="utf-8"))


def build_execution_plan() -> dict[str, Any]:
    invalidation = load_invalidation()
    consumers = invalidation.get("invalidated_consumers", {})

    planned_steps = []

    for index, consumer in enumerate(EXECUTION_ORDER, start=1):
        info = consumers.get(consumer, {})
        if not info.get("invalidated", False):
            continue

        planned_steps.append({
            "order": index,
            "consumer": consumer,
            "reason": info.get("reasons", []),
            "description": info.get("description", ""),
            "execution_mode": "planned_only_not_executed",
        })

    result = {
        "schema": SCHEMA,
        "phase": "17C.12C",
        "feature": "INCREMENTAL_UPDATE_EXECUTION_PLAN",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "PLAN_ONLY_NO_CONSUMER_EXECUTION_NO_DELETE",
        "summary": {
            "available_consumers": len(EXECUTION_ORDER),
            "planned_consumer_count": len(planned_steps),
            "plan_only": True,
            "consumer_execution_started": False,
            "delete_allowed": False,
            "automatic_delete_allowed": False,
        },
        "planned_steps": planned_steps,
        "safety_policy": {
            "consumer_execution_started": False,
            "delete_allowed": False,
            "automatic_delete_allowed": False,
            "reason": "17C.12C only creates the execution plan. Actual execution requires a later execution gate.",
        },
        "completion_notice": "PHASE_17C12C_COMPLETE_INCREMENTAL_UPDATE_EXECUTION_PLAN_ESTABLISHED",
        "next_phase": "17C.12D_INCREMENTAL_UPDATE_EXECUTION_GATE",
    }

    return result


def write_report() -> dict[str, Any]:
    result = build_execution_plan()

    json_path = OUT / "incremental_update_execution_plan_phase_17c12c.json"
    txt_path = OUT / "incremental_update_execution_plan_phase_17c12c.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    s = result["summary"]
    lines = [
        "LEAF PHASE 17C.12C INCREMENTAL UPDATE EXECUTION PLAN",
        "=====================================================",
        f"schema={result['schema']}",
        f"mode={result['mode']}",
        f"available_consumers={s['available_consumers']}",
        f"planned_consumer_count={s['planned_consumer_count']}",
        f"plan_only={s['plan_only']}",
        f"consumer_execution_started={s['consumer_execution_started']}",
        f"delete_allowed={s['delete_allowed']}",
        f"automatic_delete_allowed={s['automatic_delete_allowed']}",
        "",
        "PLANNED_STEPS",
    ]

    for step in result["planned_steps"]:
        lines.append(f"{step['order']}. {step['consumer']} reasons={','.join(step['reason'])}")

    if not result["planned_steps"]:
        lines.append("none")

    lines.extend([
        "",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"json={json_path.relative_to(ROOT)}",
    ])

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    result["artefacts"] = {
        "report": txt_path.relative_to(ROOT).as_posix(),
        "json": json_path.relative_to(ROOT).as_posix(),
    }
    return result


if __name__ == "__main__":
    payload = write_report()
    s = payload["summary"]

    print("PASS_INCREMENTAL_UPDATE_EXECUTION_PLAN_PHASE_17C12C")
    print(f"available_consumers={s['available_consumers']}")
    print(f"planned_consumer_count={s['planned_consumer_count']}")
    print(f"plan_only={s['plan_only']}")
    print(f"consumer_execution_started={s['consumer_execution_started']}")
    print(f"delete_allowed={s['delete_allowed']}")
    print(f"automatic_delete_allowed={s['automatic_delete_allowed']}")
    print(f"report={payload['artefacts']['report']}")
    print(f"json={payload['artefacts']['json']}")
    print(f"next_phase={payload['next_phase']}")
