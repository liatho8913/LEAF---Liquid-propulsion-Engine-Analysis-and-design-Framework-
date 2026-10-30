from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.sorting_safe_execution_sandbox_phase_23c import (
    SCHEMA as PHASE_23C_SCHEMA,
    SandboxExecutionLog,
    SandboxExecutionPlan,
    SandboxOperation,
    SortingSafeExecutionSandbox,
)

SCHEMA = "LEAF_SORTING_SMALL_BATCH_EXECUTION_PHASE_23D_V1"

EXECUTION_LAB_ROOT = "_leaf_artifacts/workspace_architecture/phase_23d/execution_lab"
SUPPORTED_SMALL_BATCH_OPERATIONS = ("move", "copy", "import_route")
FORBIDDEN_SMALL_BATCH_OPERATIONS = ("delete", "archive", "remove", "unlink", "rmdir")
SMALL_BATCH_LIMIT = 5


@dataclass(frozen=True)
class SmallBatchOperationExecution:
    operation_id: str
    operation_type: str
    source_path: str
    destination_path: str
    executed: bool
    rollback_reference_id: str
    source_exists_before: bool
    destination_exists_after: bool
    source_exists_after: bool
    content_hash_after: str
    execution_blockers: tuple[str, ...]


@dataclass(frozen=True)
class SmallBatchExecutionResult:
    schema: str
    phase: str
    source_sandbox_schema: str
    plan_id: str
    batch_id: str
    operation_count: int
    executed_operation_count: int
    execution_lab_root: str
    active_repository_mutated: bool
    execution_lab_only: bool
    delete_operations_performed: bool
    archive_operations_performed: bool
    automatic_execution: bool
    continuous_watcher: bool
    rollback_manifest_created: bool
    blocker_count: int
    passed: bool
    operations: tuple[SmallBatchOperationExecution, ...]
    blockers: tuple[str, ...]
    deterministic_result_hash: str


def _stable_hash(payload: Any, length: int = 24) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _file_hash(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:24]


def _is_relative_safe(value: str) -> bool:
    path = Path(value)
    if not value:
        return False
    if path.is_absolute():
        return False
    if any(part in {"..", ""} for part in path.parts):
        return False
    return True


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


