from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_scan_controller_phase_17c11a import (
    build_repository_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c12a"
OUT.mkdir(parents=True, exist_ok=True)

BASELINE = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c11a" / "repository_scan_controller_snapshot_phase_17c11a.json"

SCHEMA = "LEAF_INCREMENTAL_SNAPSHOT_CONTROLLER_PHASE_17C12A_V1"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def by_path(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["path"]: item for item in snapshot.get("files", []) if "path" in item}


def compare_snapshots(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    old_files = by_path(old)
    new_files = by_path(new)

    old_paths = set(old_files)
    new_paths = set(new_files)

    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)

    changed = []
    unchanged = []

    for path in sorted(old_paths & new_paths):
        old_item = old_files[path]
        new_item = new_files[path]

        if (
            old_item.get("sha256") != new_item.get("sha256")
            or old_item.get("size_bytes") != new_item.get("size_bytes")
            or old_item.get("modified_ns") != new_item.get("modified_ns")
        ):
            changed.append(path)
        else:
            unchanged.append(path)

    affected = sorted(set(added) | set(removed) | set(changed))

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "affected": affected,
    }


def build_incremental_snapshot_report() -> dict[str, Any]:
    baseline = load_json(BASELINE)
    current = build_repository_snapshot()
    delta = compare_snapshots(baseline, current)

    result = {
        "schema": SCHEMA,
        "phase": "17C.12A",
        "feature": "INCREMENTAL_SNAPSHOT_CONTROLLER_FOUNDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "BASELINE_SNAPSHOT_DELTA_DETECTION_NO_DELETE",
        "summary": {
            "baseline_files": len(baseline.get("files", [])),
            "current_files": len(current.get("files", [])),
            "added_count": len(delta["added"]),
            "removed_count": len(delta["removed"]),
            "changed_count": len(delta["changed"]),
            "unchanged_count": len(delta["unchanged"]),
            "affected_count": len(delta["affected"]),
            "incremental_update_available": True,
            "delete_allowed": False,
            "automatic_delete_allowed": False,
        },
        "delta": delta,
        "safety_policy": {
            "delete_allowed": False,
            "automatic_delete_allowed": False,
            "reason": "Incremental snapshot detection only identifies repository changes. Deletion remains locked behind 17C.10D eligibility and 17C.10E controlled removal.",
        },
        "completion_notice": "PHASE_17C12A_COMPLETE_INCREMENTAL_SNAPSHOT_CONTROLLER_FOUNDATION_ESTABLISHED",
        "next_phase": "17C.12B_INCREMENTAL_CONSUMER_INVALIDATION_MAP",
    }

    return result


def write_report() -> dict[str, Any]:
    result = build_incremental_snapshot_report()

    json_path = OUT / "incremental_snapshot_controller_phase_17c12a.json"
    txt_path = OUT / "incremental_snapshot_controller_phase_17c12a.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    s = result["summary"]
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.12A INCREMENTAL SNAPSHOT CONTROLLER",
            "====================================================",
            f"schema={result['schema']}",
            f"mode={result['mode']}",
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

    print("PASS_INCREMENTAL_SNAPSHOT_CONTROLLER_PHASE_17C12A")
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
    print(f"report={payload['artefacts']['report']}")
    print(f"json={payload['artefacts']['json']}")
    print(f"next_phase={payload['next_phase']}")
