from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from project_maintenance.workspace_architecture.sorting_user_approval_rules_phase_23b import (
    build_sorting_user_approval_rules,
)

SCHEMA = "LEAF_SORTING_SAFE_EXECUTION_SANDBOX_PHASE_23C_V2"
SANDBOX_ROOT = "_leaf_artifacts/workspace_architecture/sorting_execution_sandbox"
SUPPORTED_SIMULATED_OPERATIONS = ("move", "copy", "import_route")
FORBIDDEN_OPERATION_TYPES = ("delete", "archive", "remove", "unlink", "rmdir")


@dataclass(frozen=True)
class SandboxApprovalState:
    source_approved: bool
    destination_approved: bool
    operation_approved: bool
    rollback_approved: bool
    batch_approved: bool
    approved_by: str = "manual_user_approval_required"

    @property
    def fully_approved(self) -> bool:
        return all((
            self.source_approved,
            self.destination_approved,
            self.operation_approved,
            self.rollback_approved,
            self.batch_approved,
        ))


@dataclass(frozen=True)
class SandboxRollbackReference:
    rollback_id: str
    snapshot_required: bool
    snapshot_available: bool
    restore_source_path: str
    restore_destination_path: str
    rollback_plan_hash: str = ""


@dataclass(frozen=True)
class SandboxOperation:
    operation_id: str
    source_path: str
    destination_path: str
    operation_type: str
    approval: SandboxApprovalState
    rollback: SandboxRollbackReference
    simulated_only: bool = True
    real_filesystem_mutation: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SandboxExecutionPlan:
    plan_id: str
    batch_id: str
    operations: tuple[SandboxOperation, ...]
    created_by: str = "LEAF_PHASE_23C_SAFE_EXECUTION_SANDBOX"
    simulation_only: bool = True
    automatic_execution: bool = False
    continuous_watcher: bool = False
    real_filesystem_mutation_allowed: bool = False
    delete_operations_allowed: bool = False
    archive_operations_allowed: bool = False
    small_batch_limit: int = 5


@dataclass(frozen=True)
class SandboxOperationResult:
    operation_id: str
    operation_type: str
    source_path: str
    destination_path: str
    approved: bool
    simulated: bool
    rollback_reference_created: bool
    deterministic_destination_hash: str
    deterministic_operation_hash: str
    blockers: tuple[str, ...]
    execution_log_line: str


@dataclass(frozen=True)
class SandboxExecutionLog:
    plan_id: str
    batch_id: str
    operation_count: int
    simulated_operation_count: int
    rollback_reference_count: int
    blocker_count: int
    plan_hash: str
    result_hash: str
    sandbox_passed: bool
    real_filesystem_mutation_performed: bool
    operations: tuple[SandboxOperationResult, ...]
    blockers: tuple[str, ...]


def _normalise_relative_path(value: str) -> str:
    return Path(value).as_posix().strip()


def _stable_hash(payload: Any, length: int = 16) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _is_safe_relative_path(value: str) -> bool:
    if not value:
        return False
    path = Path(value)
    if path.is_absolute():
        return False
    if any(part in {"..", ""} for part in path.parts):
        return False
    return True


def _operation_to_payload(operation: SandboxOperation) -> dict[str, Any]:
    return asdict(operation)


def _plan_to_payload(plan: SandboxExecutionPlan) -> dict[str, Any]:
    return asdict(plan)