class SortingSmallBatchExecutionEngine:
    """Controlled tiny-batch executor for Phase 23D.

    This is deliberately limited to a disposable execution lab under
    _leaf_artifacts. It proves the execution pipeline without touching active
    LEAF source, user designs, projects, reports, or exports.
    """

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.execution_lab_root = self.project_root / EXECUTION_LAB_ROOT
        self.source_root = self.execution_lab_root / "source"
        self.destination_root = self.execution_lab_root / "destination"
        self.rollback_root = self.execution_lab_root / "rollback_manifest"
        self.result_json = self.project_root / "_leaf_artifacts" / "workspace_architecture" / "phase_23d" / "sorting_small_batch_execution_result_phase_23d.json"
        self.report_txt = self.project_root / "_leaf_artifacts" / "workspace_architecture" / "phase_23d" / "sorting_small_batch_execution_report_phase_23d.txt"

    def reset_execution_lab(self) -> None:
        if self.execution_lab_root.exists():
            shutil.rmtree(self.execution_lab_root)
        self.source_root.mkdir(parents=True, exist_ok=True)
        self.destination_root.mkdir(parents=True, exist_ok=True)
        self.rollback_root.mkdir(parents=True, exist_ok=True)

    def create_fixture_file(self, relative_path: str, content: str) -> str:
        target = self.execution_lab_root / relative_path
        if not _is_inside(target, self.execution_lab_root):
            raise ValueError(f"Fixture path escaped execution lab: {relative_path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target.relative_to(self.project_root).as_posix()

    def build_small_batch_plan(self) -> SandboxExecutionPlan:
        self.reset_execution_lab()

        move_source = self.create_fixture_file(
            "source/move_candidate_alpha.py",
            "print('phase_23d_move_candidate_alpha')\n",
        )
        copy_source = self.create_fixture_file(
            "source/copy_candidate_beta.py",
            "print('phase_23d_copy_candidate_beta')\n",
        )
        import_source = self.create_fixture_file(
            "source/import_route_candidate_gamma.leaf.json",
            '{"name": "phase_23d_import_route_candidate_gamma"}\n',
        )

        sandbox = SortingSafeExecutionSandbox(self.project_root)
        operations = (
            sandbox.build_operation(
                operation_id="small_batch_move_001",
                source_path=move_source,
                destination_path=(self.destination_root / "move_candidate_alpha.py").relative_to(self.project_root).as_posix(),
                operation_type="move",
                approved=True,
                snapshot_available=True,
                notes=("phase_23d_execution_lab_only", "tiny_batch"),
            ),
            sandbox.build_operation(
                operation_id="small_batch_copy_001",
                source_path=copy_source,
                destination_path=(self.destination_root / "copy_candidate_beta.py").relative_to(self.project_root).as_posix(),
                operation_type="copy",
                approved=True,
                snapshot_available=True,
                notes=("phase_23d_execution_lab_only", "tiny_batch"),
            ),
            sandbox.build_operation(
                operation_id="small_batch_import_route_001",
                source_path=import_source,
                destination_path=(self.destination_root / "import_route_candidate_gamma.leaf.json").relative_to(self.project_root).as_posix(),
                operation_type="import_route",
                approved=True,
                snapshot_available=True,
                notes=("phase_23d_execution_lab_only", "tiny_batch"),
            ),
        )

        seed = tuple(asdict(operation) for operation in operations)
        return SandboxExecutionPlan(
            plan_id=f"small_batch_plan_{_stable_hash(seed, 20)}",
            batch_id=f"small_batch_batch_{_stable_hash({'batch': seed}, 20)}",
            operations=operations,
            small_batch_limit=SMALL_BATCH_LIMIT,
            simulation_only=False,
            real_filesystem_mutation_allowed=True,
            automatic_execution=False,
            continuous_watcher=False,
            delete_operations_allowed=False,
            archive_operations_allowed=False,
        )

    def validate_plan_for_small_batch_execution(self, plan: SandboxExecutionPlan) -> tuple[str, ...]:
        blockers: list[str] = []

        if len(plan.operations) > SMALL_BATCH_LIMIT:
            blockers.append(f"small_batch_limit_exceeded:{len(plan.operations)}>{SMALL_BATCH_LIMIT}")

        if plan.automatic_execution is not False:
            blockers.append("automatic_execution_enabled")

        if plan.continuous_watcher is not False:
            blockers.append("continuous_watcher_enabled")

        if plan.delete_operations_allowed is not False:
            blockers.append("delete_operations_allowed")

        if plan.archive_operations_allowed is not False:
            blockers.append("archive_operations_allowed")

        if plan.real_filesystem_mutation_allowed is not True:
            blockers.append("small_batch_execution_not_enabled_for_execution_lab")

        sandbox = SortingSafeExecutionSandbox(self.project_root)
        sandbox_log: SandboxExecutionLog = sandbox.simulate_plan(
            SandboxExecutionPlan(
                plan_id=plan.plan_id,
                batch_id=plan.batch_id,
                operations=plan.operations,
                simulation_only=True,
                automatic_execution=False,
                continuous_watcher=False,
                real_filesystem_mutation_allowed=False,
                delete_operations_allowed=False,
                archive_operations_allowed=False,
                small_batch_limit=SMALL_BATCH_LIMIT,
            )
        )

        if sandbox_log.blockers:
            blockers.extend(f"sandbox_validation_blocker:{blocker}" for blocker in sandbox_log.blockers)

        for operation in plan.operations:
            source = self.project_root / operation.source_path
            destination = self.project_root / operation.destination_path

            if operation.operation_type in FORBIDDEN_SMALL_BATCH_OPERATIONS:
                blockers.append(f"forbidden_operation_type:{operation.operation_id}:{operation.operation_type}")

            if operation.operation_type not in SUPPORTED_SMALL_BATCH_OPERATIONS:
                blockers.append(f"unsupported_operation_type:{operation.operation_id}:{operation.operation_type}")

            if not _is_relative_safe(operation.source_path):
                blockers.append(f"unsafe_source_path:{operation.operation_id}")

            if not _is_relative_safe(operation.destination_path):
                blockers.append(f"unsafe_destination_path:{operation.operation_id}")

            if not _is_inside(source, self.execution_lab_root):
                blockers.append(f"source_outside_execution_lab:{operation.operation_id}")

            if not _is_inside(destination, self.execution_lab_root):
                blockers.append(f"destination_outside_execution_lab:{operation.operation_id}")

            if not source.exists():
                blockers.append(f"source_missing:{operation.operation_id}")

            if not operation.approval.fully_approved:
                blockers.append(f"manual_approval_incomplete:{operation.operation_id}")

            if not operation.rollback.rollback_id:
                blockers.append(f"rollback_reference_missing:{operation.operation_id}")

        return tuple(blockers)

    def _write_rollback_manifest(self, operation: SandboxOperation, source_hash_before: str) -> Path:
        manifest = {
            "schema": SCHEMA,
            "phase": "23D",
            "operation_id": operation.operation_id,
            "operation_type": operation.operation_type,
            "source_path": operation.source_path,
            "destination_path": operation.destination_path,
            "rollback_reference": asdict(operation.rollback),
            "source_hash_before": source_hash_before,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        path = self.rollback_root / f"{operation.operation_id}_rollback_manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    def execute_plan(self, plan: SandboxExecutionPlan) -> SmallBatchExecutionResult:
        plan_blockers = list(self.validate_plan_for_small_batch_execution(plan))
        operation_results: list[SmallBatchOperationExecution] = []

        if plan_blockers:
            return self._build_result(plan, operation_results, tuple(plan_blockers), passed=False)

        for operation in plan.operations:
            execution_blockers: list[str] = []
            source = self.project_root / operation.source_path
            destination = self.project_root / operation.destination_path

            source_exists_before = source.exists()
            source_hash_before = _file_hash(source)
            self._write_rollback_manifest(operation, source_hash_before)

            destination.parent.mkdir(parents=True, exist_ok=True)

            if operation.operation_type == "move":
                shutil.move(str(source), str(destination))
            elif operation.operation_type in {"copy", "import_route"}:
                shutil.copy2(str(source), str(destination))
            else:
                execution_blockers.append(f"unsupported_operation_type:{operation.operation_type}")

            destination_exists_after = destination.exists()
            source_exists_after = source.exists()
            content_hash_after = _file_hash(destination)

            if not destination_exists_after:
                execution_blockers.append("destination_missing_after_execution")

            if operation.operation_type == "move" and source_exists_after:
                execution_blockers.append("move_source_still_exists_after_execution")

            if operation.operation_type in {"copy", "import_route"} and not source_exists_after:
                execution_blockers.append("copy_source_missing_after_execution")

            if source_hash_before and content_hash_after and source_hash_before != content_hash_after:
                execution_blockers.append("content_hash_changed_during_execution")

            operation_results.append(SmallBatchOperationExecution(
                operation_id=operation.operation_id,
                operation_type=operation.operation_type,
                source_path=operation.source_path,
                destination_path=operation.destination_path,
                executed=not execution_blockers,
                rollback_reference_id=operation.rollback.rollback_id,
                source_exists_before=source_exists_before,
                destination_exists_after=destination_exists_after,
                source_exists_after=source_exists_after,
                content_hash_after=content_hash_after,
                execution_blockers=tuple(execution_blockers),
            ))

        blockers = tuple(
            blocker
            for operation_result in operation_results
            for blocker in operation_result.execution_blockers
        )

        return self._build_result(plan, operation_results, blockers, passed=not blockers)

    def _build_result(
        self,
        plan: SandboxExecutionPlan,
        operation_results: list[SmallBatchOperationExecution],
        blockers: tuple[str, ...],
        *,
        passed: bool,
    ) -> SmallBatchExecutionResult:
        rollback_manifest_created = all(
            (self.rollback_root / f"{operation.operation_id}_rollback_manifest.json").exists()
            for operation in plan.operations
        )

        seed = {
            "plan_id": plan.plan_id,
            "batch_id": plan.batch_id,
            "operations": [asdict(operation) for operation in operation_results],
            "blockers": blockers,
        }

        return SmallBatchExecutionResult(
            schema=SCHEMA,
            phase="23D",
            source_sandbox_schema=PHASE_23C_SCHEMA,
            plan_id=plan.plan_id,
            batch_id=plan.batch_id,
            operation_count=len(plan.operations),
            executed_operation_count=sum(1 for operation in operation_results if operation.executed),
            execution_lab_root=EXECUTION_LAB_ROOT,
            active_repository_mutated=False,
            execution_lab_only=True,
            delete_operations_performed=False,
            archive_operations_performed=False,
            automatic_execution=False,
            continuous_watcher=False,
            rollback_manifest_created=rollback_manifest_created,
            blocker_count=len(blockers),
            passed=passed,
            operations=tuple(operation_results),
            blockers=blockers,
            deterministic_result_hash=_stable_hash(seed, 24),
        )

    def write_result(self, result: SmallBatchExecutionResult) -> dict[str, str]:
        self.result_json.parent.mkdir(parents=True, exist_ok=True)
        self.result_json.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

        self.report_txt.write_text("\n".join([
            "LEAF PHASE 23D SMALL BATCH EXECUTION REPORT",
            "============================================",
            f"schema={result.schema}",
            f"source_sandbox_schema={result.source_sandbox_schema}",
            f"plan_id={result.plan_id}",
            f"batch_id={result.batch_id}",
            f"operation_count={result.operation_count}",
            f"executed_operation_count={result.executed_operation_count}",
            f"execution_lab_root={result.execution_lab_root}",
            f"active_repository_mutated={result.active_repository_mutated}",
            f"execution_lab_only={result.execution_lab_only}",
            f"delete_operations_performed={result.delete_operations_performed}",
            f"archive_operations_performed={result.archive_operations_performed}",
            f"automatic_execution={result.automatic_execution}",
            f"continuous_watcher={result.continuous_watcher}",
            f"rollback_manifest_created={result.rollback_manifest_created}",
            f"blocker_count={result.blocker_count}",
            f"passed={result.passed}",
            f"deterministic_result_hash={result.deterministic_result_hash}",
            "",
            "Executed operations:",
            *[
                " | ".join([
                    operation.operation_id,
                    operation.operation_type,
                    operation.source_path,
                    "=>",
                    operation.destination_path,
                    f"executed={operation.executed}",
                    f"rollback={operation.rollback_reference_id}",
                ])
                for operation in result.operations
            ],
            "",
            "Blockers:",
            *(result.blockers or ("none",)),
        ]), encoding="utf-8")

        return {
            "json": self.result_json.relative_to(self.project_root).as_posix(),
            "report": self.report_txt.relative_to(self.project_root).as_posix(),
        }


def run_sorting_small_batch_execution(project_root: str | Path = ".") -> dict[str, Any]:
    engine = SortingSmallBatchExecutionEngine(project_root)
    plan = engine.build_small_batch_plan()
    result = engine.execute_plan(plan)
    paths = engine.write_result(result)
    return {
        "schema": SCHEMA,
        "phase": "23D",
        "feature": "SORTING_SMALL_BATCH_EXECUTION",
        "source_sandbox_schema": PHASE_23C_SCHEMA,
        "result": asdict(result),
        "paths": paths,
        "completion_notice": "PHASE_23D_COMPLETE_SMALL_BATCH_EXECUTION_ESTABLISHED" if result.passed else "PHASE_23D_BLOCKED",
        "next_phase": "23E_ROLLBACK_VALIDATION",
    }


if __name__ == "__main__":
    run = run_sorting_small_batch_execution(Path.cwd())
    result = run["result"]
    print("PASS_PHASE_23D_SMALL_BATCH_EXECUTION_WRITTEN" if result["passed"] else "FAIL_PHASE_23D_SMALL_BATCH_EXECUTION_WRITTEN")
    print(f"schema={run['schema']}")
    print(f"source_sandbox_schema={run['source_sandbox_schema']}")
    print(f"operation_count={result['operation_count']}")
    print(f"executed_operation_count={result['executed_operation_count']}")
    print(f"active_repository_mutated={result['active_repository_mutated']}")
    print(f"execution_lab_only={result['execution_lab_only']}")
    print(f"rollback_manifest_created={result['rollback_manifest_created']}")
    print(f"blocker_count={result['blocker_count']}")
    print(f"passed={result['passed']}")
    print(f"completion_notice={run['completion_notice']}")
    print(f"report={run['paths']['report']}")
    print(f"json={run['paths']['json']}")
    print(f"next_phase={run['next_phase']}")
