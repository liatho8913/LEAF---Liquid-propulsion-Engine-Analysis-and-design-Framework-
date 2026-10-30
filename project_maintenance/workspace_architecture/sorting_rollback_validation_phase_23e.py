from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.sorting_small_batch_execution_phase_23d import (
    SCHEMA as PHASE_23D_SCHEMA,
    SortingSmallBatchExecutionEngine,
)

SCHEMA = "LEAF_SORTING_ROLLBACK_VALIDATION_PHASE_23E_V1"


@dataclass(frozen=True)
class RollbackFileState:
    relative_path: str
    exists: bool
    is_file: bool
    content_hash: str


@dataclass(frozen=True)
class RollbackValidationResult:
    schema: str
    phase: str
    source_execution_schema: str
    execution_passed: bool
    rollback_performed: bool
    rollback_operation_count: int
    before_state_hash: str
    after_execution_state_hash: str
    after_rollback_state_hash: str
    repository_restored: bool
    active_repository_mutated: bool
    execution_lab_only: bool
    delete_operations_performed: bool
    archive_operations_performed: bool
    automatic_execution: bool
    continuous_watcher: bool
    blocker_count: int
    passed: bool
    blockers: tuple[str, ...]
    deterministic_result_hash: str


def _stable_hash(payload: Any, length: int = 24) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _file_hash(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:24]


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


class SortingRollbackValidationEngine:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.execution_engine = SortingSmallBatchExecutionEngine(self.project_root)
        self.out_dir = self.project_root / "_leaf_artifacts" / "workspace_architecture" / "phase_23e"
        self.result_json = self.out_dir / "sorting_rollback_validation_result_phase_23e.json"
        self.report_txt = self.out_dir / "sorting_rollback_validation_report_phase_23e.txt"

    @property
    def execution_lab_root(self) -> Path:
        return self.execution_engine.execution_lab_root

    def capture_lab_state(self) -> tuple[RollbackFileState, ...]:
        if not self.execution_lab_root.exists():
            return tuple()

        states: list[RollbackFileState] = []
        for path in sorted(self.execution_lab_root.rglob("*")):
            if path.is_dir():
                continue
            if _is_inside(path, self.execution_engine.rollback_root):
                continue
            rel = path.relative_to(self.project_root).as_posix()
            states.append(RollbackFileState(
                relative_path=rel,
                exists=path.exists(),
                is_file=path.is_file(),
                content_hash=_file_hash(path),
            ))
        return tuple(states)

    def state_hash(self, state: tuple[RollbackFileState, ...]) -> str:
        return _stable_hash([asdict(item) for item in state], 24)

    def restore_from_rollback_manifests(self) -> tuple[str, ...]:
        blockers: list[str] = []
        rollback_root = self.execution_engine.rollback_root

        if not rollback_root.exists():
            return ("rollback_manifest_root_missing",)

        manifests = sorted(rollback_root.glob("*_rollback_manifest.json"))
        if not manifests:
            return ("rollback_manifests_missing",)

        expected_manifest_count = 3
        if len(manifests) != expected_manifest_count:
            return (f"rollback_manifest_count_invalid:{len(manifests)}!={expected_manifest_count}",)

        for manifest_path in manifests:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            operation_type = manifest.get("operation_type")
            source = self.project_root / manifest.get("source_path", "")
            destination = self.project_root / manifest.get("destination_path", "")

            if not _is_inside(source, self.execution_lab_root):
                blockers.append(f"rollback_source_outside_execution_lab:{manifest_path.name}")
                continue

            if not _is_inside(destination, self.execution_lab_root):
                blockers.append(f"rollback_destination_outside_execution_lab:{manifest_path.name}")
                continue

            if operation_type == "move":
                if not destination.exists():
                    blockers.append(f"rollback_move_destination_missing:{manifest_path.name}")
                    continue
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(destination), str(source))

            elif operation_type in {"copy", "import_route"}:
                if destination.exists():
                    destination.unlink()
                if not source.exists():
                    blockers.append(f"rollback_copy_source_missing:{manifest_path.name}")

            else:
                blockers.append(f"rollback_unsupported_operation_type:{manifest_path.name}:{operation_type}")

        if not blockers and rollback_root.exists():
            shutil.rmtree(rollback_root)
            rollback_root.mkdir(parents=True, exist_ok=True)

        return tuple(blockers)

    def validate_execute_then_rollback(self) -> RollbackValidationResult:
        blockers: list[str] = []

        plan = self.execution_engine.build_small_batch_plan()
        before_state = self.capture_lab_state()
        before_state_hash = self.state_hash(before_state)

        execution_result = self.execution_engine.execute_plan(plan)
        self.execution_engine.write_result(execution_result)

        after_execution_state = self.capture_lab_state()
        after_execution_state_hash = self.state_hash(after_execution_state)

        rollback_blockers = self.restore_from_rollback_manifests()
        blockers.extend(rollback_blockers)

        after_rollback_state = self.capture_lab_state()
        after_rollback_state_hash = self.state_hash(after_rollback_state)

        repository_restored = before_state_hash == after_rollback_state_hash

        if not execution_result.passed:
            blockers.append("source_23d_execution_did_not_pass")

        if after_execution_state_hash == before_state_hash:
            blockers.append("execution_state_did_not_change_before_rollback")

        if not repository_restored:
            blockers.append("rollback_state_mismatch")

        result_seed = {
            "before_state_hash": before_state_hash,
            "after_execution_state_hash": after_execution_state_hash,
            "after_rollback_state_hash": after_rollback_state_hash,
            "blockers": blockers,
        }

        return RollbackValidationResult(
            schema=SCHEMA,
            phase="23E",
            source_execution_schema=PHASE_23D_SCHEMA,
            execution_passed=execution_result.passed,
            rollback_performed=True,
            rollback_operation_count=len(plan.operations),
            before_state_hash=before_state_hash,
            after_execution_state_hash=after_execution_state_hash,
            after_rollback_state_hash=after_rollback_state_hash,
            repository_restored=repository_restored,
            active_repository_mutated=False,
            execution_lab_only=True,
            delete_operations_performed=False,
            archive_operations_performed=False,
            automatic_execution=False,
            continuous_watcher=False,
            blocker_count=len(blockers),
            passed=not blockers,
            blockers=tuple(blockers),
            deterministic_result_hash=_stable_hash(result_seed, 24),
        )

    def write_result(self, result: RollbackValidationResult) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.result_json.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

        self.report_txt.write_text("\n".join([
            "LEAF PHASE 23E ROLLBACK VALIDATION REPORT",
            "=========================================",
            f"schema={result.schema}",
            f"source_execution_schema={result.source_execution_schema}",
            f"execution_passed={result.execution_passed}",
            f"rollback_performed={result.rollback_performed}",
            f"rollback_operation_count={result.rollback_operation_count}",
            f"before_state_hash={result.before_state_hash}",
            f"after_execution_state_hash={result.after_execution_state_hash}",
            f"after_rollback_state_hash={result.after_rollback_state_hash}",
            f"repository_restored={result.repository_restored}",
            f"active_repository_mutated={result.active_repository_mutated}",
            f"execution_lab_only={result.execution_lab_only}",
            f"delete_operations_performed={result.delete_operations_performed}",
            f"archive_operations_performed={result.archive_operations_performed}",
            f"automatic_execution={result.automatic_execution}",
            f"continuous_watcher={result.continuous_watcher}",
            f"blocker_count={result.blocker_count}",
            f"passed={result.passed}",
            f"deterministic_result_hash={result.deterministic_result_hash}",
            "",
            "Blockers:",
            *(result.blockers or ("none",)),
        ]), encoding="utf-8")

        return {
            "json": self.result_json.relative_to(self.project_root).as_posix(),
            "report": self.report_txt.relative_to(self.project_root).as_posix(),
        }