class SortingSafeExecutionSandbox:
    """Deterministic simulation engine for approved sorting operations.

    Phase 23C deliberately performs no repository mutation.
    """

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.sandbox_root = self.project_root / SANDBOX_ROOT
        self.plan_path = self.sandbox_root / "safe_execution_sandbox_plan_phase_23c.json"
        self.result_path = self.sandbox_root / "safe_execution_sandbox_result_phase_23c.json"
        self.report_path = self.sandbox_root / "safe_execution_sandbox_report_phase_23c.txt"

    def build_operation(
        self,
        *,
        operation_id: str,
        source_path: str,
        destination_path: str,
        operation_type: str,
        approved: bool = True,
        snapshot_available: bool = True,
        notes: Iterable[str] = (),
    ) -> SandboxOperation:
        source = _normalise_relative_path(source_path)
        destination = _normalise_relative_path(destination_path)
        rollback_seed = {
            "operation_id": operation_id,
            "source_path": source,
            "destination_path": destination,
            "operation_type": operation_type,
        }
        rollback_id = f"rollback_{_stable_hash(rollback_seed, 20)}"
        rollback_hash = _stable_hash({"rollback": rollback_seed}, 24)

        return SandboxOperation(
            operation_id=operation_id,
            source_path=source,
            destination_path=destination,
            operation_type=operation_type,
            approval=SandboxApprovalState(
                source_approved=approved,
                destination_approved=approved,
                operation_approved=approved,
                rollback_approved=approved,
                batch_approved=approved,
            ),
            rollback=SandboxRollbackReference(
                rollback_id=rollback_id,
                snapshot_required=True,
                snapshot_available=snapshot_available,
                restore_source_path=source,
                restore_destination_path=destination,
                rollback_plan_hash=rollback_hash,
            ),
            simulated_only=True,
            real_filesystem_mutation=False,
            notes=tuple(notes),
        )

    def build_sample_plan(self) -> SandboxExecutionPlan:
        operations = (
            self.build_operation(
                operation_id="sandbox_move_001",
                source_path="_leaf_repository_cleanup_candidates/example_move_source.py",
                destination_path="project_maintenance/workspace_architecture/example_move_destination.py",
                operation_type="move",
                notes=("simulation_only", "no_real_move"),
            ),
            self.build_operation(
                operation_id="sandbox_copy_001",
                source_path="_leaf_repository_cleanup_candidates/example_copy_source.py",
                destination_path="leaf_qt/example_copy_destination.py",
                operation_type="copy",
                notes=("simulation_only", "no_real_copy"),
            ),
            self.build_operation(
                operation_id="sandbox_import_route_001",
                source_path="LEAF_Designs/example_design.leaf.json",
                destination_path="LEAF_Projects/example_project/example_design.leaf.json",
                operation_type="import_route",
                notes=("user_facing_storage_route", "no_real_import"),
            ),
        )
        plan_seed = tuple(_operation_to_payload(operation) for operation in operations)

        return SandboxExecutionPlan(
            plan_id=f"sandbox_plan_{_stable_hash(plan_seed, 20)}",
            batch_id=f"sandbox_batch_{_stable_hash({'batch': plan_seed}, 20)}",
            operations=operations,
            small_batch_limit=5,
        )

    def validate_operation(self, operation: SandboxOperation) -> tuple[str, ...]:
        blockers: list[str] = []
        op_id = operation.operation_id or "missing_operation_id"

        if not operation.operation_id:
            blockers.append("operation_id_missing")
        if operation.operation_type in FORBIDDEN_OPERATION_TYPES:
            blockers.append(f"forbidden_operation_type:{op_id}:{operation.operation_type}")
        if operation.operation_type not in SUPPORTED_SIMULATED_OPERATIONS:
            blockers.append(f"unsupported_operation_type:{op_id}:{operation.operation_type}")
        if not _is_safe_relative_path(operation.source_path):
            blockers.append(f"unsafe_source_path:{op_id}")
        if not _is_safe_relative_path(operation.destination_path):
            blockers.append(f"unsafe_destination_path:{op_id}")
        if operation.source_path == operation.destination_path:
            blockers.append(f"source_destination_identical:{op_id}")
        if operation.approval.fully_approved is not True:
            blockers.append(f"manual_approval_incomplete:{op_id}")
        if operation.rollback.snapshot_required is not True:
            blockers.append(f"rollback_snapshot_not_required:{op_id}")
        if operation.rollback.snapshot_available is not True:
            blockers.append(f"rollback_snapshot_missing:{op_id}")
        if not operation.rollback.rollback_id:
            blockers.append(f"rollback_id_missing:{op_id}")
        if not operation.rollback.rollback_plan_hash:
            blockers.append(f"rollback_plan_hash_missing:{op_id}")
        if operation.simulated_only is not True:
            blockers.append(f"operation_not_marked_simulation_only:{op_id}")
        if operation.real_filesystem_mutation is not False:
            blockers.append(f"real_filesystem_mutation_requested:{op_id}")

        return tuple(blockers)

    def validate_plan(self, plan: SandboxExecutionPlan) -> tuple[str, ...]:
        blockers: list[str] = []

        if not plan.plan_id:
            blockers.append("plan_id_missing")
        if not plan.batch_id:
            blockers.append("batch_id_missing")
        if not plan.operations:
            blockers.append("operation_list_empty")
        if len(plan.operations) > plan.small_batch_limit:
            blockers.append(f"small_batch_limit_exceeded:{len(plan.operations)}>{plan.small_batch_limit}")
        if plan.simulation_only is not True:
            blockers.append("plan_not_simulation_only")
        if plan.real_filesystem_mutation_allowed is not False:
            blockers.append("real_filesystem_mutation_allowed")
        if plan.delete_operations_allowed is not False:
            blockers.append("delete_operations_allowed")
        if plan.archive_operations_allowed is not False:
            blockers.append("archive_operations_allowed")
        if plan.automatic_execution is not False:
            blockers.append("automatic_execution_enabled")
        if plan.continuous_watcher is not False:
            blockers.append("continuous_watcher_enabled")

        operation_ids = [operation.operation_id for operation in plan.operations]
        if len(operation_ids) != len(set(operation_ids)):
            blockers.append("duplicate_operation_ids")

        destinations = [operation.destination_path for operation in plan.operations]
        if len(destinations) != len(set(destinations)):
            blockers.append("duplicate_destinations")

        for operation in plan.operations:
            blockers.extend(self.validate_operation(operation))

        return tuple(blockers)

    def simulate_plan(self, plan: SandboxExecutionPlan) -> SandboxExecutionLog:
        plan_blockers = list(self.validate_plan(plan))
        operation_results: list[SandboxOperationResult] = []

        for index, operation in enumerate(plan.operations, start=1):
            operation_blockers = self.validate_operation(operation)
            operation_payload = _operation_to_payload(operation)
            destination_hash = _stable_hash({
                "destination_path": operation.destination_path,
                "operation_type": operation.operation_type,
            }, 18)
            operation_hash = _stable_hash(operation_payload, 24)
            rollback_created = bool(operation.rollback.rollback_id and operation.rollback.rollback_plan_hash)
            approved = operation.approval.fully_approved and not operation_blockers
            log_line = " | ".join((
                f"{index:03d}",
                operation.operation_id,
                operation.operation_type,
                operation.source_path,
                "=>",
                operation.destination_path,
                f"simulated={True}",
                f"approved={approved}",
                f"rollback={operation.rollback.rollback_id}",
                f"hash={operation_hash}",
            ))

            operation_results.append(SandboxOperationResult(
                operation_id=operation.operation_id,
                operation_type=operation.operation_type,
                source_path=operation.source_path,
                destination_path=operation.destination_path,
                approved=approved,
                simulated=True,
                rollback_reference_created=rollback_created,
                deterministic_destination_hash=destination_hash,
                deterministic_operation_hash=operation_hash,
                blockers=operation_blockers,
                execution_log_line=log_line,
            ))

        result_seed = tuple(asdict(result) for result in operation_results)
        result_hash = _stable_hash({"results": result_seed, "plan_id": plan.plan_id}, 24)
        plan_hash = _stable_hash(_plan_to_payload(plan), 24)
        all_blockers = tuple(plan_blockers)

        return SandboxExecutionLog(
            plan_id=plan.plan_id,
            batch_id=plan.batch_id,
            operation_count=len(plan.operations),
            simulated_operation_count=len(operation_results),
            rollback_reference_count=sum(1 for result in operation_results if result.rollback_reference_created),
            blocker_count=len(all_blockers),
            plan_hash=plan_hash,
            result_hash=result_hash,
            sandbox_passed=len(all_blockers) == 0,
            real_filesystem_mutation_performed=False,
            operations=tuple(operation_results),
            blockers=all_blockers,
        )

    def write_plan_and_result(self, plan: SandboxExecutionPlan, log: SandboxExecutionLog) -> dict[str, Any]:
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

        plan_payload = {
            "schema": SCHEMA,
            "phase": "23C",
            "feature": "SORTING_SAFE_EXECUTION_SANDBOX_PLAN",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "plan": _plan_to_payload(plan),
        }

        result_payload = {
            "schema": SCHEMA,
            "phase": "23C",
            "feature": "SORTING_SAFE_EXECUTION_SANDBOX_RESULT",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "execution_log": asdict(log),
            "safety_policy": {
                "simulation_only": True,
                "real_filesystem_mutation_performed": False,
                "imports_files": False,
                "copies_real_files": False,
                "moves_real_files": False,
                "deletes_files": False,
                "archives_files": False,
                "automatic_execution": False,
                "continuous_watcher": False,
            },
        }

        self.plan_path.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")
        self.result_path.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")

        self.report_path.write_text("\n".join([
            "LEAF PHASE 23C SAFE EXECUTION SANDBOX REPORT",
            "================================================",
            f"schema={SCHEMA}",
            f"plan_id={log.plan_id}",
            f"batch_id={log.batch_id}",
            f"operation_count={log.operation_count}",
            f"simulated_operation_count={log.simulated_operation_count}",
            f"rollback_reference_count={log.rollback_reference_count}",
            f"blocker_count={log.blocker_count}",
            f"sandbox_passed={log.sandbox_passed}",
            f"plan_hash={log.plan_hash}",
            f"result_hash={log.result_hash}",
            f"real_filesystem_mutation_performed={log.real_filesystem_mutation_performed}",
            "",
            "Simulated execution log:",
            *[result.execution_log_line for result in log.operations],
            "",
            "Blockers:",
            *(log.blockers or ("none",)),
        ]), encoding="utf-8")

        return {
            "plan_json": self.plan_path.relative_to(self.project_root).as_posix(),
            "result_json": self.result_path.relative_to(self.project_root).as_posix(),
            "report_txt": self.report_path.relative_to(self.project_root).as_posix(),
        }

    def run_default_simulation(self) -> dict[str, Any]:
        plan = self.build_sample_plan()
        log = self.simulate_plan(plan)
        paths = self.write_plan_and_result(plan, log)
        return {"plan": plan, "log": log, "paths": paths}


