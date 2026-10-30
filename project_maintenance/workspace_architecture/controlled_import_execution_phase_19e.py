from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.manual_import_approval_gate_phase_19d import (
    build_manual_import_approval_gate,
)

SCHEMA = "LEAF_CONTROLLED_IMPORT_EXECUTION_PHASE_19E_V1"

APPROVAL_ARTIFACT = Path("_leaf_artifacts/workspace_architecture/phase_19d/manual_import_approval_gate_phase_19d.json")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_approval_source(root: Path) -> dict[str, Any]:
    artifact = root / APPROVAL_ARTIFACT
    if artifact.exists():
        return json.loads(artifact.read_text(encoding="utf-8"))
    return build_manual_import_approval_gate(root)


def _is_record_approved(record: dict[str, Any]) -> bool:
    return (
        record.get("approval_state") == "APPROVED"
        and record.get("approved") is True
        and record.get("execution_unlocked") is True
        and record.get("copy_import_unlocked") is True
        and bool(record.get("manual_approver"))
    )


def build_controlled_import_execution_plan(root: str | Path = ".", *, execute: bool = False) -> dict[str, Any]:
    root = Path(root)
    approval = _load_approval_source(root)
    approval_records = approval.get("approval_records", {})

    prepared: dict[str, dict[str, Any]] = {}
    blocked: dict[str, dict[str, Any]] = {}
    executed: dict[str, dict[str, Any]] = {}
    failures: list[str] = []

    for review_id, record in approval_records.items():
        source = root / str(record.get("source_path", ""))
        destination = root / str(record.get("recommended_destination", ""))

        approved = _is_record_approved(record)

        base = {
            "review_id": review_id,
            "plan_id": record.get("plan_id"),
            "source_path": record.get("source_path"),
            "destination_path": record.get("recommended_destination"),
            "operation": "COPY_IMPORT",
            "copy_not_move": True,
            "preserve_source": True,
            "delete_source_allowed": False,
            "archive_source_allowed": False,
            "move_source_allowed": False,
            "overwrite_allowed": False,
            "approved": approved,
            "manual_approver": record.get("manual_approver", ""),
            "source_sha256_expected": record.get("source_sha256"),
            "execution_requested": execute,
        }

        block_reasons = []

        if not approved:
            block_reasons.append("manual_approval_missing_or_incomplete")

        if not source.exists() or not source.is_file():
            block_reasons.append("source_missing")

        if destination.exists():
            block_reasons.append("destination_already_exists")

        if source.exists() and source.is_file():
            actual_hash = _sha256(source)
            base["source_sha256_actual"] = actual_hash
            if actual_hash != record.get("source_sha256"):
                block_reasons.append("source_hash_mismatch")
        else:
            base["source_sha256_actual"] = ""

        if block_reasons:
            blocked[review_id] = {
                **base,
                "status": "BLOCKED",
                "block_reasons": block_reasons,
                "execution_allowed": False,
                "executed": False,
            }
            continue

        prepared[review_id] = {
            **base,
            "status": "READY_FOR_CONTROLLED_COPY" if execute else "READY_BUT_NOT_EXECUTED_DRY_RUN",
            "block_reasons": [],
            "execution_allowed": bool(execute),
            "executed": False,
        }

        if execute:
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                copied_hash = _sha256(destination)

                if copied_hash != base["source_sha256_actual"]:
                    failures.append(f"copied_hash_mismatch:{review_id}")
                    continue

                executed[review_id] = {
                    **prepared[review_id],
                    "status": "EXECUTED_COPY_IMPORT",
                    "destination_sha256": copied_hash,
                    "executed": True,
                    "execution_allowed": True,
                    "executed_timestamp": datetime.now().isoformat(timespec="seconds"),
                }
            except Exception as exc:
                failures.append(f"copy_failed:{review_id}:{exc!r}")

    return {
        "schema": SCHEMA,
        "phase": "19E",
        "feature": "CONTROLLED_IMPORT_EXECUTION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_approval_schema": approval.get("schema"),
        "execution_mode": "EXECUTE" if execute else "DRY_RUN_VALIDATION",
        "design_principle": "Controlled import execution must copy only explicitly approved records, preserve sources, verify hashes, and never delete or move originals.",
        "execution_policy": {
            "manual_approval_required": True,
            "copy_only": True,
            "preserve_source": True,
            "hash_verification_required": True,
            "overwrite_allowed": False,
            "delete_source_allowed": False,
            "archive_source_allowed": False,
            "move_source_allowed": False,
            "execute_requested": execute,
        },
        "summary": {
            "approval_records": len(approval_records),
            "approved_records_detected": sum(1 for record in approval_records.values() if _is_record_approved(record)),
            "prepared_records": len(prepared),
            "blocked_records": len(blocked),
            "executed_records": len(executed),
            "copy_operations_executed": len(executed),
            "move_operations_executed": 0,
            "delete_operations_executed": 0,
            "archive_operations_executed": 0,
            "overwrite_operations_executed": 0,
            "failures": len(failures),
        },
        "prepared_records": dict(sorted(prepared.items())),
        "blocked_records": dict(sorted(blocked.items())),
        "executed_records": dict(sorted(executed.items())),
        "failures": failures,
    }


def write_controlled_import_execution_plan(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/workspace_architecture/phase_19e/controlled_import_execution_phase_19e.json",
    *,
    execute: bool = False,
) -> dict[str, Any]:
    result = build_controlled_import_execution_plan(root, execute=execute)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = write_controlled_import_execution_plan(".", execute=False)
    summary = result["summary"]

    print("LEAF_CONTROLLED_IMPORT_EXECUTION_PHASE_19E")
    print(f"schema={result['schema']}")
    print(f"source_approval_schema={result['source_approval_schema']}")
    print(f"execution_mode={result['execution_mode']}")
    print(f"approval_records={summary['approval_records']}")
    print(f"approved_records_detected={summary['approved_records_detected']}")
    print(f"prepared_records={summary['prepared_records']}")
    print(f"blocked_records={summary['blocked_records']}")
    print(f"executed_records={summary['executed_records']}")
    print(f"copy_operations_executed={summary['copy_operations_executed']}")
