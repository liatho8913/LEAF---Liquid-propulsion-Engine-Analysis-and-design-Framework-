from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12b"
OUT.mkdir(parents=True, exist_ok=True)

DELTA_JSON = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12a" / "incremental_snapshot_controller_phase_17c12a.json"

SCHEMA = "LEAF_INCREMENTAL_CONSUMER_INVALIDATION_MAP_PHASE_17C12B_V1"


CONSUMERS = {
    "metadata": {
        "description": "file metadata index",
        "triggers": ["added", "removed", "changed"],
    },
    "knowledge_database": {
        "description": "searchable repository knowledge database",
        "triggers": ["added", "removed", "changed"],
    },
    "dependency_graph": {
        "description": "import/dependency graph",
        "triggers": ["python_added", "python_removed", "python_changed"],
    },
    "semantic_classification": {
        "description": "semantic role classification",
        "triggers": ["python_added", "python_removed", "python_changed"],
    },
    "architecture_validation": {
        "description": "architecture rule validation",
        "triggers": ["python_added", "python_removed", "python_changed"],
    },
    "duplicate_detection": {
        "description": "duplicate functionality proof",
        "triggers": ["python_added", "python_removed", "python_changed"],
    },
    "unused_file_proof": {
        "description": "unused file proof",
        "triggers": ["python_added", "python_removed", "python_changed"],
    },
    "visualisation": {
        "description": "repository architecture visualisation",
        "triggers": ["added", "removed", "changed"],
    },
    "sorter": {
        "description": "repository sorter planning",
        "triggers": ["added", "removed", "changed"],
    },
}


def load_delta() -> dict[str, Any]:
    if not DELTA_JSON.exists():
        return {}
    return json.loads(DELTA_JSON.read_text(encoding="utf-8"))


def is_python(path: str) -> bool:
    return Path(path).suffix.lower() == ".py"


def build_invalidation_map() -> dict[str, Any]:
    source = load_delta()
    delta = source.get("delta", {})

    added = list(delta.get("added", []))
    removed = list(delta.get("removed", []))
    changed = list(delta.get("changed", []))
    affected = list(delta.get("affected", []))

    event_flags = {
        "added": bool(added),
        "removed": bool(removed),
        "changed": bool(changed),
        "python_added": any(is_python(p) for p in added),
        "python_removed": any(is_python(p) for p in removed),
        "python_changed": any(is_python(p) for p in changed),
    }

    invalidated: dict[str, dict[str, Any]] = {}

    for name, config in CONSUMERS.items():
        triggers = config["triggers"]
        reasons = [trigger for trigger in triggers if event_flags.get(trigger, False)]
        invalidated[name] = {
            "invalidated": bool(reasons),
            "reasons": reasons,
            "description": config["description"],
        }

    invalidated_count = sum(1 for item in invalidated.values() if item["invalidated"])

    result = {
        "schema": SCHEMA,
        "phase": "17C.12B",
        "feature": "INCREMENTAL_CONSUMER_INVALIDATION_MAP",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "AFFECTED_CONSUMER_SELECTION_NO_DELETE",
        "summary": {
            "added_count": len(added),
            "removed_count": len(removed),
            "changed_count": len(changed),
            "affected_count": len(affected),
            "python_added_count": sum(1 for p in added if is_python(p)),
            "python_removed_count": sum(1 for p in removed if is_python(p)),
            "python_changed_count": sum(1 for p in changed if is_python(p)),
            "consumer_count": len(CONSUMERS),
            "invalidated_consumer_count": invalidated_count,
            "delete_allowed": False,
            "automatic_delete_allowed": False,
        },
        "event_flags": event_flags,
        "invalidated_consumers": invalidated,
        "safety_policy": {
            "delete_allowed": False,
            "automatic_delete_allowed": False,
            "reason": "Invalidation selects consumers to rerun only. It never moves, archives, or deletes files.",
        },
        "completion_notice": "PHASE_17C12B_COMPLETE_INCREMENTAL_CONSUMER_INVALIDATION_MAP_ESTABLISHED",
        "next_phase": "17C.12C_INCREMENTAL_UPDATE_EXECUTION_PLAN",
    }

    return result


def write_report() -> dict[str, Any]:
    result = build_invalidation_map()

    json_path = OUT / "incremental_consumer_invalidation_map_phase_17c12b.json"
    txt_path = OUT / "incremental_consumer_invalidation_map_phase_17c12b.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    s = result["summary"]
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.12B INCREMENTAL CONSUMER INVALIDATION MAP",
            "==========================================================",
            f"schema={result['schema']}",
            f"mode={result['mode']}",
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
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    result["artefacts"] = {
        "report": txt_path.relative_to(ROOT).as_posix(),
        "json": json_path.relative_to(ROOT).as_posix(),
    }
    return result


if __name__ == "__main__":
    payload = write_report()
    s = payload["summary"]

    print("PASS_INCREMENTAL_CONSUMER_INVALIDATION_MAP_PHASE_17C12B")
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
    print(f"report={payload['artefacts']['report']}")
    print(f"json={payload['artefacts']['json']}")
    print(f"next_phase={payload['next_phase']}")