def build_sorting_safe_execution_sandbox_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    approval_rules = build_sorting_user_approval_rules(project_root)
    sandbox = SortingSafeExecutionSandbox(project_root)
    run = sandbox.run_default_simulation()

    plan: SandboxExecutionPlan = run["plan"]
    log: SandboxExecutionLog = run["log"]
    paths = run["paths"]

    summary = {
        "sandbox_class": "SortingSafeExecutionSandbox",
        "sandbox_root": SANDBOX_ROOT,
        "plan_path": paths["plan_json"],
        "result_path": paths["result_json"],
        "report_path": paths["report_txt"],
        "plan_id": log.plan_id,
        "batch_id": log.batch_id,
        "operation_count": log.operation_count,
        "simulated_operation_count": log.simulated_operation_count,
        "rollback_reference_count": log.rollback_reference_count,
        "blocker_count": log.blocker_count,
        "sandbox_passed": log.sandbox_passed,
        "plan_hash": log.plan_hash,
        "result_hash": log.result_hash,
        "operation_types": sorted({operation.operation_type for operation in plan.operations}),
        "supported_simulated_operations": list(SUPPORTED_SIMULATED_OPERATIONS),
        "manual_approval_required": approval_rules.get("summary", {}).get("manual_approval_required"),
        "rollback_snapshot_required": approval_rules.get("summary", {}).get("rollback_snapshot_required"),
        "small_batch_limit_required": approval_rules.get("summary", {}).get("small_batch_limit_required"),
        "simulation_only": True,
        "real_filesystem_mutation_performed": False,
        "imports_files": False,
        "copies_real_files": False,
        "moves_real_files": False,
        "deletes_files": False,
        "archives_files": False,
        "automatic_execution": False,
        "continuous_watcher": False,
        "ready_for_23d_small_batch_execution": True,
    }

    return {
        "schema": SCHEMA,
        "phase": "23C",
        "feature": "SORTING_SAFE_EXECUTION_SANDBOX",
        "source_approval_rules_schema": approval_rules.get("schema"),
        "execution_model": {
            "plan_model": "SandboxExecutionPlan",
            "operation_model": "SandboxOperation",
            "approval_model": "SandboxApprovalState",
            "rollback_model": "SandboxRollbackReference",
            "result_model": "SandboxOperationResult",
            "log_model": "SandboxExecutionLog",
        },
        "summary": summary,
    }


