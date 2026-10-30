from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_SORTING_CONTROLLED_EXECUTION_GATE_PHASE_23F_V1"

PHASE_23C_GATE = "_leaf_artifacts/workspace_architecture/phase_23c/sorting_safe_execution_sandbox_gate_phase_23c.json"
PHASE_23D_GATE = "_leaf_artifacts/workspace_architecture/phase_23d/sorting_small_batch_execution_gate_phase_23d.json"
PHASE_23E_GATE = "_leaf_artifacts/workspace_architecture/phase_23e/sorting_rollback_validation_gate_phase_23e.json"


@dataclass(frozen=True)
class ControlledExecutionAvailability:
    schema: str
    phase: str
    phase_23c_passed: bool
    phase_23d_passed: bool
    phase_23e_passed: bool
    controlled_execution_available: bool
    automatic_execution_enabled: bool
    continuous_watcher_enabled: bool
    delete_operations_enabled: bool
    archive_operations_enabled: bool
    rollback_required: bool
    manual_approval_required: bool
    small_batch_required: bool
    active_repository_mutation_default: bool
    execution_lab_validation_required: bool
    blocker_count: int
    blockers: tuple[str, ...]
    deterministic_gate_hash: str


def _stable_hash(payload: Any, length: int = 24) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


class ControlledExecutionGate:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.out_dir = self.project_root / "_leaf_artifacts" / "workspace_architecture" / "phase_23f"
        self.result_json = self.out_dir / "sorting_controlled_execution_gate_phase_23f.json"
        self.report_txt = self.out_dir / "sorting_controlled_execution_gate_phase_23f.txt"

    def evaluate(self) -> ControlledExecutionAvailability:
        blockers: list[str] = []

        phase_23c = _read_json(self.project_root / PHASE_23C_GATE)
        phase_23d = _read_json(self.project_root / PHASE_23D_GATE)
        phase_23e = _read_json(self.project_root / PHASE_23E_GATE)

        phase_23c_passed = phase_23c.get("passed") is True
        phase_23d_passed = phase_23d.get("passed") is True
        phase_23e_passed = phase_23e.get("passed") is True

        if not phase_23c:
            blockers.append("phase_23c_gate_missing")
        if not phase_23d:
            blockers.append("phase_23d_gate_missing")
        if not phase_23e:
            blockers.append("phase_23e_gate_missing")

        if not phase_23c_passed:
            blockers.append("phase_23c_not_passed")
        if not phase_23d_passed:
            blockers.append("phase_23d_not_passed")
        if not phase_23e_passed:
            blockers.append("phase_23e_not_passed")

        c_summary = phase_23c.get("summary", {})
        d_result = phase_23d.get("result", {})
        e_result = phase_23e.get("result", {})

        safety_pairs = {
            "phase_23c_real_filesystem_mutation_performed": c_summary.get("real_filesystem_mutation_performed"),
            "phase_23c_automatic_execution": c_summary.get("automatic_execution"),
            "phase_23c_continuous_watcher": c_summary.get("continuous_watcher"),
            "phase_23d_active_repository_mutated": d_result.get("active_repository_mutated"),
            "phase_23d_delete_operations_performed": d_result.get("delete_operations_performed"),
            "phase_23d_archive_operations_performed": d_result.get("archive_operations_performed"),
            "phase_23d_automatic_execution": d_result.get("automatic_execution"),
            "phase_23d_continuous_watcher": d_result.get("continuous_watcher"),
            "phase_23e_active_repository_mutated": e_result.get("active_repository_mutated"),
            "phase_23e_delete_operations_performed": e_result.get("delete_operations_performed"),
            "phase_23e_archive_operations_performed": e_result.get("archive_operations_performed"),
            "phase_23e_automatic_execution": e_result.get("automatic_execution"),
            "phase_23e_continuous_watcher": e_result.get("continuous_watcher"),
        }

        for key, value in safety_pairs.items():
            if value is not False:
                blockers.append(f"unsafe_flag_not_false:{key}={value}")

        if c_summary.get("manual_approval_required") is not True:
            blockers.append("phase_23c_manual_approval_not_required")

        if d_result.get("execution_lab_only") is not True:
            blockers.append("phase_23d_execution_lab_only_not_true")

        if e_result.get("repository_restored") is not True:
            blockers.append("phase_23e_repository_not_restored")

        controlled_execution_available = not blockers

        seed = {
            "phase_23c_passed": phase_23c_passed,
            "phase_23d_passed": phase_23d_passed,
            "phase_23e_passed": phase_23e_passed,
            "blockers": blockers,
            "controlled_execution_available": controlled_execution_available,
        }

        return ControlledExecutionAvailability(
            schema=SCHEMA,
            phase="23F",
            phase_23c_passed=phase_23c_passed,
            phase_23d_passed=phase_23d_passed,
            phase_23e_passed=phase_23e_passed,
            controlled_execution_available=controlled_execution_available,
            automatic_execution_enabled=False,
            continuous_watcher_enabled=False,
            delete_operations_enabled=False,
            archive_operations_enabled=False,
            rollback_required=True,
            manual_approval_required=True,
            small_batch_required=True,
            active_repository_mutation_default=False,
            execution_lab_validation_required=True,
            blocker_count=len(blockers),
            blockers=tuple(blockers),
            deterministic_gate_hash=_stable_hash(seed, 24),
        )

    def write_result(self, result: ControlledExecutionAvailability) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.result_json.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

        self.report_txt.write_text("\n".join([
            "LEAF PHASE 23F CONTROLLED EXECUTION GATE",
            "=======================================",
            f"schema={result.schema}",
            f"phase_23c_passed={result.phase_23c_passed}",
            f"phase_23d_passed={result.phase_23d_passed}",
            f"phase_23e_passed={result.phase_23e_passed}",
            f"controlled_execution_available={result.controlled_execution_available}",
            f"automatic_execution_enabled={result.automatic_execution_enabled}",
            f"continuous_watcher_enabled={result.continuous_watcher_enabled}",
            f"delete_operations_enabled={result.delete_operations_enabled}",
            f"archive_operations_enabled={result.archive_operations_enabled}",
            f"rollback_required={result.rollback_required}",
            f"manual_approval_required={result.manual_approval_required}",
            f"small_batch_required={result.small_batch_required}",
            f"active_repository_mutation_default={result.active_repository_mutation_default}",
            f"execution_lab_validation_required={result.execution_lab_validation_required}",
            f"blocker_count={result.blocker_count}",
            f"deterministic_gate_hash={result.deterministic_gate_hash}",
            "",
            "Blockers:",
            *(result.blockers or ("none",)),
        ]), encoding="utf-8")

        return {
            "json": self.result_json.relative_to(self.project_root).as_posix(),
            "report": self.report_txt.relative_to(self.project_root).as_posix(),
        }


