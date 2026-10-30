from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_SORTING_CONTINUOUS_WATCH_READINESS_PHASE_23G_V1"

PHASE_23F_GATE = "_leaf_artifacts/workspace_architecture/phase_23f/sorting_controlled_execution_master_gate_phase_23f.json"


@dataclass(frozen=True)
class ContinuousWatchReadiness:
    schema: str
    phase: str
    phase_23f_passed: bool
    controlled_execution_available: bool
    continuous_watch_ready_for_future_design: bool
    continuous_watcher_enabled: bool
    automatic_execution_enabled: bool
    filesystem_monitor_created: bool
    polling_loop_created: bool
    background_task_created: bool
    mutation_allowed_from_watch: bool
    manual_approval_required: bool
    rollback_required: bool
    small_batch_required: bool
    controlled_execution_gate_required: bool
    readiness_only: bool
    blocker_count: int
    blockers: tuple[str, ...]
    deterministic_readiness_hash: str


def _stable_hash(payload: Any, length: int = 24) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


class ContinuousWatchReadinessEvaluator:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.out_dir = self.project_root / "_leaf_artifacts" / "workspace_architecture" / "phase_23g"
        self.result_json = self.out_dir / "sorting_continuous_watch_readiness_phase_23g.json"
        self.report_txt = self.out_dir / "sorting_continuous_watch_readiness_phase_23g.txt"

    def evaluate(self) -> ContinuousWatchReadiness:
        blockers: list[str] = []

        phase_23f = _read_json(self.project_root / PHASE_23F_GATE)
        result = phase_23f.get("result", {})

        phase_23f_passed = phase_23f.get("passed") is True
        controlled_execution_available = result.get("controlled_execution_available") is True

        if not phase_23f:
            blockers.append("phase_23f_gate_missing")
        if not phase_23f_passed:
            blockers.append("phase_23f_not_passed")
        if not controlled_execution_available:
            blockers.append("controlled_execution_not_available")

        for key in [
            "automatic_execution_enabled",
            "continuous_watcher_enabled",
            "delete_operations_enabled",
            "archive_operations_enabled",
            "active_repository_mutation_default",
        ]:
            if result.get(key) is not False:
                blockers.append(f"unsafe_23f_flag_not_false:{key}={result.get(key)}")

        for key in [
            "rollback_required",
            "manual_approval_required",
            "small_batch_required",
            "execution_lab_validation_required",
        ]:
            if result.get(key) is not True:
                blockers.append(f"required_23f_flag_not_true:{key}={result.get(key)}")

        ready = not blockers

        seed = {
            "phase_23f_passed": phase_23f_passed,
            "controlled_execution_available": controlled_execution_available,
            "watch_ready": ready,
            "watch_enabled": False,
            "blockers": blockers,
        }

        return ContinuousWatchReadiness(
            schema=SCHEMA,
            phase="23G",
            phase_23f_passed=phase_23f_passed,
            controlled_execution_available=controlled_execution_available,
            continuous_watch_ready_for_future_design=ready,
            continuous_watcher_enabled=False,
            automatic_execution_enabled=False,
            filesystem_monitor_created=False,
            polling_loop_created=False,
            background_task_created=False,
            mutation_allowed_from_watch=False,
            manual_approval_required=True,
            rollback_required=True,
            small_batch_required=True,
            controlled_execution_gate_required=True,
            readiness_only=True,
            blocker_count=len(blockers),
            blockers=tuple(blockers),
            deterministic_readiness_hash=_stable_hash(seed, 24),
        )

    def write_result(self, result: ContinuousWatchReadiness) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.result_json.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

        self.report_txt.write_text("\n".join([
            "LEAF PHASE 23G CONTINUOUS WATCH READINESS REPORT",
            "================================================",
            f"schema={result.schema}",
            f"phase_23f_passed={result.phase_23f_passed}",
            f"controlled_execution_available={result.controlled_execution_available}",
            f"continuous_watch_ready_for_future_design={result.continuous_watch_ready_for_future_design}",
            f"continuous_watcher_enabled={result.continuous_watcher_enabled}",
            f"automatic_execution_enabled={result.automatic_execution_enabled}",
            f"filesystem_monitor_created={result.filesystem_monitor_created}",
            f"polling_loop_created={result.polling_loop_created}",
            f"background_task_created={result.background_task_created}",
            f"mutation_allowed_from_watch={result.mutation_allowed_from_watch}",
            f"manual_approval_required={result.manual_approval_required}",
            f"rollback_required={result.rollback_required}",
            f"small_batch_required={result.small_batch_required}",
            f"controlled_execution_gate_required={result.controlled_execution_gate_required}",
            f"readiness_only={result.readiness_only}",
            f"blocker_count={result.blocker_count}",
            f"deterministic_readiness_hash={result.deterministic_readiness_hash}",
            "",
            "Blockers:",
            *(result.blockers or ("none",)),
        ]), encoding="utf-8")

        return {
            "json": self.result_json.relative_to(self.project_root).as_posix(),
            "report": self.report_txt.relative_to(self.project_root).as_posix(),
        }


def run_continuous_watch_readiness(project_root: str | Path = ".") -> dict[str, Any]:
    evaluator = ContinuousWatchReadinessEvaluator(project_root)
    result = evaluator.evaluate()
    paths = evaluator.write_result(result)

    return {
        "schema": SCHEMA,
        "phase": "23G",
        "feature": "CONTINUOUS_WATCH_READINESS",
        "result": asdict(result),
        "paths": paths,
        "completion_notice": "PHASE_23G_COMPLETE_CONTINUOUS_WATCH_READINESS_ESTABLISHED" if result.continuous_watch_ready_for_future_design else "PHASE_23G_BLOCKED",
        "next_phase": "23H_SORTING_ACTIVATION_COMPLETION",
    }


if __name__ == "__main__":
    run = run_continuous_watch_readiness(Path.cwd())
    result = run["result"]
    print("PASS_PHASE_23G_CONTINUOUS_WATCH_READINESS_WRITTEN" if result["continuous_watch_ready_for_future_design"] else "FAIL_PHASE_23G_CONTINUOUS_WATCH_READINESS_WRITTEN")
    print(f"schema={run['schema']}")
    print(f"phase_23f_passed={result['phase_23f_passed']}")
    print(f"controlled_execution_available={result['controlled_execution_available']}")
    print(f"continuous_watch_ready_for_future_design={result['continuous_watch_ready_for_future_design']}")
    print(f"continuous_watcher_enabled={result['continuous_watcher_enabled']}")
    print(f"automatic_execution_enabled={result['automatic_execution_enabled']}")
    print(f"filesystem_monitor_created={result['filesystem_monitor_created']}")
    print(f"polling_loop_created={result['polling_loop_created']}")
    print(f"background_task_created={result['background_task_created']}")
    print(f"mutation_allowed_from_watch={result['mutation_allowed_from_watch']}")
    print(f"blocker_count={result['blocker_count']}")
    print(f"completion_notice={run['completion_notice']}")
    print(f"report={run['paths']['report']}")
    print(f"json={run['paths']['json']}")
    print(f"next_phase={run['next_phase']}")