def write_sorting_safe_execution_sandbox(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_23c"
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshot = build_sorting_safe_execution_sandbox_snapshot(root)
    json_path = out_dir / "sorting_safe_execution_sandbox_snapshot_phase_23c.json"
    txt_path = out_dir / "sorting_safe_execution_sandbox_snapshot_phase_23c.txt"

    json_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    summary = snapshot["summary"]

    txt_path.write_text("\n".join([
        "LEAF PHASE 23C SAFE EXECUTION SANDBOX SNAPSHOT",
        "=================================================",
        f"schema={snapshot['schema']}",
        f"source_approval_rules_schema={snapshot['source_approval_rules_schema']}",
        f"sandbox_class={summary['sandbox_class']}",
        f"operation_count={summary['operation_count']}",
        f"simulated_operation_count={summary['simulated_operation_count']}",
        f"rollback_reference_count={summary['rollback_reference_count']}",
        f"blocker_count={summary['blocker_count']}",
        f"sandbox_passed={summary['sandbox_passed']}",
        f"simulation_only={summary['simulation_only']}",
        f"real_filesystem_mutation_performed={summary['real_filesystem_mutation_performed']}",
        f"automatic_execution={summary['automatic_execution']}",
        f"continuous_watcher={summary['continuous_watcher']}",
        f"ready_for_23d_small_batch_execution={summary['ready_for_23d_small_batch_execution']}",
    ]), encoding="utf-8")

    return {
        "snapshot": snapshot,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_sorting_safe_execution_sandbox(Path.cwd())
    summary = result["snapshot"]["summary"]
    print("PASS_PHASE_23C_SAFE_EXECUTION_SANDBOX_WRITTEN")
    print(f"schema={result['snapshot']['schema']}")
    print(f"operation_count={summary['operation_count']}")
    print(f"simulated_operation_count={summary['simulated_operation_count']}")
    print(f"rollback_reference_count={summary['rollback_reference_count']}")
    print(f"blocker_count={summary['blocker_count']}")
    print(f"sandbox_passed={summary['sandbox_passed']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