def run_controlled_execution_gate(project_root: str | Path = ".") -> dict[str, Any]:
    gate = ControlledExecutionGate(project_root)
    result = gate.evaluate()
    paths = gate.write_result(result)

    return {
        "schema": SCHEMA,
        "phase": "23F",
        "feature": "CONTROLLED_EXECUTION_GATE",
        "result": asdict(result),
        "paths": paths,
        "completion_notice": "PHASE_23F_COMPLETE_CONTROLLED_EXECUTION_GATE_ESTABLISHED" if result.controlled_execution_available else "PHASE_23F_BLOCKED",
        "next_phase": "23G_CONTINUOUS_WATCH_READINESS",
    }


if __name__ == "__main__":
    run = run_controlled_execution_gate(Path.cwd())
    result = run["result"]
    print("PASS_PHASE_23F_CONTROLLED_EXECUTION_GATE_WRITTEN" if result["controlled_execution_available"] else "FAIL_PHASE_23F_CONTROLLED_EXECUTION_GATE_WRITTEN")
    print(f"schema={run['schema']}")
    print(f"phase_23c_passed={result['phase_23c_passed']}")
    print(f"phase_23d_passed={result['phase_23d_passed']}")
    print(f"phase_23e_passed={result['phase_23e_passed']}")
    print(f"controlled_execution_available={result['controlled_execution_available']}")
    print(f"automatic_execution_enabled={result['automatic_execution_enabled']}")
    print(f"continuous_watcher_enabled={result['continuous_watcher_enabled']}")
    print(f"delete_operations_enabled={result['delete_operations_enabled']}")
    print(f"archive_operations_enabled={result['archive_operations_enabled']}")
    print(f"blocker_count={result['blocker_count']}")
    print(f"completion_notice={run['completion_notice']}")
    print(f"report={run['paths']['report']}")
    print(f"json={run['paths']['json']}")
    print(f"next_phase={run['next_phase']}")