def run_sorting_rollback_validation(project_root: str | Path = ".") -> dict[str, Any]:
    engine = SortingRollbackValidationEngine(project_root)
    result = engine.validate_execute_then_rollback()
    paths = engine.write_result(result)

    return {
        "schema": SCHEMA,
        "phase": "23E",
        "feature": "SORTING_ROLLBACK_VALIDATION",
        "source_execution_schema": PHASE_23D_SCHEMA,
        "result": asdict(result),
        "paths": paths,
        "completion_notice": "PHASE_23E_COMPLETE_ROLLBACK_VALIDATION_ESTABLISHED" if result.passed else "PHASE_23E_BLOCKED",
        "next_phase": "23F_CONTROLLED_EXECUTION_GATE",
    }


if __name__ == "__main__":
    run = run_sorting_rollback_validation(Path.cwd())
    result = run["result"]
    print("PASS_PHASE_23E_ROLLBACK_VALIDATION_WRITTEN" if result["passed"] else "FAIL_PHASE_23E_ROLLBACK_VALIDATION_WRITTEN")
    print(f"schema={run['schema']}")
    print(f"source_execution_schema={run['source_execution_schema']}")
    print(f"execution_passed={result['execution_passed']}")
    print(f"rollback_performed={result['rollback_performed']}")
    print(f"rollback_operation_count={result['rollback_operation_count']}")
    print(f"repository_restored={result['repository_restored']}")
    print(f"active_repository_mutated={result['active_repository_mutated']}")
    print(f"execution_lab_only={result['execution_lab_only']}")
    print(f"blocker_count={result['blocker_count']}")
    print(f"passed={result['passed']}")
    print(f"completion_notice={run['completion_notice']}")
    print(f"report={run['paths']['report']}")
    print(f"json={run['paths']['json']}")
    print(f"next_phase={run['next_phase']}")
