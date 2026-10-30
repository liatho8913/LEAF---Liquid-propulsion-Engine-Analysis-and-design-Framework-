from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.controlled_import_execution_phase_19e import (
    build_controlled_import_execution_plan,
)

SCHEMA = "LEAF_IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT_PHASE_19F_V1"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


def build_import_verification_rollback_snapshot(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    execution = build_controlled_import_execution_plan(root, execute=False)

    executed_records = execution.get("executed_records", {})
    prepared_records = execution.get("prepared_records", {})
    blocked_records = execution.get("blocked_records", {})

    verification_records: dict[str, dict[str, Any]] = {}
    rollback_records: dict[str, dict[str, Any]] = {}
    failures: list[str] = []

    for review_id, record in executed_records.items():
        destination = root / str(record.get("destination_path", ""))
        expected_hash = record.get("source_sha256_actual") or record.get("source_sha256_expected")

        if not destination.exists():
            status = "FAILED_DESTINATION_MISSING"
            actual_hash = ""
            failures.append(f"destination_missing:{review_id}")
        else:
            actual_hash = _sha256(destination)
            status = "VERIFIED" if actual_hash == expected_hash else "FAILED_HASH_MISMATCH"
            if status != "VERIFIED":
                failures.append(f"hash_mismatch:{review_id}")

        verification_records[review_id] = {
            "review_id": review_id,
            "destination_path": record.get("destination_path"),
            "expected_sha256": expected_hash,
            "actual_sha256": actual_hash,
            "verification_status": status,
            "verified": status == "VERIFIED",
        }

        rollback_records[review_id] = {
            "review_id": review_id,
            "rollback_type": "DELETE_IMPORTED_COPY_ONLY",
            "target_path": record.get("destination_path"),
            "source_preserved": True,
            "rollback_requires_manual_execution": True,
            "rollback_automatic_execution_allowed": False,
            "delete_original_allowed": False,
            "move_original_allowed": False,
            "archive_original_allowed": False,
            "reason": "Rollback applies only to the imported copy because the source is always preserved.",
        }

    no_op_snapshot = {
        "no_imports_executed": len(executed_records) == 0,
        "prepared_records": len(prepared_records),
        "blocked_records": len(blocked_records),
        "safe_no_op_state": len(executed_records) == 0 and len(verification_records) == 0 and len(rollback_records) == 0,
        "meaning": "No import rollback is required because no controlled import was executed.",
    }

    return {
        "schema": SCHEMA,
        "phase": "19F",
        "feature": "IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_execution_schema": execution.get("schema"),
        "source_execution_mode": execution.get("execution_mode"),
        "design_principle": "Every controlled import must be verifiable and rollback-aware; if nothing executes, the correct rollback state is a certified no-op snapshot.",
        "execution_policy": {
            "verification_is_read_only": True,
            "creates_rollback_snapshot_only": True,
            "imports_files": False,
            "copies_files": False,
            "moves_existing_files": False,
            "deletes_files": False,
            "archives_files": False,
            "rollback_execution_allowed": False,
            "manual_rollback_required": True,
        },
        "summary": {
            "executed_records": len(executed_records),
            "verification_records": len(verification_records),
            "rollback_records": len(rollback_records),
            "verified_imports": sum(1 for item in verification_records.values() if item["verified"]),
            "verification_failures": len(failures),
            "safe_no_op_state": no_op_snapshot["safe_no_op_state"],
            "rollback_execution_allowed": False,
            "delete_operations_created": 0,
            "move_operations_created": 0,
            "archive_operations_created": 0,
        },
        "no_op_snapshot": no_op_snapshot,
        "verification_records": dict(sorted(verification_records.items())),
        "rollback_records": dict(sorted(rollback_records.items())),
        "failures": failures,
    }


def write_import_verification_rollback_snapshot(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/workspace_architecture/phase_19f/import_verification_rollback_snapshot_phase_19f.json",
) -> dict[str, Any]:
    snapshot = build_import_verification_rollback_snapshot(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


if __name__ == "__main__":
    snapshot = write_import_verification_rollback_snapshot(".")
    summary = snapshot["summary"]

    print("LEAF_IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT_PHASE_19F")
    print(f"schema={snapshot['schema']}")
    print(f"source_execution_schema={snapshot['source_execution_schema']}")
    print(f"source_execution_mode={snapshot['source_execution_mode']}")
    print(f"executed_records={summary['executed_records']}")
    print(f"verification_records={summary['verification_records']}")
    print(f"rollback_records={summary['rollback_records']}")
    print(f"safe_no_op_state={summary['safe_no_op_state']}")
